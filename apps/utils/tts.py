#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/3
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartlamp.settings")

import django
django.setup()

import urllib3
import logging
import requests

from django.conf import settings

from setting.models import Setting
from utils.decorators import singleton


_logger = logging.getLogger('smartlamp')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 禁用安全请求警告


# API_KEY = '4E1BG9lTnlSeIf1NQFlrSq6h'
# SECRET_KEY = '544ca4657ba8002e3dea3ac2f5fdd241'

# 发音人选择, 0为普通女声，1为普通男生，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女声
PER = 0
# 语速，取值0-15，默认为5中语速
SPD = 5
# 音调，取值0-15，默认为5中语调
PIT = 5
# 音量，取值0-9，默认为5中音量
VOL = 5
# 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
AUE = 3

FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
FORMAT = FORMATS[AUE]

CUID = "123456PYTHON"

TTS_URL = 'http://tsn.baidu.com/text2audio'


class DemoError(Exception):
    pass

TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
SCOPE = 'audio_tts_post'  # 有此scope表示有tts能力，没有请在网页里勾选


class BaseTTS(object):

    def __init__(self):
        self.audio_path = os.path.join(settings.MEDIA_ROOT, 'audio/')
        self.App_ID = Setting.objects.get(
            option='tts_APPID').value  # '11368596'
        self.API_Key = Setting.objects.get(
            option='tts_APIKEY').value  # '79BBtBU9vTqRGHuz3XEbIkGk'
        self.Secret_Key = Setting.objects.get(
            option='tts_Secret_Key').value  # 'PWScKEHdjQ95zXD5FCW8O4K6xUCGqNAM'

    def fetch_token(self):
        params = {
            'client_id': self.API_Key,
            'client_secret': self.Secret_Key,
            'grant_type': 'client_credentials'
        }
        url = 'https://openapi.baidu.com/oauth/2.0/token?'
        ret = requests.get(url, params=params, verify=False)
        result = ret.json()
        if 'access_token' in result.keys() and 'scope' in result.keys():
            if not SCOPE in result['scope'].split(' '):
                raise DemoError('scope is not correct')
            print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (
                result['access_token'], result['expires_in']))
            return result['access_token']
        else:
            raise DemoError(
                'MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

    def fetch_audio_content(self, text):
        token = self.fetch_token()
        params = {'tok': token, 'tex': text, 'per': PER, 'spd': SPD, 'pit': PIT,
                  'vol': VOL, 'aue': AUE, 'cuid': self.App_ID,
                  'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数
        url = 'https://tsn.baidu.com/text2audio?'
        res = requests.get(url, params=params, verify=False)
        headers = res.headers
        if 'Content-Type' not in headers.keys() or headers[
                'Content-Type'].find('audio/') < 0:
            return
        return res.content
        # save_file = os.path.join(self.audio_path, 'result.' + FORMAT)
        # with open(save_file, 'wb') as f:
        #     f.write(res.content)

    def generate_text(self, body):
        raise NotImplementedError('`generate_text()` must be implemented.')

    def generate_tts_name(self, body):
        raise NotImplementedError('`generate_tts_name()` must be implemented.')

    def generate_audio(self, body):
        # 生成告警文本
        text = self.generate_text(body)
        # 生成告警语音content
        audio_content = self.fetch_audio_content(text)
        # 存入文件
        file_name = self.generate_tts_name(body)
        with open(file_name, 'wb') as f:
            f.write(audio_content)


@singleton
class AlertTTS(BaseTTS):

    def generate_text(self, alert_body):
        level_map = {
            1: '低',
            2: '中',
            3: '严重'
        }
        type_map = {
            'hub': '集控',
            'lamp': '路灯'
        }
        object = alert_body.get('object')
        object_type = type_map.get(alert_body.get('object_type'))
        event = alert_body.get('event')
        alert_source = alert_body.get('alert_source')
        level = level_map.get(alert_body.get('level'))
        text = object_type + object + '产生告警:' + event + '。告警等级:' + level
        return text

    def generate_tts_name(self, alert_body):
        alert_id = alert_body.get('id')
        name = 'alert_{}.{}'.format(alert_id, FORMAT)
        file_name = os.path.join(self.audio_path, name)
        return file_name


@singleton
class WorkorderTTS(BaseTTS):

    def generate_text(self, body):
        """
        :param body: workorder body
        {
            'id': workorder_id,
            'message': 'message'
        }
        """
        text = u'您有新的工单，' + body.get('message', '')
        return text

    def generate_tts_name(self, body):
        workorder_id = body.get('id')
        name = 'workorder_{}.{}'.format(workorder_id, FORMAT)
        file_name = os.path.join(self.audio_path, name)
        return file_name


if __name__ == '__main__':
    tts = AlertTTS()
    tts2 = AlertTTS()
    print(tts)
    print(tts2)
    tts = WorkorderTTS()
    workorder_body = {
        'id': 1,
        'message': '集控1111有问题'
    }
    tts.generate_audio(workorder_body)
    # alert_body = {
    #     'id': 1,
    #     'object': '800000000001',
    #     'object_type': 'hub',
    #     'event': '集控拖网',
    #     'alert_source': '800000000001',
    #     'level': 3
    # }
    # tts.generate_audio(alert_body)

