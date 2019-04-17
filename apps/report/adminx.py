#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from report.models import (
    DailyTotalConsumption, HubDailyTotalConsumption, MonthTotalConsumption,
    HubMonthTotalConsumption, DeviceConsumption, LampCtrlConsumption
)


class DailyTotalConsumptionAdmin(object):

    list_display = [
        "consumption", "date"
    ]
    list_filter = [
        "consumption"
    ]
    search_fields = [
        "consumption", "date"
    ]


class HubDailyTotalConsumptionAdmin(object):

    list_display = [
        "hub", "consumption", "date"
    ]
    list_filter = [
        "hub", "consumption"
    ]
    search_fields = [
        "hub", "consumption", "date"
    ]


class MonthTotalConsumptionAdmin(object):

    list_display = [
        "consumption", "month"
    ]
    list_filter = [
        "consumption"
    ]
    search_fields = [
        "consumption", "month"
    ]


class HubMonthTotalConsumptionAdmin(object):

    list_display = [
        "hub", "consumption", "month"
    ]
    list_filter = [
        "hub", "consumption"
    ]
    search_fields = [
        "hub", "consumption", "month"
    ]


class DeviceConsumptionAdmin(object):

    list_display = [
        "hub", "hub_consumption", "lamps_consumption", "loss_consumption"
    ]
    list_filter = [
        "hub", "hub_consumption", "lamps_consumption", "loss_consumption"
    ]
    search_fields = [
        "hub", "hub_consumption", "lamps_consumption", "loss_consumption"
    ]


class LampCtrlConsumptionAdmin(object):

    list_display = [
        "lampctrl", "consumption"
    ]
    list_filter = [
        "lampctrl", "consumption"
    ]
    search_fields = [
        "lampctrl", "consumption"
    ]


xadmin.site.register(DailyTotalConsumption, DailyTotalConsumptionAdmin)
xadmin.site.register(HubDailyTotalConsumption, HubDailyTotalConsumptionAdmin)
xadmin.site.register(MonthTotalConsumption, MonthTotalConsumptionAdmin)
xadmin.site.register(HubMonthTotalConsumption, HubMonthTotalConsumptionAdmin)
xadmin.site.register(DeviceConsumption, DeviceConsumptionAdmin)
xadmin.site.register(LampCtrlConsumption, LampCtrlConsumptionAdmin)
