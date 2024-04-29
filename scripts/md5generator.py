"""
@author: Wang Zian
"""
import os
import hashlib
import sys


def generate_md5(input_folder, output_file):
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, input_folder)
                md5_hash = hashlib.md5()
                with open(file_path, "rb") as f2:
                    # Read and update hash string value in blocks of 4K
                    for byte_block in iter(lambda: f2.read(4096), b""):
                        md5_hash.update(byte_block)
                md5_digest = md5_hash.hexdigest()
                msg = f"{relative_path}-{md5_digest}\n"
                print(msg)
                f.write(msg)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python md5generator.py input_folder md5.txt")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_file = sys.argv[2]
    generate_md5(input_folder, output_file)
    print("MD5 file generated successfully.")
