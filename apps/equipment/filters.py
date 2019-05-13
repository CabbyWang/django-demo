#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/9
"""
from django_filters import rest_framework as filters

from base.models import Unit
from equipment.models import Lamp, Pole, CBox, Cable, LampCtrl, Hub


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


class HubFilter(filters.FilterSet):
    """
    Filter of hubs.
    """

    sn = filters.CharFilter(field_name='sn', method='filter_sn')
    rf_band = filters.NumberFilter(field_name='rf_band', lookup_expr='icontains')
    rf_addr = filters.NumberFilter(field_name='rf_addr', lookup_expr='icontains')
    status = filters.NumberFilter(field_name='status')
    unit = filters.CharFilter(field_name='unit', method='filter_unit')
    address = filters.CharFilter(field_name='address', lookup_expr='icontains')
    start_time = filters.DateFilter(field_name='registered_time', lookup_expr='gte')
    end_time = filters.DateFilter(field_name='registered_time', lookup_expr='lte')

    class Meta:
        model = Hub
        fields = (
            'sn', 'rf_band', 'rf_addr', 'status', 'address',
            'start_time', 'end_time', 'unit'
        )

    @staticmethod
    def filter_sn(queryset, name, value):
        """支持筛选多个集控编号
        2018,2019
        """
        sns = value.split(',')
        return queryset.filter(sn__in=sns)

    @staticmethod
    def filter_unit(queryset, name, value):
        """通过管理单元筛选"""
        queryset.filter(unit__in=Unit.objects.filter_by(name=value))
        return queryset

