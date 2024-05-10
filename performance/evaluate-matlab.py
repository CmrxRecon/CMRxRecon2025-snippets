# date cpu ram, gpu_ratio, gpu_ram
from evaluate import get_gpu_load, get_host_load
import pynvml
import time
import os
from datetime import datetime


# 初始化 NVML
pynvml.nvmlInit()


with open('wangfei-log.txt', 'a+') as f:
    f.write('version: 1.0\n')

cpu_camulate = 0
while os.path.exists('/host-data/fei_wang_matlab/v3/CMRxRecon-flyer-Task1-v3/wangfei.pid'):
    interval = 3
    cpu_r, memory_usage = get_host_load(interval)

    # 获取设备句柄，固定使用第一张显卡
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    gpu_r, gpu_ram = get_gpu_load(handle)
    cpu_camulate += (cpu_r * interval * 40) # 40个cpu核心
    with open('wangfei-log.txt', 'a+') as f:
        log = f'{datetime.now()}, {cpu_camulate}, {memory_usage}, {memory_usage}, ' \
              f'{gpu_r}, {gpu_ram}\n'
        print(log)
        f.write(log)

pynvml.nvmlShutdown()

with open('wangfei-log.txt', 'a+') as f:
    f.write(f'>>> End of log. {datetime.now()}')
