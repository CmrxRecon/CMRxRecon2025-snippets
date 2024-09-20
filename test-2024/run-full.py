import docker
import os
import json
import logging
from docker.models.containers import Container
from docker.types.containers import DeviceRequest

import status
from t4u import mail

FULL_SET = True

logger = logging.getLogger(__name__)


class ExecutationRequest:
    def __init__(self, request: dict) -> None:
        self._data = request
        r = request
        self.uid = r['uid']
        self.type = r['type']
        self.image = r['image']
        self.team_name = r['team_name']
        self.email = r['email']
        self.synapse_address = r['synapse_address']

    def json(self):
        return self._data


client = docker.from_env()
api = client.api

def pull_and_run(r: ExecutationRequest, workplace: os.PathLike, gpu_id="0"):
    image = r.image
    # image = 'dev.passer.zyheal.com:8087/passer/passer-vtk-rendering-server:CI-devel_latest'
    logger.info(f'pulling image: {image}')
    client.images.pull(image)
    FIXED_NAME = f'test-phase-{r.uid}'
    container = client.containers.run(image,
                         volumes=[
                             f'{input_dir}:/input/:ro',
                             f'{workplace}/infer:/output'
                         ],
                         name=FIXED_NAME,
                        stderr=True,
                        network_mode=None,
                        shm_size='32g',
                        #  remove=True,
                        # tty=True,
                        detach=True,
                         device_requests=[DeviceRequest(device_ids=[gpu_id], capabilities=[['gpu']])],
                        #  entrypoint='ls -alh /input'
                         )
    # print(str(logs_bytes, 'utf-8'))
    container.wait()
    c = client.containers.get(FIXED_NAME)
    logs_bytes = container.logs()
    # print(str(logs_bytes))
    with open(os.path.join(workplace, 'infer.log'), 'wb') as f:
        f.write(bytes(f'image: {image}\n {r.json()}\n', encoding='utf8'))
        f.write(logs_bytes)
        # if len(logs_bytes) != 0: return
    container.remove()

def score(r: ExecutationRequest, workplace: os.PathLike):
    image = 'dev.passer.zyheal.com:8087/playground/cmrxrecon2024-validation:latest'
    name = f'score-{r.uid}'
    container = client.containers.run(image,
                        volumes=[
                            f'{repo_dir}:/app/:ro',
                            f'{storage_dir}:/CMRxRecon2024:ro',
                            f'{workplace}/infer:/output'
                        ],
                        name=name,
                    stderr=True,
                    network_mode=None,
                    shm_size='32g',
                    #  remove=True,
                    # tty=True,
                    detach=True,
                    entrypoint=entrypoint
                        )
    container.wait()
    c = client.containers.get(name)
    logs_bytes = container.logs()
    # print(str(logs_bytes))
    with open(os.path.join(workplace, 'score.log'), 'wb') as f:
        f.write(bytes(f'image: {image}\n {r.json()}\n', encoding='utf8'))
        f.write(logs_bytes)
        # if len(logs_bytes) != 0: return
    container.remove()
    assert os.path.isfile(os.path.join(workplace, 'infer', 'Result/result.csv'))


def notification(request: ExecutationRequest):
    r = request
    # TODO send notification and the logs as attachment

    content = f"""
Dear {r.team_name}:
    
    Your Test request executed, request id: {r.uid}.

Best regards,
CMRxRecon Team
                   """
    e = os.environ
    server = mail.get_smtp_server(e['SMTP_SERVER'], int(e['SMTP_PORT']), 
                                 e['EMAIL'], e['EMAIL_TOKEN'])
    mail.send_text_mail(e['EMAIL'], 'xuziqiang@zyheal.com',
                   f'Test result notification', content,
                   server)



if __name__ == '__main__':
    import sys
    # 通过命令行指定python
    uid = sys.argv[1]
    gpu_id = sys.argv[2]


    storage_dir = '/mnt/raid/CMRxRecon2024'
    repo_dir = '/home/guanli/CMRxRecon2024-snippets'
    if FULL_SET:
        input_dir = f'{storage_dir}/test-input'
        output_dir = f'{storage_dir}/test-output'
        state_json = f'{repo_dir}/test-2024/test-data/full-status.json'    
    else:
        input_dir = f'{storage_dir}/input-demo/input'
        output_dir = f'{storage_dir}/output-demo'
        state_json = f'{repo_dir}/test-2024/test-data/status.json'
    
    s = status.load(state_json)
    with open(f'./test-data/json/{uid}.json') as f:
        request = json.load(f)
    r = ExecutationRequest(request)

    if FULL_SET:
        entrypoint = f'python /app/evaluation-2024/Test_Score2024.py -g /CMRxRecon2024/test-GT/ -i /CMRxRecon2024/test-input/ -t {r.type[:5]} -o /output'
    else:
        entrypoint = f'python /app/evaluation-2024/Test_Score2024.py -g /CMRxRecon2024/test-GT/ -i /CMRxRecon2024/input-demo/input/ -t {r.type[:5]} -o /output'
        
    uid = str(r.uid)
    workplace = os.path.join(output_dir, uid)
    os.makedirs(workplace, exist_ok=True)
    info = s.get(uid, {'status': 'unknown'})
    s[uid] = info
    current_status = info['status']
    if current_status == status.UNKNOWN:
        pull_and_run(r, workplace, gpu_id=gpu_id)
        s = status.load(state_json)
        info = s.get(uid, {'status': status.INFERED})
        s[uid] = info
        status.save(s, state_json)

    current_status = s[uid]['status']
    if current_status == status.INFERED:
        score(r, workplace)
        s = status.load(state_json)
        info = s.get(uid, {'status': status.SCORED})
        s[uid] = info
        status.save(s, state_json)

    current_status = s[uid]['status']
    if current_status == status.SCORED:
        # TODO notification
        # notification(request)
        # s[r.uid]['status'] = status.NOTIFIED
        # status.save(s)
        pass
