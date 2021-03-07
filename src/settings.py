import os
from datetime import timedelta
from typing import List
from pydantic import (
    BaseSettings,
    AnyHttpUrl,
    SecretStr,
    HttpUrl,
)
import pytz

LOCAL_TZ = pytz.timezone("Europe/Copenhagen")

class AcousticConfiguration(BaseSettings):
    ACOUSTIC_BASE_URL_XML: HttpUrl = "https://api-campaign-eu-1.goacoustic.com/XMLAPI"
    ACOUSTIC_BASE_URL_REST: HttpUrl = "https://api-campaign-eu-1.goacoustic.com/rest"
    ACOUSTIC_AUTH_URL: HttpUrl = "https://api-campaign-eu-1.goacoustic.com/oauth/token"
    ACOUSTIC_CLIENT_ID: str = "ACOUSTIC_CLIENT_ID"
    ACOUSTIC_CLIENT_SECRET: SecretStr = "ACOUSTIC_CLIENT_SECRET"
    ACOUSTIC_REFRESH_TOKEN: SecretStr = "ACOUSTIC_REFRESH_TOKEN"

    delay: timedelta = timedelta(seconds=10)

    class Config:
        env_file = os.environ.get("DOTENV_FILE", default=".env")
        env_file_encoding = "utf-8"

# TODO Implement PostgresDsn or MariadbDsn from pydantic at some point
# Find out what else to do, ask nicwi maybe
class DatabaseConfiguration(BaseSettings):
    from dotenv import load_dotenv
    load_dotenv()
    MARIADB_CONFIG = {
        "user": os.environ["MARIADB_USR"],
        "psw": os.environ["MARIADB_PSW"],
        "host": "cubus.cxxwabvgrdub.eu-central-1.rds.amazonaws.com",
        "port": 3306,
        "db": "input",
    }

    #CONN_STRING = f"{SCHEME}://{MARIADB_USR}:{MARIADB_PSW}@{HOST}:{PORT}/{DB}"

db_settings = DatabaseConfiguration()
acoustic_settings = AcousticConfiguration()
