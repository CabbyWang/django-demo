#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/14
"""
import xadmin

from user.models import UserGroup, User, Permission


class UserGroupAdmin(object):
    list_display = ["name", "memo"]


class UserAdmin(object):
    list_display = [
        "id", "mobile", "email", "is_read_only", "is_receive_alarm",
        "password_modified_time", "user_group", "updated_user",
        "organization", "memo", "is_deleted", "created_time",
        "updated_time", "deleted_time"
    ]


class PermissionAdmin(object):
    list_display = ["is_deleted", "created_time", "updated_time", "deleted_time"]


xadmin.site.register(UserGroup, UserGroupAdmin)
xadmin.site.unregister(User)
xadmin.site.register(User, UserAdmin)
xadmin.site.register(Permission, PermissionAdmin)
