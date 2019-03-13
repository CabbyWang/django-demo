#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/12
"""
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from setting.models import Setting


class CustomPagination(PageNumberPagination):
    """
    自定义分页类， 让分页可以配置
    """

    # page_size = 30
    # page_size_query_param = 'page_size'
    # max_page_size = 10000

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
        """
        # TODO 每次都需要去查询数据库， 是否可以通过刷新django配置， 或信号的方式来解决?
        try:
            setting = Setting.objects.get(option='pagination')
            page_size = int(setting.value)
        except (Setting.DoesNotExist, ValueError):
            page_size = 30
        self.page_size = page_size
        return page_size
