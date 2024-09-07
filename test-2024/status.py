import json


UNKNOWN = 'unknown'
INFERED = 'infered'
SCORED = 'scored' 
NOTIFIED = 'notified'


def load():
    with open('./test-data/status.json') as f:
        return json.load(f)


def save(status: dict):
    with open('./test-data/status.json', 'w') as f:
        json.dump(status, f, ensure_ascii=False, indent=4)
