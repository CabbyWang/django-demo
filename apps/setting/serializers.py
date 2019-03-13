#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/4
"""
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from setting.models import SettingType, Setting


class SettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Setting
        fields = "__all__"


class SettingTypeSerializer(serializers.ModelSerializer):
    settings = SettingSerializer(many=True)

    class Meta:
        model = SettingType
        fields = "__all__"


class SettingUpdateSerializer(serializers.ModelSerializer):

    option = serializers.CharField(required=False, max_length=255, validators=[
        UniqueValidator(queryset=Setting.objects.all())
    ])
    option_zhcn = serializers.CharField(required=False, max_length=255)
    value = serializers.FloatField(required=False)
    s_type = serializers.PrimaryKeyRelatedField(required=False, queryset=SettingType.objects.all())

    def validate_value(self, value):
        name = self.instance.option
        if name in (
            'request_timeout', 'daily_consumption', 'pagination',
            'hub_status_count_threshold', 'lamp_status_count_threshold',
            'cycle_time', 'min_current'
        ):
            try:
                if value <= 0:
                    raise serializers.ValidationError("the '{}' field must be a number greater than 0".format(name))
            except ValueError:
                raise serializers.ValidationError("the '{}' field must be a number".format(name))
        return value

    def validate(self, attrs):
        for k, v in attrs.items():
            if k == "value":
                continue
            attrs[k] = getattr(self.instance, k)
        return attrs

    class Meta:
        model = Setting
        fields = "__all__"
