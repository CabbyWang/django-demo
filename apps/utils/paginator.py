#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/12
"""
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination, _positive_int
from rest_framework.response import Response

from setting.models import Setting


class CustomPagination(PageNumberPagination):
    """
    自定义分页类， 让分页可以配置
    """

    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        """
        分页返回结果
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('page_size', self.page_size),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_page_size(self, request):
        """
        配置每页显示行数
        page_size使用顺序
        1. 查询参数中指定page_size
        2. 配置中的page_size
        3. 默认
        """
        try:
            self.page_size = _positive_int(
                request.query_params[self.page_size_query_param],
                strict=True,
                cutoff=self.max_page_size
            )
        except (KeyError, ValueError):
            # 使用配置
            # TODO 每次都需要去查询数据库， 是否可以通过刷新django配置，
            #  或信号的方式来解决?
            try:
                setting = Setting.objects.get(option='pagination')
                self.page_size = int(setting.value)
            except (Setting.DoesNotExist, ValueError):
                self.page_size = 30

        return self.page_size
