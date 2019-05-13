#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 
"""
# TODO 研究一下数据库处理操作是否可以通过django自定义信号量的方式来完成(或许可以)
import copy
import datetime
import random

from django.db import transaction

from equipment.models import LampCtrl
from group.models import LampCtrlGroup
from notify.models import Alert

from equipment.models import Hub
from base.models import Unit
from status.models import HubStatus
from projectinfo.models import ProjectInfo
from workorder.models import WorkOrder
from utils.alert import record_alarm
from utils import refresh_connections
from utils.data_handle import record_inventory, record_default_group


class SLMS(object):
    """
    interface
    """

    @classmethod
    def register(cls, inventory, default_group):
        """
        注册
        """
        refresh_connections()
        print('network_service >> api.py >> register')
        try:
            with transaction.atomic():
                hub_inventory = inventory.get('hub', {})
                hub_sn = hub_inventory.get('sn')
                record_inventory(inventory=inventory)
                record_default_group(hub_sn=hub_sn,
                                     default_group=default_group)
        except Exception as ex:
            return dict(code=1, message=str(ex))
        else:
            return dict(code=0, message='注册成功')

    @staticmethod
    def record_offline_hub(hub_sn):
        """
        集控脱网
        :param hub_sn: 集控sn号
        """
        refresh_connections()
        print('network_service >> api.py >> record_offline_hub')
        # TODO 集控是否在数据库中， 在则删除
        Hub.objects.filter_by(sn=hub_sn).update(status=3)
        # TODO 产生告警， 存在则更新时间， 不存在则新增告警 逻辑是否需要在record_alarm中实现
        hub = Hub.objects.filter_by(sn=hub_sn).first()
        if not hub:
            return
        alert, is_created = Alert.objects.update_or_create(
            event='集控脱网', level=3, object=hub.sn,
            object_type='hub', alert_source=hub, is_solved=False
        )

        if is_created:
            # 集控之前正常，告警
            record_alarm(
                event='集控脱网', object_type='hub', alert_source=hub,
                object=hub_sn, level=3, status=3
            )
            pass

    @classmethod
    def record_connect_hub(cls, hub_sn):
        """
        1. 集控连接
        2. 集控重连
        :param hub_sn: 集控sn号
        """
        refresh_connections()
        print('network_service >> api.py >> record_connect_hub')
        # TODO 集控状态更新 status=1
        Hub.objects.filter_by(sn=hub_sn).update(status=1)
        # TODO 如果存在未处理告警，变为已处理， 告警生成的工单变为已处理
        alert_qs = Alert.objects.filter_by(
            event='集控脱网', level=3, alert_source=hub_sn, object_type='hub',
            object=hub_sn, is_solved=False
        )
        WorkOrder.objects.filter_by(alert__in=alert_qs).update(
            finished_time=datetime.datetime.now(),
            status='finished', memo='集控重连，自动完成'
        )
        alert_qs.update(
            solved_time=datetime.datetime.now(), is_solved=True, memo='集控重连'
        )

    @staticmethod
    def prepare_report_status_content(content):
        """集控上报三相电能数据预处理"""
        # TODO 数据预处理
        return content

    @classmethod
    def report_status(cls, content):
        """
        集控定时上报三相电能数据
        :param content: 三相电数据 dict 反序列化后的 集控上报的数据包
        """
        refresh_connections()
        print('network_service >> api.py >> report_status')
        assert isinstance(content, dict)
        cls.prepare_report_status_content(content)
        # TODO 是否需要进行格式检验

        hub_sn = content.get('sender')
        body = content.get('body')
        hub_status = body.get('hub', {}) or {}
        lamps_status = body.get('lamps', {}) or {}
        # TODO 存入数据库
        try:
            with transaction.atomic():
                # HubStatus表
                # HubStatus.objects.create(body)
                # TODO
                pass
        # TODO 分析三相电数据，作相应更新和告警
        except Exception as ex:
            return dict(code=1, message=str(ex))
        else:
            return dict(code=0, message='上报成功')

    @staticmethod
    def prepare_report_alarms_content(content):
        """集控上报告警数据预处理"""
        # TODO 数据预处理
        return content

    @classmethod
    def report_alarms(cls, content):
        """
        集控定时上报告警
        :param content: 告警数据 dict 反序列化后的 集控上报的数据包
        """
        refresh_connections()
        print('network_service >> api.py >> report_alarms')
        assert isinstance(content, dict)
        cls.prepare_report_alarms_content(content)
        # TODO 是否需要进行格式检验

        # TODO 分析数据，告警 改变灯控状态
        hub_sn = content.get('sender')
        body = content.get('body')
        try:
            with transaction.atomic():

                pass
        except Exception as ex:
            return dict(code=1, message=str(ex))
        else:
            return dict(code=0, message='上报成功')
