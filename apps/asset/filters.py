#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/17
"""
from django_filters import rest_framework as filters

from . models import Pole, Lamp, CBox, Cable


class PoleFilter(filters.FilterSet):
    """
    Filter of Pole.
    """

    sn = filters.CharFilter(field_name='sn', lookup_expr='icontains')
    vendor = filters.CharFilter(field_name='vendor', lookup_expr='icontains')
    is_used = filters.BooleanFilter(field_name='is_used')
    start_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Pole
        fields = ('sn', 'vendor', 'is_used', 'start_date', 'end_date')


class LampFilter(filters.FilterSet):
    """
    Filter of Lamp.
    """

    sn = filters.CharFilter(field_name='sn', lookup_expr='icontains')
    vendor = filters.CharFilter(field_name='vendor', lookup_expr='icontains')
    is_used = filters.BooleanFilter(field_name='is_used')
    start_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Lamp
        fields = ('sn', 'vendor', 'is_used', 'start_date', 'end_date')


class CBoxFilter(filters.FilterSet):
    """
    Filter of CBox.
    """

    sn = filters.CharFilter(field_name='sn', lookup_expr='icontains')
    vendor = filters.CharFilter(field_name='vendor', lookup_expr='icontains')
    is_used = filters.BooleanFilter(field_name='is_used')
    start_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = CBox
        fields = ('sn', 'vendor', 'is_used', 'start_date', 'end_date')


class CableFilter(filters.FilterSet):
    """
    Filter of Cable.
    """

    sn = filters.CharFilter(field_name='sn', lookup_expr='icontains')
    vendor = filters.CharFilter(field_name='vendor', lookup_expr='icontains')
    start_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Cable
        fields = ('sn', 'vendor', 'start_date', 'end_date')
