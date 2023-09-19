import sys                                                                                                                                                                                                                                                                                                                                                                
import json                                                                                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                                                                                          
def json_to_csv(json_file):                                                                                                                                                                                                                                                                                                                                               
    # 读取 JSON 文件并转换为 DataFrame                                                                                                                                                                                                                                                                                                                                    
    with open(json_file, 'rb') as f:                                                                                                                                                                                                                                                                                                                                      
        data = json.load(f)                                                                                                                                                                                                                                                                                                                                               
    head = ""                                                                                                                                                                                                                                                                                                                                                             
    line = ""
    for k, v in data.items():
        head += f'{k}, '
        line += f'{v}, '
    print(head)
    print(line)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('请提供输入的 JSON 文件路径作为命令行参数')
    else:
        json_file = sys.argv[1]
        json_to_csv(json_file)
