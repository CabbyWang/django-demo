#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/14
"""
import xadmin

from xadmin import views

from user.models import UserGroup, User, Permission


class UserGroupAdmin(object):
    list_display = ["name", "memo", "created_time"]


class UserAdmin(object):
    list_display = [
        "id", "mobile", "email", "read_only_user", "receive_alarm",
        "password_modified_time", "user_group", "updated_user",
        "organization", "memo", "is_deleted", "created_time",
        "updated_time", "deleted_time"
    ]


class PermissionAdmin(object):
    list_display = ["is_deleted", "created_time", "updated_time", "deleted_time"]


class BaseSettings(object):
    enable_themes = True
    use_bootswatch = True


class GlobalSettings(object):
    site_title = "smartlamp后台管理系统"
    site_footer = "smartlamp"


xadmin.site.register(UserGroup, UserGroupAdmin)
xadmin.site.unregister(User)
xadmin.site.register(User, UserAdmin)
xadmin.site.register(Permission, PermissionAdmin)

xadmin.site.register(views.BaseAdminView, BaseSettings)
xadmin.site.register(views.CommAdminView, GlobalSettings)
