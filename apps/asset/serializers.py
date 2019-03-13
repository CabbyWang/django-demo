#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/13
"""
from rest_framework import serializers

from .models import Pole, Lamp, Cable, CBox


class PoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pole
        fields = "__all__"


class LampSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lamp
        fields = "__all__"


class CableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cable
        fields = "__all__"


class CBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = CBox
        fields = "__all__"
