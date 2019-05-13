#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/4
"""
import xadmin
from base.models import Unit
from xadmin import views


class BaseSettings(object):
    enable_themes = True
    use_bootswatch = True


class GlobalSettings(object):
    site_title = "smartlamp后台管理系统"
    site_footer = "smartlamp"


class UnitAdmin(object):
    list_display = ["name"]


xadmin.site.register(views.BaseAdminView, BaseSettings)
xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(Unit, UnitAdmin)
