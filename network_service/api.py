#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 
"""
# TODO 研究一下数据库处理操作是否可以通过django自定义信号量的方式来完成(或许可以)
import datetime

from django.db import connections, transaction

from notify.models import Alert

from hub.models import Hub, Unit


class SLMS(object):
    """
    interface
    """

    @staticmethod
    def register(inventory, default_group):
        """
        注册
        """
        for conn in connections.all():
            conn.queries_log.clear()
            conn.close_if_unusable_or_obsolete()

        print('network_service >> api.py >> register')
        hub = inventory.get('hub', {})
        lamps = inventory.get('lamps', {}) or {}
        try:
            with transaction.atomic():
                # 有管理单元
                unit = None
                unit_name = hub.get('unit')
                if unit_name:
                    unit, _ = Unit.objects.get_or_create(name=unit_name)
                hub_data = dict(
                    status = hub.get('status'),
                    rf_band=hub.get('rf_band'),
                    rf_addr=hub.get('rf_addr'),
                    address=hub.get('address'),
                    longitude=hub.get('longitude'),
                    latitude=hub.get('latitude'),
                    memo=hub.get('memo'),
                    unit=unit,
                    registered_time=hub.get('registered_time') or datetime.date.today()
                )
        except:
            pass



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
            event='集控脱网', level=3, object=hub,
            object_type='hub', alert_source=hub_sn, is_solved=False,
            defaults=dict(is_solved=False)
        )

        if is_created:
            # 集控之前正常，告警
            alert.record_alarm(event='集控脱网', level=3, object=hub_sn,
                               object_type='hub',
                               alert_source=hub_sn, value=1, status=3)
            pass

    @staticmethod
    def record_connect_hub(hub_sn):
        """
        1. 集控连接
        2. 集控重连
        :param hub_sn: 集控sn号
        """
        print('network_service >> api.py >> record_connect_hub')
        # TODO 集控状态更新 status=1
        # TODO 如果存在未处理告警，变为已处理， 告警生成的工单变为已处理
        return dict(code=0, reason="")

    @staticmethod
    def report_status(content):
        """
        集控定时上报三相电能数据
        :param body: 三相电数据
        """
        print('network_service >> api.py >> report_status')
        assert isinstance(content, dict)
        # TODO 是否需要进行格式检验

        # TODO 存入数据库
        # TODO 分析三相电数据，作相应更新和告警
        return dict(code=0, reason="")

    @staticmethod
    def report_alarms(content):
        """
        集控定时上报告警
        :param hub_sn: 集控sn号
        :param body: 告警数据
        """
        print('network_service >> api.py >> report_alarms')
        assert isinstance(content, dict)
        # TODO 是否需要进行格式检验

        # TODO 分析数据，告警 改变灯控状态
        return dict(code=0, reason="")
