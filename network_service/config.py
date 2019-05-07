#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/10
"""

# NS监听端口
LISTEN_PORT = 9995
# 集控心跳周期(秒)
HEART_CYCLE = 60

# 集控上报集控字段
HUB_FIELDS = (
    'sn', 'status', 'rf_band', 'rf_addr', 'address',
    'longitude', 'latitude', 'unit', 'registered_time', 'memo'
)

# 集控上报灯控字段
LAMPCTRL_FIELDS = (
    'sn', 'is_repeated', 'sequence', 'status', 'rf_band',
    'latitude', 'longitude', 'address', 'rf_addr',
    'memo', 'registered_time', 'lamp_type'
)

# 集控上报集控状态数据字段
HUBSTATUS_FIELDS = ()

# 集控上报灯控状态数据字段
LAMP_CTRL_STATUS_FIELDS = ()

# 集控上报告警数据字段
ALERT_FIELDS = ()
