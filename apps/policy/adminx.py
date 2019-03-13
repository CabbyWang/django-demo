#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/21
"""
import xadmin

from policy.models import Policy, PolicySet, PolicySetRelation, PolicySetSendDown


class PolicyAdmin(object):

    list_display = [
        "name", "item", "memo", "creator", "is_deleted", "created_time",
        "updated_time", "deleted_time"
    ]
    list_filter = [
        "name", "item", "memo", "creator", "is_deleted"
    ]
    search_fields = [
        "name", "item", "memo", "creator", "is_deleted", "created_time",
        "updated_time", "deleted_time"
    ]


class PolicySetAdmin(object):

    list_display = [
        "policys", "name", "memo", "creator", "is_deleted", "created_time",
        "updated_time", "deleted_time"
    ]
    list_filter = [
        "policys", "name", "memo", "creator", "is_deleted"
    ]
    search_fields = [
        "policys", "name", "memo", "creator", "is_deleted", "created_time",
        "updated_time", "deleted_time"
    ]


class PolicySetRelationAdmin(object):

    list_display = [
        "policy", "policyset", "execute_date", "is_deleted", "created_time",
        "updated_time", "deleted_time"
    ]
    list_filter = [
        "policy", "policyset", "execute_date", "is_deleted"
    ]
    search_fields = [
        "policy", "policyset", "execute_date", "is_deleted", "created_time",
        "updated_time", "deleted_time"
    ]


class PolicySetSendDownAdmin(object):

    list_display = [
        "policyset", "hub", "group_id", "is_deleted", "created_time",
        "updated_time", "deleted_time"
    ]
    list_filter = [
        "policyset", "hub", "group_id", "is_deleted"
    ]
    search_fields = [
        "policyset", "hub", "group_id", "is_deleted", "created_time",
        "updated_time", "deleted_time"
    ]


xadmin.site.register(Policy, PolicyAdmin)
xadmin.site.register(PolicySet, PolicySetAdmin)
xadmin.site.register(PolicySetRelation, PolicySetRelationAdmin)
xadmin.site.register(PolicySetSendDown, PolicySetSendDownAdmin)
