from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

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
    get_light_rate:
        灯控投运率
        控灯
        采集单灯状态
    """
    permission_classes = [IsAuthenticated, IsOwnHubOrSuperUser]
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = LampCtrlFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return LampCtrl.objects.filter_by()
        queryset = LampCtrl.objects.none()
        for hub in self.request.user.hubs.all():
            queryset |= hub.hub_lampctrl.all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return LampCtrlPartialUpdateSerializer
        return LampCtrlSerializer

    @action(methods=['GET'], detail=False, url_path='putin-rate')
    def get_light_rate(self, request, *args, **kwargs):
        """灯控投运率（灯控 正常/故障/脱网 占比）
        GET /lampctrls/putin-rate/
        :return:
        {
            "name": "灯控投运率",
            "total": 2455,
            "normal": 5,
            "trouble": 11,
            "offline": 2439,
            "putin_rate": 95 %
        }
        """
        # TODO 使用serializer
        # TODO 是否需要根据集控权限不同来显示不同的投运率
        total = LampCtrl.objects.filter_by().count()
        normal = LampCtrl.objects.filter_by(status=1).count()
        trouble = LampCtrl.objects.filter_by(status=2).count()
        offline = LampCtrl.objects.filter_by(status=3).count()
        putin_rate = '{:.0%}'.format(float(normal) / float(total) if total else 0)
        return Response(dict(
            name="灯控投运率",
            total=total,
            normal=normal,
            trouble=trouble,
            offline=offline,
            putin_rate=putin_rate
        ))


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
