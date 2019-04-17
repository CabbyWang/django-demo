#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from asset.models import Pole, Lamp, CBox, Cable


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


xadmin.site.register(Pole, PoleAdmin)
xadmin.site.register(Lamp, LampAdmin)
xadmin.site.register(CBox, CboxAdmin)
xadmin.site.register(Cable, CableAdmin)
