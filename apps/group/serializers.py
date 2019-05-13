#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/9
"""
from rest_framework import serializers

from equipment.models import Hub, LampCtrl
from group.models import LampCtrlGroup
from policy.models import PolicySetSendDown


class LampCtrlGroupSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    working_policyset = serializers.SerializerMethodField()

    def get_working_policyset(self, instance):
        """获取该分组下的策略方案"""
        ins = PolicySetSendDown.objects.filter_by(
            group_num=instance.group_num,
            hub=instance.hub
        ).first()
        working_policyset = ins.policyset.name if ins else '默认策略'
        return working_policyset

    class Meta:
        model = LampCtrlGroup
        fields = "__all__"


class GetLampCtrlserializer(serializers.ModelSerializer):

    hub = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Hub.objects.filter_by()
    )
    group_num = serializers.IntegerField(required=True)
    is_default = serializers.BooleanField(required=True)

    class Meta:
        model = LampCtrl
        read_only_fields = (
            'sn', 'sequence', 'rf_band', 'rf_addr',
            'address', 'longitude', 'latitude'
        )
        fields = ("sn", "hub", "is_default", "group_num")
