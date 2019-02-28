#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/15
"""
from rest_framework import permissions


class IsSuperUser(permissions.IsAdminUser):
    """
    判断是否是superuser
    """

    message = "你没有该操作权限"

    def has_permission(self, request, view):
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True


class IsAdminUser(permissions.IsAdminUser):
    """
    判断是否是admin
    """

    message = "你没有该操作权限"

    def has_permission(self, request, view):
        return request.user.username == 'admin'

    def has_object_permission(self, request, view, obj):
        if request.user.username == 'admin':
            return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user
