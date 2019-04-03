#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/13
"""
from rest_framework import serializers

from .models import Pole, Lamp, Cable, CBox, CBoxImage, LampImage, PoleImage


class PoleImageSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M')

    class Meta:
        model = PoleImage
        fields = ('id', 'image', 'created_time')


class PoleDetailSerializer(serializers.ModelSerializer):
    image = PoleImageSerializer(read_only=True)
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M')
    updated_time = serializers.DateTimeField(write_only=True)
    deleted_time = serializers.DateTimeField(write_only=True)
    is_deleted = serializers.BooleanField(write_only=True)

    class Meta:
        model = Pole
        fields = "__all__"


class PoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pole
        fields = "__all__"


class LampImageSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M')

    class Meta:
        model = LampImage
        fields = ('id', 'image', 'created_time')


class LampDetailSerializer(serializers.ModelSerializer):
    image = LampImageSerializer(read_only=True)
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M')
    updated_time = serializers.DateTimeField(write_only=True)
    deleted_time = serializers.DateTimeField(write_only=True)
    is_deleted = serializers.BooleanField(write_only=True)

    class Meta:
        model = Lamp
        fields = "__all__"


class LampSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lamp
        fields = "__all__"


class CBoxImageSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M')

    class Meta:
        model = CBoxImage
        fields = fields = ('id', 'image', 'created_time')


class CBoxDetailSerializer(serializers.ModelSerializer):
    image = CBoxImageSerializer(read_only=True)
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M')
    updated_time = serializers.DateTimeField(write_only=True)
    deleted_time = serializers.DateTimeField(write_only=True)
    is_deleted = serializers.BooleanField(write_only=True)

    class Meta:
        model = CBox
        fields = "__all__"


class CBoxSerializer(serializers.ModelSerializer):

    class Meta:
        model = CBox
        fields = "__all__"


class CableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cable
        fields = "__all__"
