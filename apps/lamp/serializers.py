#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/6
"""
from collections import defaultdict

from rest_framework import serializers

from hub.models import Hub
from lamp.models import LampCtrl, LampCtrlGroup, LampCtrlStatus
from policy.models import PolicySetSendDown
from utils.exceptions import InvalidInputError


class LampCtrlSerializer(serializers.ModelSerializer):
    # failure_date = serializers.DateField(read_only=True, format='%Y-%m-%d')
    registered_time = serializers.DateField(read_only=True, format='%Y-%m-%d')
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    lamp_status = serializers.SerializerMethodField()
    hub_is_redirect = serializers.SerializerMethodField()
    real_address = serializers.SerializerMethodField()

    @staticmethod
    def get_lamp_status(instance):
        """
        lamp_status分四种状态， 正常开灯/正常熄灯/故障/脱网（正常分为两种状态）1/0/2/3
        """
        status = instance.status
        switch_status = instance.switch_status
        lamp_status = status
        if lamp_status == 1 and switch_status == 0:
            lamp_status = 0
        return lamp_status

    @staticmethod
    def get_real_address(instance):
        """获取lampctrl的真正地址"""
        address = instance.address
        new_address = instance.new_address or ''
        new_address = new_address.strip()
        return new_address or address

    @staticmethod
    def get_hub_is_redirect(instance):
        """集控是否重定位"""
        hub = instance.hub
        return hub.is_redirect
        # try:
        #     hub_instance = Hub.objects.get(sn=hub_sn)
        # except Hub.DoesNotExist:
        #     raise serializers.ValidationError("集控不存在")
        # return hub_instance.is_redirect

    class Meta:
        model = LampCtrl
        fields = "__all__"


class LampCtrlGroupSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    working_policyset = serializers.SerializerMethodField()

    def get_working_policyset(self, instance):
        """获取该分组下的策略方案"""
        ins = PolicySetSendDown.objects.filter_by(
            group_num=instance.group_num,
            hub=instance.hub
        ).first()
        working_policyset = ins.policyset.name if ins else '默认策略'
        return working_policyset

    class Meta:
        model = LampCtrlGroup
        fields = "__all__"


class GetLampCtrlserializer(serializers.ModelSerializer):

    hub = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Hub.objects.filter_by()
    )
    group_num = serializers.IntegerField(required=True)
    is_default = serializers.BooleanField(required=True)

    class Meta:
        model = LampCtrl
        read_only_fields = (
            'sn', 'sequence', 'rf_band', 'rf_addr',
            'address', 'longitude', 'latitude'
        )
        fields = ("sn", "hub", "is_default", "group_num")


class GetGroupserializer(serializers.ModelSerializer):

    hub = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Hub.objects.filter_by()
    )
    is_default = serializers.BooleanField(required=True)

    def validate(self, attrs):
        a = self.initial_data
        return attrs

    class Meta:
        model = LampCtrlGroup
        read_only_fields = (
            'group_num', 'lampctrl'
        )
        fields = "__all__"


class LampCtrlPartialUpdateSerializer(serializers.ModelSerializer):
    new_address = serializers.CharField()

    def validate(self, attrs):
        for k, v in attrs.items():
            if k == "new_address":
                continue
            attrs[k] = getattr(self.instance, k)
        return attrs

    class Meta:
        model = LampCtrl
        fields = "__all__"


class LampCtrlStatusSerializer(serializers.ModelSerializer):
    lampctrl = serializers.PrimaryKeyRelatedField(queryset=LampCtrl.objects.all())
    voltage = serializers.DecimalField(max_digits=32, decimal_places=1)
    current = serializers.DecimalField(max_digits=32, decimal_places=1)
    power = serializers.DecimalField(max_digits=32, decimal_places=1)
    power_consumption = serializers.DecimalField(max_digits=32, decimal_places=1)
    time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    created_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = LampCtrlStatus
        fields = "__all__"


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
