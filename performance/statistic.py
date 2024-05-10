import os
import json
import numpy as np
from datetime import datetime


p = '/home3/HWGroup/do-not-touch-daryl/perf/tasks'
for file in os.listdir(p):
    if not file.endswith('.json'):
        continue
    with open(os.path.join(p, file), 'r') as f:
        task = json.load(f)
    if file.find('cine') > -1:
        task_type = 'cine'
    else: 
        task_type = 'mapping'
    log_file = os.path.join(p, f'{file}.workplace/log.txt')
    with open(log_file, 'r') as f:
        f.readline()
        line1 = f.readline()
        lines = f.readlines()
        time_start = lines[0].split(',')[0]
        time_stop = lines[-2].split(',')[0]
        time_comsume = lines[-2].split(',')[1]
        # cpu累计计算时间
        start = datetime.fromisoformat(time_start)
        stop = datetime.fromisoformat(time_stop)

        arr = np.zeros((len(lines) - 1, 3))
        i = 0
        # print(task["team_name"])
        for l in lines[:-1]:
            log = l.split(',')   
            assert len(log) == 6
            mem = float(log[3])
            gpu_r = float(log[4])
            gpu_ram = float(log[5])
            arr[i, 0] = mem
            arr[i, 1] = gpu_r
            arr[i, 2] = gpu_ram
            i += 1
        # print(f'{arr[:, 0].max()}, {arr[:, 1].mean()}, {arr[:, 2].max()}')

        # 推理总时间
        # {datetime} {cpu_usage}, {mem_usage}, {max_mem_usage}, {gpu_r}, {gpu_ram}
        print(f'{task_type}, {task["team_name"]}, {stop.timestamp() - start.timestamp()}, {time_comsume}, '
              f'{arr[:, 0].max()}, {arr[:, 1].mean()}, {arr[:, 2].max()}')
