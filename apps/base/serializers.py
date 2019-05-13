#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/9
"""
from rest_framework import serializers

from base.models import Unit


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = ("id", "name", )
