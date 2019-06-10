#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/10
"""
import datetime
from collections import defaultdict

from equipment.models import LampCtrl
from group.models import LampCtrlGroup
from policy.models import PolicySet, Policy, PolicySetSendDown
from utils.data_handle import record_inventory
from utils.sunrise_sunset import calculate_sunrise_sunset


def before_update_group(instance, serializer_data):
    """下发(模式)分组之前 数据库操作"""
    hub = instance
    group_num = serializer_data['group_num']
    lampctrl_sns = serializer_data['lampctrl']

    if not LampCtrlGroup.objects.filter_by(is_default=False).exists():
        # 自定义分组不存在
        for lampctrl_sn in lampctrl_sns:
            lampctrl = LampCtrl.objects.get(sn=lampctrl_sn)
            LampCtrlGroup.objects.create(
                hub=hub, lampctrl=lampctrl, group_num=group_num
            )
    else:
        # 自定义分组存在 灯控有分组则修改 无分组则创建
        for lampctrl_sn in lampctrl_sns:
            lampctrl = LampCtrl.objects.get(sn=lampctrl_sn)
            LampCtrlGroup.objects.filter_by().update_or_create(
                hub=hub, lampctrl=lampctrl, is_default=False,
                defaults=dict(group_num=group_num)
            )

    # 更新后的自定义分组配置
    group_config = defaultdict(list)
    group_nums = set(LampCtrlGroup.objects.filter_by(hub=hub,
                                                     is_default=False).values_list(
        'group_num', flat=True))
    for group_num in group_nums:
        group_config[group_num] = list(
            LampCtrlGroup.objects.filter_by(hub=hub,
                                            group_num=group_num).values_list(
                'lampctrl', flat=True))

    return group_config


def before_pattern_grouping(instance, serializer_data):
    """下发(模式)分组之前 数据库操作"""
    hub = instance
    group_num = serializer_data['group_num']
    memo = serializer_data['memo']
    group_num_rest = serializer_data['group_num_rest']
    memo_rest = serializer_data['memo_rest']
    seg = serializer_data['segmentation']
    sel = serializer_data['select']
    group_config = {group_num: [], group_num_rest: []}
    # # 删除已存在分组
    # hub.hub_group.filter_by().soft_delete()
    # 创建分组
    lampctrls = hub.hub_lampctrl.filter_by().order_by('sequence')
    for i, lampctrl in enumerate(lampctrls):
        if i % (seg + sel) in range(seg):
            # 未被选的lampctrl
            LampCtrlGroup.objects.create(
                hub=hub,
                lampctrl=lampctrl,
                group_num=group_num_rest,
                memo=memo_rest
            )
            group_config[group_num_rest].append(lampctrl.sn)
        else:
            # 被选的lampctrl
            LampCtrlGroup.objects.create(
                hub=hub,
                lampctrl=lampctrl,
                group_num=group_num,
                memo=memo
            )
            group_config[group_num].append(lampctrl.sn)
    return group_config


def before_custom_grouping(instance, serializer_data):
    """下发(自定义)分组之前 数据库操作"""
    hub = instance
    configs = serializer_data['configs']
    group_config = defaultdict(list)
    # # 删除已存在分组
    # hub.hub_group.filter_by().soft_delete()
    # 创建分组
    for config in configs:
        lampctrl_sns = config['lampctrl']
        group_num = config['group_num']
        memo = config['memo']
        # 创建分组
        for lampctrl_sn in lampctrl_sns:
            lampctrl = LampCtrl.objects.get_or_404(sn=lampctrl_sn)
            LampCtrlGroup.objects.create(
                hub=hub,
                lampctrl=lampctrl,
                group_num=group_num,
                memo=memo
            )
            group_config[group_num].append(lampctrl_sn)
    return group_config


def before_recycle_group(instance):
    """回收集控下的所有分组之前 数据库操作"""
    hub = instance
    # 删除所有自定义分组
    for i in hub.hub_group.filter_by(is_default=False):
        i.soft_delete()


def before_recycle_policy_set(instance):
    """回收集控下发策略集之前 数据库操作"""
    hub = instance
    # 删除所有自定义策略
    for i in hub.hub_send_down_policysets.all():
        i.soft_delete()


def after_gather_group(instance, custom_group, default_group):
    """
    采集分组后
    :param instance:
    :param custom_group: 自定义分组
    :param default_group: 默认分组
    :return:
    """
    pass


def before_send_down_policy_set(instance, item):
    """下发策略方案之前 数据处理+数据库操作
    :param instance:
    :param item: 集控下发策略详细信息
    [
        {
            "hub": "hub_sn2"
            "group_num": "1",
            "policyset_id": "1"
        },
        {
            "hub": "hub_sn2"
            "group_num": "2",
            "policyset_id": "1"
        }
    ]
    """
    # 先删除已有的下发策略
    for i in PolicySetSendDown.objects.filter_by(hub=instance):
        i.soft_delete()
    # 数据处理
    for im in item:
        group_num = im.get('group_num')
        policyset_id = im.get('policyset_id')
        policyset = PolicySet.objects.filter_by(id=policyset_id).first()

        policy_map = defaultdict(list)  # 策略-策略详情
        # policy map
        policy_ids = set(policyset.policys.filter_by().values_list('id', flat=True))
        for policy_id in policy_ids:
            # TODO 根据不同item产生不同结果
            a = Policy.objects.get(id=policy_id).item
            policy_map[policy_id] = convert_item(Policy.objects.get(id=policy_id).item)

        policys = defaultdict(list)  # 分组-日期/策略
        # 没有分组 默认为全部 标记为100
        group_num = group_num or "100"
        # policys[group_num] = {'detail': [], 'policyset_name': "xx", "policyset_id": 1}
        policys[group_num] = {'detail': []}
        for relation in policyset.policyset_relations.filter_by():
            # policys[group_num].append(
            #     dict(execute_date=relation.execute_date.strftime('%Y-%m-%d'),
            #          policy=relation.policy.id)
            # )
            policys[group_num]['detail'].append(
                dict(execute_date="'{}'".format(relation.execute_date.strftime('%Y-%m-%d')),
                     policy=relation.policy.id)
            )

        # TODO 不指定分组， 如何存策略集下发表
        # 数据库同步 100分组代表下发所有分组
        PolicySetSendDown.objects.create(
            hub=instance,
            policyset=policyset,
            group_num=int(group_num)
        )
        return policy_map, policys


def convert_item(items):
    """
    将不同类型item转换为统一格式的item(暂时只处理时控和经纬控，其他的之后在处理)
    :param items:
    时控:
    {
        "type": 0,
        "action": "99,99",
        "minute": "55",
        "hour": "16"
    }
    经纬控:
    {
        "type": 1,
        "action": "99,99",
        "longitude": 122.22,
        "latitude": 22,
        "s_type": "sunset",
        "offset": -1
    }
    :return: 统一格式
    {
        "hour": "6",
        "minute": "30",
        "second": "20",
        "action": "0,0"
    }
    """
    ret_items = []
    for item in items:
        type = item.get('type')
        ret_item = {}
        # 如果添加type类型，直接加条件语句进行处理
        if type == 0:
            # 时控
            ret_item["hour"] = item.get("hour")
            ret_item["minute"] = item.get("minute")
            ret_item["second"] = item.get("second", "0")
            ret_item["action"] = item.get("action")
        elif type == 1:
            # 经纬控
            # TODO 这里固定date值，之后经纬度的计算需要放到集控上进行
            ss = calculate_sunrise_sunset(longitude=item.get("longitude"), latitude=item.get("latitude"), date="2019-06-04")
            sunrise = ss.get('sunrise')
            sunset = ss.get('sunset')
            s_type = item.get('s_type')
            if s_type == 'sunset':
                t = sunset + datetime.timedelta(minutes=item['offset'])
            elif s_type == 'sunrise':
                t = sunrise + datetime.timedelta(minutes=item['offset'])
            ret_item["hour"] = str(t.hour)
            ret_item["minute"] = str(t.minute)
            ret_item["second"] = str(t.second)
            ret_item["action"] = item.get("action")
        else:
            # 无效type
            pass
        if ret_item:
            ret_items.append(ret_item)
    return ret_items


def after_load_inventory(instance, inventory):
    """采集集控配置后 数据库操作"""
    # TODO 采集配置和注册时的操作相似， 是否需要合并?
    record_inventory(inventory=inventory)
