#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/26
"""
from rest_framework import permissions


class IsOwnerOrPriority(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.username == 'admin':
            return True
        if request.user.is_superuser and not obj.is_superuser:
            return True

        # is owner
        return obj == request.user


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsPriority(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.username == 'admin':
            return True
        if request.user.is_superuser and not obj.is_superuser:
            return True
        return False

