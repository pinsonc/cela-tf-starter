import os
import csv
import math
from pathlib import Path

# gets the distribution that should go in each subset
def get_dist(directory, training_percent, validation_percent, test_percent):
    rootdir = Path(directory)

    cur = directory

    with open(cur, 'r') as f:
        csv_reader = csv.reader(f, delimiter = ',')
        row_count = sum(1 for row in csv_reader)
        print('There are {} entries in {}.'.format(row_count,cur))
        # remove this if for larger datasets
        if row_count == 2:
            print('\tPut {} entries in Training\n\tPut {} entries in Validation\n\tPut {} entries in Test'.format(2,0,0))
            return 2, 0, 0
        else:
            training_num = math.ceil(row_count * training_percent)
            validation_num = round(row_count * validation_percent)
            test_num = math.floor(row_count * test_percent)
            print('\tPut {} entries in Training\n\tPut {} entries in Validation\n\tPut {} entries in Test'.format(training_num,validation_num,test_num))
            return training_num, validation_num, test_num
