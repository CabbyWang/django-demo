import uuid

from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from hub.models import Hub
from lamp.filters import LampCtrlFilter, LampCtrlStatusFilter
from lamp.models import LampCtrl, LampCtrlStatus
from lamp.serializers import (
    LampCtrlStatusSerializer, LampCtrlSerializer,
    LampCtrlPartialUpdateSerializer,
    GatherLampCtrlSerializer, ControlLampSerializer)
from lamp.permissions import IsOwnHubOrSuperUser
from utils.alert import record_alarm
from utils.exceptions import ConnectHubTimeOut, HubError

from utils.mixins import ListModelMixin
from utils.msg_socket import MessageSocket


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
    get_lamp_ctrl_status:
        采集灯控状态
    control_lamp:
        控灯
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
        if self.action == 'get_lamp_ctrl_status':
            return GatherLampCtrlSerializer
        if self.action == 'control_lamp':
            return ControlLampSerializer
        return LampCtrlSerializer

    @action(methods=['GET'], detail=False, url_path='putin-rate')
    def get_putin_rate(self, request, *args, **kwargs):
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

    @action(methods=['POST'], detail=False, url_path='get-status')
    def get_lamp_ctrl_status(self, request, *args, **kwargs):
        """
        采集灯控状态(支持多灯采集)
        POST /lampctrls/get-status/
        {
            "lampctrl": ["001", "002"]
        }
        """
        # TODO 灯控根据集控分类
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lampctrls = serializer.data.get('lampctrl')

        ret_data = []

        for hub_sn, lampctrl_sns in lampctrls.items():
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "get_lamp_status",
                    "type": "cmd",
                    "lamp_sn": lampctrl_sns
                }
                msg_socket.send_single_message(receiver=hub_sn, body=body,
                                               sender=sender)
                recv = msg_socket.receive_data()
                code = recv.get('code')
                if code == 101:
                    # 集控脱网, 告警
                    record_alarm(
                        event="集控脱网", object_type='hub', alert_source=hub_sn,
                        object=hub_sn, level=3, status=3
                    )
                    raise ConnectHubTimeOut('connect hub [{}] time out'.format(hub_sn))
                if code != 0:
                    raise HubError("hub [{}] unknown error".format(hub_sn))
                lamp_status = recv.get('status')
                for lampctrl_sn, status in lamp_status.items():
                    route1, route2 = status.get('brightness', [0, 0])
                    electric_energy = status.get("electric_energy", {})
                    routes = dict(route1=route1, route2=route2)
                    ret_data.append({'hub_sn': hub_sn, **routes, **electric_energy})
        return Response(data=ret_data)

    @action(methods=['POST'], detail=False, url_path='control')
    def control_lamp(self, request, *args, **kwargs):
        """
        控灯
        {
            "lampctrl": ["001", "002", "003"],
            "action": "0,80"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lampctrls = serializer.data['lampctrl']
        action = serializer.data['action']
        switch_status = 0 if action == "0,0" else 1

        for hub_sn, lampctrl_sns in lampctrls.items():
            # 是否是控制所有灯控
            hub = Hub.object.get(sn=hub_sn)
            is_all = all(i in lampctrl_sns for i in LampCtrl.objects.filter(hub=hub).values_list('sn', flat=True))
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "lighten",
                    "type": "cmd",
                    "detail": {
                        "hub_sn": hub_sn,
                        "lamp_sn": lampctrl_sns,
                        "action": action,
                        "all": is_all
                    }
                }
                msg_socket.send_single_message(receiver=hub_sn, body=body,
                                               sender=sender)
                recv = msg_socket.receive_data()
                code = recv.get('code')
                if code == 101:
                    # 集控脱网, 告警
                    record_alarm(
                        event="集控脱网", object_type='hub', alert_source=hub_sn,
                        object=hub_sn, level=3, status=3
                    )
                    raise ConnectHubTimeOut('connect hub [{}] time out'.format(hub_sn))
                if code != 0:
                    raise HubError("hub [{}] unknown error".format(hub_sn))
                if code == 0:
                    # 控灯成功 更新灯具状态
                    if is_all:
                        LampCtrl.objects.filter(hub=hub).update(switch_status=switch_status)
                    else:
                        LampCtrl.objects.filter(sn__in=lampctrl_sns).update(switch_status=switch_status)
        return Response(data={'detail': 'control lamps success'})


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
