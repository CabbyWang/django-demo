#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/2
"""
from datetime import datetime

from rest_framework import serializers

from workorder.models import WorkOrder
from .models import Log, Alert, AlertAudio
from user.models import User


class LogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Log
        fields = '__all__'


class AlertAudioSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlertAudio
        fields = ("id", "audio")
        read_only_fields = ('audio', )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class AlertSerializer(serializers.ModelSerializer):
    solver = UserSerializer()
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    solved_time = serializers.DateTimeField(read_only=True,
                                            format='%Y-%m-%d %H:%M:%S')

    alert_audio = AlertAudioSerializer(source='not_listen_audio')

    class Meta:
        model = Alert
        fields = '__all__'


class AlertUpdateSerializer(serializers.ModelSerializer):
    event = serializers.CharField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    alert_source = serializers.CharField(read_only=True)
    object_type = serializers.CharField(read_only=True)
    object = serializers.CharField(read_only=True)

    solver = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    solved_time = serializers.HiddenField(default=datetime.now)

    is_solved = serializers.BooleanField(required=True, help_text='是否解决')
    memo = serializers.CharField(required=True, max_length=255)

    class Meta:
        model = Alert
        fields = '__all__'

    def validate(self, attrs):
        # TODO 使用signal来实现
        if self.initial_data['is_solved']:
            # 告警撤销  工单变已处理
            WorkOrder.objects.filter_by(alert=self.instance).update(
                finished_time=datetime.now(),
                status='finished', description='告警手动撤销'
            )
        else:
            # 告警撤销解除  工单变未处理
            WorkOrder.objects.filter_by(alert=self.instance).update(
                finished_time=None, user=None,
                status='todo', description=None
            )
        return attrs
