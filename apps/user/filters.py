#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/14
"""
from django_filters import rest_framework as filters

from user.models import UserGroup, User


class UserFilter(filters.FilterSet):
    """
    Filter of User.
    """
    username = filters.CharFilter(field_name='username')
    user_group = filters.CharFilter(field_name='user_group')

    class Meta:
        model = User
        fields = (
            'user_group',
            'username'
        )


class UserGroupFilter(filters.FilterSet):
    """
    Filter of UserGroup.
    """

    class Meta:
        model = UserGroup
        fields = (
            'id',
        )
