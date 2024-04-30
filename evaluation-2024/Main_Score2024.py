#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 24 2024

@author: Mobbyjj

This works for the validation dataset. 
"""

import numpy as np
import os
from loadFun import loadmat
import pandas as pd
import time
from Evaluation import calmetric
import gzip
import tarfile
import zipfile
import rarfile
import json

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
    return mean_psnr, mean_ssim, mean_nmse, num_success_files, num_total_files

def ungz(filename, output_dir):
    gz_file = gzip.GzipFile(filename)
    out_filename = os.path.join(output_dir, filename[:-3])
    with open(out_filename, "wb+") as file:
        file.write(gz_file.read())
    return out_filename

def untar(filename, output_dir):
    tar = tarfile.open(filename)
    tar.extractall(path=output_dir)
    tar.close()
    return output_dir

def unzip(filename, output_dir):
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    return output_dir

def unrar(filename, output_dir):
    with rarfile.RarFile(filename) as rar_ref:
        rar_ref.extractall(output_dir)
    return output_dir

def unzipfile(fpth, output_dir):
# TODO: 我把源文件的remove注释掉了
    if '.' in fpth:
        suffix = fpth.split('.')[-1]
        if suffix == 'gz':
            new_filename = ungz(fpth, output_dir)
            if new_filename.split('.')[-1] == 'tar':
                folder_dir = untar(new_filename, output_dir)
                os.remove(new_filename)
        elif suffix == 'tar':
            folder_dir = untar(fpth, output_dir)
            # os.remove(fpth)
        elif suffix == 'zip':
            folder_dir = unzip(fpth, output_dir)
            # os.remove(fpth)
        elif suffix == 'rar':
            folder_dir = unrar(fpth, output_dir)
            # os.remove(fpth)
        else:
            raise Exception('Not supported format')
        return folder_dir
    else:
        raise Exception('Not supported format')

def main(submission_unzipped_path: str,
         tasknum: int = 1):
    # for validation, we read the random mapping from a csv file
    #TODO: 修改这个mapping映射的路径 & 存储路径。
    # REPLY: 可以暂时用着这个目录
    dataframe = pd.read_csv('/home/wangfw/CMRxRecon2024Organizer/Code/newID.csv')
    rootdir = '/home2/Raw_data/MICCAIChallenge2024'

    # placeholder for all metrics.
    Metrics = ['PSNR', "SSIM", "NMSE"]
    PSNR_ALL, SSIM_ALL, NMSE_ALL = [], [], []
    # dict to write 
    scores = {}
    # for task 2, no Flow2d and BlackBlood
    if tasknum == 1:
        Modality = ['Tagging', 'Mapping', 'Cine', 'Aorta', 'BlackBlood', 'Flow2d']
        undermasklist = ["Uniform4", "Uniform8", "Uniform10"]
    elif tasknum == 2:
        Modality = ['Tagging', 'Mapping', 'Cine', 'Aorta']
        undermasklist = ["ktUniform", "ktGaussian", "ktRadial"]

    SetType = 'ValidationSet'
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
        # get the cases from the subdir
        # REPLY： 这个路径从命令行参数取得
        gtpath = os.path.join(rootdir, 
                            'GroundTruth4Ranking', 
                            'MultiCoil', 
                            Modal, 
                            SetType, 
                            Taskx)
        cases = os.listdir(gtpath)
        for Case in cases:
            gtdir = os.path.join(gtpath, Case)
            print(Case)
            if SetType == 'ValidationSet':
            # get validation random 
                Under1 = dataframe.loc[dataframe['file_info22'] == Case, 'file_info23'].item()
                Under2 = dataframe.loc[dataframe['file_info22'] == Case, 'file_info24'].item()
                Under3 = dataframe.loc[dataframe['file_info22'] == Case, 'file_info25'].item()
            else:
                Under1 = Case
                Under2 = Case
                Under3 = Case
            Underlist = [Under1, Under2, Under3]
            for file in filelist:
                if not os.path.exists(os.path.join(gtdir, (file + '.mat'))):
                    print('No file exist for ground truth: ', Modal, Case, file)
                    new_frame = pd.DataFrame({
                        'Case': [Case],
                        'File': [file],
                        'KUS': [np.nan],
                        'PSNR': [np.nan],
                        'SSIM': [np.nan],
                        'NMSE': [np.nan],
                        'Comments': 'No file exist for ground truth'
                    }, index=[0])
                    ranks = pd.concat([ranks, new_frame], ignore_index=True)
                    continue
                gtmat = loadmat(os.path.join(gtdir, (file + '.mat')))
                sorted_masklist = []
                for under, undermask in zip(Underlist, undermasklist):
                    underdir = os.path.join(rootdir, 
                                            'ChallengeData',
                                            'MultiCoil',
                                            Modal,
                                            SetType,
                                            Mask_Task,
                                            under)
                    masklist = os.listdir(underdir)
                    masklist = [mask for mask in masklist if mask.startswith(file + '_mask_' + undermask)]
                    masklist = [mask.split('_')[-1].split('.')[0] for mask in masklist]
                    sorted_masklist.append(masklist[0])
                for mask, undercase in zip(sorted_masklist, Underlist):
                    # change the casenum due to different suffix. 
                    recondir = os.path.join(submission_unzipped_path,
                                            Modal, 
                                            SetType, 
                                            Taskx, 
                                            undercase)
                    filename = file + '_kus_' + mask + '.mat'
                    # get the mask from the suffix
                    # check wether the file exists，if not exist, give nan to all metrics
                    if not os.path.exists(os.path.join(recondir, filename)):
                        print('No file exist for case, mask: ', Case, mask)
                        new_frame = pd.DataFrame({
                            'Case': [Case],
                            'File': [file],
                            'KUS': [mask],
                            'PSNR': [np.nan],
                            'SSIM': [np.nan],
                            'NMSE': [np.nan],
                            'Comments': 'No file exist for recon'
                        }, index=[0])
                        ranks = pd.concat([ranks, new_frame], ignore_index=True)
                        continue
                    reconmat = loadmat(os.path.join(recondir, filename))
                    # calculate the metrics
                    # check whether the data is with the same dim
                    if gtmat.shape != reconmat.shape:
                        print('The shape of the GT and Recon is not the same for case, mask: ', Case, mask)
                        new_frame = pd.DataFrame({
                            'Case': [Case],
                            'File': [file],
                            'KUS': [mask],
                            'PSNR': [np.nan],
                            'SSIM': [np.nan],
                            'NMSE': [np.nan],
                            'Comments': 'The shape of the GT and Recon is not the same'
                        }, index=[0])
                        ranks = pd.concat([ranks, new_frame], ignore_index=True)
                        continue
                    psnr, ssim, nmse = calmetric(gtmat, reconmat)
                    # take mean for each case
                    psnr_mean = np.mean(psnr)
                    ssim_mean = np.mean(ssim)
                    nmse_mean = np.mean(nmse)
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

    # save the ranks to the csv file
    # TODO: 可以换个结果存储路径？
    # REPLY：命令行参数给定了output folder，存放在output目录下即可
    resultdir = submission_unzipped_path
    filename = 'Result_' + Taskx + '.csv'
    ranks.to_csv(os.path.join(resultdir,filename))

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
    num_all_files = ranks.loc[ranks['Comments']!= "No file exist for ground truth"].shape[0]
    num_good_files = ranks.loc[ranks['Comments'].isna()].shape[0]

    scores["Num_Files"] = str(num_good_files) + "/" + str(num_all_files)
    
    for modality in Modality:
        for undermask in undermasklist:
            mean_psnr, mean_ssim, mean_nmse, num_success_files, num_total_files = statis_metrics_and_num_files(ranks = ranks, modal = modality.lower(), kus = undermask)
            key = f"num_file_{modality}_{undermask}"
            scores[key] = str(num_success_files) + "/" + str(num_total_files)
            metric_values = [mean_psnr, mean_ssim, mean_nmse]
            PSNR_ALL.append(mean_psnr)
            SSIM_ALL.append(mean_ssim)
            NMSE_ALL.append(mean_nmse)
            for metric, metric_value in zip(Metrics, metric_values):
                key = f"{modality}_{undermask}_{metric}"
                scores[key] = metric_value
                # store the metrics_value for final calculation 
    
    # Calculate the means of PSNR_ALL, SSIM_ALL, and NMSE_ALL
    mean_psnr_all = round(np.nanmean(PSNR_ALL),4)
    mean_ssim_all = round(np.nanmean(SSIM_ALL),4)
    mean_nmse_all = round(np.nanmean(NMSE_ALL),4)

    # Assign these mean values to the 'All' category in the scores dictionary
    scores[f"All_PSNR"] = mean_psnr_all
    scores[f"All_SSIM"] = mean_ssim_all
    scores[f"All_NMSE"] = mean_nmse_all
    # save the scores as a json

    with open(os.path.join(submission_unzipped_path,"results.json"), "w") as out:
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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the submission file or folder')
    parser.add_argument('-g', '--grundtruth', type=str, required=True, help='Path to the GroundTruth')
    parser.add_argument('-t', '--task', type=str, required=True, help='Task1 or Task2')
    parser.add_argument('-o', '--output', type=str, required=False, default='./', help='Path of output saving folder')
    args = parser.parse_args()

    rootpath = "/home2/Raw_data/MICCAIChallenge2024"
    # task_num = 2 # 1/2
    if args.task.find('1') != -1:
        task_num = 1
    else:
        task_num =2
    sub_zip_filename = "SubmissionTask" + str(task_num) + ".zip"
    submission_zip_path = os.path.join(rootpath, "ChallengeResult",sub_zip_filename)
    submission_zip_path = args.input
    # TODO: 我修改了原本函数，会生成一个新的文件夹，适应task1/task2, 不过因为最后所有都是submission.zip, 后续需要修改。
    # REPLY：输出目录通过命令行参数传入
    output_dir = os.path.join(rootpath, "ChallengeResult", ("SubmissionTask" + str(task_num)))
    output_dir = args.output

    start_time = time.time()
    unzipfile(submission_zip_path, output_dir)
    main(submission_unzipped_path = output_dir, tasknum = task_num)
    end_time = time.time()
    # 计算代码执行时间
    execution_time = end_time - start_time
    print("代码执行时间：", execution_time, "秒")
