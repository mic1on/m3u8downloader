# -*- coding: utf-8 -*-
import os
from loguru import logger
from Crypto.Cipher import AES
import requests

URI_PREFIXES = ('https://', 'http://', 's3://', 's3a://', 's3n://')


def is_url(uri):
    return uri.startswith(URI_PREFIXES)


class Downloader(object):

    def __init__(self, file_path=None, key_uri=None):
        self.files = []
        self.cipher = None
        self.file_path = file_path or '.'
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        if key_uri:
            self._make_cipher(key_uri)

    def _download(self, url):
        with requests.get(url=url) as resp:
            return resp.content

    def _make_cipher(self, key_uri: str):
        if is_url(key_uri):
            key = self._download(url=key_uri)
        else:
            with open(key_uri, mode='rb') as f:
                key = f.read()
        self.cipher = AES.new(key, AES.MODE_CBC, key)

    def _ts(self, url):
        logger.info(f"正在下载{url}")
        file_name = os.path.basename(url).split('?')[0]
        content = self._download(url=url)
        full_file_path = os.path.join(self.file_path, file_name)
        with open(full_file_path, mode='wb') as f:
            if self.cipher:
                f.write(self.cipher.decrypt(content))
            else:
                f.write(content)
            self.files.append(full_file_path)

    def download(self, ts_url):
        self._ts(ts_url)
