#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/12
"""

from rest_framework import serializers

from hub.models import Hub, Unit
from lamp.models import LampCtrl


class HubSerializer(serializers.ModelSerializer):

    hub_unit = serializers.ReadOnlyField()

    class Meta:
        model = Hub
        fields = "__all__"

    lamps_num = serializers.SerializerMethodField()

    @staticmethod
    def get_lamps_num(obj):
        hub_sn = obj.sn
        return obj.hub_lampctrl.count()
        # return LampCtrl.objects.filter(hub_sn=hub_sn).count()


class UnitSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Unit
        fields = ("name", )
