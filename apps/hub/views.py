import uuid
from math import sqrt

from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hub.filters import HubFilter
from hub.models import Hub, Unit
from hub.permissions import IsOwnHubOrSuperUser
from hub.serializers import (
    HubPartialUpdateSerializer, HubDetailSerializer, UnitSerializer,
    LoadInventorySerializer)
from lamp.models import LampCtrl
from utils.alert import record_alarm
from utils.msg_socket import MessageSocket
from utils.paginator import CustomPagination
from utils.mixins import ListModelMixin
from utils.permissions import IsAdminUser
from utils.exceptions import DeleteOnlineHubError, ConnectHubTimeOut, HubError


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
    layout:
        对集控下的指定路灯进行划线排布(单边分布/奇偶分布)
    drop_layout:
        取消集控下路灯的布放
    get_layout_lamps:
        获取路灯布放的情况
    load_inventory:
        采集集控配置
    """
    pagination_class = CustomPagination
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = HubFilter

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
        if self.action == 'load_inventory':
            return LoadInventorySerializer
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

    @action(methods=['POST'], detail=True, url_path='layout')
    def layout(self, request, *args, **kwargs):
        """
        对指定集控下的路灯进行划线排布(支持单边分布和奇偶分布)
        POST /hubs/{sn}/layout/
        单边:
            {
                # "hub_sn": "201803210014",
                "odd-even": False,
                "points": [[116.203048, 39.801835],  [116.226478, 39.82416],  [116.256912, 39.873809]],
                "sequence": [1, 2, 3, 4, 5, 7]
            }
        奇偶:
            {
                # "hub_sn": "201803210014",
                "odd-even": True,
                "points": {
                    "odd": [],
                    "even": []
                },
                "sequence": [1, 2, 3, 4, 5, 7]
            }
        """
        request_data = request.data
        hub_sn = kwargs.get('pk')
        points = request_data.get('points')
        is_odd_even = request_data.get('odd-even')
        sequence = request_data.get('sequence')

        if not is_odd_even:
            # 单边分布
            ret_points = self.average_endpoints(points, len(sequence))
        else:
            # 奇偶分布
            odd_points = points.get('odd')
            even_points = points.get('even')
            odd_sequence = sequence[::2]
            even_sequence = sequence[1::2]
            odd_ret_points = self.average_endpoints(odd_points,
                                                    len(odd_sequence))
            even_ret_points = self.average_endpoints(even_points,
                                                     len(even_sequence))
            ret_points = odd_ret_points + even_ret_points

        # 写入数据库
        for i, point in enumerate(ret_points):
            longitude, latitude = point
            sequence_num = sequence[i]
            hub = Hub.objects.get(sn=hub_sn)
            LampCtrl.objects.filter(hub=hub,
                                    sequence=sequence_num).update(
                on_map=True,
                longitude=longitude,
                latitude=latitude
            )

        return Response(status=status.HTTP_200_OK,
                        data={'detail': '路灯布放成功'})

    @action(methods=['POST'], detail=True, url_path='drop-layout')
    def drop_layout(self, request, *args, **kwargs):
        """
        取消指定集控下路灯的布放
        POST /hubs/{sn}/drop-layout/
        """
        hub_sn = kwargs.get('pk')
        hub = Hub.objects.get(sn=hub_sn)
        lon = hub.longitude
        lat = hub.latitude
        lamps_on_map = LampCtrl.objects.filter(hub=hub, on_map=True)

        for lamp in lamps_on_map:
            LampCtrl.objects.filter_by(sn=lamp).update(
                on_map=False, longitude=lon, latitude=lat)

        return Response(data={'detail': '布放撤销成功'})

    @action(methods=['GET'], detail=True, url_path='layout-lamps')
    def get_layout_lamps(self, request, *args, **kwargs):
        """
        获取路灯布放的情况
        GET /hubs/{sn}/layout-lamps/
        """
        hub_sn = kwargs.get('pk')
        hub = Hub.objects.get(sn=hub_sn)
        hub.hub_lampctrl.filter_by()
        result = {
            "on_map": hub.hub_lampctrl.filter_by(hub=hub, on_map=True).values_list('sequence', flat=True),
            "not_on_map": hub.hub_lampctrl.filter_by(hub=hub, on_map=False).values_list('sequence', flat=True)
        }
        return Response(data=result)

    @action(methods=['POST'], detail=False, url_path='load-inventory')
    def load_inventory(self, request, *args, **kwargs):
        """采集集控配置, 同步数据库(支持采集多个集控)
        POST /hubs/load_inventory/
        {
            "hub": [hub1, hub2, ...]
        }
        """
        # TODO 采集集控配置
        # _logger.info("load inventory")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.data.get('hub')

        error_hubs = []
        for hub_sn in hubs:
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "load_inventory",
                    "type": "cmd"
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
                    raise ConnectHubTimeOut()
                if code != 0:
                    raise HubError
                inventory = recv.get('inventory')
                hub_inventory = inventory.get('hub', {}) or {}
                lamp_inventory = inventory.get('lamps', {}) or {}
                # TODO 容错处理？ 非model中的字段需要过滤掉
                try:
                    with transaction.atomic():
                        # 更新hub表
                        Hub.objects.update(**hub_inventory)
                        # 更新lamp表
                        for lamp_sn, item in lamp_inventory.items():
                            lamp = LampCtrl.objects.filter_by(sn=lamp_sn).first()
                            if lamp and lamp.on_map:
                                item.pop('longitude', None)
                                item.pop('latitude', None)
                            LampCtrl.objects.filter(sn=lamp_sn).update(**item)
                            # 删除数据库中存在 实际不存在的灯控
                            LampCtrl.objects.exclude(sn__in=list(lamp_inventory.keys())).delete()
                except Exception as ex:
                    # _logger.error(str(ex))
                    error_hubs.append(hub_sn)

        if error_hubs:
            return Response(status=status.HTTP_408_REQUEST_TIMEOUT,
                            data={'detail': '集控[{}]采集失败'.format(','.join(error_hubs))})

        return Response(data={'detail': '采集配置成功'})

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
                            data={'detail': data.get('message')})

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
                            hub_sn: {'detail': '连接该集控超时'}}
                    elif recv_code != 0:
                        error_data = {hub_sn: {'detail': recv.get('message')}}
                if error_data:
                    raise SocketException(error_code=2, error_data=error_data)
        except SocketException as ex:
            error_code, error_message, error_data = ex.error_code, ex.error_message, ex.error_data
            if error_code in (0, 1):
                return Response(status=status.HTTP_408_REQUEST_TIMEOUT,
                                data={'detail': error_message})
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
                                data={'detail': '有部分集控连接失败',
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

    @staticmethod
    def average_endpoints(endpoints, divide_point_num):
        """
        将divide_point_num个点均匀分布在endpoints连成的线段上
        :param endpoints: 顶点列表
        :param divide_point_num: 使用divide_point_num个点来均分(包含起点和终点)
        :return: 返回均分过后 各个点的坐标的列表
        """
        # 妈的 想复杂了
        if divide_point_num == 1:
            # 只有一个点, 直接取起点
            return [endpoints[0]]
        seg_num = divide_point_num - 1  # 分成多少段
        distance_list = []
        last_xy = ()  # 上一个点
        ret_points = []

        # 求总距离
        sum_distance = 0  # 总距离
        for i, (x, y) in enumerate(endpoints):
            if i == 0:
                last_xy = (x, y)
                continue
            x0, y0 = last_xy
            dst = sqrt(pow((x - x0), 2) + pow((y - y0), 2))
            distance_list.append(dst)  # 记录每条线段的长度
            sum_distance += dst  # 计算总长度
            last_xy = (x, y)
        # 求每两个点之间的距离
        seg = sum_distance / seg_num  # 每条线段的长度
        # 遍历序列号 求各个终端的坐标
        last_xy = endpoints.pop(0)
        next_xy = endpoints[0]
        distance = distance_list.pop(0)
        distance_from_start = 0
        temp = 0  # 已经计算过的线段总长度
        for i in range(divide_point_num):
            # (索引, 序列号)
            if i == 0:
                # 第一个点就是起点
                point = last_xy
                ret_points.append(point)
                continue
            # 距离起点的距离
            distance_from_start = seg * i
            # 遇到线段转角
            if i != seg_num - 1 and distance_from_start - temp > distance:  # 解决计算误差进入语句的问题
                temp += distance
                last_xy = endpoints.pop(0)
                next_xy = endpoints[0]
                distance = distance_list.pop(0)
            # 上一个端点 last_xy
            x1, y1 = last_xy
            # 下一个端点 next_xy
            x2, y2 = next_xy
            # 到上一个顶点的距离
            d = distance_from_start - temp
            # 线段长度 distance
            # 等比公式 (x - x1) / (x2 - x1) = d / distance
            x = (x2 - x1) * d / distance + x1
            y = (y2 - y1) * d / distance + y1
            ret_points.append((x, y))
        return ret_points

