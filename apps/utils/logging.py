#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/18
"""


# TODO 研究一下xadmin的log entries实现，能否改进logging模块


class SqlLog(object):

    pass


def log_before(func):
    """
    记录操作日志(在函数执行之前执行)
    """
    def wrapper(*args, **kwargs):
        request = args[1]
        kwargs.update(dict(request=request))
        getattr(SqlLog, func.__name__)(*args, **kwargs)
        return


def log_after(func):
    """
    记录操作日志(在函数执行之后执行)
    """
    pass
