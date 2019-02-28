#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/12
"""


def jwt_response_payload_handler(token, user=None, request=None):
    """为返回的结果添加用户相关信息"""
    return {
        'token': token,
        'user_id': user.id
    }
