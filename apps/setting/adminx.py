#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from setting.models import SettingType, Setting


class SettingTypeAdmin(object):

    list_display = [
        "name", "name_zhcn"
    ]
    list_filter = [
        "name", "name_zhcn"
    ]
    search_fields = [
        "name", "name_zhcn"
    ]


class SettingAdmin(object):

    list_display = [
        "option", "option_zhcn", "value", "s_type"
    ]
    list_filter = [
        "option", "option_zhcn", "value", "s_type"
    ]
    search_fields = [
        "option", "option_zhcn", "value", "s_type"
    ]


xadmin.site.register(SettingType, SettingTypeAdmin)
xadmin.site.register(Setting, SettingAdmin)
