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
