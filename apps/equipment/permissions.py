#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/9
"""
from rest_framework import permissions

from user.models import Permission


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow superuser to edit it.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # User must be a superuser.
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # User must be a superuser.
        return request.user.is_superuser


class IsOwnHubOrSuperUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if Permission.objects.filter_by(hub=obj.hub, user=request.user).exists:
            return True
