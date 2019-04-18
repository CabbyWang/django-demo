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


class ConnectHubTimeOut(APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = _("connect hub timeout")
    default_code = 'connect error'


class HubError(APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = _("hub unknown error")
    default_code = 'hub error'


class ObjectHasExisted(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("object has been existed")
    default_code = 'object exist error'


class InvalidInputError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid input.')
    default_code = 'invalid'
