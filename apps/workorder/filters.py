#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/16
"""
import datetime

from django_filters import rest_framework as filters

from .models import WorkOrder, Inspection


class WorkOrderFilter(filters.FilterSet):
    """
    Filter of WorkOrder.
    """

    id = filters.NumberFilter(field_name='id', lookup_expr='icontains')
    alert = filters.CharFilter(field_name='alert', method='filter_alert')
    memo = filters.CharFilter(field_name='memo', lookup_expr='icontains')
    description = filters.CharFilter(field_name='description',
                                     lookup_expr='icontains')
    user = filters.CharFilter(field_name='user')
    start_time = filters.DateFilter(field_name='created_time',
                                    lookup_expr='gte')
    end_time = filters.DateFilter(field_name='created_time', lookup_expr='lte',
                                  method='filter_end_time')
    status = filters.CharFilter(field_name='status')
    lampctrl = filters.CharFilter(method='filter_lampctrl')

    @staticmethod
    def filter_alert(queryset, name, value):
        """通过告警编号 模糊查询(关系字段不支持icontains)"""
        return queryset.filter(alert__id__icontains=value)

    @staticmethod
    def filter_end_time(queryset, name, value):
        value = value + datetime.timedelta(days=1)
        return queryset.filter(created_time__lt=value)

    @staticmethod
    def filter_lampctrl(queryset, name, value):
        """通过灯控筛选工单(设备维修历史)"""
        # TODO type待确定
        return queryset.filter(type=2, obj_sn=value)

    class Meta:
        model = WorkOrder
        fields = (
            'id', 'alert', 'memo', 'description', 'user',
            'start_time', 'end_time', 'status'
        )


class InspectionFilter(filters.FilterSet):
    """
    Filter of Inspection.
    """

    id = filters.NumberFilter(field_name='id', lookup_expr='icontains')
    hub = filters.CharFilter(field_name='hub')
    start_time = filters.DateFilter(field_name='created_time',
                                    lookup_expr='gte')
    end_time = filters.DateFilter(field_name='created_time', lookup_expr='lte',
                                  method='filter_end_time')

    class Meta:
        model = Inspection
        fields = ('id', 'hub', 'start_time', 'end_time')

    @staticmethod
    def filter_end_time(queryset, name, value):
        value = value + datetime.timedelta(days=1)
        return queryset.filter(created_time__lt=value)
