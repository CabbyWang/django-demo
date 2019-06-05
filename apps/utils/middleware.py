#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/14
"""
import json
from re import sub

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.deprecation import MiddlewareMixin

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rest_framework_jwt.authentication import (
    jwt_decode_handler, jwt_get_username_from_payload
)
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer

from user.models import User
from notify.models import Log

# from rest_framework_jwt.utils import
from utils.exceptions import ServerError

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
SUCCESS = 0
FAIL = 1


class LogMiddleware(MiddlewareMixin):

    """
    Middleware for log.

    login:
        用户登录
    """
    request_data = {}
    query_params = {}
    pk = None
    response_data = {}
    function = None
    user = None
    status = None

    # def process_request(self, request):
    #     if request.method in SAFE_METHODS:
    #         return None
    #     self.request_data = json.loads(
    #         request.body.decode('utf-8')) if request.body else {}
    #     self.query_params = request.GET
    #     header_token = request.META.get('HTTP_AUTHORIZATION')
    #     self.user = None
    #     if header_token:
    #         try:
    #             token = sub('JWT ', '', header_token)
    #             valid_data = VerifyJSONWebTokenSerializer().validate({'token': token})
    #             self.user = valid_data.get('user')
    #         except ValidationError as v:
    #             print('validation error', v)
    #     return None
    #
    # def process_view(self, request, view_func, view_args, view_kwargs):
    #     method = request.method.lower()
    #     if method == 'get':
    #         return None
    #     self.pk = view_kwargs.get('pk')
    #     # viewset_name = view_func.__name__
    #     # full_path = request.get_full_path()
    #     actions = getattr(view_func, 'actions', None)
    #     self.function = '{}_{}'.format(method, actions.get(method))
    #     return None
    #
    # def process_response(self, request, response):
    #     method = request.method
    #     if method in SAFE_METHODS:
    #         return response
    #     # if not str(response.status_code).startswith('2'):
    #     #     return response
    #     if isinstance(response, Response):
    #         self.response_data = response.data
    #
    #     self.status = SUCCESS if str(response.status_code).startswith('2') else FAIL
    #     log_function = getattr(self, self.function, None)
    #     if log_function:
    #         log_function(
    #             request_data=self.request_data,
    #             response_data=self.response_data,
    #             pk=self.pk
    #         )
    #     # TODO 修改response返回信息, 添加message
    #     # res_data = response.data
    #     # if not res_data.get('message'):
    #     #     response.data['message'] = res_data.get('detail')
    #     return response

    def process_exception(self, request, exception):
        if settings.DEBUG:
            return None
        raise ServerError(str(exception))
        return None

    def post_custom_grouping(self, request_data, response_data, pk):
        """下发分组(自定义分组)"""
        username = self.user.username if self.user else ''
        hub = request_data.get('hub')
        configs = request_data.get('configs')
        msg = "[{username}]对集控[{object}]下发分组. "
        for config in configs:
            group_num = config['group_num']
            lampctrl_sns = config['lampctrl']
            msg += "{}分组:集控{}; ".format(group_num, ','.join(lampctrl_sns))
        memo = msg.format(username=username, object=hub)
        Log.objects.create(
            event=_("send down groups(custom group)"),
            username=username,
            object=hub,
            status=self.status,
            memo=memo
        )

    def post_pattern_grouping(self, request_data, response_data, pk):
        """下发分组(模式分组)"""
        username = self.user.username if self.user else ''
        hub = request_data.get('hub')
        group_num = request_data.get('group_num')
        group_num_rest = request_data.get('group_num_rest')
        segmentation = request_data.get('segmentation')
        select = request_data.get('select')
        # TODO 翻译
        msg = "[{username}]对集控[{object}]下发分组[{group_num}, " \
              "{group_num_rest}], 模式为隔{segmentation}选{select}"
        memo = msg.format(
            username=username,
            object=hub,
            group_num=group_num,
            group_num_rest=group_num_rest,
            segmentation=segmentation,
            select=select
        )
        Log.objects.create(
            event=_("send down groups(group by pattern)"),
            username=username,
            object=hub,
            status=self.status,
            memo=memo
        )

    def post_gather_group(self, request_data, response_data, pk):
        """集控分组采集"""
        username = self.user.username if self.user else ''
        hubs = ','.join(request_data.get('hub'))
        error_hubs = ','.join(response_data.get('error_hubs'))
        if self.status == FAIL:
            # TODO 翻译
            msg = "[{username}]采集了集控[{object}]的分组, 部分集控[{error_hubs}]采集失败"
            memo = msg.format(
                username=username,
                object=hubs,
                error_hubs=error_hubs
            )
        elif self.status == SUCCESS:
            msg = "[{username}]采集了集控[{object}]的分组"
            memo = msg.format(
                username=username,
                object=hubs
            )
        Log.objects.create(
            event=_("gather hub groups"),
            username=username,
            object=hubs,
            status=self.status,
            memo=memo
        )

    def post_gather_hub_status(self, request_data, response_data, pk):
        """采集集控状态"""
        username = self.user.username if self.user else ''
        hubs = ','.join(request_data.get('hub'))
        error_hubs = ','.join(response_data.get('error_hubs'))
        if self.status == FAIL:
            # TODO 翻译
            msg = "[{username}]采集了集控[{object}]的状态, 部分集控[{error_hubs}]采集失败"
            memo = msg.format(
                username=username,
                object=hubs,
                error_hubs=error_hubs
            )
        elif self.status == SUCCESS:
            msg = "[{username}]采集了集控[{object}]的状态"
            memo = msg.format(
                username=username,
                object=hubs
            )
        Log.objects.create(
            event=_("gather hub status"),
            username=username,
            object=hubs,
            status=self.status,
            memo=memo
        )

    def post_load_inventory(self, request_data, response_data, pk):
        """采集集控配置"""
        username = self.user.username if self.user else ''
        hubs = ','.join(request_data.get('hub'))
        error_hubs = ','.join(response_data.get('error_hubs'))
        if self.status == FAIL:
            # TODO 翻译
            msg = "[{username}]采集了集控[{object}]的配置, 部分集控[{error_hubs}]采集失败"
            memo = msg.format(
                username=username,
                object=hubs,
                error_hubs=error_hubs
            )
        elif self.status == SUCCESS:
            msg = "[{username}]采集了集控[{object}]的配置"
            memo = msg.format(
                username=username,
                object=hubs
            )
        Log.objects.create(
            event=_("gather hub configuration"),
            username=username,
            object=hubs,
            status=self.status,
            memo=memo
        )

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
