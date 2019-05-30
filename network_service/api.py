#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 
"""
# TODO 研究一下数据库处理操作是否可以通过django自定义信号量的方式来完成(或许可以)
import datetime

from django.db import transaction

from equipment.models import LampCtrl
from network_service.config import REPORT_STATUS_CYCLE
from notify.models import Alert

from equipment.models import Hub
from report.models import HubConsumption, LampCtrlConsumption
from setting.models import Setting
from status.models import HubStatus, HubLatestStatus, LampCtrlStatus, \
    LampCtrlLatestStatus
from workorder.models import WorkOrder
from utils.alert import record_alarm, record_report_alarm, \
    record_hub_disconnect
from utils import refresh_connections
from utils.data_handle import record_inventory, record_default_group
from utils.settings import HUB_ALARMS, LAMP_ALARMS


class SLMS(object):
    """
    interface
    """

    @classmethod
    def register(cls, data):
        """
        注册
        """
        refresh_connections()
        print('network_service >> api.py >> register')
        try:
            with transaction.atomic():
                hub_inventory = data.get('hub', {})
                hub_sn = hub_inventory.get('sn')
                record_inventory(inventory=data)
                record_default_group(
                    hub_sn=hub_sn,
                    default_group=data.get('default_group')
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
        refresh_connections()
        print('network_service >> api.py >> record_offline_hub')
        # TODO 集控是否在数据库中， 在则删除
        Hub.objects.filter_by(sn=hub_sn).update(status=3)
        # TODO 产生告警， 存在则更新时间， 不存在则新增告警 逻辑是否需要在record_alarm中实现
        hub = Hub.objects.filter_by(sn=hub_sn).first()
        if not hub:
            return
        # alert, is_created = Alert.objects.update_or_create(
        #     event='集控脱网', level=3, object=hub.sn,
        #     object_type='hub', alert_source=hub, is_solved=False
        # )

        # if is_created:
        # 集控之前正常，告警
        # record_alarm(
        #     event='集控脱网', object_type='hub', alert_source=hub,
        #     object=hub_sn, level=3, status=3
        # )
        record_hub_disconnect(hub)

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
            status='finished', description='集控重连，自动完成'
        )
        alert_qs.update(
            solved_time=datetime.datetime.now(), is_solved=True, memo='集控重连'
        )

    @classmethod
    def report_status(cls, content):
        """
        集控定时上报三相电能数据
        1. 记录集控上报状态信息(HubStatus/LampCtrlStatus)(HubLatestStatus/LampLatestCtrlStatus)
        2. 能耗报表的维护更新(便于报表生成)
        3. 单灯告警检验(通过电流判断是否 节点异常/节点漏电)
        :param content: 三相电数据 dict 反序列化后的 集控上报的数据包
        """
        # TODO 老板赶时间 后期再优化吧
        refresh_connections()
        print('network_service >> api.py >> report_status')
        assert isinstance(content, dict)
        # TODO 是否需要进行格式检验
        # cls.prepare_report_status_content(content)

        hub_sn = content.get('sender')
        body = content.get('body', {})
        hub_status = body.get('hub', {}) or {}
        lamps_status = body.get('lamps', {}) or {}
        # TODO 存入数据库
        try:
            with transaction.atomic():
                # HubStatus表和HubLatestStatus表
                for hub_sn, value in hub_status.items():
                    hub = Hub.objects.get(sn=hub_sn)
                    # TODO 保留小数点后两位
                    data = {
                        'A_voltage': value.get('A_voltage'),
                        'A_current': value.get('A_current'),
                        'A_power': value.get('A_voltage') * value.get('A_current'),
                        'A_consumption': value.get('A_consumption'),
                        'B_voltage': value.get('B_voltage'),
                        'B_current': value.get('B_current'),
                        'B_power': value.get('B_voltage') * value.get('B_current'),
                        'B_consumption': value.get('B_consumption'),
                        'C_voltage': value.get('C_voltage'),
                        'C_current': value.get('C_current'),
                        'C_power': value.get('C_voltage') * value.get('C_current'),
                        'C_consumption': value.get('C_consumption'),
                        'consumption': value.get('consumption'),
                        'power': 1.732 * 0.38 * value.get('A_current') * 0.8,  # 单位KW
                        'voltage': 1.732 * (value.get('A_voltage') + value.get('B_voltage') + value.get('C_voltage')) / 3,
                        'current': (value.get('A_current') + value.get('B_current') + value.get('C_current')) / 3
                    }
                    HubStatus.objects.create(hub=hub, **data)

                    voltage = data.get('voltage')
                    current = data.get('current')
                    consumption = data.get('consumption')
                    has_three_phase = voltage and current
                    if has_three_phase and consumption:
                        # 集控有三相电，上报数据有能耗
                        last_status = HubLatestStatus.objects.filter_by(hub=hub).first()
                        last_csp = last_status.consumption if last_status else 0
                        gap = consumption - last_csp
                        hub_csp = HubConsumption.objects.filter_by(hub=hub, date=datetime.date.today()).first()
                        csp = hub_csp + gap if hub_csp else gap
                        HubConsumption.objects.update_or_create(
                            hub=hub, date=datetime.date.today(),
                            defaults={'consumption': csp}
                        )
                    else:
                        # 集控无三相电，上报数据无能耗
                        hub_csp = HubConsumption.objects.filter_by(
                            hub=hub,
                            date=datetime.date.today()
                        ).first()
                        gap = voltage * current * REPORT_STATUS_CYCLE
                        csp = hub_csp + gap if hub_csp else gap
                        HubConsumption.objects.update_or_create(
                            hub=hub, date=datetime.date.today(),
                            defaults={'consumption': csp}
                        )

                    HubLatestStatus.objects.update_or_create(
                        sn=hub_sn, defaults=data
                    )

                # LampCtrlStatus表和LampCtrlLatestStatus表
                for lampctrl_sn, item in lamps_status.items():
                    lampctrl = LampCtrl.objects.get(sn=lampctrl_sn)
                    route1, route2 = item.get("brightness", (0, 0)) or (0, 0)  # 兼容brightness=[]
                    energy = item.get("electric_energy", {})
                    data = {
                        'route_one': route1,
                        'route_two': route2,
                        'voltage': energy.get('voltage'),
                        'power': energy.get('power'),
                        'current': energy.get('current'),
                        'consumption': energy.get('consumption')
                    }
                    LampCtrlStatus.objects.create(lampctrl=lampctrl, hub=hub, **data)

                    voltage = data.get('voltage')
                    current = data.get('current')

                    lampctl_csp = LampCtrlConsumption.objects.filter_by(
                            lampctrl=lampctrl,
                            date=datetime.date.today()
                        ).first()
                    gap = voltage * current * REPORT_STATUS_CYCLE
                    csp = lampctl_csp + gap if lampctl_csp else gap
                    LampCtrlConsumption.objects.update_or_create(
                        lampctrl=lampctrl, hub=hub, date=datetime.date.today(),
                        defaults={'consumption': csp}
                    )

                    LampCtrlLatestStatus.objects.update_or_create(
                        lampctrl=lampctrl, hub=hub, defaults=data
                    )

                    # 记录灯具开关状态
                    # switch_status = 1 if energy.get('route2') or energy.get('route1') else 0  # 灯具打开则为1， 关闭为0
                    switch_status = 1 if energy.get('current') and energy.get('voltage') else 0  # 灯具打开则为1， 关闭为0
                    LampCtrl.objects.filter_by(sn=lampctrl_sn).update(switch_status=switch_status)

                    # 单灯告警 判断电流(current)是否低于设置阈值
                    # 获取最小阈值和最大阈值
                    min_current_obj = Setting.objects.filter(option='min_current').first()
                    # TODO 配置中有max_current参数？
                    max_current_obj = Setting.objects.filter(option='max_current').first()
                    # 未设置最小电流阈值时使用默认阈值
                    # TODO 默认值写入配置文件中
                    min_current = float(min_current_obj.value) if min_current_obj else 0.02
                    max_current = float(max_current_obj.value) if max_current_obj else 2
                    current = data.get('current', 0)
                    if switch_status:
                        # 电流小于最小阈值
                        if current < min_current:
                            record_alarm(
                                event=u'节点异常', object_type='lamp',
                                alert_source=hub, object=lampctrl_sn,
                                level=1, status=2
                            )
                        # 电流大于最大阈值
                        if current > max_current:
                            record_alarm(
                                event=u'节点漏电', object_type='lamp',
                                alert_source=hub, object=lampctrl_sn,
                                level=1, status=2
                            )
                    else:
                        if current > min_current:
                            record_alarm(
                                event=u'节点漏电', object_type='lamp',
                                alert_source=hub, object=lampctrl_sn,
                                level=1, status=2
                            )

        # TODO 能耗报表的维护?
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
        1. 记录告警信息
        2. 改变集控/灯控状态
        :param content: 告警数据 dict 反序列化后的 集控上报的数据包
        """
        refresh_connections()
        print('network_service >> api.py >> report_alarms')
        assert isinstance(content, dict)
        cls.prepare_report_alarms_content(content)
        # TODO 是否需要进行格式检验
        hub_sn = content.get('sender')
        body = content.get('body', {}).get('data', {})
        hub = Hub.objects.filter_by(sn=hub_sn).first()
        try:
            with transaction.atomic():
                if not hub:
                    return
                # 集控告警
                hub_alarms = body.get('hub', {})
                for k, v in HUB_ALARMS.items():
                    time_value = hub_alarms.get(k, {})
                    record_report_alarm(
                        event=v.get('event'), object_type='hub',
                        alert_source=hub, object=hub_sn,
                        level=v.get('level'), status=v.get('status'),
                        occurred_time=time_value.get('datetime'),
                        value=time_value.get('value')
                    )
                # 灯控告警
                lampctrl_alarms = body.get('lamps', {})
                for lampctrl_sn, alarms in lampctrl_alarms.items():
                    lampctrl = LampCtrl.objects.filter_by(sn=lampctrl_sn).first()
                    if not lampctrl:
                        continue
                    for k, v in LAMP_ALARMS.items():
                        time_value = alarms.get(k, {})
                        record_report_alarm(
                            event=v.get('event'), object_type='hub',
                            alert_source=hub, object=lampctrl_sn,
                            level=v.get('level'), status=v.get('status'),
                            occurred_time=time_value.get('datetime'),
                            value=time_value.get('value')
                        )
        except Exception as ex:
            return dict(code=1, message=str(ex))
        else:
            return dict(code=0, message='上报成功')
