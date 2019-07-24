import boto3
import boto
import os
from pathlib import Path
import ntpath
import paramiko
import csv
'''
IP = '13.58.170.185'

key = paramiko.RSAKey.from_private_key_file('/home/connerpinson/Downloads/conner_key.pem')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
'''

# insert directory with the parent folders
# i.e. the EXP3 folder on the drive
test_dir = '.'

# get all files in a folder
def get_files(a_dir):
    a_dir = Path(a_dir)
    return [f for f in a_dir.glob('**/*') if f.is_file()]

def get_matching_s3_keys(bucket, prefix='', suffix=''):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                yield key

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break

def main():
    #connect to s3
    s3 = boto3.client('s3')
    conn = boto.connect_s3()
    destbucket = conn.get_bucket('cela-input')
    n = int(input('How many subjects are there? '))
    #iterate through each frame in the n subjects
    for i in range(4,n+1):
        print('Moving frames of S{}C2...'.format(i))
        #This gets each key from each subject's video
        for key in get_matching_s3_keys(bucket='cela-input', prefix='framedata/S{}C2/S'.format(i)):
            keyFound = False
            # stores a string version of the number of the frame so we have it for moving files later
            frame_str = key[19:]
            # stores an integer version of the filename for comparison
            frame_num = int(key[19:-4])
            # gets all procedures performed on the subject
            procedure = get_files('Data/S{}C2/'.format(i))
            # for each procedure performed on the subject
            for entry in procedure:
                #open -locally stored- list of operations
                with open(entry, 'r') as procedure_list:
                    # make a csv reader for the current procedure
                    csv_reader = csv.reader(procedure_list, delimiter=',')
                    # iterate through each row of the reader (each row has two entries, the start and end frame)
                    for row in csv_reader:
                        if frame_num > float(row[0]) and frame_num < float(row[1]):
                            keyFound = True
                            proc_name = ntpath.basename(entry)[:-4] + '/'
                            #use subjects 1-5 for training
                            if i < 6:
                                destbucket.copy_key('framedata/Data/Training/{}/S{}C2{}'.format(proc_name,i,frame_str), 'cela-input', key)
                            #use subject 6 for validation
                            if i == 6:
                                destbucket.copy_key('framedata/Data/Validation/{}/S{}C2{}'.format(proc_name,i,frame_str), 'cela-input', key)
                            #use subject 7 for test
                            if i == 7:
                                destbucket.copy_key('framedata/Data/Test/{}/S{}C2{}'.format(proc_name,i,frame_str), 'cela-input', key)
                            break
                if keyFound:
                    break
                            

main()
print('Complete.')
