#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from workorder.models import (
    WorkOrder, WorkorderImage, Inspection,
    InspectionImage, InspectionItem
)


class WorkOrderAdmin(object):

    list_display = [
        "alert", "w_type", "obj_sn", "lampctrl", "sequence", "user",
        "message", "status", "created_time", "finished_time", "memo"
    ]
    list_filter = [
        "alert", "w_type", "obj_sn", "lampctrl", "sequence", "user",
        "message", "status", "memo"
    ]
    search_fields = [
        "alert", "w_type", "obj_sn", "lampctrl", "sequence", "user",
    "message", "status", "created_time", "finished_time", "memo"
    ]


class WorkorderImageAdmin(object):

    list_display = [
        "order", "image", "image_type", "created_time"
    ]
    list_filter = [
        "order", "image", "image_type"
    ]
    search_fields = [
        "order", "image", "image_type", "created_time"
    ]


class InspectionAdmin(object):

    list_display = [
        "user", "hub", "memo", "created_time"
    ]
    list_filter = [
        "user", "hub", "memo"
    ]
    search_fields = [
        "user", "hub", "memo", "created_time"
    ]


class InspectionImageAdmin(object):

    list_display = [
        "inspection", "image", "created_time"
    ]
    list_filter = [
        "inspection", "image"
    ]
    search_fields = [
        "inspection", "image", "created_time"
    ]


class InspectionItemAdmin(object):

    list_display = [
        "inspection", "hub", "lamp", "sequence", "status", "memo"
    ]
    list_filter = [
        "inspection", "hub", "lamp", "sequence", "status", "memo"
    ]
    search_fields = [
        "inspection", "hub", "lamp", "sequence", "status", "memo"
    ]


xadmin.site.register(WorkOrder, WorkOrderAdmin)
xadmin.site.register(WorkorderImage, WorkorderImageAdmin)
xadmin.site.register(Inspection, InspectionAdmin)
xadmin.site.register(InspectionImage, InspectionImageAdmin)
xadmin.site.register(InspectionItem, InspectionItemAdmin)
