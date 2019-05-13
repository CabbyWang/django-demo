#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/12
"""
import copy
import datetime

import requests
from django.conf import settings

from notify.models import Alert
from equipment.models import Hub, LampCtrl
from setting.models import Setting
from user.models import Permission, User
from workorder.models import WorkOrder
# from utils.sms import SMS

from .tts import AlertTTS, WorkorderTTS
from .sms import send_alert_sms


def record_hub_alarm(value=0):
    event, alert_source, object_type, object, level, status = {}
    record_alarm(event, alert_source, object_type, object, level, status)


def record_alarm(event, object_type, alert_source, object, level, status):
    """
    记录告警
    :param event: 故障名称
    :param object_type: 故障设备的类型
    :param alert_source: 告警源(hub instance)
    :param object: 故障设备sn号
    :param level: 故障级别
    :param status: 1正常、2故障还是3脱网
    """

    if object_type == 'hub':
        # 改变集控状态
        Hub.objects.filter_by(sn=object).update(status=status)
    elif object_type == 'lamp':
        # 改变灯控状态
        LampCtrl.objects.filter_by(sn=object).update(status=status)

    # 告警不存在， 新增告警 / 告警存在， 更新时间
    alert, is_created = Alert.objects.filter_by().update_or_create(
        event=event, object_type=object_type, alert_source=alert_source,
        object=object, level=level, is_solved=False
    )

    if is_created:
        # 生成告警语音
        tts = AlertTTS()
        body = dict(
            id=alert.id,
            event=event,
            object_type=object_type,
            alert_source=alert_source,
            object=object,
            level=level
        )
        tts.generate_audio(body)

        # 生成工单
        # TODO 工单type需要根据之后的类型进行修改
        WorkOrder.objects.create(
            alert=alert, type=2, obj_sn=object,
            memo='{}，由告警自动生成'.format(event), status='todo'
        )

        # 发送告警短信
        send_alert_sms(**body)
