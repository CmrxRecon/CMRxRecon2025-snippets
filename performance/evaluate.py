import argparse
import json
import docker
import nvidia_smi
from datetime import datetime


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
    # 初始化 NVIDIA 管理库
    nvidia_smi.nvmlInit()

    # # 获取 NVIDIA GPU 数量
    # device_count = nvidia_smi.nvmlDeviceGetCount()

    # # 遍历每个 GPU
    # for i in range(device_count):
    # 根据索引获取 GPU
    handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)

    # 获取 GPU 的使用率
    utilization = nvidia_smi.nvmlDeviceGetUtilizationRates(handle)
    gpu_utilization = utilization.gpu

    # 获取 GPU 的显存占用
    memory_info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
    memory_used = memory_info.used

    # 打印 GPU 的使用率和显存占用
    print(f"GPU Utilization: {gpu_utilization}%")
    print(f"GPU Memory Used: {memory_used} bytes")

    # 关闭 NVIDIA 管理库
    nvidia_smi.nvmlShutdown()
    return gpu_utilization, memory_used

def monitor(log_path: str, pid_path: str):
    assert not os.path.exists(log_path)
    f = open(log_path, 'w')
    f.write('version: 1.0')

    while os.path.exists(pid_path):
        cpu_r, ram_r = get_cpu_load()
        gpu_r, gpu_ram = get_gpu_load()
        f.write(f'{datetime.now()}, {cpu_r}, {ram_r}, {gpu_r}, {gpu_ram}')
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
    # os.system(docker_cmd)

    # 在pid文件中写入容器id
    os.system(f'touch {pid_path}')

    # 在后台执行
    monitor(log_path, pid_path)

    # stop monitor
    os.remove(pid_path)
