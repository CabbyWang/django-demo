#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/9
"""
import xadmin
from group.models import LampCtrlGroup


class LampCtrlGroupAdmin(object):

    list_display = [
        "hub", "lampctrl", "group_num", "memo", "is_default"
    ]
    list_filter = [
        "hub", "lampctrl", "group_num", "memo", "is_default"
    ]
    search_fields = [
        "hub", "lampctrl", "group_num", "memo", "is_default"
    ]


xadmin.site.register(LampCtrlGroup, LampCtrlGroupAdmin)
