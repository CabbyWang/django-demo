import re
import platform
import subprocess

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from projectinfo.models import ProjectInfo
from projectinfo.serializers import ProjectInfoSerializer
from utils.mixins import ListModelMixin
from apps import __version__


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

    serializer_class = ProjectInfoSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        if self.action == 'get_position':
            # 取第一条记录展示
            return ProjectInfo.objects.filter_by()[:1]
        return ProjectInfo.objects.filter_by()

    @action(detail=False, methods=['GET'], url_path='position')
    def get_position(self, request, *args, **kwargs):
        a = self.get_queryset()
        serializer = self.get_serializer(get_object_or_404(self.get_queryset()))
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='version')
    def get_version(self, request, *args, **kwargs):
        project = ProjectInfo.objects.first()
        name = project.name if project else ""
        city = project.city if project else ""
        # version = '5.0'
        # if platform.system() == 'Linux':
        #     process = subprocess.Popen('rpm -q smartlamp_core', shell=True,
        #                                stdout=subprocess.PIPE)
        #     ret = process.stdout.readline()
        #     if ret:
        #         match_str = re.match('smartlamp_core-(.*?)debug.noarch', ret)
        #         version = match_str.group(1)
        return Response(dict(
            version=__version__, name=name, city=city
        ))
