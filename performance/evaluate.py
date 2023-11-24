import argparse
import json
import docker
from docker.models.containers import Container
import pynvml
from datetime import datetime
import threading
import time


def get_container_load(container: Container):
    stats = container.stats(stream=False)

    ## 从统计信息中提取负载数据
    # 容器从启动到现在使用的CPU时间(纳秒  -->  秒)
    cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage'] * 1e-9

    # 这一时刻的内存消耗
    memory_usage = stats['memory_stats']['usage'] / 1024 / 1024
    # 一段时间使用的最大内存量
    max_memory_usage = stats['memory_stats']['max_usage'] / 1024 / 1024


    # 打印负载信息
    print(f"CPU Usage: {cpu_usage}s")
    print(f"Memory Usage: {memory_usage} MB")
    return cpu_usage, memory_usage, max_memory_usage, stats


def get_gpu_load(handle):
    # 获取显存使用情况
    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    # print(f"Memory Usage - Total: {mem_info.total / 1024 / 1024} MB, Used: {mem_info.used / 1024 / 1024} MB")
    memory_used = mem_info.used / 1024 / 1024

    # 获取 GPU 使用率
    gpu_utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
    # print(f'GPU mem: {mem_info}, utilization: {gpu_utilization}')

    # 打印 GPU 的使用率和显存占用
    print(f"GPU Utilization: {gpu_utilization.gpu}%")
    print(f"GPU Memory Used: {memory_used} MB")

    return gpu_utilization.gpu, memory_used


def monitor(log_path: str, pid_path: str):
    assert not os.path.exists(log_path)
    f = open(log_path, 'w')
    f.write('version: 1.0')

    while os.path.exists(pid_path):
        # cpu_r, ram_r = get_cpu_load()
        cpu_r, ram_r = 0, 0
        gpu_r, gpu_ram = get_gpu_load()
        f.write(f'{datetime.now()}, {cpu_r}, {ram_r}, {gpu_r}, {gpu_ram}\n')
        f.flush()
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
    workplace_abs = os.path.abspath(workplace)
    container_stats_dir = os.path.join(workplace_abs, 'container_stats')
    os.mkdir(workplace)
    os.mkdir(container_stats_dir)
    pid_path = f'{workplace}/pid'

    # start monitor, gather HPC load
    log_path = os.path.join(workplace, 'log.txt')
    
    # start docker
    client: docker.DockerClient = docker.from_env()
    container_config = {
        'image': info['image'],
        'device_requests':[
            docker.types.DeviceRequest(device_ids=['0'], capabilities=[['gpu']])
        ],
        'network_mode': 'none',
        # 使用参赛团队中使用的最大值
        'shm_size': '32G',  
        'detach': True,
        'volumes': {
            '/host-data/input-test': {'bind': '/input', 'mode': 'ro'},
            f'{workplace_abs}/output': {'bind': '/output', 'mode': 'rw'},
            # '/host-data/test.sh': {'bind': '/docker-entrypoint.sh'}
            },
    }
    container: Container = client.containers.run(**container_config)
    print(container.name, container.id)
    container.start()
    
    assert not os.path.exists(log_path)
    f = open(log_path, 'w')
    f.write('version: 1.0\n')
    count = 0
    
    # 初始化 NVML
    pynvml.nvmlInit()
    # 获取设备句柄，固定使用第一张显卡
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)

    while container.status != 'exit':
        time.sleep(3)
        print('status:', container.status)
        try:
            cpu_usage, mem_usage, max_mem_usage, stats = get_container_load(container)
        except KeyError:
            break
        gpu_r, gpu_ram = get_gpu_load(handle)
        if count % 10 == 0:
            # 每间隔10次采样记录一次详尽的性能监控
            with open(os.path.join(container_stats_dir, f'{count}.json'), 'w') as stats_file:
                json.dump(stats, stats_file)
        f.write(f'{datetime.now()}, {cpu_usage}, {mem_usage}, {max_mem_usage}, {gpu_r}, {gpu_ram}\n')
        f.flush()
        count += 1

    pynvml.nvmlShutdown()
    f.write(f'>>> End of log. {datetime.now()}')
    f.close()
    # container.remove()
    exit(0)

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

