#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/5
"""
from rest_framework.validators import UniqueValidator as _UniqueValidator


class UniqueValidator(_UniqueValidator):

    def exclude_current_instance(self, queryset):
        queryset = queryset.filter(is_deleted=False)
        return super(UniqueValidator, self).exclude_current_instance(queryset)
