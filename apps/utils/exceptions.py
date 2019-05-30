#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/6
"""
from django.http import Http404
from django.core.exceptions import PermissionDenied

from rest_framework import exceptions
from rest_framework import status
from rest_framework.views import set_rollback
from rest_framework.response import Response

from django.utils.translation import ugettext_lazy as _


class DeleteOnlineHubError(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("can't delete the hub online")
    default_code = 'invalid'


class ConnectNSError(exceptions.APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = _("can't connect network service")
    default_code = 'server error'


class AuthenticateNSError(exceptions.APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = _("authenticate failed when connect network service")
    default_code = 'authentication error'


class ConnectHubTimeOut(exceptions.APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = _("connect hub timeout")
    default_code = 'connect error'


class DownLoadLogTimeOut(exceptions.APIException):
    status_code = status.HTTP_200_OK
    default_detail = _("connect hub timeout")
    default_code = 'connect error'


class HubError(exceptions.APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = _("hub unknown error")
    default_code = 'hub error'


class DownLoadLogError(exceptions.APIException):
    status_code = status.HTTP_200_OK
    default_detail = _("hub unknown error")
    default_code = 'hub error'


class ObjectHasExisted(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("object has been existed")
    default_code = 'object exist error'


class InvalidInputError(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid input.')
    default_code = 'invalid'


class DMLError(exceptions.APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = _('Server Error')
    default_code = 'server error'


class UnknownError(exceptions.APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = _('Server Error')
    default_code = 'server error'


def custom_exception_handler(exc, context):
    """
        Returns the response that should be used for any given exception.

        By default we handle the REST framework `APIException`, and also
        Django's built-in `Http404` and `PermissionDenied` exceptions.

        Any unhandled exceptions may return `None`, which will cause a 500 error
        to be raised.
        """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        # if isinstance(exc.detail, (list, dict)):
        #     data = exc.detail
        # else:
        #     data = {'detail': exc.detail}
        data = {'message': ''}
        if isinstance(exc.detail, list):
            data['detail'] = exc.detail
            data['message'] = exc.detail[0]
        elif isinstance(exc.detail, dict):
            data['detail'] = exc.detail
            key = list(exc.detail.keys())[0]
            data['message'] = exc.detail[key][0]
        else:
            data['message'] = data['detail'] = exc.detail

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None
