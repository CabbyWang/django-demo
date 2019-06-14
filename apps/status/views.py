import re
import platform
import subprocess
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from status.filters import LampCtrlStatusFilter
from status.models import LampCtrlStatus
from setting.models import Setting
from status.serializers import LampCtrlStatusSerializer
from utils.mixins import ListModelMixin
from equipment.models import Hub
from status.models import HubStatus
from equipment.serializers import HubDetailSerializer


class StatusViewSet(viewsets.GenericViewSet):

    """
    状态
    get_database_status:
        获取数据库状态
    """

    queryset = Hub.objects.filter_by()
    serializer_class = HubDetailSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    @action(methods=['GET'], detail=False, url_path='database')
    def get_database_status(self, request, *args, **kwargs):
        """
        获取数据库状态
        GET /status/database/
        :return
        {
            "hub_status_count": hub_status_count,
            "lamp_status_count": lamp_status_count,
            "threads_count": threads_count,
            "database_memory": mysql_memory
        }
        """
        hub_status_count = HubStatus.objects.count()
        lamp_status_count = LampCtrlStatus.objects.count()
        threads_count = 1
        mysql_memory = 0

        if platform.system() == 'Linux':
            # mysql当前连接数
            process = subprocess.Popen('mysqladmin -uroot -psmartlamp status',
                                       shell=True, stdout=subprocess.PIPE)
            ret = process.stdout.readline()
            if ret:
                match = re.search('Threads.*?(\d+).*?', ret.decode('utf-8'))
                try:
                    threads_count = match.group(1)
                except IndexError:
                    pass
            # mysql数据库占用内存
            sql = "SELECT SUM(DATA_LENGTH+INDEX_LENGTH) as total FROM information_schema.TABLES"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                mysql_memory = int(result[0]) if result else 0
        ret_data = {
            "hub_status_count": hub_status_count,
            "lamp_status_count": lamp_status_count,
            "threads_count": threads_count,
            "database_memory": mysql_memory
        }
        return Response(data=ret_data)

    @action(methods=['GET'], detail=False, url_path='threshold')
    def get_threshold(self, request, *args, **kwargs):
        """
        获取集控上报状态次数阈值和终端上报状态阈值
        GET /status/threshold/
        :return:
        {
            'hub_status_count_threshold': hub_status_count_threshold,
            'lamp_status_count_threshold': lamp_status_count_threshold
        }
        """
        hub_status = Setting.objects.filter_by(
            option='hub_status_count_threshold').first()
        lamp_status = Setting.objects.filter_by(
            option='lamp_status_count_threshold').first()
        hub_status_count_threshold = int(hub_status.value) if hub_status else 5000000
        lamp_status_count_threshold = int(lamp_status.value) if lamp_status else 5000000
        ret_data = {
            'hub_status_count_threshold': hub_status_count_threshold,
            'lamp_status_count_threshold': lamp_status_count_threshold
        }
        return Response(data=ret_data)


class LampCtrlStatusViewSet(ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """
    灯控状态
    list:
        获取单灯历史状态
    """
    queryset = LampCtrlStatus.objects.all()
    serializer_class = LampCtrlStatusSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = LampCtrlStatusFilter


class HubLogViewSet(mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    集控日志
    retrieve:
        获取集控日志
    """

    queryset = Hub.objects.filter_by()
    serializer_class = HubDetailSerializer
    permission_classes = []
    authentication_classes = []

    def retrieve(self, request, *args, **kwargs):
        hub = self.get_object()
        log_dir = Path(settings.MEDIA_ROOT) / 'logs' / hub.sn
        file_name = 'hub.log'
        # TODO 下载zip文件
        try:
            f = open(log_dir / file_name, 'rb')
        except FileNotFoundError:
            return Response(data={
                "message": "file not found",
                "detail": "file not found"
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        response = FileResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response[
            'Content-Disposition'] = 'attachment;filename="{}"'.format(
            file_name)
        return response
