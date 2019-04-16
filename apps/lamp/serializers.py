#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/6
"""
from lamp.models import LampCtrl, LampCtrlGroup, LampCtrlStatus

from rest_framework import serializers


class LampCtrlSerializer(serializers.ModelSerializer):
    failure_date = serializers.DateField(read_only=True, format='%Y-%m-%d')
    registered_time = serializers.DateField(read_only=True, format='%Y-%m-%d')
    created_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

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
