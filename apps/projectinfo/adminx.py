#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from projectinfo.models import ProjectInfo


class ProjectInfoAdmin(object):

    list_display = [
        "name", "city", "longitude", "latitude", "zoom_level"
    ]
    list_filter = [
        "name", "city", "longitude", "latitude", "zoom_level"
    ]
    search_fields = [
        "name", "city", "longitude", "latitude", "zoom_level"
    ]


xadmin.site.register(ProjectInfo, ProjectInfoAdmin)
