#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from notify.models import Log, Alert, AlertAudio


class LogAdmin(object):

    list_display = [
        "user", "event", "object", "memo", "created_time"
    ]
    list_filter = [
        "user", "event", "object", "memo"
    ]
    search_fields = [
        "user", "event", "object", "memo", "created_time"
    ]


class AlertAdmin(object):

    list_display = [
        "event", "level", "alert_source", "object_type", "object",
        "occurred_time", "memo", "is_solved", "solver", "solved_time"
    ]
    list_filter = [
        "event", "level", "alert_source", "object_type", "object",
        "memo", "is_solved", "solver"
    ]
    search_fields = [
        "event", "level", "alert_source", "object_type", "object",
        "occurred_time", "memo", "is_solved", "solver", "solved_time",
    ]


class AlertAudioAdmin(object):

    list_display = [
        "alert", "audio", "times", "created_time"
    ]
    list_filter = [
        "alert", "audio", "times"
    ]
    search_fields = [
        "alert", "audio", "times", "created_time"
    ]


xadmin.site.register(Log, LogAdmin)
xadmin.site.register(Alert, AlertAdmin)
xadmin.site.register(AlertAudio, AlertAudioAdmin)
