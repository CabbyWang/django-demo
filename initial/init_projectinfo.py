# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/11
"""
import os
import sys
from pathlib import Path


# the base_dir should be added into system path.
cur_file = Path(__file__).cwd()
base_dir = cur_file.parent
sys.path.insert(0, str(base_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartlamp.settings")

import django
django.setup()

import logging

from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from setting.models import Setting, SettingType
from projectinfo.models import ProjectInfo


_logging = logging.getLogger('smartlamp')


setting_types = [
    {
        'id': 1,
        'option': 'voice',
        'name': _('voice')
    },  # 语音
    {
        'id': 2,
        'option': 'message',
        'name': _('message')
    },  # 短信
    {
        'id': 3,
        'option': 'interface',
        'name': _('interface')
    },  # 界面
    {
        'id': 4,
        'option': 'communication',
        'name': _('communication')
    },  # 通讯
    {
        'id': 5,
        'option': 'alert',
        'name': _('alert')
    },  # 告警
    {
        'id': 6,
        'option': 'report',
        'name': _('report')
    },  # 报表
    {
        'id': 99,
        'option': 'others',
        'name': _('others')
    },  # 其它
]

# tts 语音合成账号密码
TTS_APPID = '11368596'
TTS_APIKEY = '79BBtBU9vTqRGHuz3XEbIkGk'
# tts 密钥
TTS_SECRET_KEY = 'PWScKEHdjQ95zXD5FCW8O4K6xUCGqNAM'
# 超时时间
REQUEST_TIMEOUT = '60'
# 单个集控初始每日能耗
DAILY_CONSUMPTION = '5000.0'
# sms 短信网关类型 'llt' or 'hy' or ?
SMS_TYPE = 'llt'

# llt 流量通
LLT_SMS_ACCOUNT = 'llt-a4fc806d'
LLT_SMS_PWD = 'PW901818af'

# hy 互亿
HY_SMS_ACCOUNT = 'C05725569'
HY_SMS_PWD = '1dc06ec87cb61bae729b22012a3763e1'

# 分页 每页显示数据行数
PAGINATION = '25'
# 集控上报状态次数阈值
HUB_STATUS_COUNT_THRESHOLD = '5000000'
# 终端上报状态次数阈值
LAMP_STATUS_COUNT_THRESHOLD = '5000000'
# 单灯电流告警阈值
LAMP_MIN_CURRENT = '0.01'
# 集控采集周期 (定时上报)
HUB_REPORT_CYCLE_TIME = '7500'
# 用电异常告警门限
POWER_CONSUMPTION_THRESHOLD = 1.3
# "节点通讯丢失"告警忽略时间段
# abnormal power usage threshold
LOST_IGNORE_TIME = '6:00,18:00'


settings = [
    {
        'id': 1,
        'option': 'tts_APPID',
        'name': '语音合成APP_ID',
        'value': TTS_APPID,
        'type_id': 1
     },  # 语音合成APP_ID
    {
        'id': 2,
        'option': 'tts_APIKEY',
        'name': '语音合成API_KEY',
        'value': TTS_APIKEY,
        'type_id': 1
    },  # 语音合成API_KEY
    {
        'id': 3,
        'option': 'tts_Secret_Key',
        'name': '语音合成Secret_Key',
        'value': TTS_SECRET_KEY,
        'type_id': 1
    },  # 语音合成Secret_Key
    {
        'id': 4,
        'option': 'request_timeout',
        'name': '超时时间(秒)',
        'value': REQUEST_TIMEOUT,
        'type_id': 4
    },  # 超时时间(秒)
    {
        'id': 5,
        'option': 'daily_consumption',
        'name': '每日能耗（千瓦·时）',
        'value': DAILY_CONSUMPTION,
        'type_id': 6
    },  # 每日能耗（千瓦·时）
    {
        'id': 6,
        'option': 'sms_type',
        'name': '短信网关',
        'value': SMS_TYPE,
        'type_id': 2
    },  # 短信网关
    {
        'id': 7,
        'option': 'llt_sms_account',
        'name': '账号',
        'value': LLT_SMS_ACCOUNT,
        'type_id': 2
    },  # 账号
    {
        'id': 8,
        'option': 'llt_sms_pswd',
        'name': '密码',
        'value': LLT_SMS_PWD,
        'type_id': 2
    },  # 密码
    {
        'id': 9,
        'option': 'pagination',
        'name': '分页（行数/页）',
        'value': PAGINATION,
        'type_id': 3
    },  # 分页（行数/页）
    {
        'id': 10,
        'option': 'lost_ignore_time',
        'name': '"节点通讯丢失"告警忽略时间段',
        'value': LOST_IGNORE_TIME,
        'type_id': 5
    },  # 节点通讯丢失"告警忽略时间段
    {
        'id': 11,
        'option': 'hub_status_count_threshold',
        'name': '集控上报状态次数阈值',
        'value': HUB_STATUS_COUNT_THRESHOLD,
        'type_id': 5
    },  # 集控上报状态次数阈值
    {
        'id': 12,
        'option': 'lamp_status_count_threshold',
        'name': '终端上报状态次数阈值',
        'value': LAMP_STATUS_COUNT_THRESHOLD,
        'type_id': 5
    },  # 终端上报状态次数阈值
    {
        'id': 13,
        'option': 'min_current',
        'name': '单灯电流告警阈值(安)',
        'value': LAMP_MIN_CURRENT,
        'type_id': 5
    },  # 单灯电流告警阈值(安)
    {
        'id': 14,
        'option': 'cycle_time',
        'name': '集控采集周期(秒)',
        'value': HUB_REPORT_CYCLE_TIME,
        'type_id': 4
    },  # 集控采集周期(秒)
    {
        'id': 15,
        'option': 'hy_sms_account',
        'name': '账号',
        'value': HY_SMS_ACCOUNT,
        'type_id': 2
    },  # 账号
    {
        'id': 16,
        'option': 'hy_sms_pswd',
        'name': '密码',
        'value': HY_SMS_PWD,
        'type_id': 2
    },  # 密码
    {
        'id': 17,
        'option': 'power_consumption_threshold',
        'name': '用电告警误差',
        'value': POWER_CONSUMPTION_THRESHOLD,
        'type_id': 5
    },  # 用电告警误差
]

project_info = {
    "name": u"天恒智能",
    "city": u"扬州",
    "longitude": 119.322703,
    "latitude": 32.691419,
    "zoom_level": 17
}


# 初始数据函数
def run():
    _logging.info("初始化数据库...")
    try:
        with transaction.atomic():
            # setting数据
            _logging.info("插入setting_type表...")
            print('插入setting_type表...')
            for setting_type in setting_types:
                SettingType.objects.create(**setting_type)
            _logging.info("插入setting表...")
            print('插入setting表...')
            for setting in settings:
                Setting.objects.create(**setting)
            # for key, value in settings_data.items():
            #     if not Setting.objects.filter_by(option=key):
            #         Setting.objects.create(option=key, value=value)
            # 公司数据
            print('插入公司数据...')
            _logging.info('插入公司数据...')
            ProjectInfo.objects.create(**project_info)

    except Exception as ex:
        print(ex)
        print('出现错误，已经回滚到原始状态')
        _logging.error("初始化数据库失败[{}], 数据回滚".format(ex))
    else:
        _logging.info("初始化数据库成功")


if __name__ == '__main__':
    run()

