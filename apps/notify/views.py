from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Log, Alert, AlertAudio
from .serializers import LogSerializers, AlertSerializers, \
    AlertAudioSerializers, AlertUpdateSerializers
from utils.mixins import ListModelMixin


class LogViewSet(ListModelMixin,
                 mixins.CreateModelMixin,
                 viewsets.GenericViewSet):
    """
    日志
    list:
        获取所有日志信息
    create:
        创建日志
    """
    queryset = Log.objects.all()
    serializer_class = LogSerializers
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)


class AlertViewSet(ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    """
    告警
    list:
        获取所有告警信息
    retrieve:
        获取单个告警信息
    create:
        创建告警
    partial_update:
        解除告警/撤销解除
    """
    queryset = Alert.objects.all()
    # serializer_class = AlertSerializers
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        # return AlertSerializers
        if self.action in ('partial_update', 'update'):
            return AlertUpdateSerializers
        else:
            return AlertSerializers


class AlertAudioViewSet(mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    告警语音
    destroy:
        删除告警语音(通过alert_id删除)
    """
    queryset = AlertAudio.objects.all()
    serializer_class = AlertAudioSerializers
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = 'alert_id'

    def perform_destroy(self, instance):
        # TODO times + 1
        # TODO times==2时，删除告警语音文件
        instance.delete()
