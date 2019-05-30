#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/4
"""
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.settings import api_settings

from setting.models import SettingType, Setting


class SettingSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Setting
        fields = ('id', 'option', 'name', 'value',
                  'created_time', 'updated_time')


class SettingTypeSerializer(serializers.ModelSerializer):
    # settings = SettingSerializer(many=True)
    settings = serializers.SerializerMethodField()

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    def get_settings(self, instance):
        queryset = instance.settings.filter_by()
        return SettingSerializer(
            queryset, many=True, context={'request': self.context['request']}
        ).data

    class Meta:
        model = SettingType
        fields = "__all__"


# TODO 研究一下drf里得api_settings， 将系统设置独立出来

class SettingUpdateSerializer(serializers.ModelSerializer):

    option = serializers.CharField(required=False, max_length=255, validators=[
        UniqueValidator(queryset=Setting.objects.filter_by())
    ])
    value = serializers.CharField(required=True)
    s_type = serializers.PrimaryKeyRelatedField(
        required=False, queryset=SettingType.objects.filter_by()
    )

    def validate_value(self, value):
        setting = self.instance
        option = setting.option
        if option in ('daily_consumption', 'min_current',
                      'power_consumption_threshold'):
            try:
                value = float(value)
                if value <= 0:
                    msg = _("'{name}' should be a number greater than 0")
                    raise serializers.ValidationError(msg.format(name=setting.name))
            except ValueError:
                msg = _("'{name}' should be a number")
                raise serializers.ValidationError(msg.format(name=setting.name))
        elif option in ('request_timeout', 'pagination',
                        'hub_status_count_threshold',
                        'lamp_status_count_threshold'):
            try:
                value = int(value)
                if value <= 0:
                    msg = _("'{name}' should be a integer greater than 0")
                    raise serializers.ValidationError(msg.format(name=setting.name))
            except ValueError:
                msg = _("'{name}' should be a integer")
                raise serializers.ValidationError(msg.format(name=setting.name))
        elif option in ('lost_ignore_time', ):
            try:
                value = value.split(',')
                start_time, end_time = value
                if not start_time or not end_time:
                    raise ValueError
            except ValueError:
                msg = _("invalid input")
                raise serializers.ValidationError(msg)
        elif option in ('cycle_time', ):
            # 调用其他接口, 该接口中不改变值
            value = setting.value
        return value

    def validate(self, attrs):
        # 只允许修改value
        for k, v in attrs.items():
            if k == "value":
                continue
            attrs[k] = getattr(self.instance, k)
        return attrs

    class Meta:
        model = Setting
        fields = "__all__"
