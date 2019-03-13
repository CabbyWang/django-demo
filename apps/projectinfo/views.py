import re
import platform
import subprocess

from django.http import Http404
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404 as _get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from projectinfo.models import ProjectInfo
from projectinfo.serializers import ProjectInfoSerializer
from utils.mixins import ListModelMixin


def get_object_or_404(queryset, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.
    """
    try:
        return _get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except (TypeError, ValueError, ValidationError):
        raise NotFound


class ProjectInfoViewSet(ListModelMixin,
                         viewsets.GenericViewSet):
    """
    list:
        获取项目信息
    get_position:
        获取城市中心点信息
    get_version:
        获取系统版本信息
    """

    queryset = ProjectInfo.objects.all()
    serializer_class = ProjectInfoSerializer

    @action(detail=False, methods=['GET'], url_path='position')
    def get_position(self, request, *args, **kwargs):
        serializer = self.get_serializer(get_object_or_404(self.get_queryset()))
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='version')
    def get_version(self, request, *args, **kwargs):
        if platform.system() == 'Linux':
            process = subprocess.Popen('rpm -q smartlamp_core', shell=True,
                                       stdout=subprocess.PIPE)
            ret = process.stdout.readline()
            if ret:
                match_str = re.match('smartlamp_core-(.*?)debug.noarch', ret)
                version = match_str.group(1)
            return Response(status=status.HTTP_200_OK,
                            data={'version': version})
        return Response(status=status.HTTP_200_OK, data={'version': '5.0'})
