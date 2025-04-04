from rclone_python import rclone
import os
import shutil
from datetime import datetime


def main():

    

    shutil.unpack_archive("test.zip", "/tmp/backup")

    rclone.copy("/tmp/backup", "vk:pelican-media-assets")



if __name__ == '__main__':

    main()