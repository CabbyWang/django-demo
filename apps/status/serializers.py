#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/25
"""
from rest_framework import serializers

from equipment.models import LampCtrl, Hub
from status.models import LampCtrlStatus, LampCtrlLatestStatus


class LampCtrlStatusSerializer(serializers.ModelSerializer):
    lampctrl = serializers.PrimaryKeyRelatedField(queryset=LampCtrl.objects.all())
    hub = serializers.PrimaryKeyRelatedField(
        queryset=Hub.objects.filter_by()
    )
    route_one = serializers.IntegerField()
    route_two = serializers.IntegerField()
    voltage = serializers.DecimalField(max_digits=32, decimal_places=2)
    current = serializers.DecimalField(max_digits=32, decimal_places=2)
    power = serializers.DecimalField(max_digits=32, decimal_places=2)
    consumption = serializers.DecimalField(max_digits=32, decimal_places=2)
    created_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S'
    )
    updated_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S'
    )
    deleted_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S'
    )

    class Meta:
        model = LampCtrlStatus
        fields = "__all__"


class LampCtrlLatestStatusSerializer(serializers.ModelSerializer):
    route_one = serializers.IntegerField()
    route_two = serializers.IntegerField()
    voltage = serializers.DecimalField(max_digits=32, decimal_places=2)
    current = serializers.DecimalField(max_digits=32, decimal_places=2)
    power = serializers.DecimalField(max_digits=32, decimal_places=2)
    consumption = serializers.DecimalField(max_digits=32, decimal_places=2)
    updated_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S'
    )

    class Meta:
        model = LampCtrlLatestStatus
        fields = (
            'route_one', 'route_two', 'voltage', 'current', 'power',
            'consumption', 'updated_time'
        )
