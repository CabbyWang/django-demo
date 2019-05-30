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


class GatherLampCtrlSerializer(serializers.Serializer):

    lampctrl = serializers.ListField(
        required=True, min_length=1,
        child=serializers.PrimaryKeyRelatedField(
            queryset=LampCtrl.objects.filter_by(),
            error_messages={
                'does_not_exist': _("lamp control [{pk_value}] does not exist.")
            }
        )
    )

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
        ret = defaultdict(list)
        for lampctrl in lampctrls:
            ret[lampctrl.hub].append(lampctrl.sn)
        return ret


class ControlLampSerializer(GatherLampCtrlSerializer):
    action = serializers.CharField(required=True)

    @staticmethod
    def validate_action(action):
        actions = action.split(',')
        if len(actions) != 2:
            msg = _("the format of action must like '0,80'")
            raise serializers.ValidationError(msg)
        route1, route2 = [int(i) for i in actions]
        if route1 < 0 or route1 > 255 or route2 < 0 or route2 > 255:
            msg = _('the brightness value must between 0 and 255')
            raise serializers.ValidationError(msg)
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
                'does_not_exist': _("hub [{pk_value}] does not exist.")
            }
        )
    )


class ControlAllSerializer(HubIsExistedSerializer):

    action = serializers.ChoiceField(
        choices=['open', 'close'],
        error_messages={
            'invalid_choice': _("the value of 'action' should be 'open' or 'close'")
        }
    )

    @staticmethod
    def validate_action(action):
        if action == 'open':
            return '255,255'
        return '0,0'


class PatternGroupSerializer(serializers.Serializer):
    """下发(模式)分组"""

    hub = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Hub.objects.filter_by(),
        error_messages={
            'does_not_exist': _("hub [{pk_value}] does not exist.")
        }
    )
    group_num = serializers.IntegerField(
        required=True, max_value=99, min_value=1,
        error_messages={'required': _("field 'group_num' is required.")}
    )
    memo = serializers.CharField(
        required=False, allow_blank=True,
        error_messages={
            'required': _("field 'memo' is required.")}
    )
    group_num_rest = serializers.IntegerField(
        required=True, max_value=99, min_value=1,
        error_messages={
            'required': _("field 'group_num_rest' is required.")}
    )
    memo_rest = serializers.CharField(
        required=False, allow_blank=True,
        error_messages={
            'required': _("field 'memo_rest' is required.")}
    )
    segmentation = serializers.IntegerField(
        required=True, max_value=6, min_value=1,
        error_messages={
            'required': _("field 'segmentation' is required.")}
    )
    select = serializers.IntegerField(
        required=True, max_value=5, min_value=1,
        error_messages={
            'required': _("field 'select' is required.")}
    )

    def validate(self, attrs):
        hub_sn = self.initial_data['hub']
        hub = Hub.objects.filter_by(sn=hub_sn).first()
        if not hub:
            msg = _("hub '{}' does not exist")
            raise serializers.ValidationError(msg.format(hub_sn))
        # 自定义分组已存在
        if LampCtrlGroup.objects.filter_by(hub=hub, is_default=False).exists():
            msg = _('custom group already exists')
            raise serializers.ValidationError(msg)
        # 两个分组id不能相同
        if attrs["group_num"] == attrs["group_num_rest"]:
            msg = _('two group id should be different')
            raise serializers.ValidationError(msg)
        # 分组id不能与默认分组的id相同
        # hub_sn = self.context['view'].kwargs.get('pk')
        # hub = Hub.objects.get_or_404(sn=hub_sn)
        default_groups = hub.hub_group.filter_by(is_default=True).values_list(
            'group_num', flat=True)
        if attrs['group_num'] in default_groups or attrs['group_num_rest'] in default_groups:
            msg = _('group number should be different with default groups')
            raise serializers.ValidationError(msg)
        return attrs


class CustomGroupingSerializer(serializers.Serializer):
    """下发(自定义)分组"""

    hub = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Hub.objects.filter_by(),
        error_messages={
            'does_not_exist': _("hub [{pk_value}] does not exist.")
        }
    )
    configs = serializers.ListField(required=True)

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
        hub = Hub.objects.filter_by(sn=hub_sn).first()
        if not hub:
            msg = _("hub '{}' does not exist")
            raise serializers.ValidationError(msg.format(hub_sn))
        # 自定义分组已存在
        if LampCtrlGroup.objects.filter_by(hub=hub, is_default=False).exists():
            raise serializers.ValidationError('custom group already exists')
        for item in configs:
            # 数据项中必须包含"lampctrl", "group_num", "memo"字段
            if any(i not in item for i in ("lampctrl", "group_num", "memo")):
                msg = _("fields('lampctrl', 'group_num', 'memo')"
                        "should be include in the 'configs' items")
                raise serializers.ValidationError(msg)
            lampctrl_sns = item.get('lampctrl')
            for lampctrl_sn in lampctrl_sns:
                # 灯控必须存在
                if not LampCtrl.objects.filter_by(sn=lampctrl_sn).exists():
                    msg = _('lamp control [{lampctrl_sn}] does not exist')
                    raise serializers.ValidationError(msg.format(lampctrl_sn))
        return configs


class UpdateGroupSerializer(serializers.Serializer):
    """修改分组"""

    hub = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Hub.objects.filter_by(),
        error_messages={
            'does_not_exist': _("hub [{pk_value}] does not exist.")
        }
    )
    lampctrl = serializers.ListField(
        required=True,
        child=serializers.PrimaryKeyRelatedField(
            queryset=LampCtrl.objects.filter_by()
        )
    )
    group_num = serializers.IntegerField(required=True)


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
            hub1: [
                {
                    "hub": "hub_sn1"
                    "group_num": null,
                    "policyset_id": "1"
                }
            ],
            hub2: [
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
        error_hubs = []
        for item in data:
            if any(i not in item for i in ("hub", "group_num", "policyset_id")):
                msg = _("fields('hub', 'group_num', 'policyset_id') should be include in the 'configs' items")
                raise serializers.ValidationError(msg)
            hub_sn = item.get('hub')
            hub = Hub.objects.filter_by(sn=hub_sn).first()
            if not hub:
                error_hubs.append(hub_sn)
                continue
                # raise _("hub [{pk_value}] does not exist.").format(hub_sn)
            ret_data[hub].append(item)
        if error_hubs:
            raise _("hub [{pk_value}] does not exist.").format(
                pk_value=','.join(error_hubs)
            )
        return ret_data


class DownloadHubLogSerializer(serializers.Serializer):
    """下载集控日志"""

    hub = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Hub.objects.filter_by(),
        error_messages={
            'does_not_exist': _("hub [{pk_value}] does not exist.")
        }
    )
