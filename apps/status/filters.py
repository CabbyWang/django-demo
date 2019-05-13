#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/25
"""
import datetime

from django_filters import rest_framework as filters

from status.models import LampCtrlStatus


class LampCtrlStatusFilter(filters.FilterSet):
    """
    Filter of LampCtrlStatus
    """
    lampctrl = filters.CharFilter(field_name='lampctrl')
    start_time = filters.DateFilter(field_name='created_time',
                                    lookup_expr='gte')
    end_time = filters.DateFilter(field_name='created_time',
                                  lookup_expr='lte', method='filter_end_time')

    @staticmethod
    def filter_end_time(queryset, name, value):
        value = value + datetime.timedelta(days=1)
        return queryset.filter(created_time__lt=value)

    class Meta:
        model = LampCtrlStatus
        fields = ('lampctrl', 'start_time', 'end_time')
