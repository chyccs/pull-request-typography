# src/get_num_square.py
import os

dir_path = "./"

files = []
for (root, directories, files) in os.walk(dir_path):
    for d in directories:
        d_path = os.path.join(root, d)

    for file in files:
        file_path = os.path.join(root, file)
        files.append(file_path)

print(f"::set-output name=files::{files}")

# get the input and convert it to int
num = os.environ.get("INPUT_NUM")
if num:
    try:
        num = int(num)
    except Exception:
        exit('ERROR: the INPUT_NUM provided ("{}") is not an integer'.format(num))
else:
    num = 1

# to set output, print to shell in following syntax
print(f"::set-output name=num_squared::{num ** 2}")
