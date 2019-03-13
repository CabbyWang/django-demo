from django.shortcuts import render

# Create your views here.

from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hub.models import Hub, Unit
from hub.permissions import IsOwnHubOrSuperUser
from hub.serializers import (
    HubPartialUpdateSerializer, HubDetailSerializer, UnitSerializer
)
from utils.paginator import CustomPagination
from utils.mixins import ListModelMixin
from utils.permissions import IsAdminUser
from utils.exceptions import DeleteOnlineHubError


class UnitViewSet(ListModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        获取所有管理单元
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)


class HubViewSet(ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    """
    list:
        集控列表数据
    retrieve:
        集控详情
    destroy:
        删除集控
    update:
        修改集控信息
    partial_update:
        集控重定位

    """
    pagination_class = CustomPagination
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        # 管理员拥有所有集控的权限
        if self.request.user.is_superuser:
            return Hub.objects.filter(is_deleted=False)
        user = self.request.user
        return user.hubs.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return HubDetailSerializer
        if self.action == 'partial_update':
            return HubPartialUpdateSerializer
        return HubDetailSerializer

    def get_permissions(self):
        if self.action == 'destory':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated(), IsOwnHubOrSuperUser()]

    def get_object(self):
        obj = super(HubViewSet, self).get_object()
        if self.action == 'destroy' and obj.status != 3:
            raise DeleteOnlineHubError
        return obj

    @action(methods=['POST'], detail=False, url_path='load_inventory')
    def load_inventory(self, request, *args, **kwargs):
        """采集集控配置, 同步数据库(支持采集多个集控)
        POST /hubs/load_inventory/
        {
            "targets": [hub1, hub2, ...]
        }
        """
        # TODO 采集集控配置
        # _logger.info("load inventory")
        hubs = request.data.get('targets')
        if not hubs:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE,
                            data={'code': 1, 'message': '勾选至少一个集控'})

        error_hubs = []
        for hub_sn in hubs:
            data = THHub.get_hub_config(hub_sn)
            code = data.get('code')
            ret_data = data.get('ret_data')
            if code == 101:
                # 集控脱网 告警
                record_alarm(event='集控脱网', level=3, object=hub_sn,
                             object_type='hub',
                             alert_source=hub_sn, value=1, status=3)
            if code != 0:  # if code in (1, 101, 2, 3):
                # error
                error_hubs.append(hub_sn)
            else:
                # code=0 (sync database)
                try:
                    with transaction.atomic():
                        inventory = ret_data.get('inventory')
                        # 创建或更新hub表
                        hub_inventory = inventory.get('hub')
                        hub_sn = hub_inventory.get('sn')
                        # 创建或更新lamp表
                        lamp_invertorys = inventory.get('lamps')
                        for lamp_sn, lamp_invertory in lamp_invertorys.items():
                            defaults = {'hub_sn': hub_sn}
                            defaults.update(lamp_invertory)
                            # 将不是model中字段的key过滤掉
                            defaults = dict(filter(
                                lambda x: x[0] in LampCtrl.model_fields(),
                                defaults.items()))
                            LampCtrl.objects.update_or_create(sn=lamp_sn,
                                                              hub_sn=hub_sn,
                                                              defaults=defaults)
                except Exception as ex:
                    _logger.error(str(ex))
                    error_hubs.append(hub_sn)

        if error_hubs:
            return Response(status=status.HTTP_408_REQUEST_TIMEOUT,
                            data={'code': 2, 'message': '部分集控采集失败',
                                  'error_hubs': error_hubs})
        # success
        return Response(status=status.HTTP_200_OK,
                        data={'code': 0, 'message': '采集配置成功'})

    @action(methods=['GET'], detail=True, url_path='status')
    def get_status(self, request, *args, **kwargs):
        """
        采集集控的状态(开关、电压电流功率等)，直接返回给前端，不入库
        (不支持同时采集多个集控的状态)
        """
        hub_sn = kwargs.get('pk')

        data = THHub.get_hub_status(hub_sn)
        code = data.get('code')
        if code == 101:
            # 集控脱网 告警
            record_alarm(event='集控脱网', level=3, object=hub_sn,
                         object_type='hub',
                         alert_source=hub_sn, value=1, status=3)
        if code != 0:  # if code in (1, 101, 2, 3):
            # error
            return Response(status=status.HTTP_408_REQUEST_TIMEOUT,
                            data={'code': 2, 'message': data.get('message')})

        # success
        ret_data = data.get('ret_data')
        lamp_status = ret_data.get('hub_status')
        return Response(status=status.HTTP_200_OK, data=lamp_status)

    @action(methods=['PUT'], detail=False, url_path='cycle_time')
    def change_cycle_time(self, request, *args, **kwargs):
        """
        修改集控采集周期
        PUT /hubs/cycle_time/
        {
            "cycle_time": 2*3600,
            "hubs": ['hub_sn1', 'hub_sn2', 'hub_sn3']  # 为空时， 修改全部集控
        }
        """

        all_hub_sns = [instance.sn for instance in Hub.objects.all()]

        data = request.data
        cycle_time = data.get('cycle_time')
        hub_sns = data.get('hubs') or all_hub_sns

        try:
            with transaction.atomic():
                # 修改数据库
                setting = Setting.objects.get(option='cycle_time')
                setting.value = cycle_time
                msg_socket = None
                try:
                    msg_socket = MessageSocket(*SERVER_ADDR)
                    sender = 'cmd-' + str(uuid.uuid1())
                    verify = msg_socket.verify(sender)
                except socket.error:
                    raise SocketException()
                if not verify:
                    raise SocketException(error_code=1)
                body = {
                    "action": "change_cycle_time",
                    "cycle_time": cycle_time
                }
                ret_data = {}
                for hub_sn in hub_sns:
                    msg_socket.send_single_message(receiver=hub_sn,
                                                   body=json.dumps(body),
                                                   sender=sender)
                    recv = msg_socket.receive_data()
                    recv_code = recv.get('code')
                    if recv_code == 101:
                        # 集控脱网
                        error_data = {
                            hub_sn: {'code': 101, 'message': '连接该集控超时'}}
                    elif recv_code != 0:
                        error_data = {hub_sn: {'code': recv_code,
                                               'message': recv.get('message')}}
                if error_data:
                    raise SocketException(error_code=2, error_data=error_data)
        except SocketException as ex:
            error_code, error_message, error_data = ex.error_code, ex.error_message, ex.error_data
            if error_code in (0, 1):
                return Response(status=status.HTTP_408_REQUEST_TIMEOUT,
                                data={'code': 2, 'message': error_message})
            elif error_code == 2:
                # 集控脱网
                for hub_sn, v in error_data.items():
                    if v.get('code') != 101:
                        continue
                    # 集控脱网
                    record_alarm(event='集控脱网', level=3, object=hub_sn,
                                 object_type='hub',
                                 alert_source=hub_sn, value=1, status=3)
                return Response(status=status.HTTP_408_REQUEST_TIMEOUT,
                                data={'code': 2, 'message': '有部分集控连接失败',
                                      'data': error_data})
        else:
            return Response(status=status.HTTP_200_OK)
        finally:
            if msg_socket: del msg_socket

    @action(methods=['POST'], detail=True, url_path='download_log')
    def download_hub_log(self, request, *args, **kwargs):
        """
        下载集控日志
        POST /hubs/{sn}/download_log/
        """
        pass
