#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/30
"""
from datetime import datetime

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Hub
from workorder.models import WorkOrder


@receiver(pre_delete, sender=Hub)
def delete_hub(sender, instance=None, using=None, **kwargs):
    """删除集控时， 同步删除相关联项"""
    del_kw = dict(
        deleted_time=datetime.now(),
        is_deleted=True
    )
    # 删除集控状态历史纪录
    instance.hub_status.update(**del_kw)
    # 删除灯控
    instance.hub_lampctrl.update(**del_kw)
    # 删除灯控分组
    instance.hub_group.update(**del_kw)
    # 删除告警
    # self.hub_alert.update(**del_kw)
    instance.hub_alert.delete()
    # 删除策略下发表
    instance.hub_send_down_policysets.update(**del_kw)
    # 删除集控当天能耗表
    instance.hub_consumption.update(**del_kw)
    # 删除用户权限
    instance.hub_permision.update(**del_kw)
    # 删除巡检报告
    instance.hub_inspetion.update(**del_kw)
    # TODO 删除工单？
    # type=1 obj_sn=self.sn
    # self.hub_lampctrl.update(deleted_time=datetime.now(), is_deleted=True)
    # 删除巡检报告具体项表
    instance.hub_inspection_item.update(**del_kw)
