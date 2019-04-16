#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/12
"""
from django_filters import rest_framework as filters

from .models import Hub, Unit


class HubFilter(filters.FilterSet):
    """
    Filter of hubs.
    """

    hub_sn = filters.CharFilter(field_name='sn', method='filter_hub_sn')
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
            'hub_sn', 'rf_band', 'rf_addr', 'status', 'address',
            'start_time', 'end_time', 'unit'
        )

    @staticmethod
    def filter_hub_sn(queryset, name, value):
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
