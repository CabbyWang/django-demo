#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/8
"""
import random

from equipment.models import Hub, LampCtrl
from base.models import Unit
from group.models import LampCtrlGroup
from projectinfo.models import ProjectInfo

__all__ = ("record_inventory", "record_default_group")


def _prepare_inventory(inventory):
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
        if k not in Hub.fields():
            hub.pop(k)
    # hub = {k: v for k, v in hub.items() if k in Hub.fields()}

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
            if k not in LampCtrl.fields():
                item.pop(k)
        # item = {k: v for k, v in item.items() if k in LampCtrl.fields()}
    return inventory


def _prepare_default_group(default_group):
    """清洗数据"""
    assert isinstance(default_group, dict), '"default_group" should be a dict'
    return default_group or {}


def record_inventory(inventory):
    """
    数据库记录集控上报信息
    :param inventory:
    :return:
    """
    _prepare_inventory(inventory=inventory)
    hub_inventory = inventory.get('hub', {})
    hub_sn = hub_inventory.get('sn')
    lamps = inventory.get('lamps', {}) or {}
    # 修改或创建集控信息
    hub, _ = Hub.objects.update_or_create(sn=hub_sn,
                                          defaults=hub_inventory)
    # 删除数据库中存在 上报数据中却不存在的灯控
    LampCtrl.objects.filter_by().exclude(sn__in=set(lamps.keys())).delete()
    # 修改或创建灯控信息
    for lampctrl_sn, item in lamps.items():
        LampCtrl.objects.update_or_create(
            sn=lampctrl_sn,
            hub=hub,
            defaults=lamps.get(lampctrl_sn)
        )


def record_default_group(hub_sn, default_group):
    """
    数据库记录集控默认分组信息
    :param hub_sn:
    :param default_group:
    :return:
    """
    _prepare_default_group(default_group=default_group)
    hub = Hub.objects.get(sn=hub_sn)
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

