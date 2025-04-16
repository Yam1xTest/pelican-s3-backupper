from rclone_python import rclone
import os
import shutil
from datetime import datetime


def main():

    path = "/tmp/backup"

    bucket="s3:pelican-local-env"

    backup_filename = "test.zip"

    if(os.path.exists(path)):
        if(not os.listdir(path)):
            print("нет файлов")
            shutil.unpack_archive(backup_filename, "/tmp/backup")
            print(os.listdir(path))
            rclone.copy("/tmp/backup", bucket)
            shutil.rmtree(path)
    else:
        print("нет файлов2")
        os.mkdir(path)
        shutil.unpack_archive(backup_filename, "/tmp/backup")
        print(os.listdir(path))
        rclone.copy("/tmp/backup", bucket)
        shutil.rmtree(path)



if __name__ == '__main__':

    main()