#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/10
"""

# NS监听端口
LISTEN_PORT = 9999
# 集控心跳周期(秒)  根据集控来配置，和集控一致
HEART_CYCLE = 60
# 集控全量数据上报周期(秒)  根据集控来配置，和集控一致
# REPORT_STATUS_CYCLE = 3600
REPORT_STATUS_CYCLE = 180

# 集控接三相电后是否能上报consumption(能耗)
# IS_REPORT_CONSUMPTION = True

# # 集控上报集控字段
# HUB_FIELDS = (
#     'sn', 'status', 'rf_band', 'rf_addr', 'address',
#     'longitude', 'latitude', 'unit', 'registered_time', 'memo'
# )
#
# # 集控上报灯控字段
# LAMPCTRL_FIELDS = (
#     'sn', 'is_repeated', 'sequence', 'status', 'rf_band',
#     'latitude', 'longitude', 'address', 'rf_addr',
#     'memo', 'registered_time', 'lamp_type'
# )

# 集控上报集控状态数据字段
HUBSTATUS_FIELDS = ()

# 集控上报灯控状态数据字段
LAMP_CTRL_STATUS_FIELDS = ()

# 集控上报告警数据字段
ALERT_FIELDS = ()
