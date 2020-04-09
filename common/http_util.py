import json

import requests

from common.constant import HttpCode, ErrorCode
from common.exception import ServerException
from common.log import Logger

log = Logger(__name__)


class HttpUtil:
    def __init__(self, url, headers=None, body=None, method='GET'):
        self.url = url
        self.headers = headers if headers else {'Content-Type': 'application/json'}
        self.body = body
        self.method = method
        self.timeout = 60 * 5

    def request(self):
        log.info(f'request from {self.__dict__}')
        response = None
        if self.method == 'GET':
            response = requests.get(
                self.url,
                headers=self.headers
            )
        if self.method == 'POST':
            response = requests.post(
                self.url,
                data=json.dumps(self.body),
                headers=self.headers,
                timeout=self.timeout
            )
        if self.method == 'PUT':
            response = requests.put(
                self.url,
                headers=self.headers,
                json=self.body
            )
        if self.method == 'DELETE':
            response = requests.delete(
                self.url,
                headers=self.headers
            )
        if response is None or response.status_code not in HttpCode.HTTP_SUCCESS:
            raise ServerException(ErrorCode.FAILED, f'request failed{response.json()}')
        return response

    def get(self):
        return requests.get(
            self.url,
            headers=self.headers
        )

    def post(self):
        return requests.post(
            self.url,
            data=json.dumps(self.body),
            headers=self.headers
        )
