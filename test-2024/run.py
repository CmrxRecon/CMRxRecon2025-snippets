import docker
import os
import json
import logging
from docker.models.containers import Container
from docker.types.containers import DeviceRequest

import status
from t4u import mail



logger = logging.getLogger(__name__)


class ExecutationRequest:
    def __init__(self, request: dict) -> None:
        r = request
        self.uid = r['uid']
        self.type = r['type']
        self.image = r['image']
        self.team_name = r['team_name']
        self.email = r['email']
        self.synapse_address = r['synapse_address']


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
        f.write(bytes(f'image: {image}\n', encoding='utf8'))
        f.write(logs_bytes)
        # if len(logs_bytes) != 0: return
    container.remove()


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

    input_dir = '/mnt/raid/CMRxRecon2024/input-demo/input'
    output_dir = '/home/guanli/CMRxRecon2024-snippets/test-2024/output'
    
    s = status.load()
    with open(f'./test-data/json/{uid}.json') as f:
        request = json.load(f)
    r = ExecutationRequest(request)
    uid = str(r.uid)
    workplace = os.path.join(output_dir, uid)
    os.makedirs(workplace, exist_ok=True)
    info = s.get(uid, {'status': 'unknown'})
    s[uid] = info
    current_status = info['status']
    if current_status == status.UNKNOWN:
        pull_and_run(r, workplace, gpu_id=gpu_id)
        s[uid]['status'] = status.INFERED
        status.save(s)

    current_status = s[uid]['status']
    if current_status == status.INFERED:
        # TODO score
        # s[r.uid]['status'] = status.SCORED
        # status.save(s)
        pass

    current_status = s[uid]['status']
    if current_status == status.SCORED:
        # TODO notification
        # notification(request)
        # s[r.uid]['status'] = status.NOTIFIED
        # status.save(s)
        pass
