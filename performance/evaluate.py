import argparse
import json
import docker
import pynvml
from datetime import datetime
import threading
import time


def get_cpu_load():

    # 创建 Docker 客户端
    client = docker.from_env()

    # 容器名称或 ID
    container_name_or_id = 'your-container-name-or-id'

    # 获取容器对象
    container = client.containers.get(container_name_or_id)

    # 获取容器的统计信息
    stats = container.stats(stream=False)

    # 从统计信息中提取负载数据
    cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
    memory_usage = stats['memory_stats']['usage']

    # 打印负载信息
    print(f"CPU Usage: {cpu_usage}")
    print(f"Memory Usage: {memory_usage}")
    return cpu_usage, memory_usage

def get_gpu_load():
    # 初始化 NVML
    pynvml.nvmlInit()

    # 获取设备句柄
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)

    # 获取显卡名称
    name = pynvml.nvmlDeviceGetName(handle)

    # 获取显存使用情况
    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    print(f"Memory Usage - Total: {mem_info.total / 1024 / 1024} MB, Used: {mem_info.used / 1024 / 1024} MB")
    memory_used = mem_info.used / 1024 / 1024

    # 获取 GPU 使用率
    gpu_utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

    # 清理 NVML
    pynvml.nvmlShutdown()

    # 打印 GPU 的使用率和显存占用
    print(f"GPU Utilization: {gpu_utilization}%")
    print(f"GPU Memory Used: {memory_used} bytes")

    return gpu_utilization, memory_used

def monitor(log_path: str, pid_path: str):
    assert not os.path.exists(log_path)
    f = open(log_path, 'w')
    f.write('version: 1.0')

    while os.path.exists(pid_path):
        # cpu_r, ram_r = get_cpu_load()
        cpu_r, ram_r = 0, 0
        gpu_r, gpu_ram = get_gpu_load()
        f.write(f'{datetime.now()}, {cpu_r}, {ram_r}, {gpu_r}, {gpu_ram}\n')
        time.sleep(1)
    # timestamp, GPU_LOAD, GPU_memory, CPU_LOAD, Memory
    f.close()


if __name__ == '__main__':
    import sys
    import os

    assert len(sys.argv) == 2
    team_json = sys.argv[1]
    assert os.path.exists(team_json)
    with open(team_json, 'r') as f:
        info = json.load(f)
    workplace = f'{team_json}.workplace'
    os.mkdir(workplace)
    pid_path = f'{workplace}/pid'

    # start monitor, gather HPC load
    log_path = os.path.join(workplace, 'log.txt')
    
    # start docker
    docker_cmd = info['docker_cmd']
    print('This is the command to be executed: ', docker_cmd)

    # 在pid文件中写入容器id
    os.system(f'touch {pid_path}')

    # 在后台执行
    thread = threading.Thread(target=monitor, args=(log_path, pid_path))
    thread.start()
    os.system(docker_cmd)
    # stop monitor
    os.remove(pid_path)
    thread.join()

