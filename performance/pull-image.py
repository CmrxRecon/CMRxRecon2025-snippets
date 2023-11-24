import os
import json

json_path = ['/home/guanli/CMRxRecon-Test-phase-scoring/performance/teams/mapping',
             "/home/guanli/CMRxRecon-Test-phase-scoring/performance/teams/cine"]
for p in json_path:
    for i in os.listdir(p):
        full_path = os.path.join(p, i)
        with open(full_path, 'rb') as f:
            info = json.load(f)
        os.system(f'docker pull {info["image"]}')
