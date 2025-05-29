import os
import boto3
import pytest
import zipfile

@pytest.fixture(scope="module")
def source_s3():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('SOURCE_S3_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('SOURCE_S3_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('SOURCE_S3_AWS_ENDPOINT'),
    )

@pytest.fixture(scope="module")
def dest_s3():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('DESTINATION_S3_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('DESTINATION_S3_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('DESTINATION_S3_AWS_ENDPOINT'),
    )

@pytest.fixture(scope="module")
def source_bucket():
    return os.getenv('SOURCE_S3_AWS_BUCKET_NAME')

@pytest.fixture(scope="module")
def dest_bucket():
    return os.getenv('DESTINATION_S3_AWS_BUCKET_NAME')

def test_backup_archive_created(dest_s3, dest_bucket):
    response = dest_s3.list_objects_v2(Bucket=dest_bucket)
    assert 'Contents' in response, "No files found in destination bucket"
    
    backups = [obj for obj in response['Contents'] 
              if obj['Key'].startswith(os.getenv('S3_BACKUPS_FILENAME_PREFIX'))]
    assert len(backups) > 0, "No backup archives found"
    
    for backup in backups:
        assert backup['Size'] > 0, f"Backup file {backup['Key']} is empty"

def test_backup_content(source_s3, dest_s3, source_bucket, dest_bucket):
    # Get latest backup
    response = dest_s3.list_objects_v2(Bucket=dest_bucket)
    backups = [obj for obj in response['Contents'] 
              if obj['Key'].startswith(os.getenv('S3_BACKUPS_FILENAME_PREFIX'))]
    latest = max(backups, key=lambda x: x['LastModified'])
    
    # Download backup
    tmp_file = '/tmp/latest_backup.zip'
    dest_s3.download_file(dest_bucket, latest['Key'], tmp_file)
    
    # Verify zip content
    with zipfile.ZipFile(tmp_file, 'r') as zip_ref:
        files = zip_ref.namelist()
        assert len(files) > 0, "Backup archive is empty"
        
        # Verify at least one file matches source
        source_objects = source_s3.list_objects_v2(
            Bucket=source_bucket,
            Prefix=os.getenv('SOURCE_S3_AWS_BUCKET_SUBFOLDER_NAME', '')
        ).get('Contents', [])
        
        source_files = [obj['Key'] for obj in source_objects]
        assert any(f in source_files for f in files), "Backup doesn't contain source files"