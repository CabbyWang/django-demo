#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/2
"""
from datetime import datetime

from rest_framework import serializers

from .models import Log, Alert, AlertAudio
from user.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class LogSerializer(serializers.ModelSerializer):
    user = UserSerializer()

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
        fields = '__all__'


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

    audio = serializers.SerializerMethodField()

    @staticmethod
    def get_audio(instance):
        # 返回语音文件路径，或None
        try:
            alert_audio = instance.alert_audio
            if alert_audio.is_deleted:
                return
            return alert_audio.audio.path
        except:
            return

    class Meta:
        model = Alert
        fields = '__all__'


class AlertUpdateSerializer(serializers.ModelSerializer):
    is_deleted = serializers.BooleanField(read_only=True)
    deleted_time = serializers.DateTimeField(read_only=True)
    event = serializers.CharField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    alert_source = serializers.CharField(read_only=True)
    object_type = serializers.CharField(read_only=True)
    object = serializers.CharField(read_only=True)
    # occurred_time = serializers.DateTimeField(read_only=True)

    memo = serializers.CharField(max_length=255, allow_blank=True)
    is_solved = serializers.BooleanField(default=False, help_text='是否解决')
    solver = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    solved_time = serializers.HiddenField(default=datetime.now)

    class Meta:
        model = Alert
        fields = '__all__'
