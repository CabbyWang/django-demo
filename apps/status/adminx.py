#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/25
"""
import xadmin
from status.models import (
    LampCtrlStatus, HubStatus, LampCtrlLatestStatus, HubLatestStatus
)


class HubStatusAdmin(object):
    list_display = [
        "hub", "A_voltage", "A_current", "A_power", "A_consumption",
        "B_voltage", "B_current", "B_power", "B_consumption",
        "C_voltage", "C_current", "C_power", "C_consumption",
        "voltage", "current", "power", "consumption"
    ]


class HubLatestStatusAdmin(object):
    list_display = [
        "hub", "A_voltage", "A_current", "A_power", "A_consumption",
        "B_voltage", "B_current", "B_power", "B_consumption",
        "C_voltage", "C_current", "C_power", "C_consumption",
        "voltage", "current", "power", "consumption"
    ]


class LampCtrlStatusAdmin(object):

    list_display = [
        "lampctrl", "hub", "voltage", "current", "power", "consumption"
    ]
    list_filter = [
        "lampctrl", "hub", "voltage", "current", "power", "consumption"
    ]
    search_fields = [
        "lampctrl", "hub", "voltage", "current", "power", "consumption"
    ]


class LampCtrlLatestStatusAdmin(object):

    list_display = [
        "lampctrl", "hub", "voltage", "current", "power", "consumption"
    ]
    list_filter = [
        "lampctrl", "hub", "voltage", "current", "power", "consumption"
    ]
    search_fields = [
        "lampctrl", "hub", "voltage", "current", "power", "consumption"
    ]


xadmin.site.register(HubStatus, HubStatusAdmin)
xadmin.site.register(HubLatestStatus, HubLatestStatusAdmin)
xadmin.site.register(LampCtrlStatus, LampCtrlStatusAdmin)
xadmin.site.register(LampCtrlLatestStatus, LampCtrlLatestStatusAdmin)
