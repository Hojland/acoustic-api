%load_ext autoreload
%autoreload 2
import sqlalchemy
import re
from datetime import datetime, timedelta
import requests
import boto3

from utils import utils, sql_utils
from paid_media.acoustic import AcousticApi
from settings import db_settings, acoustic_settings

def test_creds():
    session = boto3.Session(
        aws_access_key_id=os.environ["ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
    )

    s3_client = session.client("s3")

    bucket = session.resource("s3").Bucket('punica-dump')
    [obj for obj in bucket.objects.all()]
    buckets = [bucket["Name"] for bucket in response["Buckets"]]

def main():
    mariadb_engine = sql_utils.create_engine(db_config=db_settings.MARIADB_CONFIG, db_type='mariadb', db_name=db_settings.MARIADB_CONFIG['db'])
    acoustic = AcousticApi()
    acoustic.test()

if __name__ == '__main__':
    main()