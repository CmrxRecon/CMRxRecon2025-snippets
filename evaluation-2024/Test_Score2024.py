# python 3.10.14
# -*- coding: utf-8 -*-
"""
Created on August 24 2024

@author: Mobbyjj

This works for the test dataset. No cropping on the GT data.
"""

import numpy as np
import os
from loadFun import loadmat
import pandas as pd
import time
from Evaluation import calmetric
import json
import argparse


def statis_metrics_and_num_files(ranks: pd.DataFrame,
                                 modal:str, 
                                 kus:str):
    '''
    This files read the different modalites and the undersampling tragectories
    then do the statistics
    '''
    if modal == 'mapping':
        df = ranks.loc[(ranks['File'].str.contains('map')) & (ranks['KUS'].str.contains(kus))]
    elif modal == 'cine':
        df = ranks.loc[(ranks['File'].str.contains('cine')) & (ranks['KUS'].str.contains(kus))]
    elif modal == 'aorta':
        df = ranks.loc[(ranks['File'].str.contains('aorta')) & (ranks['KUS'].str.contains(kus))]
    else:
        df = ranks.loc[(ranks['File'] == modal) & (ranks['KUS'].str.contains(kus))]
    # get the num of validated 
    num_total_files = df.loc[df['Comments'] != 'No file exist for ground truth'].shape[0]
    num_success_files = df.loc[df['Comments'].isna()].shape[0]
    # leave 4 decimals
    mean_psnr = round(df['PSNR'].mean(),4)
    mean_ssim = round(df['SSIM'].mean(),4)
    mean_nmse = round(df['NMSE'].mean(),4)
    # add weighted metrics, sum up the metrics with success cases over total cases
    if num_success_files == 0:
        adj_psnr = np.nan
        adj_ssim = np.nan
        adj_nmse = np.nan
    else:
        adj_psnr = round(df['PSNR'].loc[df['Comments'].isna()].sum() /num_total_files, 4)
        adj_ssim = round(df['SSIM'].loc[df['Comments'].isna()].sum() /num_total_files, 4)
        adj_nmse = round(df['NMSE'].loc[df['Comments'].isna()].sum() /num_total_files, 4) 
    return adj_psnr, adj_ssim, adj_nmse, mean_psnr, mean_ssim, mean_nmse, num_success_files, num_total_files



