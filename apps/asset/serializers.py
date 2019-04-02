#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/13
"""
import os

from django.conf import settings
from rest_framework import serializers

from .models import Pole, Lamp, Cable, CBox, CBoxImage, LampImage, PoleImage


class PoleImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PoleImage
        fields = '__all__'


class PoleSerializer(serializers.ModelSerializer):
    image = PoleImageSerializer()

    class Meta:
        model = Pole
        fields = "__all__"


class LampImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = LampImage
        fields = '__all__'


class LampSerializer(serializers.ModelSerializer):
    image = LampImageSerializer()

    class Meta:
        model = Lamp
        fields = "__all__"


class CBoxImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = CBoxImage
        fields = '__all__'


class CBoxSerializer(serializers.ModelSerializer):
    image = CBoxImageSerializer()

    class Meta:
        model = CBox
        fields = "__all__"


class CableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cable
        fields = "__all__"
