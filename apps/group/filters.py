#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/9
"""
from django_filters import rest_framework as filters

from group.models import LampCtrlGroup


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
