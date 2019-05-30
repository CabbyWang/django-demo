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


def record_alarm(event, object_type, alert_source, object, level, status, occurred_time=datetime.datetime.now()):
    """
    记录告警
    :param event: 故障名称
    :param object_type: 故障设备的类型
    :param alert_source: 告警源(hub instance)
    :param object: 故障设备sn号
    :param level: 故障级别
    :param status: 1正常、2故障还是3脱网
    :param occurred_time: 告警发生时间, 默认为当前时间
    """

    if object_type == 'hub':
        # 改变集控状态
        Hub.objects.filter_by(sn=object).update(status=status)
    elif object_type == 'lamp':
        # 改变灯控状态
        LampCtrl.objects.filter_by(sn=object).update(status=status)
    else:
        # TODO illegal object type(warning)
        return

    # 告警不存在， 新增告警 / 告警存在， 更新时间
    alert, is_created = Alert.objects.filter_by().update_or_create(
        event=event, object_type=object_type, alert_source=alert_source,
        object=object, level=level, is_solved=False,
        defaults=dict(occurred_time=occurred_time)
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
            alert=alert, type=2 if object_type == 'lamp' else 1,
            obj_sn=object,
            memo='{}，由告警自动生成'.format(event), status='todo'
        )

        # 发送告警短信
        send_alert_sms(**body)


def record_report_alarm(event, object_type, alert_source, object, level, status, occurred_time, value):
    """
    处理集控上报告警
    :param event: 故障名称
    :param object_type: 故障设备的类型
    :param alert_source: 告警源(hub instance)
    :param object: 故障设备sn号
    :param level: 故障级别
    :param status: 1正常、2故障还是3脱网
    :param occurred_time: 告警发生时间, 默认为当前时间
    :param value: 0/1 0：无告警  1：有告警
    """
    if value == 0:
        # value为0，表示没有故障  消除告警
        unsolved_alert = Alert.objects.filter_by(
            event=event, object_type=object_type, alert_source=alert_source,
            object=object, level=level, status=status, is_solved=False
        ).first()
        if unsolved_alert:
            # 告警生成的工单变为已完成
            WorkOrder.objects.filter_by(alert=unsolved_alert).update(
                status='finished', finished_time=datetime.datetime.now(),
                memo='集控重连，自动完成'
            )
            unsolved_alert.__dict__.update(
                solved_time=datetime.datetime.now(),
                is_solved=True, memo='集控重连'
            )
    elif value == 1:
        # value为1, 表示存在故障  记录告警
        record_alarm(
            event=event, object_type=object_type, alert_source=alert_source,
            object=object, level=level, status=status,
            occurred_time=occurred_time
        )
    else:
        # TODO 无效value，日志记录
        pass


def record_hub_disconnect(hub):
    """
    记录集控脱网
    :param hub: Hub instance
    """
    record_alarm(
        event="集控脱网", object_type='hub', alert_source=hub,
        object=hub.sn, level=3, status=3
    )


def record_lamp_ctrl_trouble(lampctrl):
    """
    记录灯控故障
    :param lampctrl: LampCtrl instance
    """
    if not lampctrl:
        return
    assert isinstance(lampctrl, LampCtrl), \
        "lampctrl should be a instance of LampCtrl"
    lampctrl.status = 2
    lampctrl.save()
