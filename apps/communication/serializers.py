#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/10
"""
from collections import defaultdict

from rest_framework import serializers

from django.utils.translation import ugettext_lazy as _

from equipment.models import LampCtrl, Hub
from group.models import LampCtrlGroup
from utils.exceptions import InvalidInputError


class GatherLampCtrlSerializer(serializers.Serializer):

    lampctrl = serializers.ListField(required=True, min_length=1)

    @staticmethod
    def validate_lampctrl(lampctrls):
        """
        检验灯控是否存在
        :param lampctrls: 灯控列表
        :return:
        {
            "hub1": ["lamp1", "lamp2"],
            "hub2": ["lamp3", "lamp4"]
        }
        """
        # 验证灯控是否存在
        not_exists_lampctrl = []
        for sn in lampctrls:
            if not LampCtrl.objects.filter_by(sn=sn).exists():
                not_exists_lampctrl.append(sn)
        if not_exists_lampctrl:
            raise serializers.ValidationError(
                'Lamp controls [{}] are not exist.'.format(
                    ', '.join(not_exists_lampctrl))
            )

        ret = defaultdict(list)
        hub_sns = LampCtrl.objects.filter(
            sn__in=lampctrls).values_list('hub', flat=True)
        for sn in lampctrls:
            lampctrl = LampCtrl.objects.get(sn=sn)
            ret[lampctrl.hub.sn].append(sn)
        # for hub_sn in hub_sns:
        #     hub = Hub.objects.get_or_404(sn=hub_sn)
        #     lampctrls = LampCtrl.objects.filter(hub=hub).values_list('sn', flat=True)
        #     ret[hub_sn] = list(lampctrls)
        return ret


class ControlLampSerializer(GatherLampCtrlSerializer):
    action = serializers.CharField(required=True)

    @staticmethod
    def validate_action(action):
        actions = action.split(',')
        if len(actions) != 2:
            raise InvalidInputError('the format of action must like "0,80"')
        route1, route2 = [int(i) for i in actions]
        if route1 < 0 or route1 > 255 or route2 < 0 or route2 > 255:
            raise InvalidInputError(
                'the brightness value must between 0 and 255')
        return action


class HubIsExistedSerializer(serializers.Serializer):
    """
    验证列表中的集控是否存在
    """

    hub = serializers.ListField(
        required=True, min_length=1,
        child=serializers.PrimaryKeyRelatedField(
            queryset=Hub.objects.filter_by(),
            error_messages={
                'does_not_exist': _('hub "{pk_value}" does not exist.')
            }
        )
    )

    @staticmethod
    def validate_hub(hubs):
        not_exists_hub = []
        for hub_sn in hubs:
            if not Hub.objects.filter_by(sn=hub_sn).exists():
                not_exists_hub.append(hub_sn)
        if not_exists_hub:
            raise serializers.ValidationError(
                'hubs [{}] are not exist.'.format(', '.join(not_exists_hub)))
        return hubs


class ControlAllSerializer(serializers.Serializer):

    hub = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Hub.objects.filter_by()
        )
    )
    action = serializers.ChoiceField(choices=['open', 'close'])

    @staticmethod
    def validate_action(action):
        if action == 'open':
            return '255,255'
        return '0,0'


class PatternGroupSerializer(serializers.Serializer):
    """下发(模式)分组"""

    hub = serializers.CharField(required=True)
    group_num = serializers.IntegerField(required=True, max_value=99, min_value=1)
    memo = serializers.CharField(required=False, allow_blank=True)
    group_num_rest = serializers.IntegerField(required=True, max_value=99, min_value=1)
    memo_rest = serializers.CharField(required=False, allow_blank=True)
    segmentation = serializers.IntegerField(required=True, max_value=6, min_value=1)
    select = serializers.IntegerField(required=True, max_value=5, min_value=1)

    @staticmethod
    def validate_hub(hub_sn):
        if not Hub.objects.filter_by(sn=hub_sn).exists():
            msg = _('hub [{}] is not exist.'.format(', '.join(hub_sn)))
            raise InvalidInputError(msg)
        return hub_sn

    def validate(self, attrs):
        hub_sn = self.initial_data['hub']
        hub = Hub.objects.get_or_404(sn=hub_sn)
        # 自定义分组已存在
        if LampCtrlGroup.objects.filter_by(hub=hub, is_default=False).exists():
            raise InvalidInputError('custom group has been existed')
        # 两个分组id不能相同
        if attrs["group_num"] == attrs["group_num_rest"]:
            raise InvalidInputError('two group id must be different')
        # 分组id不能与默认分组的id相同
        hub_sn = self.context['view'].kwargs.get('pk')
        hub = Hub.objects.get_or_404(sn=hub_sn)
        default_groups = hub.hub_group.filter_by(is_default=True).values_list(
            'group_num', flat=True)
        if attrs['group_num'] in default_groups or attrs['group_num_rest'] in default_groups:
            raise InvalidInputError(
                'group number must be different with default groups')
        return attrs


class CustomGroupingSerializer(serializers.Serializer):
    """下发(自定义)分组"""

    hub = serializers.CharField(required=True)
    configs = serializers.ListField(required=True)

    @staticmethod
    def validate_hub(hub_sn):
        if not Hub.objects.filter_by(sn=hub_sn).exists():
            msg = _('hub [{}] is not exist.'.format(', '.join(hub_sn)))
            raise InvalidInputError(msg)
        return hub_sn

    def validate_configs(self, configs):
        """
        {
            "configs": [
                {
                    "lampctrl": ["001", "002"],
                    "group_num": 1,
                    "memo": ""
                },
                {
                    "lampctrl": ["003", "004"],
                    "group_num": 2,
                    "memo": ""
                }
            ]
        }
        """
        hub_sn = self.initial_data['hub']
        hub = Hub.objects.get_or_404(sn=hub_sn)
        # 自定义分组已存在
        if LampCtrlGroup.objects.filter_by(hub=hub, is_default=False).exists():
            raise InvalidInputError('custom group has been existed')
        for item in configs:
            # 数据项中必须包含"lampctrl", "group_num", "memo"字段
            if any(i not in item for i in ("lampctrl", "group_num", "memo")):
                raise InvalidInputError(
                    'you should include "lampctrl", "group_num", "memo" in the list items'
                )
            lampctrl_sns = item.get('lampctrl')
            for lampctrl_sn in lampctrl_sns:
                # 灯控必须存在
                if not LampCtrl.objects.filter_by(sn=lampctrl_sn).exists():
                    raise InvalidInputError(
                        'lamp control [{}] not existed'.format(lampctrl_sn))
        return configs


class UpdateGroupSerializer(serializers.Serializer):
    """修改分组"""

    hub = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Hub.objects.filter_by()
    )
    lampctrl = serializers.ListField(
        required=True,
        child=serializers.PrimaryKeyRelatedField(
            queryset=LampCtrl.objects.filter_by()
        )
    )
    group_num = serializers.IntegerField(required=True)

    @staticmethod
    def validated_hub(hub):
        if not Hub.objects.filter_by(sn=hub).exists():
            msg = _('hub [{}] is not exist.'.format(', '.join(hub)))
            raise InvalidInputError(msg)
        return hub


class SendDownPolicySetSerializer(serializers.Serializer):
    """下发策略方案表单验证"""

    policys = serializers.ListField(required=True, min_length=1)

    # TODO 嵌套验证 自定义Field？
    def validate_policys(self, data):
        """
        :param data:
        {
            "policys": [
                {
                    "hub": "hub_sn1"
                    "group_num": null,
                    "policyset_id": "1"
                },
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
        }
        :return
        {
            "hub_sn1": [
                {
                    "hub": "hub_sn1"
                    "group_num": null,
                    "policyset_id": "1"
                }
            ],
            "hub_sn2": [
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
        }
        """
        ret_data = defaultdict(list)
        for item in data:
            if any(i not in item for i in ("hub", "group_num", "policyset_id")):
                msg = _('"hub","group_num" and "policyset_id" are required')
                raise InvalidInputError(msg)
            ret_data[item.get('hub')].append(item)
        return ret_data
