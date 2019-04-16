#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/6
"""
from rest_framework import status
from rest_framework.exceptions import APIException

from django.utils.translation import ugettext_lazy as _


class DeleteOnlineHubError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("can't delete the hub online")
    default_code = 'invalid'


class ConnectNSError(APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = _("can't connect network service")
    default_code = 'server error'


class AuthenticateNSError(APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = _("authenticate failed when connect network service")
    default_code = 'authentication error'
