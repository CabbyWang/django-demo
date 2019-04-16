#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/16
"""
import datetime

from django_filters import rest_framework as filters

from hub.models import Hub
from .models import LampCtrl, LampCtrlStatus


class LampCtrlFilter(filters.FilterSet):
    """
    Filter of lampctrls.
    """

    sn = filters.CharFilter(field_name='sn', lookup_expr='icontains',
                            method='filter_sn')
    sequence = filters.CharFilter(field_name='sequence',
                                  lookup_expr='icontains')
    hub_sn = filters.CharFilter(field_name='hub', method='filter_hub_sn')
    rf_band = filters.CharFilter(field_name='rf_band', lookup_expr='icontains')
    rf_addr = filters.CharFilter(field_name='rf_addr', lookup_expr='icontains')
    address = filters.CharFilter(field_name='address', lookup_expr='icontains')
    lamp_type = filters.NumberFilter(field_name='lamp_type')
    lamp_status = filters.NumberFilter(field_name='status',
                                       method='filter_lamp_status')
    start_time = filters.DateFilter(field_name='registered_time',
                                    lookup_expr='gte')
    end_time = filters.DateFilter(field_name='registered_time',
                                  lookup_expr='lte')

    @staticmethod
    def filter_sn(queryset, name, value):
        """支持筛选多个灯控编号
        0001,0002
        """
        sns = value.split(',')
        return queryset.filter(sn__in=sns)

    @staticmethod
    def filter_hub_sn(queryset, name, value):
        hub_sns = value.split(',')
        hubs = Hub.objects.filter_by(sn__in=hub_sns)
        return queryset.filter(hub__in=hubs)

    @staticmethod
    def filter_lamp_status(queryset, name, value):
        """通过(正常开灯/正常熄灯/故障/脱网（正常分为两种状态）1/0/2/3)四种状态
        来筛选
        实际通过status和switch_status来筛选
        """
        if value == 0:
            status = 1
            switch_status = 0
            return queryset.filter(status=status, switch_status=switch_status)
        elif value == 1:
            status = 1
            switch_status = 1
            return queryset.filter(status=status, switch_status=switch_status)
        else:
            status = value
            return queryset.filter(status=status)

    class Meta:
        model = LampCtrl
        fields = (
            'sn', 'sequence', 'hub_sn', 'lamp_type', 'rf_band', 'rf_addr',
            'address', 'lamp_type', 'lamp_status', 'start_time', 'end_time'
        )


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
