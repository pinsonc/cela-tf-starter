
import os
import csv
from pathlib import Path

# deletes all files in a directory
def clean(directory):
    rootdir = Path(directory)
    # Return a list of regular files only, not directories
    file_list = [f for f in rootdir.glob('**/*') if f.is_file()]

    file_count = 0

    for cur in file_list:
        os.remove(cur)
