import os

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from notify.filters import LogFilter, AlertFilter
from .models import Log, Alert, AlertAudio
from .serializers import LogSerializer, AlertSerializer, \
    AlertAudioSerializer, AlertUpdateSerializer
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
    serializer_class = LogSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = LogFilter

    def get_queryset(self):
        # 只有admin可以看到admin日志
        if self.request.user.username == 'admin':
            return Log.objects.filter_by()
        elif self.request.user.is_superuser:
            return Log.objects.filter_by().exclude(username='admin')
        else:
            return Log.objects.filter_by(username=self.request.user.username)


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
    queryset = Alert.objects.filter_by()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = AlertFilter

    def get_serializer_class(self):
        if self.action in ('partial_update', 'update'):
            return AlertUpdateSerializer
        else:
            return AlertSerializer


class AlertAudioViewSet(mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    告警语音
    destroy:
        删除告警语音(通过alert_id删除)
    """
    queryset = AlertAudio.objects.filter_by()
    serializer_class = AlertAudioSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = 'alert_id'

    def perform_destroy(self, instance):
        instance.times += 1
        instance.save()
