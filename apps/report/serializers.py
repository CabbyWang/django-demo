#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/4
"""
from rest_framework import serializers

from .models import (
    DailyTotalConsumption, HubDailyTotalConsumption, MonthTotalConsumption,
    HubMonthTotalConsumption, DeviceConsumption, LampCtrlConsumption
    )


class HubDailyTotalConsumptionSerializer(serializers.ModelSerializer):
    """集控日能耗"""

    class Meta:
        model = HubDailyTotalConsumption
        fields = ("hub", "consumption", "date")


class DailyTotalConsumptionSerializer(serializers.ModelSerializer):
    """所有集控日能耗"""

    class Meta:
        model = DailyTotalConsumption
        fields = ("consumption", "date")


class HubMonthTotalConsumptionSerializer(serializers.ModelSerializer):
    """集控月能耗"""

    class Meta:
        model = HubMonthTotalConsumption
        fields = ("hub", "consumption", "month")


class MonthTotalConsumptionSerializer(serializers.ModelSerializer):
    """所有集控月能耗"""

    class Meta:
        model = MonthTotalConsumption
        fields = ("consumption", "month")


class DeviceConsumptionSerializer(serializers.ModelSerializer):
    """设备能耗分布"""

    class Meta:
        model = DeviceConsumption
        fields = ("hub", "hub_consumption", "lamps_consumption",
                  "loss_consumption")


class LampCtrlConsumptionSerializer(serializers.ModelSerializer):
    """灯控能耗"""

    class Meta:
        model = LampCtrlConsumption
        fields = ("lampctrl", "consumption")