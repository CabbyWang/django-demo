#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/14
"""
from django.utils.translation import ugettext_lazy as _
from django.utils.deprecation import MiddlewareMixin

from rest_framework_jwt.authentication import (
    jwt_decode_handler, jwt_get_username_from_payload
)

from user.models import User
from notify.models import Log

# from rest_framework_jwt.utils import


class LogMiddleware(MiddlewareMixin):

    """
    Middleware for log.

    login:
        用户登录
    """

    def process_view(self, request, view_func, view_func_args, view_func_kwargs):
        if request.method == 'GET':
            return None
        fun = request.path.split('/')[1]
        try:
            getattr(self, fun, 'default')(request, view_func, view_func_args, view_func_kwargs)
        except Exception as ex:
            # TODO log exception
            pass
        return None

    def process_response(self, request, response):
        method = request.method
        if method == 'GET':
            return response
        fun = request.path.split('/')[1]
        try:
            getattr(self, fun, 'default')(request, response)
        except Exception as ex:
            # TODO log exception
            pass
        return response

    def default(self, request, response):
        """pass"""
        pass

    # def login(self, request, response):
    #     """用户登录"""
    #     event = _('用户登录')
    #     ip = request.META.get('REMOTE_ADDR', '<none>')
    #     if str(response.status_code).startswith('2'):
    #         # 登录成功
    #         data = response.data
    #         user = User.objects.get(id=data.get('user_id'))
    #         username = user.username
    #         status = 0
    #         msg = _('[用户{username}在[{ip}]登录]')
    #         memo = msg.format(username=username, ip=ip)
    #         Log.objects.create(
    #             user=None, event=event, object=ip, status=status, memo=memo
    #         )
    #     # jwt_value = request.COOKIES.get('jwt', '')
    #     # payload = jwt_decode_handler(jwt_value)
    #     # username = jwt_get_username_from_payload(payload)

    def login(self, request, view_func, view_func_args, view_func_kwargs):
        """用户登录"""
        # 用户登录
        event = _("log in")
        ip = request.META.get('REMOTE_ADDR', '<none>')
        # [用户[{username}]在[{ip}]登录]
        msg = _('user [{username}] log in on ip [{ip}]')
        memo = msg.format(username='', ip=ip)
        Log.objects.create(
            user=None, event=event, object=ip, status=0, memo=memo
        )
