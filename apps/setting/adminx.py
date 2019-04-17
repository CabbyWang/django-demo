#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from setting.models import SettingType, Setting


class SettingTypeAdmin(object):

    list_display = [
        "name",
    ]
    list_filter = [
        "name",
    ]
    search_fields = [
        "name",
    ]


class SettingAdmin(object):

    list_display = [
        "option", "name", "value", "type"
    ]
    list_filter = [
        "option", "name", "value", "type"
    ]
    search_fields = [
        "option", "name", "value", "type"
    ]


xadmin.site.register(SettingType, SettingTypeAdmin)
xadmin.site.register(Setting, SettingAdmin)
