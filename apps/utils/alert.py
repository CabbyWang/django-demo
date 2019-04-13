#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/12
"""
import copy
import datetime

from django.conf import settings

from notify.models import Alert
from hub.models import Hub
from lamp.models import LampCtrl
from user.models import Permission, User
from workorder.models import WorkOrder
# from utils.sms import SMS

from .tts import AlertTTS, WorkorderTTS


def record_hub_alarm(value=0):
    event, alert_source, object_type, object, level, status = {}
    record_alarm(event, alert_source, object_type, object, level, status)


def record_alarm(event, object_type, alert_source, object, level, status):
    """
    记录告警
    :param event: 故障名称
    :param object_type: 故障设备的类型
    :param alert_source: 告警源
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
    alert, is_created = Alert.object.update_or_create(
        event=event, object_type=object_type, alert_source=alert_source,
        object=object, level=level,
        defaults=dict(status=status)
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

        # alert = models.OneToOneField(Alert, related_name='alert_workorder',
        #                              null=True, blank=True, help_text='告警编号')
        # type = models.IntegerField(choices=TYPES, help_text='工单类型')
        # obj_sn = models.CharField(max_length=32, null=True, blank=True,
        #                           help_text='对象编号')
        # lampctrl = models.ForeignKey(LampCtrl,
        #                              related_name='lampctrl_workorder',
        #                              null=True, blank=True)
        # sequence = models.IntegerField(null=True,
        #                                blank=True)  # 维修历史根据逻辑号查，因为sn号可能会改变
        # user = models.ForeignKey(User, related_name='user_workorder',
        #                          null=True, blank=True)
        # message = models.CharField(max_length=255)

        # 生成工单
        message = '{}，由告警自动生成'.format(event)

        WorkOrder.objects.create(alert=alert, type=2, obj_sn=object, lampctrl)
