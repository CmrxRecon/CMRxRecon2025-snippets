from io import TextIOWrapper
from datetime import datetime

class Logger:
    def __init__(self, target: TextIOWrapper):
        self._target = target

    def log(self, msg: str):
        msg = f'{datetime.now().isoformat()}: {msg}\n'
        print(msg)
        self._target.writelines([msg])

    @classmethod
    def to_file(cls, path: str):
        f = open(path, 'w')
        return cls(f)
    
    def close(self):
        self._target.flush()
        self._target.close()

if __name__ == '__main__':
    logger = Logger.to_file('test.txt')
    logger.log('hello')
    logger.close()