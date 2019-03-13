#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/6
"""
from rest_framework import permissions

from user.models import Permission


class IsOwnHubOrSuperUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if Permission.objects.filter(hub=obj, user=request.user).exists:
            return True
