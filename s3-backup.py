import boto3
import os
import shutil
from datetime import datetime


def main():
    directory_path = "/tmp/backup"

    archive_name = "s3-backup" + '_' + datetime.strftime(datetime.utcnow(), "%Y.%m.%d.%H-%M-%S") + 'UTC'
    
    s3_download = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID_DOWNLOAD'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY_DOWNLOAD'),
        endpoint_url=os.getenv('AWS_HOST_DOWNLOAD'),
    )

    bucket_name_download = os.getenv('AWS_BUCKET_NAME_DOWNLOAD')
    
    s3_upload = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID_UPLOAD'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY_UPLOAD'),
        endpoint_url=os.getenv('AWS_HOST_UPLOAD'),
    )
    
    bucket_name_upload = os.getenv('AWS_BUCKET_NAME_UPLOAD')
    
    download_dir(directory_path, bucket_name_download, s3_download)

    if os.path.exists(directory_path):

        shutil.make_archive(archive_name, 'zip', directory_path)

        upload_to_s3(archive_name + ".zip", s3_upload, bucket_name_upload)

        shutil.rmtree(directory_path)
        os.remove(archive_name + ".zip")

def download_dir(local, bucket, client):
    """
    params:
    - local: local path to folder in which to place files
    - bucket: s3 bucket with target contents
    - client: initialized s3 client object
    """
    keys = []
    dirs = []
    next_token = ''
    base_kwargs = {
        'Bucket':bucket,
    }

    while next_token is not None:
        kwargs = base_kwargs.copy()

        if next_token != '':
            kwargs.update({'ContinuationToken': next_token})
        
        results = client.list_objects_v2(**kwargs)

        contents = results.get('Contents')

        if contents is not None:
            for i in contents:
                k = i.get('Key')
                if k[-1] != '/':
                    keys.append(k)
                else:
                    dirs.append(k)

        next_token = results.get('NextContinuationToken')

    for d in dirs:
        dest_pathname = os.path.join(local, d)

        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))

    for k in keys:
        dest_pathname = os.path.join(local, k)

        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
        
        client.download_file(bucket, k, dest_pathname)

     
def upload_to_s3(path, s3, bucket):
    with open(path, "rb") as data:
        s3.upload_fileobj(data, bucket, path)
    
    
if __name__ == '__main__':

    main()