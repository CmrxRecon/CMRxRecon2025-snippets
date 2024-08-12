import docker
import os
import json
import logging
from docker.models.containers import Container
from docker.types.containers import DeviceRequest

from t4u import mail


logger = logging.getLogger(__name__)

input_dir = '/cmrxrecon2024/input'
output_dir = '/cmrxrecon2024/output'


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

def pull_and_run(r: ExecutationRequest):
    image = r.image
    # image = 'dev.passer.zyheal.com:8087/passer/passer-vtk-rendering-server:CI-devel_latest'
    logger.info(f'pulling image: {image}')
    client.images.pull(image)
    logs_bytes = client.containers.run(image,
                         volumes=[
                             f'{input_dir}:/input:ro',
                             f'{output_dir}/{r.uid}/infer:/output'
                         ],
                         remove=True,
                         device_requests=[DeviceRequest(device_ids=0, capabilities=[['gpu']])]
                        #  entrypoint='ls -alh /input'
                         )
    print(str(logs_bytes, 'utf-8'))


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
    with open('/home/xuzq/git/CMRxRecon2024-snippets/test-2024/test-data/json/1.json') as f:
        r = json.load(f)
    request = ExecutationRequest(r)
    pull_and_run(request)
    # TODO score
    # notification(request)
