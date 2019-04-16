from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from lamp.filters import LampCtrlFilter, LampCtrlStatusFilter
from lamp.models import LampCtrl, LampCtrlStatus
from lamp.serializers import (
    LampCtrlStatusSerializer, LampCtrlSerializer,
    LampCtrlPartialUpdateSerializer
)
from lamp.permissions import IsOwnHubOrSuperUser

from utils.mixins import ListModelMixin


class LampCtrlViewSet(ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    """
    灯控
    list:
        获取所有灯控信息
    retrieve:
        获取单个灯控详情
    update:
        修改灯控信息
    partial_update:
        修改灯控地址
        控灯
        采集单灯状态
    """
    permission_classes = [IsAuthenticated, IsOwnHubOrSuperUser]
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = LampCtrlFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return LampCtrl.objects.filter(is_deleted=False)
        queryset = LampCtrl.objects.none()
        for hub in self.request.user.hubs.all():
            queryset |= hub.hub_lampctrl.all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return LampCtrlPartialUpdateSerializer
        return LampCtrlSerializer


class LampCtrlStatusViewSet(ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """
    灯控状态
    """
    queryset = LampCtrlStatus.objects.all()
    serializer_class = LampCtrlStatusSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend,)
    filter_class = LampCtrlStatusFilter
