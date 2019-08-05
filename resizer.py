import cv2
import boto
import boto3
import os

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
    s3r = boto3.resource('s3')
    s3c = boto3.client('s3')
    n=0
    total = 80460
    for key in get_matching_s3_keys(bucket='cela-input', prefix='framedata/Data/Validation'): #iterate through all keys under data
        key_path = os.path.basename(key) # get just the file's name
        label = key.split('/')[3] # get parent folder (label) of the file
        keyFound = False
        for key_check in get_matching_s3_keys(bucket='cela-input',prefix='framedata/Resize/Validation/{}'.format(label,key_path)):
            if os.path.basename(key_check) == key_path:
                keyFound = True
            else:
                break
        if not keyFound:
            if key_path != '':
                print('\tConverting {}'.format(key))
                s3r.Bucket('cela-input').download_file(key, 'download/{}'.format(key_path)) # download the current key
                img = cv2.imread('download/{}'.format(key_path), cv2.IMREAD_UNCHANGED) # read current file into cv2
                print("\tOriginal Dimension: {}".format(img.shape))
                reimg = cv2.resize(img, (244, 244), interpolation = cv2.INTER_AREA) # resize image
                print("\tResized Dimension: {}".format(reimg.shape))
                cv2.imwrite('download/{}'.format(key_path),reimg) # save resized image
                subset = key.split('/')[2] # get the data set the image belongs in
                s3c.upload_file('download/{}'.format(key_path), 'cela-input', 'framedata/Resize/{}/{}/{}'.format(subset,label,key_path)) # upload the resized file
                os.remove('download/{}'.format(key_path)) # delete the file locally
                print("\tDeleted file {}".format(key_path))
        else:
            print('Skipped existing file.')
        n =+ 1
        print('Progress: {}/{}\n'.format(n,total))

main()
