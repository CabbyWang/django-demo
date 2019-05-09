#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/1/25
"""
from django.db import connections


def refresh_connections():
    for conn in connections.all():
        conn.queries_log.clear()
        conn.close_if_unusable_or_obsolete()

