#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/25
"""
import xadmin
from status.models import LampCtrlStatus, HubStatus


class HubStatusAdmin(object):
    list_display = [
        "sn", "A_voltage", "A_current", "A_power", "A_power_consumption",
        "B_voltage", "B_current", "B_power", "B_power_consumption",
        "C_voltage", "C_current", "C_power", "C_power_consumption",
        "voltage", "current", "power", "power_consumption", "time"
    ]


class LampCtrlStatusAdmin(object):

    list_display = [
        "lampctrl", "voltage", "current", "power", "power_consumption", "time"
    ]
    list_filter = [
        "lampctrl", "voltage", "current", "power", "power_consumption", "time"
    ]
    search_fields = [
        "lampctrl", "voltage", "current", "power", "power_consumption", "time"
    ]


xadmin.site.register(HubStatus, HubStatusAdmin)
xadmin.site.register(LampCtrlStatus, LampCtrlStatusAdmin)
