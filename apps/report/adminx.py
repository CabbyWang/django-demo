#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from report.models import TotalPowerConsumption, Consumption


class TotalPowerConsumptionAdmin(object):

    list_display = [
        "power_consumption", "date"
    ]
    list_filter = [
        "power_consumption"
    ]
    search_fields = [
        "power_consumption", "date"
    ]


class ConsumptionAdmin(object):

    list_display = [
        "hub", "consumption", "date"
    ]
    list_filter = [
        "hub", "consumption"
    ]
    search_fields = [
        "hub", "consumption", "date"
    ]


xadmin.site.register(TotalPowerConsumption, TotalPowerConsumptionAdmin)
xadmin.site.register(Consumption, ConsumptionAdmin)
