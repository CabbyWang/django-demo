#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/9
"""
from django_filters import rest_framework as filters

from .models import Policy, PolicySet, PolicySetRelation, PolicySetSendDown


class PolicyFilter(filters.FilterSet):
    """
    Policy Filter.
    """

    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    memo = filters.CharFilter(field_name='memo', lookup_expr='icontains')
    creator = filters.CharFilter(field_name='creator__username')
    is_used = filters.BooleanFilter(method='filter_is_used')

    @staticmethod
    def filter_is_used(queryset, name, value):
        """通过是否使用筛选"""
        ret_qs = Policy.objects.none()
        for instance in queryset:
            if PolicySetRelation.objects.filter_by(policy=instance).exists() == value:
                ret_qs |= Policy.objects.filter_by(id=instance.id)
        return ret_qs

    class Meta:
        model = Policy
        fields = ('name', 'memo', 'creator', 'is_used')


class PolicySetFilter(filters.FilterSet):
    """
    Policy set Filter.
    """

    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    memo = filters.CharFilter(field_name='memo', lookup_expr='icontains')
    creator = filters.CharFilter(field_name='creator__username')
    is_used = filters.BooleanFilter(method='filter_is_used')

    @staticmethod
    def filter_is_used(queryset, name, value):
        """通过是否使用筛选"""
        ret_qs = PolicySet.objects.none()
        for instance in queryset:
            if PolicySetSendDown.objects.filter_by(policyset=instance).exists() == value:
                ret_qs |= PolicySet.objects.filter_by(id=instance.id)
        return ret_qs

    class Meta:
        model = PolicySet
        fields = ('name', 'memo', 'creator', 'is_used')
