#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/16
"""
import datetime

from django_filters import rest_framework as filters

from hub.models import Hub
from .models import LampCtrl, LampCtrlStatus, LampCtrlGroup


class LampCtrlFilter(filters.FilterSet):
    """
    Filter of lampctrls.
    """

    sn = filters.CharFilter(field_name='sn', lookup_expr='icontains',
                            method='filter_sn')
    sequence = filters.CharFilter(field_name='sequence',
                                  lookup_expr='icontains')
    hub = filters.CharFilter(field_name='hub', method='filter_hub')
    rf_band = filters.CharFilter(field_name='rf_band', lookup_expr='icontains')
    rf_addr = filters.CharFilter(field_name='rf_addr', lookup_expr='icontains')
    address = filters.CharFilter(field_name='address', lookup_expr='icontains')
    lamp_type = filters.NumberFilter(field_name='lamp_type')
    lamp_status = filters.CharFilter(field_name='status',
                                     method='filter_lamp_status')
    status = filters.NumberFilter(field_name='status', method='filter_status')
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
    def filter_hub(queryset, name, value):
        hub_sns = value.split(',')
        hubs = Hub.objects.filter_by(sn__in=hub_sns)
        return queryset.filter(hub__in=hubs)

    @staticmethod
    def filter_status(queryset, name, value):
        """
        通过(正常/故障/脱网 1/2/3)三种状态来筛选
        (支持多个状态筛选 2,3)
        """
        return queryset.filter(status__in=value.split(','))

    @staticmethod
    def filter_lamp_status(queryset, name, value):
        """通过(正常开灯/正常熄灯/故障/脱网（正常分为两种状态）1/0/2/3)四种状态
        来筛选(支持多个状态筛选 2,3)
        实际通过status和switch_status来筛选
        """
        # TODO 优化代码
        statuss = value.split(',')
        qs = LampCtrl.objects.none()
        for lamp_status in statuss:
            lamp_status = int(lamp_status)
            if lamp_status == 0:
                status = 1
                switch_status = 0
                qs |= queryset.filter(status=status, switch_status=switch_status)
            elif lamp_status == 1:
                status = 1
                switch_status = 1
                qs |= queryset.filter(status=status, switch_status=switch_status)
            else:
                status = lamp_status
                qs |= queryset.filter(status=status)
        return qs

    class Meta:
        model = LampCtrl
        fields = (
            'sn', 'sequence', 'hub', 'lamp_type', 'rf_band', 'rf_addr',
            'address', 'lamp_type', 'lamp_status', 'status', 'switch_status',
            'start_time', 'end_time'
        )


class LampCtrlGroupFilter(filters.FilterSet):
    """
    Filter of LampCtrlGroup
    """
    hub = filters.CharFilter(field_name='hub')
    is_default = filters.BooleanFilter(field_name='is_default')
    group_num = filters.NumberFilter(field_name='group_num',
                                     method='filter_group_num')

    def filter_group_num(self, queryset, name, value):
        if value == 0:
            # 0分组  返回未分组所有灯控
            pass
        return queryset

    class Meta:
        model = LampCtrlGroup
        fields = ('hub', 'is_default', 'group_num')


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
