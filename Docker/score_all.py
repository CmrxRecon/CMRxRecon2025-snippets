import os
import json


root = '/home/guanli/CMRxRecon-Test-phase-scoring/performance/nfs-perf/tasks'
error_record = open('error-team.txt', 'w')
for i in os.listdir(root):
    full_path: str = os.path.join(root, i)
    if not full_path.endswith('.json'):
        continue
    with open(full_path, 'r') as f:
        team_info = json.load(f)
    
    team_workplace = f'{full_path}.workplace/output/Submission'
    if os.path.exists(f'{full_path}.workplace/output/MultiCoil') \
        or os.path.exists(f'{full_path}.workplace/output/SingleCoil') :
        team_workplace = f'{full_path}.workplace/output/'

    file_ = ''
    type_ = 'Cine'
    if i.find('mapping') != -1:
        type_ = 'Mapping'

    team_name = team_info['team_name']
    script = '/home/guanli/CMRxRecon-Test-phase-scoring/Docker/score_with_std_enhance.py'

    tmp_dir = f'tmp/score_all/{team_name}-{type_}'
    os.makedirs(tmp_dir, exist_ok=True)
    cmd = f'cd "{tmp_dir}" && python {script} -f {team_workplace} -g /host-data/GT-test/ -t {type_} -r "result.pkl" && cd -'
    res = os.system(cmd)
    if res != 0:
        error_record.write(f'{team_name}\n')
error_record.close()
# python score_with_std_enhance.py -f tmp/hellopipu-cine.json.workplace/output/Submission/ -g /host-data/GT-test/ -t Cine -r "results.pkl"
