#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/16
"""
import datetime

from django_filters import rest_framework as filters

from .models import Log, Alert


class LogFilter(filters.FilterSet):
    """
    Filter of logs.
    """

    username = filters.CharFilter(field_name='user', method='filter_username')
    event = filters.CharFilter(field_name='event', lookup_expr='icontains')
    start_time = filters.DateFilter(field_name='created_time',
                                    lookup_expr='gte')
    end_time = filters.DateFilter(field_name='created_time', lookup_expr='lte',
                                  method='filter_end_time')

    @staticmethod
    def filter_username(queryset, name, value):
        """通过用户名筛选"""
        return queryset.filter(user__username=value)

    @staticmethod
    def filter_end_time(queryset, name, value):
        value = value + datetime.timedelta(days=1)
        return queryset.filter(created_time__lt=value)

    class Meta:
        model = Log
        fields = ('username', 'event', 'start_time', 'end_time')


class AlertFilter(filters.FilterSet):
    """
    Filter of alerts.
    """

    id = filters.NumberFilter(field_name='id', lookup_expr='icontains')
    alert_source = filters.CharFilter(field_name='alert_source')
    level = filters.NumberFilter(field_name='level')
    start_time = filters.DateFilter(field_name='created_time',
                                    lookup_expr='gte')
    end_time = filters.DateFilter(field_name='created_time', lookup_expr='lte',
                                  method='filter_end_time')
    is_solved = filters.BooleanFilter(field_name='is_solved')

    @staticmethod
    def filter_end_time(queryset, name, value):
        value = value + datetime.timedelta(days=1)
        return queryset.filter(created_time__lt=value)

    class Meta:
        model = Alert
        fields = ('id', 'alert_source', 'level',
                  'start_time', 'end_time', 'is_solved')
