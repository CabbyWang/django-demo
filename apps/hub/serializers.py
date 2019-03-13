#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/12
"""

from rest_framework import serializers

from hub.models import Hub, Unit


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = ("name", )


class HubDetailSerializer(serializers.ModelSerializer):

    unit = UnitSerializer()
    lamps_num = serializers.SerializerMethodField()

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
