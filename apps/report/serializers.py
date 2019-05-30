#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/4
"""
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from setting.models import Setting
from .models import LampCtrlConsumption
from equipment.models import Hub


class LampCtrlConsumptionSerializer(serializers.ModelSerializer):

    """灯控每日能耗"""

    class Meta:
        model = LampCtrlConsumption
        fields = '__all__'


class NeedHubSerializer(serializers.Serializer):

    """需要提供集控"""
    hub = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Hub.objects.filter_by(),
        error_messages={
            'null': _("hub may not be null."),
            'does_not_exist': _('hub [{pk_value}] does not exist.')
        }
    )


class GetConsumptionSerializer(NeedHubSerializer):

    """集控能耗图参数校验"""
    month = serializers.CharField(
        required=False, allow_null=True
    )


class HubIsExistedSerializer(serializers.Serializer):

    """集控是否存在"""
    hub = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        queryset=Hub.objects.filter_by(),
        error_messages={
            'does_not_exist': _('hub [{pk_value}] does not exist.')
        }
    )

    def validate(self, attrs):
        return attrs


class DailyConsumptionSerializer(serializers.Serializer):

    def validate(self, attrs):
        try:
            setting = Setting.objects.get(option='daily_consumption')
            daily_consumption = float(setting.value)
        except Setting.DoesNotExist:
            # 未初始化数据
            msg = _("you may have not initialized settings")
            raise serializers.ValidationError(msg)
        attrs['daily_consumption'] = daily_consumption
        return attrs
