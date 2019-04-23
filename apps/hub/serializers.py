#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/12
"""

from rest_framework import serializers

from hub.models import Hub, Unit
from utils.exceptions import InvalidInputError
from lamp.models import LampCtrl, LampCtrlGroup


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = ("id", "name", )


class HubDetailSerializer(serializers.ModelSerializer):

    unit = UnitSerializer()
    lamps_num = serializers.SerializerMethodField()

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_lamps_num(obj):
        return obj.hub_lampctrl.count()

    class Meta:
        model = Hub
        fields = "__all__"


class HubPartialUpdateSerializer(serializers.ModelSerializer):
    longitude = serializers.FloatField(max_value=180, min_value=0)
    latitude = serializers.FloatField(max_value=90, min_value=0)

    def validate(self, attrs):
        if all(i in attrs for i in ('longitude', 'latitude')):
            # 集控重定位, is_redirect=True
            attrs['is_redirect'] = True
        return attrs

    class Meta:
        model = Hub
        fields = "__all__"


class LoadInventorySerializer(serializers.Serializer):

    hub = serializers.ListField(required=True, min_length=1)

    @staticmethod
    def validate_hub(hubs):
        not_exists_hub = []
        for hub_sn in hubs:
            if not Hub.objects.filter_by(sn=hub_sn).exists():
                not_exists_hub.append(hub_sn)
        if not_exists_hub:
            raise serializers.ValidationError('hubs [{}] are not exist.'.format(', '.join(not_exists_hub)))
        return hubs


class ControlAllSerializer(serializers.Serializer):

    action = serializers.ChoiceField(choices=['open', 'close'])

    def validate_action(self, action):
        if action == 'open':
            return '255,255'
        return '0,0'


class PatternGroupSerializer(serializers.Serializer):

    group = serializers.IntegerField(required=True, max_value=99, min_value=1)
    memo = serializers.CharField(required=False, allow_blank=True)
    group_rest = serializers.IntegerField(required=True, max_value=99, min_value=1)
    memo_rest = serializers.CharField(required=False, allow_blank=True)
    segmentation = serializers.IntegerField(required=True, max_value=6, min_value=1)
    select = serializers.IntegerField(required=True, max_value=5, min_value=1)

    def validate(self, attrs):
        hub_sn = self.context['view'].kwargs.get('pk')
        hub = Hub.objects.get_or_404(sn=hub_sn)
        # 自定义分组已存在
        if LampCtrlGroup.objects.filter_by(hub=hub, is_default=False).exists():
            raise InvalidInputError('custom group has been existed')
        # 两个分组id不能相同
        if attrs["group"] == attrs["group_rest"]:
            raise InvalidInputError('two group id must be different')
        # 分组id不能与默认分组的id相同
        hub_sn = self.context['view'].kwargs.get('pk')
        hub = Hub.objects.get_or_404(sn=hub_sn)
        default_groups = hub.hub_group.filter_by(is_default=True).values_list(
            'group_num', flat=True)
        if attrs['group'] in default_groups or attrs['group_rest'] in default_groups:
            raise InvalidInputError(
                'group id must be different with default groups')
        return attrs


class CustomGroupingSerializer(serializers.Serializer):

    configs = serializers.ListField(required=True)

    def validate_configs(self, configs):
        """
        "configs": [
            {
                "lampctrl": ["001", "002"],
                "group": 1,
                "memo": ""
            },
            {
                "lampctrl": ["003", "004"],
                "group": 2,
                "memo": ""
            }
        ]
        """
        hub_sn = self.context['view'].kwargs.get('pk')
        hub = Hub.objects.get_or_404(sn=hub_sn)
        # 自定义分组已存在
        if LampCtrlGroup.objects.filter_by(hub=hub, is_default=False).exists():
            raise InvalidInputError('custom group has been existed')
        for item in configs:
            # 数据项中必须包含"lampctrl", "group", "memo"字段
            if any(i not in item for i in ("lampctrl", "group", "memo")):
                raise InvalidInputError(
                    'you should include "lampctrl", "group", "memo" in the list items'
                )
            lampctrl_sns = item.get('lampctrl')
            for lampctrl_sn in lampctrl_sns:
                # 灯控必须存在
                if not LampCtrl.objects.filter_by(sn=lampctrl_sn).exists():
                    raise InvalidInputError(
                        'lamp control [{}] not existed'.format(lampctrl_sn))
        return configs
