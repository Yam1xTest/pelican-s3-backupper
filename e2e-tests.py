import boto3
import os
import zipfile

def main():
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('DESTINATION_S3_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('DESTINATION_S3_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('DESTINATION_S3_AWS_ENDPOINT')
    )

    objects_list = s3.list_objects_v2(Bucket="pelican-backups")
    try:
        contents = objects_list["Contents"]
        print(contents[-1]['Key'])
        last_backup_size = contents[-1]['Size']

        s3.download_file(Bucket="pelican-backups", Key=contents[-1]['Key'], Filename=contents[-1]['Key'])
        zip_file_name = contents[-1]['Key']
        with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
            file_names = zip_ref.namelist()
            print(file_names)
    except:
        raise Exception("Bucket is empty")

    if(last_backup_size == 0):
        raise Exception("Backup size is 0")

if __name__ == '__main__':
    main()
