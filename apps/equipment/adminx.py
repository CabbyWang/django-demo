#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/9
"""
import xadmin
from equipment.models import Pole, Lamp, CBox, Cable, Hub, LampCtrl


class PoleAdmin(object):
    list_display = [
        "sn", "vendor", "model", "height", "date", "longitude",
        "latitude", "created_time", "address", "memo", "is_used",
        "image"
    ]
    list_filter = [
        "sn", "vendor", "model", "height", "date", "longitude",
        "latitude", "address", "memo", "is_used", "image"
    ]
    search_fields = [
        "sn", "vendor", "model", "height", "date", "longitude",
        "latitude", "created_time", "address", "memo", "is_used",
        "image"
    ]


class LampAdmin(object):
    list_display = [
        "sn", "vendor", "model", "bearer", "controller", "date",
        "created_time", "address", "memo", "is_used", "image"
    ]
    list_filter = [
        "sn", "vendor", "model", "bearer", "controller", "address",
        "memo", "is_used", "image"
    ]
    search_fields = [
        "sn", "vendor", "model", "bearer", "controller", "date",
        "created_time", "address", "memo", "is_used", "image"
    ]


class CboxAdmin(object):

    list_display = [
        "sn", "vendor", "model", "date", "created_time", "longitude",
        "latitude", "address", "memo", "is_used", "image"
    ]
    list_filter = [
        "sn", "vendor", "model", "longitude", "latitude", "address",
        "memo", "is_used", "image"
    ]
    search_fields = [
        "sn", "vendor", "model", "date", "created_time", "longitude",
        "latitude", "address", "memo", "is_used", "image"
    ]


class CableAdmin(object):

    list_display = [
        "sn", "vendor", "model", "length", "date", "created_time",
        "address", "memo"
    ]
    list_filter = [
        "sn", "vendor", "model", "length", "address", "memo"
    ]
    search_fields = [
        "sn", "vendor", "model", "length", "date", "created_time",
        "address", "memo"
    ]


class HubAdmin(object):
    list_display = [
        "sn", "status", "rf_band", "rf_addr", "address", "longitude",
        "latitude", "memo", "registered_time", "is_redirect", "is_deleted",
        "created_time", "updated_time", "deleted_time"
    ]


class LampCtrlAdmin(object):

    list_display = [
        "sn", "hub", "sequence", "status", "switch_status", "lamp_type",
        "is_repeated", "rf_band", "rf_addr", "address", "new_address",
        "longitude", "latitude", "on_map", "memo",
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
        "longitude", "latitude", "on_map", "memo",
        "registered_time", "is_deleted", "created_time", "updated_time",
        "deleted_time"
    ]


xadmin.site.register(Pole, PoleAdmin)
xadmin.site.register(Lamp, LampAdmin)
xadmin.site.register(CBox, CboxAdmin)
xadmin.site.register(Cable, CableAdmin)
xadmin.site.register(Hub, HubAdmin)
xadmin.site.register(LampCtrl, LampCtrlAdmin)
