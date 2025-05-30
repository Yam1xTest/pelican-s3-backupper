import os
import boto3
import zipfile

def test_backup_file_created_in_s3():
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('DESTINATION_S3_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('DESTINATION_S3_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('DESTINATION_S3_AWS_ENDPOINT'),
    )

    dest_bucket = os.getenv('DESTINATION_S3_AWS_BUCKET_NAME')

    response = s3.list_objects_v2(Bucket=dest_bucket)

    if 'Contents' not in response:
        raise Exception("No files found in S3 bucket")
    
    backup_files = []
    for obj in response['Contents']:
        prefix = os.getenv('S3_BACKUPS_FILENAME_PREFIX')
        if obj['Key'].startswith(prefix):
            backup_files.append(obj)

    if len(backup_files) <= 0:
        raise Exception("No backup files found with the correct prefix")
    
    for backup_file in backup_files:
        file_size = backup_file['Size']
        if file_size <= 0:
            raise Exception(f"Empty backup file: {backup_file['Key']}")

def test_s3_backup_content():
    source_s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('SOURCE_S3_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('SOURCE_S3_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('SOURCE_S3_AWS_ENDPOINT'),
    )

    source_bucket = os.getenv('SOURCE_S3_AWS_BUCKET_NAME')

    dest_s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('DESTINATION_S3_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('DESTINATION_S3_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('DESTINATION_S3_AWS_ENDPOINT'),
    )

    dest_bucket = os.getenv('DESTINATION_S3_AWS_BUCKET_NAME')

    response = dest_s3.list_objects_v2(Bucket=dest_bucket)

    backup_files = []
    for obj in response['Contents']:
        prefix = os.getenv('DB_BACKUPS_FILENAME_PREFIX')
        if obj['Key'].startswith(prefix):
            backup_files.append(obj)

    latest_backup = None
    for file in backup_files:
        if latest_backup is None or file['LastModified'] > latest_backup['LastModified']:
            latest_backup = file

    tmp_file = '/tmp/latest_s3_backup.backup'
    dest_s3.download_file(dest_bucket, latest_backup['Key'], tmp_file)

    with zipfile.ZipFile(tmp_file, 'r') as zip_ref:
        files = zip_ref.namelist()
        if not files:
            raise Exception("Backup archive is empty")
        
        source_objects = source_s3.list_objects_v2(
            Bucket=source_bucket,
            Prefix=os.getenv('SOURCE_S3_AWS_BUCKET_SUBFOLDER_NAME', '')
        ).get('Contents', [])
        
        source_files = []  
        for obj in source_objects:
            file_key = obj['Key']
            source_files.append(file_key)
        if not any(f in source_files for f in files):
            raise Exception("Backup doesn't contain source files")
        
def run_tests():
    test_backup_file_created_in_s3()
    test_s3_backup_content()
    print("All tests passed!")

if __name__ == "__main__":
    run_tests()
