#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from lamp.models import LampCtrl, LampCtrlStatus, LampCtrlGroup


class LampCtrlAdmin(object):

    list_display = [
        "sn", "hub", "sequence", "status", "switch_status", "lamp_type",
        "is_repeated", "rf_band", "rf_addr", "address", "new_address",
        "longitude", "latitude", "on_map", "memo", "failure_date",
        "registered_time", "is_deleted", "created_time", "updated_time",
        "deleted_time"
    ]
    list_filter = [
        "sn", "hub", "sequence", "status", "switch_status", "lamp_type",
        "is_repeated", "rf_band", "rf_addr", "address", "new_address",
        "longitude", "latitude", "on_map", "memo"
    ]
    search_fields = [
        "sn", "hub", "sequence", "status", "switch_status", "lamp_type",
        "is_repeated", "rf_band", "rf_addr", "address", "new_address",
        "longitude", "latitude", "on_map", "memo", "failure_date",
        "registered_time", "is_deleted", "created_time", "updated_time",
        "deleted_time"
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


xadmin.site.register(LampCtrl, LampCtrlAdmin)
xadmin.site.register(LampCtrlStatus, LampCtrlStatusAdmin)
xadmin.site.register(LampCtrlGroup, LampCtrlGroupAdmin)
