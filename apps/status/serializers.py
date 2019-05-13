#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/25
"""
from rest_framework import serializers

from equipment.models import LampCtrl
from status.models import LampCtrlStatus


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
