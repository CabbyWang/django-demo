#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/17
"""


# server address
SERVER_ADDR = ('127.0.0.1', 9994)

# alarms dict
# level: 1/2/3 告警/故障/严重故障
# status: 1/2/3 正常/故障/脱网
HUB_ALARMS = {
    'Lost': {'event': '集控脱网', 'level': 3, 'status': 3},
    'OverTemp': {'event': '集控过温', 'level': 2, 'status': 2},
    'OverVol': {'event': '集控过压', 'level': 2, 'status': 2},
    'UnderVol': {'event': '集控欠压', 'level': 2, 'status': 2},
    'EngyErr': {'event': '集控电能采集模块异常', 'level': 2, 'status': 2},
    'GPSErr': {'event': '集控GPS异常', 'level': 1, 'status': 2},
    'PA_VolErr': {'event': 'A相电压异常', 'level': 3, 'status': 2},
    'PA_CurErr': {'event': 'A相电流异常', 'level': 3, 'status': 2},
    'PB_VolErr': {'event': 'B相电压异常', 'level': 3, 'status': 2},
    'PB_CurErr': {'event': 'B相电流异常', 'level': 3, 'status': 2},
    'PC_VolErr': {'event': 'C相电压异常', 'level': 3, 'status': 2},
    'PC_CurErr': {'event': 'C相电流异常', 'level': 3, 'status': 2},
    'DoorOpened': {'event': '控制箱开门告警', 'level': 1, 'status': 2},
    'Rel1Err': {'event': '送电接触器1故障', 'level': 3, 'status': 2},
    'Rel2Err': {'event': '送电接触器2故障', 'level': 3, 'status': 2},
    'Rel3Err': {'event': '送电接触器3故障', 'level': 3, 'status': 2},
    'IOErr': {'event': '集控IO通讯模块异常', 'level': 2, 'status': 2},
    'RTCErr': {'event': '集控RTC异常', 'level': 2, 'status': 2},
    'LampOnAhead': {'event': '阴雨天提前亮灯', 'level': 1, 'status': 1},
    # TODO 这两个新加的告警是什么鬼？
    'HighLuxCloseLamps': {'event': '自动关灯', 'level': 1, 'status': 2},
    'LowLuxOpenLamps': {'event': '自动开灯', 'level': 1, 'status': 2}
}
# HUB_ALARMS = {
#     'Lost': {'event': u'集控脱网', 'level': 3},
#     'OverTemp': {'event': u'集控过温', 'level': 2},
#     'OverVol': {'event': u'集控过压', 'level': 2},
#     'UnderVol': {'event': u'集控欠压', 'level': 2},
#     'EngyErr': {'event': u'集控电能采集模块异常', 'level': 2},
#     'GPSErr': {'event': u'集控GPS异常', 'level': 1},
#     'PA_VolErr': {'event': u'A相电压异常', 'level': 3},
#     'PA_CurErr': {'event': u'A相电流异常', 'level': 3},
#     'PB_VolErr': {'event': u'B相电压异常', 'level': 3},
#     'PB_CurErr': {'event': u'B相电流异常', 'level': 3},
#     'PC_VolErr': {'event': u'C相电压异常', 'level': 3},
#     'PC_CurErr': {'event': u'C相电流异常', 'level': 3},
#     'DoorOpened': {'event': u'控制箱开门告警', 'level': 1},
#     'Rel1Err': {'event': u'送电接触器1故障', 'level': 3},
#     'Rel2Err': {'event': u'送电接触器2故障', 'level': 3},
#     'Rel3Err': {'event': u'送电接触器3故障', 'level': 3},
#     'IOErr': {'event': u'集控IO通讯模块异常', 'level': 2},
#     'RTCErr': {'event': u'集控RTC异常', 'level': 2},
#     'LampOnAhead': {'event': u'阴雨天提前亮灯', 'level': 1},
# }

LAMP_ALARMS = {
    'Lost': {'event': u'节点通讯丢失', 'level': 2, 'status': 3},
    'Mismatch': {'event': u'节点反馈与控制不匹配', 'level': 1, 'status': 2},
    'OverVol': {'event': u'节点过压', 'level': 1, 'status': 2},
    'UnderVol': {'event': u'节点欠压', 'level': 1, 'status': 2},
    'OverCur': {'event': u'节点过流', 'level': 1, 'status': 2},
    'UnderCur': {'event': u'节点欠流', 'level': 1, 'status': 2},
    'PwrSamplingErr': {u'event': u'节点电能采样异常', 'level': 1, 'status': 2},
    'OverTemp': {'event': u'节点过温', 'level': 1, 'status': 2},
    'FlashRdErr': {'event': u'节点FLASH读异常', 'level': 1, 'status': 2},
    'FlashWtErr': {'event': u'节点FLASH写异常', 'level': 1, 'status': 2},
    'LampErr': {'event': u'节点异常', 'level': 1, 'status': 2},
}