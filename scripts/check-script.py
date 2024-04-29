"""
@author: Wang Zian
"""
import os
import hashlib
import argparse


def read_md5_file(md5_file):
    md5_dict = {}
    with open(md5_file, 'r') as f:
        for line in f:
            relative_path, md5_value = line.strip().split('-', 1)
            md5_dict[relative_path] = md5_value
    return md5_dict


def check_md5(input_folder, md5_file, allow_missing):
    md5_dict = read_md5_file(md5_file)
    missing_files = 0
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), input_folder)
            if file_path in md5_dict:
                md5_hash = hashlib.md5()
                full_path = os.path.join(root, file)
                with open(full_path, "rb") as f:
                    # Read and update hash string value in blocks of 4K
                    for byte_block in iter(lambda: f.read(4096), b""):
                        md5_hash.update(byte_block)
                if md5_hash.hexdigest() == md5_dict[file_path]:
                    print(f'{full_path} check passed')
                else:
                    print(f"MD5 mismatch: {file_path}")
            else:
                print(f"File not found in MD5 file: {file_path}")
                missing_files += 1
    if missing_files > allow_missing:
        print(f"Too many missing files: {missing_files}, allowed: {allow_missing}")
    else:
        print(f"Files checked successfully, {missing_files} are missed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check MD5 of files in a folder.')
    parser.add_argument('--allow-missing', type=int, default=0, help='Number of missing files allowed.')
    parser.add_argument('--md5', required=True, help='Path to the MD5 file.')
    parser.add_argument('input_folder', help='Path to the folder containing files to check.')

    args = parser.parse_args()

    check_md5(args.input_folder, args.md5, args.allow_missing)
