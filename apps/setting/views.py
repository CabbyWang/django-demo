import os
import subprocess

from django.conf import settings

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from setting.models import Setting, SettingType
from setting.serializers import (
    SettingTypeSerializer, SettingUpdateSerializer, SettingSerializer
)
from utils.mixins import ListModelMixin


class SettingViewSet(ListModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    设置
    list:
        获取所有设置
    update:
        修改系统配置
    backup_database:
        数据库备份
    """

    queryset = Setting.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            return SettingType.objects.all()
        return Setting.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SettingTypeSerializer
        if self.action in ('update', 'partial_update'):
            return SettingUpdateSerializer
        return SettingSerializer

    @action(methods=['POST'], detail=False, url_path='backup_database')
    def backup_database(self, request, *args, **kwargs):
        """
        备份数据库
        POST /settings/backup_database/
        """
        # TODO 可能需要换一种更好的方式来实现?
        backup_dir = settings.BACKUP_ROOT
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        cmd = 'mysqldump -uroot -psmartlamp smartlamp > {}/smartlamp.sql'.format(
            backup_dir)
        cmd_tar = 'tar zcvf {backup_dir}/smartlamp.tar.gz {backup_dir}/smartlamp.sql'.format(
            backup_dir=backup_dir)
        cmd_rm = 'rm -f {backup_dir}/smartlamp.sql'.format(
            backup_dir=backup_dir)
        try:
            subprocess.check_call(cmd, shell=True)
            subprocess.check_call(cmd_tar, shell=True)
            subprocess.check_call(cmd_rm, shell=True)
        except subprocess.CalledProcessError:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={'message': '备份失败'})
        return Response(status=status.HTTP_200_OK,
                        data={'message': '备份成功'})
