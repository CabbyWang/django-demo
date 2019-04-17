#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/17
"""
import datetime

from django_filters import rest_framework as filters

from .models import DeviceConsumption, HubMonthTotalConsumption, MonthTotalConsumption


class DeviceConsumptionFilter(filters.FilterSet):
    """
    Filter of DeviceConsumption.
    """

    hub = filters.CharFilter(field_name='hub')

    class Meta:
        model = DeviceConsumption
        fields = ('hub', )


class HubMonthTotalConsumptionFilter(filters.FilterSet):
    """
    Filter of HubMonthTotalConsumption.
    """

    hub = filters.CharFilter(field_name='hub')
    month = filters.CharFilter(field_name='month', method='filter_month')  # "2018-06"

    @staticmethod
    def filter_month(queryset, name, value):
        months = value.split(',')
        return queryset.filter(month__in=months)

    class Meta:
        model = HubMonthTotalConsumption
        fields = ('hub', 'month')


class MonthTotalConsumptionFilter(filters.FilterSet):
    """
    Filter of MonthTotalConsumption.
    """

    hub = filters.CharFilter(field_name='hub')
    start_month = filters.CharFilter(field_name='month', lookup_expr='gte', method='filter_start_month')  # "2018-06"
    end_month = filters.CharFilter(field_name='month', lookup_expr='lte')  # "2018-08"

    @staticmethod
    def filter_start_month(queryset, name, value):
        try:
            datetime.datetime.str
            return queryset.filter(month__gte=value)
        except:
            return queryset
        return queryset

    # @staticmethod
    # def filter_month(queryset, name, value):
    #     months = value.split(',')
    #     return queryset.filter(month__in=months)

    class Meta:
        model = HubMonthTotalConsumption
        fields = ('hub', 'month')
