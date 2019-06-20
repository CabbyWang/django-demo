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
        "alert", "type", "obj_sn", "user", "memo",
        "status", "created_time", "finished_time", "description"
    ]
    list_filter = [
        "alert", "type", "obj_sn", "user",
        "memo", "status", "description"
    ]
    search_fields = [
        "alert", "type", "obj_sn", "user", "memo",
        "status", "created_time", "finished_time", "description"
    ]


class WorkOrderImageAdmin(object):

    list_display = [
        "order", "file", "image_type", "created_time"
    ]
    list_filter = [
        "order", "file", "image_type"
    ]
    search_fields = [
        "order", "file", "image_type", "created_time"
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
        "inspection", "file", "created_time"
    ]
    list_filter = [
        "inspection", "file"
    ]
    search_fields = [
        "inspection", "file", "created_time"
    ]


class InspectionItemAdmin(object):

    list_display = [
        "inspection", "lampctrl", "status", "memo"
    ]
    list_filter = [
        "inspection", "lampctrl", "status", "memo"
    ]
    search_fields = [
        "inspection", "lampctrl", "status", "memo"
    ]


xadmin.site.register(WorkOrder, WorkOrderAdmin)
xadmin.site.register(WorkorderImage, WorkOrderImageAdmin)
xadmin.site.register(WorkOrderAudio, WorkOrderAudioAdmin)
xadmin.site.register(Inspection, InspectionAdmin)
xadmin.site.register(InspectionImage, InspectionImageAdmin)
xadmin.site.register(InspectionItem, InspectionItemAdmin)
