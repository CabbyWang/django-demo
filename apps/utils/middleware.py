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

from user.models import User, UserGroup
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
    communicate_user_groups_put_update:
        修改用户组
    communicate_user_groups_post_create:
        创建用户组
    communicate_post_custom_grouping:
        下发分组(自定义分组)
    communicate_post_pattern_grouping:
        下发分组(模式分组)
    communicate_post_gather_group:
        集控分组采集
    communicate_post_gather_hub_status:
        采集集控状态
    communicate_post_load_inventory:
        采集集控配置
    communicate_post_update_group:
        修改分组
    communicate_post_recycle_group:
        回收集控下的所有分组
        下发策略集
    communicate_post_gather_policyset:
        策略集采集
        回收策略集
    communicate_post_control_all:
        全开全关
    communicate_post_get_lamp_ctrl_status:
        采集灯控状态
    communicate_post_control_lamp:
        控灯
    """

    def process_request(self, request):
        if request.method in SAFE_METHODS:
            return None
        self.pk = None
        self.function = ''
        self.username = None
        self.status = None
        self.ip = None
        self.request_data = {}
        self.query_params = {}
        self.response_data = {}

        self.__get_request_data(request)
        self.__get_query_params(request)
        self.__get_ip(request)
        self.__get_username(request)
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        method = request.method.lower()
        if method == 'get':
            return None
        self.__get_pk_from_view_kwargs(view_kwargs)
        self.__get_func_name(method, view_func)
        return None

    def process_response(self, request, response):
        method = request.method
        if method in SAFE_METHODS:
            return response
        self.__get_response_data(response)
        self.__get_status(response)

        self.__log()
        # TODO 修改response返回信息, 添加message
        # res_data = response.data
        # if not res_data.get('message'):
        #     response.data['message'] = res_data.get('detail')
        return response

    def process_exception(self, request, exception):
        if settings.DEBUG:
            return None
        # raise ServerError(str(exception))
        raise ServerError

    def __get_request_data(self, request):
        try:
            self.request_data = json.loads(request.body.decode('utf-8') or '{}')
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.request_data = {}

    def __get_query_params(self, request):
        self.query_params = request.GET

    def __get_ip(self, request):
        self.ip = request.META.get('REMOTE_ADDR')

    def __get_username(self, request):
        header_token = request.META.get('HTTP_AUTHORIZATION')
        self.username = None
        if header_token:
            try:
                token = sub('JWT ', '', header_token)
                valid_data = VerifyJSONWebTokenSerializer().validate({'token': token})
                user = valid_data.get('user')
                self.username = user.username if user else ''
            except ValidationError as v:
                print('validation error', v)

    def __get_pk_from_view_kwargs(self, view_kwargs):
        self.pk = view_kwargs.get('pk')

    def __get_func_name(self, method, view_func):
        try:
            basename = view_func.initkwargs.get('basename')
            actions = getattr(view_func, 'actions', None)
            if not basename:
                self.function = 'login'
            else:
                self.function = '{}_{}_{}'.format(basename, method, actions.get(method))
        except (AttributeError, TypeError):
            self.function = ''

    def __get_response_data(self, response):
        self.response_data = response.data if isinstance(response, Response) else {}

    def __get_status(self, response):
        self.status = SUCCESS if str(response.status_code).startswith('2') else FAIL

    def __log(self):
        log_function = getattr(self, self.function, None)
        if log_function:
            log_function(
                request_data=self.request_data,
                response_data=self.response_data,
                pk=self.pk
            )

    def communicate_post_control_lamp(self, request_data, response_data, pk):
        """控灯"""
        lampctrl_sns = ','.join(request_data.get('lampctrl', []))
        action = request_data.get('action')
        msg = "[{username}]将灯控[{object}]亮度调至[{action}]"
        memo = msg.format(
            username=self.username,
            object=lampctrl_sns,
            action=action
        )
        Log.objects.create(
            event=_("control lamps"),
            username=self.username,
            object=lampctrl_sns,
            status=self.status,
            memo=memo
        )

    def communicate_post_get_lamp_ctrl_status(self, request_data, response_data, pk):
        """采集灯控状态"""
        lampctrl_sns = ','.join(request_data.get('lampctrl', []))
        error_lampctrls = ','.join(response_data.get('error_lampctrls', []))
        if self.status == FAIL:
            # TODO 翻译
            msg = "[{username}]采集了灯控[{object}]的状态, 灯控[{error_lampctrls}]采集失败"
            memo = msg.format(
                username=self.username,
                object=lampctrl_sns,
                error_lampctrls=error_lampctrls
            )
        elif self.status == SUCCESS:
            msg = "[{username}]采集了灯控[{object}]的状态"
            memo = msg.format(
                username=self.username,
                object=lampctrl_sns
            )
        Log.objects.create(
            event=_("gather lamp control status"),
            username=self.username,
            object=lampctrl_sns,
            status=self.status,
            memo=memo
        )

    def communicate_post_control_all(self, request_data, response_data, pk):
        """全开全关"""
        hubs = ','.join(request_data.get('hub'))
        action = '全开' if request_data.get('action') == 'open' else '全关'
        msg = "[{username}]对集控[{object}]下发[{action}]指令"
        memo = msg.format(
            username=self.username,
            object=hubs,
            action=action
        )
        Log.objects.create(
            event=_("control all"),
            username=self.username,
            object=hubs,
            status=self.status,
            memo=memo
        )

    def communicate_post_gather_policyset(self, request_data, response_data, pk):
        """采集策略集"""
        hubs = ','.join(request_data.get('hub'))
        if self.status == FAIL:
            error_hubs = ','.join(response_data.get('error_hubs', []))
            msg = "[{username}]采集了集控[{object}]的策略集, 集控[{error_hubs}]采集失败"
            memo = msg.format(
                username=self.username,
                object=hubs,
                error_hubs=error_hubs
            )
        elif self.status == SUCCESS:
            msg = "[{username}]采集了集控[{object}]的策略集"
            memo = msg.format(
                username=self.username,
                object=hubs
            )
        Log.objects.create(
            event=_("gather policy set"),
            username=self.username,
            object=hubs,
            status=self.status,
            memo=memo
        )

    def communicate_post_update_group(self, request_data, response_data, pk):
        """修改分组"""
        hub = request_data.get('hub')
        group_num = request_data.get('group_num')
        lampctrl_sns = request_data.get('lampctrl', [])
        lampctrl_sns = ','.join(lampctrl_sns)
        msg = "[{username}]修改集控[{object}]分组. 将灯控[{lampctrl_sns}]归属到[{group_num}]分组"
        memo = msg.format(
            username=self.username,
            object=hub,
            lampctrl_sns=lampctrl_sns,
            group_num=group_num
        )
        Log.objects.create(
            event=_("update group"),
            username=self.username,
            object=hub,
            status=self.status,
            memo=memo
        )

    def communicate_post_recycle_group(self, request_data, response_data, pk):
        """回收分组"""
        hubs = ','.join(request_data.get('hub'))
        if self.status == FAIL:
            error_hubs = ','.join(response_data.get('error_hubs', []))
            # TODO 翻译
            msg = "[{username}]回收了集控[{object}]的分组, 集控[{error_hubs}]采集失败"
            memo = msg.format(
                username=self.username,
                object=hubs,
                error_hubs=error_hubs
            )
        elif self.status == SUCCESS:
            msg = "[{username}]回收了集控[{object}]的分组"
            memo = msg.format(
                username=self.username,
                object=hubs
            )
        Log.objects.create(
            event=_("recycle hub group"),
            username=self.username,
            object=hubs,
            status=self.status,
            memo=memo
        )

    def communicate_user_groups_put_update(self, request_data, response_data, pk):
        """修改用户组"""
        user_group = UserGroup.objects.get(id=pk)
        msg = "[{username}]修改用户组[{object}]: 修改组名为{new_name}, 备注为{new_memo}"
        memo = msg.format(
            username=self.username,
            object=user_group.name,
            new_name=request_data.get('name'),
            new_memo=request_data.get('memo') or '空'
        )
        Log.objects.create(
            event=_("update user group"),
            username=self.username,
            object=user_group.name,
            status=self.status,
            memo=memo
        )

    def communicate_user_groups_post_create(self, request_data, response_data, pk):
        """创建用户组"""
        user_group_name = request_data.get('name')
        msg = "[{username}]创建用户组[{object}]"
        memo = msg.format(
            username=self.username,
            object=user_group_name
        )
        Log.objects.create(
            event=_("create user group"),
            username=self.username,
            object=user_group_name,
            status=self.status,
            memo=memo
        )

    def communicate_post_custom_grouping(self, request_data, response_data, pk):
        """下发分组(自定义分组)"""
        hub = request_data.get('hub')
        configs = request_data.get('configs')
        msg = "[{username}]对集控[{object}]下发分组. "
        for config in configs:
            group_num = config['group_num']
            lampctrl_sns = config['lampctrl']
            msg += "{}分组:集控{}; ".format(group_num, ','.join(lampctrl_sns))
        memo = msg.format(username=self.username, object=hub)
        Log.objects.create(
            event=_("send down groups(custom group)"),
            username=self.username,
            object=hub,
            status=self.status,
            memo=memo
        )

    def communicate_post_pattern_grouping(self, request_data, response_data, pk):
        """下发分组(模式分组)"""
        hub = request_data.get('hub')
        group_num = request_data.get('group_num')
        group_num_rest = request_data.get('group_num_rest')
        segmentation = request_data.get('segmentation')
        select = request_data.get('select')
        # TODO 翻译
        msg = "[{username}]对集控[{object}]下发分组[{group_num}, " \
              "{group_num_rest}], 模式为隔{segmentation}选{select}"
        memo = msg.format(
            username=self.username,
            object=hub,
            group_num=group_num,
            group_num_rest=group_num_rest,
            segmentation=segmentation,
            select=select
        )
        Log.objects.create(
            event=_("send down groups(group by pattern)"),
            username=self.username,
            object=hub,
            status=self.status,
            memo=memo
        )

    def communicate_post_gather_group(self, request_data, response_data, pk):
        """集控分组采集"""
        hubs = ','.join(request_data.get('hub'))
        if self.status == FAIL:
            error_hubs = ','.join(response_data.get('error_hubs', []))
            # TODO 翻译
            msg = "[{username}]采集了集控[{object}]的分组, 集控[{error_hubs}]采集失败"
            memo = msg.format(
                username=self.username,
                object=hubs,
                error_hubs=error_hubs
            )
        elif self.status == SUCCESS:
            msg = "[{username}]采集了集控[{object}]的分组"
            memo = msg.format(
                username=self.username,
                object=hubs
            )
        Log.objects.create(
            event=_("gather hub groups"),
            username=self.username,
            object=hubs,
            status=self.status,
            memo=memo
        )

    def communicate_post_gather_hub_status(self, request_data, response_data, pk):
        """采集集控状态"""
        hubs = ','.join(request_data.get('hub'))
        if self.status == FAIL:
            error_hubs = ','.join(response_data.get('error_hubs', []))
            # TODO 翻译
            msg = "[{username}]采集了集控[{object}]的状态, 集控[{error_hubs}]采集失败"
            memo = msg.format(
                username=self.username,
                object=hubs,
                error_hubs=error_hubs
            )
        elif self.status == SUCCESS:
            msg = "[{username}]采集了集控[{object}]的状态"
            memo = msg.format(
                username=self.username,
                object=hubs
            )
        Log.objects.create(
            event=_("gather hub status"),
            username=self.username,
            object=hubs,
            status=self.status,
            memo=memo
        )

    def communicate_post_load_inventory(self, request_data, response_data, pk):
        """采集集控配置"""
        hubs = ','.join(request_data.get('hub'))
        if self.status == FAIL:
            error_hubs = ','.join(response_data.get('error_hubs', []))
            # TODO 翻译
            msg = "[{username}]采集了集控[{object}]的配置, 集控[{error_hubs}]采集失败"
            memo = msg.format(
                username=self.username,
                object=hubs,
                error_hubs=error_hubs
            )
        elif self.status == SUCCESS:
            msg = "[{username}]采集了集控[{object}]的配置"
            memo = msg.format(
                username=self.username,
                object=hubs
            )
        Log.objects.create(
            event=_("gather hub configuration"),
            username=self.username,
            object=hubs,
            status=self.status,
            memo=memo
        )

    def login(self, request_data, response_data, pk):
        """用户登录"""
        # 用户登录
        username = request_data.get('username', '')
        msg = _(u"user [{username}] log in on ip [{object}]")
        memo = msg.format(
            username=username,
            object=self.ip
        )
        Log.objects.create(
            username=username,
            event=_("log in"),
            object=self.ip,
            status=self.status,
            memo=memo
        )
