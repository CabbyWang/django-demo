#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/13
"""
from rest_framework import serializers

from .models import Pole, Lamp, Cable, CBox, CBoxImage, LampImage, PoleImage


class PoleImageSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = PoleImage
        fields = ('id', 'file', 'created_time')


class PoleDetailSerializer(serializers.ModelSerializer):
    image = PoleImageSerializer(read_only=True)
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(write_only=True)
    is_deleted = serializers.BooleanField(write_only=True)

    class Meta:
        model = Pole
        fields = "__all__"


class PoleSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Pole
        fields = "__all__"


class PoleBatchDeleteSerializer(serializers.ModelSerializer):
    """批量删除灯杆格式检验"""
    sn = serializers.ListField(
        min_length=1,
        child=serializers.PrimaryKeyRelatedField(
            queryset=Pole.objects.filter_by()
        )
    )

    class Meta:
        model = Pole
        fields = ("sn", )


class LampImageSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = LampImage
        fields = ('id', 'file', 'created_time')


class LampDetailSerializer(serializers.ModelSerializer):
    image = LampImageSerializer(read_only=True)
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(write_only=True)
    is_deleted = serializers.BooleanField(write_only=True)

    class Meta:
        model = Lamp
        fields = "__all__"


class LampSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Lamp
        fields = "__all__"


class LampBatchDeleteSerializer(serializers.ModelSerializer):
    """批量删除灯具格式检验"""
    sn = serializers.ListField(
        min_length=1,
        child=serializers.PrimaryKeyRelatedField(
            queryset=Lamp.objects.filter_by()
        )
    )

    class Meta:
        model = Lamp
        fields = ("sn", )


class CBoxImageSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = CBoxImage
        fields = ('id', 'file', 'created_time')


class CBoxDetailSerializer(serializers.ModelSerializer):
    image = CBoxImageSerializer(read_only=True)
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(write_only=True)
    is_deleted = serializers.BooleanField(write_only=True)

    class Meta:
        model = CBox
        fields = "__all__"


class CBoxSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = CBox
        fields = "__all__"


class CBoxBatchDeleteSerializer(serializers.ModelSerializer):
    """批量删除控制箱格式检验"""
    sn = serializers.ListField(
        min_length=1,
        child=serializers.PrimaryKeyRelatedField(
            queryset=CBox.objects.filter_by()
        )
    )

    class Meta:
        model = CBox
        fields = ("sn", )


class CableSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Cable
        fields = "__all__"


class CableBatchDeleteSerializer(serializers.ModelSerializer):
    """批量删除电缆格式检验"""
    sn = serializers.ListField(
        min_length=1,
        child=serializers.PrimaryKeyRelatedField(
            queryset=Cable.objects.filter_by()
        )
    )

    class Meta:
        model = Cable
        fields = ("sn", )
