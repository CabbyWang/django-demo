#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 
"""
# TODO 研究一下数据库处理操作是否可以通过django自定义信号量的方式来完成(或许可以)
import copy
import datetime
import random

from django.db import connections, transaction

from lamp.models import LampCtrl, LampCtrlGroup
from notify.models import Alert

from hub.models import Hub, Unit, HubStatus
from projectinfo.models import ProjectInfo
from workorder.models import WorkOrder
from utils.alert import record_alarm

from .serializers import DataSerializer
from .config import HUB_FIELDS, LAMPCTRL_FIELDS


class SLMS(object):
    """
    interface
    """

    @staticmethod
    def refresh_connections():
        for conn in connections.all():
            conn.queries_log.clear()
            conn.close_if_unusable_or_obsolete()

    @staticmethod
    def prepare_inventory(inventory):
        """清洗数据"""
        # TODO 配置文件不规范的情况
        hub = inventory['hub'] or {}
        lamps = inventory['lamps'] or {}
        hub_sn = hub.get('sn')

        # 集控有unit字段则使用， 否则为None
        unit = None
        unit_name = hub.get('unit')
        if unit_name:
            unit, _ = Unit.objects.get_or_create(name=unit_name)
        hub['unit'] = unit

        # 集控重定位过， 不上报集控经纬度
        first = Hub.objects.filter_by(sn=hub_sn).first()
        is_redirect = first.is_redirect if first else 0
        if is_redirect:
            hub.pop('longitude', None)
            hub.pop('latitude', None)
        else:
            # 未重定位过， 如果集控上报经纬度为空或0，则使用城市中心点经纬度
            if not hub.get('longitude') or hub.get('latitude'):
                ran_lon = random.uniform(-0.001, 0.001)
                ran_lat = random.uniform(-0.0005, 0.0005)
                try:
                    first = ProjectInfo.objects.first()
                    city_longitude = first.longitude + ran_lon
                    city_latitude = first.latitude + ran_lat
                except AttributeError:
                    # projectinfo未配置
                    pass
                else:
                    hub['longitude'] = city_longitude
                    hub['latitude'] = city_latitude
        for k in list(hub.keys()):
            if k not in HUB_FIELDS:
                hub.pop(k)

        # 灯控
        # 布放过的灯控 不修改经纬度
        for lampctrl_sn, item in lamps.items():
            lampctrl = LampCtrl.objects.filter_by(sn=lampctrl_sn).first()
            on_map = lampctrl.on_map if lampctrl else False
            if on_map:
                item.pop('longitude', None)
                item.pop('latitude', None)
            item['lamp_type'] = item.get('type')
            for k in list(item.keys()):
                if k not in LAMPCTRL_FIELDS:
                    item.pop(k)
        return inventory

    @staticmethod
    def prepare_default_group(default_group):
        assert isinstance(default_group, dict)
        return default_group or {}

    @classmethod
    def register(cls, inventory, default_group):
        """
        注册
        """
        cls.refresh_connections()
        print('network_service >> api.py >> register')
        cls.prepare_inventory(inventory)
        cls.prepare_default_group(default_group)
        hub_inventory = inventory.get('hub', {})
        hub_sn = hub_inventory.get('sn')
        lamps = inventory.get('lamps', {}) or {}
        try:
            with transaction.atomic():
                # 修改或创建集控信息
                hub, _ = Hub.objects.update_or_create(sn=hub_sn, defaults=hub_inventory)
                # 删除数据库中存在 上报数据中却不存在的灯控
                LampCtrl.objects.filter_by().exclude(sn__in=set(lamps.keys())).delete()
                # 修改或创建灯控信息
                for lampctrl_sn, item in lamps.items():
                    LampCtrl.objects.update_or_create(
                        sn=lampctrl_sn,
                        hub=hub,
                        defaults=lamps.get(lampctrl_sn)
                    )

                # 删除数据库中原分组配置信息
                LampCtrlGroup.objects.filter_by(hub=hub, is_default=True).delete()
                # 创建默认分组信息
                for group_num, lamp_ctrls in default_group.items():
                    for lamp_ctrl_sn in lamp_ctrls:
                        lampctrl = LampCtrl.objects.filter_by(sn=lamp_ctrl_sn).first()
                        if not lampctrl:
                            continue
                        LampCtrlGroup.objects.create(
                            hub=hub, lampctrl=lampctrl,
                            group_num=group_num, is_default=True
                        )
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
        print('network_service >> api.py >> record_offline_hub')
        # TODO 集控是否在数据库中， 在则删除
        Hub.objects.filter_by(sn=hub_sn).update(status=3)
        # TODO 产生告警， 存在则更新时间， 不存在则新增告警 逻辑是否需要在record_alarm中实现
        hub = Hub.objects.filter_by(sn=hub_sn).first()
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
        cls.refresh_connections()
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
        cls.refresh_connections()
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
        cls.refresh_connections()
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
