import boto3
import os
import shutil
from datetime import datetime


def main():

    path = "/tmp/backup"

    bucket="pelican-local-env"

    backup_filename = "test.zip"

    s3_upload = boto3.client(
        's3',
        aws_access_key_id="secret",
        aws_secret_access_key="secret",
        endpoint_url="url"
    )

    if(os.path.exists(path)):
        if(not os.listdir(path)):
            shutil.unpack_archive(backup_filename, path)
            for item in os.listdir(path):
                upload_to_s3(f"{path}/{item}", s3_upload, bucket, item)
            shutil.rmtree(path)
        else:
            shutil.rmtree(path)
            os.mkdir(path)
            shutil.unpack_archive(backup_filename, path)
            for item in os.listdir(path):
                upload_to_s3(f"{path}/{item}", s3_upload, bucket, item)
            shutil.rmtree(path)

    else:
        os.mkdir(path)
        shutil.unpack_archive(backup_filename, path)

        for item in os.listdir(path):
                upload_to_s3(f"{path}/{item}", s3_upload, bucket, item)

        shutil.rmtree(path)


def upload_to_s3(path, s3, bucket, key):
    with open(path, "rb") as data:
        s3.upload_fileobj(Fileobj = data, Bucket = bucket, Key = key)
    
    
if __name__ == '__main__':

    main()