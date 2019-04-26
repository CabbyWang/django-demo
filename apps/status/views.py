import platform
import re
import subprocess

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from lamp.models import LampCtrlStatus
from setting.models import Setting
from utils.mixins import ListModelMixin
from hub.models import Hub, HubStatus
from hub.serializers import HubDetailSerializer


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
                match_str = re.search('Threads.*?(\d+).*?', ret)
                threads_count = match_str.group(1)
            # mysql数据库占用内存
            process2 = subprocess.Popen("ps -e -o 'args,rsz' | grep mysqld",
                                        shell=True, stdout=subprocess.PIPE)
            ret2 = ' '.join(process2.stdout.readlines())
            if ret2:
                match_str2 = re.search(
                    '/usr/sbin/mysqld --basedir=.*?(\d+).*?', ret2)
                mysql_memory = match_str2.group(1)
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
