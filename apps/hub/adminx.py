#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from hub.models import Unit, Hub, HubStatus


class UnitAdmin(object):
    list_display = ["name"]


class HubAdmin(object):
    list_display = [
        "sn", "status", "rf_band", "rf_addr", "address", "longitude",
        "latitude", "memo", "registered_time", "is_redirect", "is_deleted",
        "created_time", "updated_time", "deleted_time"
    ]


class HubStatusAdmin(object):
    list_display = [
        "sn", "A_voltage", "A_current", "A_power", "A_power_consumption",
        "B_voltage", "B_current", "B_power", "B_power_consumption",
        "C_voltage", "C_current", "C_power", "C_power_consumption",
        "voltage", "current", "power", "power_consumption", "time"
    ]


xadmin.site.register(Unit, UnitAdmin)
xadmin.site.register(Hub, HubAdmin)
xadmin.site.register(HubStatus, HubStatusAdmin)
