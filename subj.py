'''
this script takes the csv output from a .xslx file and outputs the procedure,
start frame and end frame to its own file in folder framecsv

all procedures are also given their own csv with start and end frames in Data/ALL

csv's should be placed in folder rawcsv

To make them all uniform, I created a second row that has all of the names of the procedures
where they are capitalized throughout. That means that the label is actually row 1 and not row 0.

Change subject to choose which one you want.
P5 is subject 1, P6 is subject 2, etc. so this code adds 4 automatically to whichever file you'd like

'''

import csv
import datetime as dt
import time
from pathlib import Path
import ntpath
import clean
import count
import boto
import boto3

#subject = int(input('Input which subject you would like to process: '))
subject = int(input('How many subjects are there? '))
train_percent = float(input('Enter (in decimal form) what percent of the data should go to training: '))
validation_percent = float(input('Enter (in decimal form) what percent of the data should go to validation: '))
test_percent = float(input('Enter (in decimal form) what percent of the data should go to testing: '))

destination = 'Data/ALL'
frame_rate = 30000.0/1001.0 # change to frame rate (used ffprobe to find the exact)
# this is 29.97 fps

s3c = boto3.client('s3')
# s3c.download_file('cela-input','framedata/S1C2/','S1C2000001.jpg')
conn = boto.connect_s3()
destbucket = conn.get_bucket('cela-input')
destbucket.copy_key('framedata/Data/ALL/S1C2000001.jpg', 'cela-input', 'framedata/S1C2/S1C2000001.jpg')

prev_end = 1

for i in range(1,subject+1):
    # the csv files are 4 more than the subject they represent so adding 4 to subject is needed
    print("\nP{}.csv".format(i+4))
    line_count = 0
    with open('rawcsv/P{}.csv'.format(i+4)) as csv_file:
        with open('framecsv/P{}frame.csv'.format(i+4), 'w') as output:
            csv_reader = csv.reader(csv_file, delimiter = ',')
            file_writer = csv.writer(output, delimiter=',')
            for row in csv_reader:
                # use this to skip the header row
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}'.format())
                    file_writer.writerow([row[1],row[2],row[3]])
                elif len(row[1]) != 0:
                    start_time = 0.0
                    end_time = 0.0
                    if len(row[2]) != 0:
                        x = dt.datetime.strptime(row[2][11:], '%H:%M:%S:%f') # get start time to microseconds from the row
                        start_time = dt.timedelta(hours=x.hour,minutes=x.minute,seconds=x.second,microseconds=x.microsecond).total_seconds() # convert to seconds
                    if len(row[3]) != 0:
                        x = dt.datetime.strptime(row[3][11:], '%H:%M:%S:%f') #same as above for end time
                        end_time = dt.timedelta(hours=x.hour,minutes=x.minute,seconds=x.second,microseconds=x.microsecond).total_seconds()
                    if line_count == 1:
                        origin_time = start_time # save the first start time as the first frame of the video
                    start_frame = (start_time - origin_time) * frame_rate # calculate what frame based on the time
                    end_frame = (end_time - origin_time) * frame_rate

                    print('\t{0} starts at {1:.4f} and ends at {2:.4f}.'.format(row[1],start_frame,end_frame))
                    file_writer.writerow([row[1],start_frame,end_frame]) # output procedure and start and end frame
                    with open('Data/S{}C2/{}.csv'.format(i,row[1]), 'a') as procedure_file:
                        proc_writer = csv.writer(procedure_file, delimiter=',')
                        proc_writer.writerow([start_frame,end_frame]) # output start and end frame to its specific procedure csv in ~/ALL
                line_count += 1
            print(f'Processed {line_count} lines.')

'''
clean.clean('Data/Training')
clean.clean('Data/Validation')
clean.clean('Data/Test')

rootdir = Path('Data/ALL')
# Return a list of regular files only, not directories
file_list = [f for f in rootdir.glob('**/*') if f.is_file()]

file_count = 0

#this block of code takes the files for each procedure and splits them into corresponding folders in the different subsets
for cur in file_list:
    with open(cur, 'r') as source:
        full_path = cur.absolute()
        file_path = full_path.as_posix() # convert path to string
        training_num, validation_num, test_num = count.get_dist(file_path,0.5,0.25,0.25) # get the dist of each subset
        print('Training: {} | Validation: {} | Test: {}'.format(training_num, validation_num, test_num))
        train_path = 'Data/Training/' + ntpath.basename(cur)[:-4] + '/' + ntpath.basename(cur) # location of training data
        validation_path = 'Data/Validation/' + ntpath.basename(cur)[:-4] + '/' + ntpath.basename(cur) # location of validation data
        test_path = 'Data/Test/' + ntpath.basename(cur)[:-4] + '/' + ntpath.basename(cur) # location of test data
        new_reader = csv.reader(source, delimiter = ',') # read the file we're on in the file list
        line_count = 0 # figure out which line we're on
        for row in new_reader: # for every line in the csv
            if line_count < training_num:
                with open(train_path, 'a') as tr:
                    train_writer = csv.writer(tr, delimiter = ',')
                    train_writer.writerow([row[0],row[1]])
            if line_count > training_num - 1 and line_count < training_num + validation_num:
                with open(validation_path, 'a') as val:
                    valid_writer = csv.writer(val, delimiter = ',')
                    valid_writer.writerow([row[0],row[1]])
            if line_count > training_num + validation_num - 1 and line_count < training_num + validation_num + test_num:
                with open(test_path, 'a') as ts:
                    test_writer = csv.writer(ts, delimiter = ',')
                    test_writer.writerow([row[0],row[1]])
            line_count += 1
        line_count = 0
'''