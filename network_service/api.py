#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 
"""
# TODO 研究一下数据库处理操作是否可以通过django自定义信号量的方式来完成(或许可以)

from notify.models import Alert

from hub.models import Hub


class SLMS(object):
    """
    interface
    """

    @staticmethod
    def record_offline_hub(hub_sn):
        """
        集控脱网
        :param hub_sn: 集控sn号
        """
        print('network_service >> api.py >> record_offline_hub')
        # TODO 集控是否在数据库中， 在则删除
        Hub.objects.filter(sn=hub_sn).update(status=3)
        # TODO 产生告警， 存在则更新时间， 不存在则新增告警 逻辑是否需要在record_alarm中实现
        alert, is_created = Alert.objects.update_or_create(
            event='集控脱网', level=3, object=hub_sn,
            object_type='hub', alert_source=hub_sn, is_solved=False,
            defaults=dict(status=3)
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
