#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from workorder.models import (
    WorkOrder, WorkorderImage, WorkOrderAudio,
    Inspection, InspectionImage, InspectionItem
)


class WorkOrderAdmin(object):

    list_display = [
        "alert", "type", "obj_sn", "lampctrl", "sequence", "user",
        "message", "status", "created_time", "finished_time", "memo"
    ]
    list_filter = [
        "alert", "type", "obj_sn", "lampctrl", "sequence", "user",
        "message", "status", "memo"
    ]
    search_fields = [
        "alert", "type", "obj_sn", "lampctrl", "sequence", "user",
    "message", "status", "created_time", "finished_time", "memo"
    ]


class WorkOrderImageAdmin(object):

    list_display = [
        "order", "image", "image_type", "created_time"
    ]
    list_filter = [
        "order", "image", "image_type"
    ]
    search_fields = [
        "order", "image", "image_type", "created_time"
    ]


class WorkOrderAudioAdmin(object):

    list_display = [
        "order", "audio", "times", "created_time"
    ]
    list_filter = [
        "order", "audio", "times"
    ]
    search_fields = [
        "order", "audio", "times", "created_time"
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
        "inspection", "hub", "lampctrl", "status", "memo"
    ]
    list_filter = [
        "inspection", "hub", "lampctrl", "status", "memo"
    ]
    search_fields = [
        "inspection", "hub", "lampctrl", "status", "memo"
    ]


xadmin.site.register(WorkOrder, WorkOrderAdmin)
xadmin.site.register(WorkorderImage, WorkOrderImageAdmin)
xadmin.site.register(WorkOrderAudio, WorkOrderAudioAdmin)
xadmin.site.register(Inspection, InspectionAdmin)
xadmin.site.register(InspectionImage, InspectionImageAdmin)
xadmin.site.register(InspectionItem, InspectionItemAdmin)
