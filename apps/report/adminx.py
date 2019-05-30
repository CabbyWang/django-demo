#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from report.models import LampCtrlConsumption, HubConsumption


class LampCtrlConsumptionAdmin(object):

    list_display = [
        "lampctrl", "hub", "consumption", "date"
    ]
    list_filter = [
        "lampctrl", "hub", "consumption"
    ]
    search_fields = [
        "lampctrl", "hub", "consumption", "date"
    ]


class HubConsumptionAdmin(object):

    list_display = [
        "hub", "consumption", "date"
    ]
    list_filter = [
        "hub", "consumption"
    ]
    search_fields = [
        "hub", "consumption", "date"
    ]


xadmin.site.register(LampCtrlConsumption, LampCtrlConsumptionAdmin)
xadmin.site.register(HubConsumption, HubConsumptionAdmin)
