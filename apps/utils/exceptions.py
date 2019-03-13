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
