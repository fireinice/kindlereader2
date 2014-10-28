# -*- coding: utf-8 -*-
import urllib
import json
import base64
from Crypto.Cipher import AES


class AESService(object):
    BLOCK_SIZE = 32
    PADDING = '{'
    pad = staticmethod(lambda s: s + (
        (AESService.BLOCK_SIZE - len(s) % AESService.BLOCK_SIZE)
        * AESService.PADDING))

    def __init__(self, secret):
        self.cipher = AES.new(secret)

    def getCipheredString(self, info_str):
        return self.cipher.encrypt(AESService.pad(info_str))


class PocketService(object):
    def __init__(self, host=None, aes=None):
        self.service_url = None
        self.aes = None
        if not aes or not host:
            return
        self.service_url = "http://%s/sendpks/?" % host
        self.aes = aes

    def getPocketInfo(self, url, title):
        if not self.service_url:
            return ''
        info = {'url': url,
                'title': title,
                'tags': 'kindle'}
        info_str = json.dumps(info)
        if self.aes:
            info_str = self.aes.getCipheredString(info_str)
        info_str = base64.b64encode(info_str)
        return self.service_url + urllib.urlencode({
            "info": info_str})