def main(input_dir: str,
         gt_dir: str,
         result_output_path: str,
         tasknum: int = 1):
    # read the quality control file
    # placeholder for all metrics.
    # Metrics = ["PSNR", "SSIM", "NMSE", "adj.PSNR", "adj.SSIM", "adj.NMSE"]
    Metrics = ["PSNR", "SSIM", "NMSE"]
    PSNR_ALL, SSIM_ALL, NMSE_ALL = [], [], []
    PSNR_ADJ, SSIM_ADJ, NMSE_ADJ = [], [], []
    # add placeholder for adj metrics
    # PSNR_ADJ, SSIM_ADJ, NMSE_ADJ = [], [], []

    # dict to write 
    scores = {}
    # for task 2, no Flow2d and BlackBlood
    if tasknum == 1:
        Modality = ['Tagging', 'Mapping', 'Cine', 'Aorta', 'BlackBlood', 'Flow2d']
        undermasklist = ["Uniform4", "Uniform8", "Uniform10"]
    elif tasknum == 2:
        Modality = ['Tagging', 'Mapping', 'Cine', 'Aorta']
        undermasklist = ["ktUniform", "ktGaussian", "ktRadial"]

    SetType = 'TestSet'
    Taskx = 'Task' + str(tasknum)
    Mask_Task = 'Mask_Task' + str(tasknum)
    # list all the files under task subdir.

    # placeholder for ranks 
    ranks = pd.DataFrame(columns = ['Case', 'File', 'KUS', 'PSNR', 'SSIM', 'NMSE','Comments'])

    for Modal in Modality:
        # get the list
        modal = Modal.lower()
        if modal == 'cine':
            filelist = ['cine_sax', 'cine_lax', 'cine_lvot']
        elif modal == 'mapping': 
            filelist = ['T1map', 'T2map']
        elif modal == 'aorta':
            filelist = ['aorta_sag', 'aorta_tra']
        else:
            filelist = [modal]

        gtpath = os.path.join(gt_dir, 
                              'GroundTruth4RankingNoCropping', 
                              'MultiCoil', 
                              Modal, 
                              SetType, 
                              Taskx)
        # get the input dir, because some subs may be missing for demo test
        # use the input dir to get the cases
        underpath = os.path.join(input_dir,
                                 Modal,
                                 SetType,
                                 Mask_Task)         
        cases = os.listdir(underpath)
        # get the cases from gtpath startswith P.
        for Case in cases:
            gtdir = os.path.join(gtpath, Case)
            # for gt, bad cases have already been excluded
            # get the file list 
            for file in filelist:
                if not os.path.exists(os.path.join(gtdir, (file + '.mat'))):
                    print('GT case is excluded according to quality control: ', Modal, Case, file)
                    new_frame = pd.DataFrame({
                        'Case': [Case],
                        'File': [file],
                        'KUS': [np.nan],
                        'PSNR': [np.nan],
                        'SSIM': [np.nan],
                        'NMSE': [np.nan],
                        'Comments': 'GT case is excluded according to quality control'
                    }, index=[0])
                    ranks = pd.concat([ranks, new_frame], ignore_index=True)
                    continue
                gtmat = loadmat(os.path.join(gtdir, (file + '.mat')))
                # for test, get the reconstructed files from the input dir
                sorted_masklist = []
                # get the file list from the input dir
                underdir = os.path.join(underpath,
                                        Case)
                masklist = os.listdir(underdir)
                # sort the data startwith the file name
                masklist = [mask for mask in masklist if mask.startswith(file + '_mask_')]
                sorted_masklist = [mask.split('_')[-1].split('.')[0] for mask in masklist]
                # TODO: for the test, not three of each mask are generated, we should read all the undersampled_files
                for mask in sorted_masklist:
                    # change the casenum due to different suffix. 
                    # add the comments whether the recondir exists or not
                    recondir = os.path.join(result_output_path,
                                            Modal, 
                                            SetType, 
                                            Taskx, 
                                            Case)
                    if not os.path.exists(recondir):
                        print('No recon dir or recon dir does not follow {}/{}/{}/{}.'.format(Modal, SetType, Taskx, Case))
                        new_frame = pd.DataFrame({
                            'Case': [Case],
                            'File': [file],
                            'KUS': [mask],
                            'PSNR': [np.nan],
                            'SSIM': [np.nan],
                            'NMSE': [np.nan],
                            'Comments': 'No recon dir or recon dir does not follow {}/{}/{}/{}.'.format(Modal, SetType, Taskx, Case)
                        }, index=[0])
                        ranks = pd.concat([ranks, new_frame], ignore_index=True)
                        continue
                    filename = file + '_kus_' + mask + '.mat'
                    # get the mask from the suffix
                    # check wether the file exists，if not exist, give nan to all metrics
                    if not os.path.exists(os.path.join(recondir, filename)):
                        print('No file exist for recon, mask: ', Case, mask)
                        new_frame = pd.DataFrame({
                            'Case': [Case],
                            'File': [file],
                            'KUS': [mask],
                            'PSNR': [np.nan],
                            'SSIM': [np.nan],
                            'NMSE': [np.nan],
                            'Comments': 'Recon dir exists, but recon file misses.',
                        }, index=[0])
                        ranks = pd.concat([ranks, new_frame], ignore_index=True)
                    else: 
                        try:
                            reconmat = loadmat(os.path.join(recondir, filename))
                        except:
                            print('Error in reading the file, mask: ', Case, mask)
                            new_frame = pd.DataFrame({
                                'Case': [Case],
                                'File': [file],
                                'KUS': [mask],
                                'PSNR': [np.nan],
                                'SSIM': [np.nan],
                                'NMSE': [np.nan],
                                'Comments': 'Recon file corrupts.',
                            }, index=[0])
                            ranks = pd.concat([ranks, new_frame], ignore_index=True)
                            continue
                        # calculate the metrics
                        # check whether the data is with the same dim
                        if gtmat.shape != reconmat.shape:
                            print('Undersampled {} {} got different shape of GT {} and recon {}'.format(mask, Case, gtmat.shape, reconmat.shape))
                            new_frame = pd.DataFrame({
                                'Case': [Case],
                                'File': [file],
                                'KUS': [mask],
                                'PSNR': [np.nan],
                                'SSIM': [np.nan],
                                'NMSE': [np.nan],
                                'Comments': 'Shapes of GT {}, recon {}'.format(gtmat.shape, reconmat.shape),
                            }, index=[0])
                            ranks = pd.concat([ranks, new_frame], ignore_index=True)
                        else:
                            try: 
                                psnr, ssim, nmse = calmetric(gtmat, reconmat)
                                # take mean for each case
                                psnr_mean = np.nanmean(psnr)
                                ssim_mean = np.nanmean(ssim)
                                nmse_mean = np.nanmean(nmse)
                                # save the metrics to the pandas frame
                                new_frame = pd.DataFrame({
                                    'Case': [Case],
                                    'File': [file],
                                    'KUS': [mask],
                                    'PSNR': [psnr_mean],
                                    'SSIM': [ssim_mean],
                                    'NMSE': [nmse_mean]
                                }, index=[0])        
                                ranks = pd.concat([ranks, new_frame], ignore_index=True)
                            except:
                                print('The recon matrix is not saved as magnitude', Case, mask)
                                new_frame = pd.DataFrame({
                                    'Case': [Case],
                                    'File': [file],
                                    'KUS': [mask],
                                    'PSNR': [np.nan],
                                    'SSIM': [np.nan],
                                    'NMSE': [np.nan],
                                    'Comments': 'The recon matrix is not saved as magnitude.',
                                }, index=[0])
                                ranks = pd.concat([ranks, new_frame], ignore_index=True)
                                continue

    # save the ranks to the csv file
    # REPLY：命令行参数给定了output folder，存放在output目录下即可
    # FW: 如果先前已经区分了task1/task2, 可以删掉这边的Taskx 和下面的results.json格式一致
    resultdir = os.path.join(result_output_path,'Result')
    if not os.path.exists(resultdir):
        os.makedirs(resultdir)
    ranks.to_csv(os.path.join(resultdir, 'result.csv'))

    # here calculate the json file with statistical output. 
    # read the csv and save them to a json files with:
    # fot task 1 we will validate using
    # {Modality}_{undermasklist}_{Metrics}:
    # {num_file}_{Modality}_{undermasklist}
    # {All}_{Metrics}: mean
    # for task 2 we will validate using
    # {Modality}_{undermasklist}_{Metrics}:
    # {num_file}_{Modality}_{undermasklist}
    # {All}_{Metrics}: 
    num_all_files = ranks.loc[ranks['Comments']!= "GT case is excluded according to quality control"].shape[0]
    num_good_files = ranks.loc[ranks['Comments'].isna()].shape[0]

    scores["Num_Files"] = str(num_good_files) + "/" + str(num_all_files)
    
    for modality in Modality:
        for undermask in undermasklist:
            adj_psnr, adj_ssim, adj_nmse, mean_psnr, mean_ssim, mean_nmse, num_success_files, num_total_files = statis_metrics_and_num_files(ranks = ranks, modal = modality.lower(), kus = undermask)
            key = f"num_file_{modality}_{undermask}"
            scores[key] = str(num_success_files) + "/" + str(num_total_files)
            # metric_values = [mean_psnr, mean_ssim, mean_nmse, adj_ssim]
            metric_values = [mean_psnr, mean_ssim, mean_nmse, adj_psnr, adj_ssim, adj_nmse]
            PSNR_ALL.append(mean_psnr)
            SSIM_ALL.append(mean_ssim)
            NMSE_ALL.append(mean_nmse)
            PSNR_ADJ.append(adj_psnr)
            SSIM_ADJ.append(adj_ssim)
            NMSE_ADJ.append(adj_nmse)
            for metric, metric_value in zip(Metrics, metric_values[:3]):
                key = f"{modality}_{undermask}_{metric}"
                scores[key] = metric_value
                # store the metrics_value for final calculation 
    
    # Calculate the means of PSNR_ALL, SSIM_ALL, and NMSE_ALL
    mean_psnr_all = round(np.nanmean(PSNR_ALL),4)
    mean_ssim_all = round(np.nanmean(SSIM_ALL),4)
    mean_nmse_all = round(np.nanmean(NMSE_ALL),4)

    mean_psnr_adj = round(np.nanmean(PSNR_ADJ),4)
    mean_ssim_adj = round(np.nanmean(SSIM_ADJ),4)
    mean_nmse_adj = round(np.nanmean(NMSE_ADJ),4)

    # Assign these mean values to the 'All' category in the scores dictionary
    scores[f"All_PSNR"] = mean_psnr_all
    scores[f"All_SSIM"] = mean_ssim_all
    scores[f"All_NMSE"] = mean_nmse_all
    scores[f"All_adj.PSNR"] = mean_psnr_adj
    scores[f"All_adj.SSIM"] = mean_ssim_adj
    scores[f"All_adj.NMSE"] = mean_nmse_adj
    # save the scores as a json

    with open(os.path.join(resultdir, "results.json"), "w") as out:
        for k, v in scores.items():
            print(type(v), v)
            if type(v) != str and np.isnan(v):
                scores[k] = None
        results = {
            "submission_status": "SCORED",
            **scores
        }
        out.write(json.dumps(results, indent=4))



if __name__ == "__main__":
    # input_before_recon (default): /input/...
    # output_after_recon (default): /output/...
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--groundtruth', type=str, required=True, help='Path to the GroundTruth')
    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the Input')
    parser.add_argument('-t', '--task', type=str, required=True, help='Task1 or Task2')
    parser.add_argument('-o', '--output', type=str, required=True, default='./', help='Path of output saving folder')
    args = parser.parse_args()

    # task_num = 2 # 1/2
    if args.task.find('1') != -1:
        task_num = 1
    else:
        task_num = 2
    
    # FW: Done.
    output_dir = args.output
    gt_dir = args.groundtruth
    input_dir = args.input

    start_time = time.time()
    main(input_dir = input_dir, gt_dir = gt_dir, result_output_path = output_dir, tasknum = task_num)
    end_time = time.time()
    # 计算代码执行时间
    execution_time = end_time - start_time
    print("代码执行时间：", execution_time, "秒")