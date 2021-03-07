from datetime import datetime, timedelta
from typing import Dict, List
from uuid import uuid4
import requests
import logging
from dataclasses import dataclass
import pytz
import xmltodict

from settings import acoustic_settings
import settings
from utils import utils

log = logging.getLogger(__name__)


class AcousticApi():
    def __init__(self):
        self.version = 'v1'
        self.auth_url = acoustic_settings.ACOUSTIC_AUTH_URL
        self.client_id = acoustic_settings.ACOUSTIC_CLIENT_ID
        self.client_secret = acoustic_settings.ACOUSTIC_CLIENT_SECRET
        self.refresh_token = acoustic_settings.ACOUSTIC_REFRESH_TOKEN
        self.acoustic_base_url = acoustic_settings.ACOUSTIC_BASE_URL_REST
        self.access_token_resp = self.oauth_get_access_token()

    @dataclass
    class TokenResponse:
        access_token: str
        expires: datetime

    def oauth_get_access_token(self):
        # TODO Figure "thread local caching", possibly in secure storage
        request_parameters = {
            "client_id": self.client_id,
            "client_secret": self.client_secret.get_secret_value(),
            "refresh_token": self.refresh_token.get_secret_value(),
            "grant_type": "refresh_token",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        resp = requests.post(
            self.auth_url,
            data=request_parameters,
            headers=headers,
        )
        resp.raise_for_status()

        body = resp.json()

        expires = datetime.now().replace(tzinfo=pytz.utc).astimezone(tz=settings.LOCAL_TZ) + timedelta(seconds=body["expires_in"])
        return self.TokenResponse(body["access_token"], expires)

    def get(self, edge: str):
        if self.access_token_resp.expires < utils.time_now(settings.LOCAL_TZ): #make sure this is same timezone
            self.access_token_resp = self.oauth_get_access_token()

        # could have user oauth2 from oauthlib - do if there are issues
        access_token = self.access_token_resp.access_token
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        }
        url = f"{acoustic_settings.ACOUSTIC_BASE_URL_REST}/{self.version}/{edge}"
        res = requests.get(
            url, headers=headers
        )
        res.raise_for_status()

        return res.json()

    def xml_post(self, body):
        if self.access_token_resp.expires < utils.time_now(settings.LOCAL_TZ): #make sure this is same timezone
            self.access_token_resp = self.oauth_get_access_token()

        # could have user oauth2 from oauthlib - do if there are issues
        access_token = self.access_token_resp.access_token
        headers = {
            "Content-Type": "Content-Type: text/xml;charset=utf-8",
            "Authorization": "Bearer {}".format(access_token),
        }
        url = f"{acoustic_settings.ACOUSTIC_BASE_URL_XML}"
        res = requests.post(
            url, data=body, headers=headers
        )
        res.raise_for_status()

        json_res = self._parse_acoustic_xml_response(res.text)

        return json_res

    def _parse_acoustic_xml_response(self, body: str) -> Dict:
        json_body = xmltodict.parse(body)

        res = utils.dict_to_dict(json_body)
        #convert_to_int = [
        #    "RECIPIENTS_RECEIVED",
        #    "EMAILS_SENT",
        #    "NUMBER_ERRORS",
        #    "STATUS",
        #    "ERROR_CODE",
        #]
        #for field in convert_to_int:
        #    result[field] = int(result[field], 10)

        return res

    def get_contact_lists(self):
        body = """
        <Envelope>
        <Body>
            <GetLists>
            <VISIBILITY>1</VISIBILITY>
            <LIST_TYPE>18</LIST_TYPE>
            </GetLists>
        </Body>
        </Envelope>
        """
        res = self.xml_post(body)
        return res

    def get_databases(self):
        body = """
        <Envelope>
        <Body>
            <GetLists>
            <VISIBILITY>1</VISIBILITY>
            <LIST_TYPE>15</LIST_TYPE>
            </GetLists>
        </Body>
        </Envelope>
        """
        res = self.xml_post(body)
        return res

    def segments(self):
        res = self.get(version=self.version, edge='segments')
        return res

    def doc(self):
        res = requests.get('https://api-campaign-eu-1.goacoustic.com/restdoc', headers=headers)
        return res


if __name__ == '__main__':
    self = AcousticApi()
    res = self.get(version='v1', edge='application')
    res = self.segments()