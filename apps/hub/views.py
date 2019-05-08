import uuid
from collections import defaultdict
from math import sqrt

from django.conf import settings
from django.db import transaction
from django.http import StreamingHttpResponse
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
    LoadInventorySerializer, ControlAllSerializer, PatternGroupSerializer,
    CustomGroupingSerializer, UpdateGroupSerializer, GatherGroupSerializer,
    SendDownPolicySetSerializer, RecyclePolicySetSeriailzer)
from lamp.models import LampCtrl, LampCtrlGroup
from policy.models import PolicySetSendDown, PolicySet, Policy
from utils.alert import record_alarm
from utils.msg_socket import MessageSocket
from utils.paginator import CustomPagination
from utils.mixins import ListModelMixin
from utils.permissions import IsAdminUser
from utils.exceptions import DeleteOnlineHubError, ConnectHubTimeOut, HubError, \
    InvalidInputError, DMLError


class UnitViewSet(ListModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        获取所有管理单元
    """
    queryset = Unit.objects.filter_by()
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
    get_putin_rate:
        集控投运率
    layout:
        对集控下的指定路灯进行划线排布(单边分布/奇偶分布)
    drop_layout:
        取消集控下路灯的布放
    get_layout_lamps:
        获取路灯布放的情况
    get_custom_groups:
        获取集控下的自定义分组
    get_default_groups:
        获取集控下的默认分组
    load_inventory:
        采集集控配置
    gather_hub_status:
        采集集控状态
    gather_group:
        分组采集
    pattern_grouping:
        下发分组(按模式分组)
    custom_grouping:
        下发分组(自定义分组)
    recycle_group:
        回收集控下的所有分组
    send_down_policyset:
        下发策略集
    gather_policyset:
        策略集采集
    recycle_policyset:
        回收策略集
    control_all:
        全开全关（控制集控下所有灯控）
    download_hub_log:
        下载集控日志
    """
    pagination_class = CustomPagination
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = HubFilter

    def get_queryset(self):
        # 管理员拥有所有集控的权限
        if self.request.user.is_superuser:
            return Hub.objects.filter_by()
        user = self.request.user
        return user.hubs.filter_by()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return HubDetailSerializer
        if self.action == 'partial_update':
            return HubPartialUpdateSerializer
        if self.action == 'load_inventory':
            return LoadInventorySerializer
        if self.action == 'control_all':
            return ControlAllSerializer
        if self.action == 'pattern_grouping':
            return PatternGroupSerializer
        if self.action == 'custom_grouping':
            return CustomGroupingSerializer
        if self.action == 'update_group':
            return UpdateGroupSerializer
        if self.action == 'gather_policyset':
            return GatherGroupSerializer
        if self.action == 'send_down_policyset':
            return SendDownPolicySetSerializer
        if self.action == 'recycle_policyset':
            return RecyclePolicySetSeriailzer
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

    @action(methods=['GET'], detail=False, url_path='putin-rate')
    def get_putin_rate(self, request, *args, **kwargs):
        """集控投运率（集控 正常/故障/脱网 占比）
        GET /hubs/putin-rate/
        :return:
        {
            "name": "集控投运率",
            "total": 2455,
            "normal": 5,
            "trouble": 11,
            "offline": 2439,
            "putin_rate": 95 %
        }
        """
        # TODO 使用serializer
        # TODO 是否需要根据集控权限不同来显示不同的投运率
        total = Hub.objects.filter_by().count()
        normal = Hub.objects.filter_by(status=1).count()
        trouble = Hub.objects.filter_by(status=2).count()
        offline = Hub.objects.filter_by(status=3).count()
        putin_rate = '{:.0%}'.format(
            float(normal) / float(total) if total else 0)
        return Response(dict(
            name="集控投运率",
            total=total,
            normal=normal,
            trouble=trouble,
            offline=offline,
            putin_rate=putin_rate
        ))

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
            LampCtrl.objects.filter_by(hub=hub,
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
        lamps_on_map = LampCtrl.objects.filter_by(hub=hub, on_map=True)

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

    @action(methods=['GET'], detail=True, url_path='custom-groups')
    def get_custom_groups(self, request, *args, **kwargs):
        """获取集控下的自定义分组
        GET /hubs/{sn}/custom-groups/
        """
        hub = self.get_object()
        ret_data = []
        group_nums = set(hub.hub_group.filter_by(is_default=False).values_list('group_num', flat=True))
        for group_num in group_nums:
            ins = PolicySetSendDown.objects.filter_by(hub=hub, group_num=group_num).first()
            working_policyset = ins.policyset.name if ins else '默认策略'
            group = LampCtrlGroup.objects.filter_by(hub=hub,
                                                    group_num=group_num).first()
            ret_data.append(dict(
                group_num=group_num,
                # hub=hub.sn,
                is_default=False,
                working_policyset=working_policyset,
                memo=group and group.memo or ''
            ))
        # 未分组的灯控 返回时归到0分组
        lamp_in_group = hub.hub_group.values_list('lampctrl', flat=True)
        if LampCtrl.objects.filter_by(hub=hub).exclude(sn__in=lamp_in_group):
            pass
        return Response(data=ret_data)

    @action(methods=['GET'], detail=True, url_path='default-groups')
    def get_default_groups(self, request, *args, **kwargs):
        """获取集控下的默认分组
        GET /hubs/{sn}/default-groups/
        """
        hub = self.get_object()
        ret_data = []
        group_nums = set(
            hub.hub_group.filter_by(is_default=True).values_list('group_num',
                                                                 flat=True))
        for group_num in group_nums:
            ins = PolicySetSendDown.objects.filter_by(hub=hub,
                                                      group_num=group_num).first()
            working_policyset = ins.policyset.name if ins else '默认策略'
            group = LampCtrlGroup.objects.filter_by(hub=hub, group_num=group_num).first()
            ret_data.append(dict(
                group_num=group_num,
                hub=hub.sn,
                is_default=True,
                working_policyset=working_policyset,
                memo=group and group.memo or ''
            ))
        return Response(data=ret_data)

    @staticmethod
    def after_load_inventory(instance, inventory):
        """采集集控配置后 数据库操作"""
        # TODO 采集配置和注册时的操作相似， 是否需要合并?
        hub = instance
        hub_inventory = inventory.get('hub', {}) or {}
        lamp_inventory = inventory.get('lamps', {}) or {}
        # TODO 容错处理？ 非model中的字段需要过滤掉
        # 更新hub表
        hub_inventory = list(filter(lambda x: x in Hub.fields(), hub_inventory))
        Hub.objects.filter_by(sn=hub.sn).update_or_create(**hub_inventory)
        # 更新lamp表
        for lamp_sn, item in lamp_inventory.items():
            lamp = LampCtrl.objects.filter_by(sn=lamp_sn).first()
            if lamp and lamp.on_map:
                item.pop('longitude', None)
                item.pop('latitude', None)
            LampCtrl.objects.filter_by(sn=lamp_sn).update(**item)
            # 删除数据库中存在 实际不存在的灯控
            LampCtrl.objects.exclude(
                sn__in=list(lamp_inventory.keys())).delete()

    @action(methods=['POST'], detail=False, url_path='load-inventory')
    def load_inventory(self, request, *args, **kwargs):
        """采集集控配置, 同步数据库(支持采集多个集控)
        POST /hubs/load-inventory/
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
            hub = Hub.objects.get(sn=hub_sn)
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
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
                    event="集控脱网", object_type='hub', alert_source=hub,
                    object=hub.sn, level=3, status=3
                )
                raise ConnectHubTimeOut()
            if code != 0:
                raise HubError
            try:
                with transaction.atomic():
                    self.after_load_inventory(
                        instance=hub,
                        inventory=recv.get('inventory')
                    )
            except Exception as ex:
                raise DMLError(str(ex))

        if error_hubs:
            return Response(status=status.HTTP_408_REQUEST_TIMEOUT,
                            data={'detail': '集控[{}]采集失败'.format(','.join(error_hubs))})

        return Response(data={'detail': '采集配置成功'})

    @action(methods=['POST'], detail=True, url_path='get-status')
    def gather_hub_status(self, request, *args, **kwargs):
        """
        采集集控的状态(开关、电压电流功率等)，直接返回给前端，不入库
        (不支持同时采集多个集控的状态)
        POST /hubs/{sn}/get-status/
        """
        hub = self.get_object()
        sender = 'cmd-{}'.format(uuid.uuid1())
        with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
            body = {
                "action": "get_hub_status",
                "type": "cmd",
                "hub_sn": hub.sn
            }
            msg_socket.send_single_message(receiver=hub.sn, body=body,
                                           sender=sender)
            recv = msg_socket.receive_data()
            code = recv.get('code')
            if code == 101:
                # 集控脱网, 告警
                record_alarm(
                    event="集控脱网", object_type='hub', alert_source=hub,
                    object=hub.sn, level=3, status=3
                )
                raise ConnectHubTimeOut()
            if code != 0:
                raise HubError
            hub_status = recv.get('status')
        return Response(data=hub_status)

    @action(methods=['POST'], detail=False, url_path='control-all')
    def control_all(self, request, *args, **kwargs):
        """
        全开全关（控制集控下所有灯控）
        POST /hubs/control-all/
        {
            "hub": ["1001", "1002", "1003"]
            "action": "open" # open/close 全开/全关
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hub_sns = serializer.data['hub']
        act = serializer.data['action']

        for hub_sn in hub_sns:
            hub = Hub.objects.get_or_404(sn=hub_sn)
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "lighten",
                    "type": "cmd",
                    "detail": {
                        "hub_sn": hub_sn,
                        "lamp_sn": [],
                        "action": act,
                        "all": True
                    }
                }
                msg_socket.send_single_message(receiver=hub_sn, body=body,
                                               sender=sender)
                recv = msg_socket.receive_data()
                code = recv.get('code')
                if code == 101:
                    # 集控脱网, 告警
                    record_alarm(
                        event="集控脱网", object_type='hub', alert_source=hub,
                        object=hub_sn, level=3, status=3
                    )
                    raise ConnectHubTimeOut(
                        'connect hub [{}] time out'.format(hub_sn))
                if code != 0:
                    raise HubError("hub [{}] unknown error".format(hub_sn))
                if code == 0:
                    # 控灯成功 更新灯具状态
                    LampCtrl.objects.filter(hub=hub).update(switch_status=1)
        return Response(data={'detail': 'control lamps success'})

    @action(methods=['POST'], detail=True, url_path='download-log')
    def download_hub_log(self, request, *args, **kwargs):
        """
        下载集控日志
        POST /hubs/{sn}/download-log/
        """
        # TODO 大文件下载问题
        hub = self.get_object()
        sender = 'cmd-{}'.format(uuid.uuid1())
        with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
            body = {
                "action": "get_hub_log",
                "type": "cmd"
            }
            msg_socket.send_single_message(receiver=hub.sn, body=body,
                                           sender=sender)
            recv = msg_socket.receive_data()
            code = recv.get('code')
            if code == 101:
                # 集控脱网, 告警
                record_alarm(
                    event="集控脱网", object_type='hub', alert_source=hub,
                    object=hub.sn, level=3, status=3
                )
                raise ConnectHubTimeOut(
                    'connect hub [{}] time out'.format(hub.sn))
            if code != 0:
                raise HubError("hub [{}] unknown error".format(hub.sn))

        resp = StreamingHttpResponse(recv["recv"]["message"])
        resp['Content-Type'] = 'application/octet-stream'
        resp[
            'Content-Disposition'] = 'attachment;filename="hub_{}.log"'.format(
            hub.sn)

        return resp

    @action(methods=['POST'], detail=True, url_path='custom-grouping')
    def custom_grouping(self, request, *args, **kwargs):
        """
        下发分组(自定义分组)
        POST /hubs/{sn}/custom-grouping/
        "{
            configs": [
                {
                    "lampctrl": ["001", "002"],
                    "group_num": 1,
                    "memo": ""
                },
                {
                    "lampctrl": ["003", "004"],
                    "group": 2,
                    "memo": ""
                }
            ]
        }
        """
        hub = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            group_config = self.before_custom_grouping(
                instance=hub, serializer_data=serializer.data
            )
            with transaction.atomic():
                sender = 'cmd-{}'.format(uuid.uuid1())
                with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                    body = {
                        "action": "send_down_group_config",
                        "type": "cmd",
                        "group_config": group_config
                    }
                    msg_socket.send_single_message(receiver=hub.sn, body=body,
                                                   sender=sender)
                    recv = msg_socket.receive_data()
                    code = recv.get('code')
                    if code == 101:
                        # 集控脱网, 告警
                        record_alarm(
                            event="集控脱网", object_type='hub', alert_source=hub,
                            object=hub.sn, level=3, status=3
                        )
                        raise ConnectHubTimeOut(
                            'connect hub [{}] time out'.format(hub.sn))
                    if code != 0:
                        raise HubError("hub [{}] unknown error".format(hub.sn))
        except (ConnectHubTimeOut, HubError):
            raise
        except Exception as ex:
            # TODO 除集控通讯外的其他异常处理
            raise
        return Response(data={'detail': 'group configuration success'})

    @action(methods=['POST'], detail=True, url_path='pattern-grouping')
    def pattern_grouping(self, request, *args, **kwargs):
        """
        下发分组(按模式分组)
        POST /hubs/{sn}/pattern-grouping/
        {
            "group_num": 1,
            "memo": "",
            "group_num_rest": 2,
            "memo_rest": "",
            "segmentation": 1,
            "select": 1
        }
        """
        hub = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 先更新数据库再下发
        try:
            with transaction.atomic():
                group_config = self.before_pattern_grouping(
                    instance=hub, serializer_data=serializer.data
                )

                sender = 'cmd-{}'.format(uuid.uuid1())
                with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                    body = {
                        "action": "send_down_group_config",
                        "type": "cmd",
                        "group_config": group_config
                    }
                    msg_socket.send_single_message(receiver=hub.sn, body=body,
                                                   sender=sender)
                    recv = msg_socket.receive_data()
                    code = recv.get('code')
                    if code == 101:
                        # 集控脱网, 告警
                        record_alarm(
                            event="集控脱网", object_type='hub',
                            alert_source=hub,
                            object=hub.sn, level=3, status=3
                        )
                        raise ConnectHubTimeOut(
                            'connect hub [{}] time out'.format(hub.sn))
                    if code != 0:
                        raise HubError("hub [{}] unknown error".format(hub.sn))
        except (ConnectHubTimeOut, HubError):
            raise
        except Exception as ex:
            # TODO 除集控通讯外的其他异常处理
            raise
        return Response(data={'detail': 'group configuration success'})

    @action(methods=['POST'], detail=True, url_path='recycle-group')
    def recycle_group(self, request, *args, **kwargs):
        """
        回收集控下的所有分组
        POST /hubs/{sn}/recycle-group/
        """
        hub = self.get_object()
        try:
            with transaction.atomic():
                self.before_recycle_group(instance=hub)
                sender = 'cmd-{}'.format(uuid.uuid1())
                with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                    body = {
                        "action": "cancel_group_config",
                        "type": "cmd"
                    }
                    msg_socket.send_single_message(receiver=hub.sn, body=body,
                                                   sender=sender)
                    recv = msg_socket.receive_data()
                    code = recv.get('code')
                    if code == 101:
                        # 集控脱网, 告警
                        record_alarm(
                            event="集控脱网", object_type='hub', alert_source=hub,
                            object=hub.sn, level=3, status=3
                        )
                        raise ConnectHubTimeOut(
                            'connect hub [{}] time out'.format(hub.sn))
                    if code != 0:
                        raise HubError("hub [{}] unknown error".format(hub.sn))
        except (ConnectHubTimeOut, HubError):
            raise
        except Exception as ex:
            # TODO 除集控通讯外的其他异常处理
            raise
        return Response(data={'detail': 'recycle group config success'})

    @action(methods=['POST'], detail=False, url_path='gather-group')
    def gather_group(self, request, *args, **kwargs):
        """分组采集, 同步数据库(支持采集多个集控)
        POST /hubs/gather-group/
        {
            "hub": [hub1, hub2, ...]
        }
        """
        # TODO 采集分组
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        for hub_sn in hubs:
            hub = Hub.objects.get(sn=hub_sn)
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR,
                               sender=sender) as msg_socket:
                body = {
                    "action": "gather_group_config",
                    "type": "cmd"
                }
                msg_socket.send_single_message(receiver=hub_sn, body=body,
                                               sender=sender)
                recv = msg_socket.receive_data()
                code = recv.get('code')
                if code == 101:
                    # 集控脱网, 告警
                    record_alarm(
                        event="集控脱网", object_type='hub',
                        alert_source=hub,
                        object=hub_sn, level=3, status=3
                    )
                    raise ConnectHubTimeOut(
                        'connect hub [{}] time out'.format(hub_sn))
                if code != 0:
                    raise HubError("hub [{}] unknown error".format(hub_sn))
                default_group = recv.get('local_group_config')
                custom_group = recv.get('slms_group_config')
                try:
                    with transaction.atomic():
                        self.after_gather_group(instance=hub,
                                                custom_group=custom_group,
                                                default_group=default_group)
                except Exception as ex:
                    # TODO 除集控通讯外的其他异常处理
                    raise
        return Response(
            data={'detail': 'gather group config success'})

    @action(methods=['POST'], detail=True, url_path='update-group')
    def update_group(self, request, *args, **kwargs):
        """
        修改分组配置(不能修改默认分组)
        POST /hubs/{sn}/update-group/
        {
            "lampctrl": ["001"],
            "group_num": 1
        }
        """
        hub = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lampctrl_sns = serializer.data['lampctrl']
        group_id = serializer.data['group_num']

        try:
            with transaction.atomic():
                sender = 'cmd-{}'.format(uuid.uuid1())
                with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                    body = {
                        "action": "lighten",
                        "type": "cmd",
                        "detail": {
                            "hub_sn": hub.sn,
                            "lamp_sn": [],
                            "action": action,
                            "all": True
                        }
                    }
                    msg_socket.send_single_message(receiver=hub.sn, body=body,
                                                   sender=sender)
                    recv = msg_socket.receive_data()
                    code = recv.get('code')
                    if code == 101:
                        # 集控脱网, 告警
                        record_alarm(
                            event="集控脱网", object_type='hub',
                            alert_source=hub, object=hub.sn,
                            level=3, status=3
                        )
                        raise ConnectHubTimeOut(
                            'connect hub [{}] time out'.format(hub.sn))
                    if code != 0:
                        raise HubError("hub [{}] unknown error".format(hub.sn))
        except (ConnectHubTimeOut, HubError):
            raise
        except Exception as ex:
            # TODO 除集控通讯外的其他异常处理
            raise
        return Response(data={'detail': 'update group config success'})

    @action(methods=['POST'], detail=False, url_path='send-down-policyset')
    def send_down_policyset(self, request, *args, **kwargs):
        """下发策略集
        POST /hubs/send-down-policyset/
        {
            "policys": [
                {
                    "hub": "hub_sn1"
                    "group_num": null,
                    "policyset_id": "1"
                },
                {
                    "hub": "hub_sn2"
                    "group_num": "1",
                    "policyset_id": "1"
                },
                {
                    "hub": "hub_sn2"
                    "group_num": "2",
                    "policyset_id": "1"
                }
            ]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        policys = serializer.validated_data['policys']
        for hub_sn, item in policys.items():
            try:
                with transaction.atomic():
                    hub = Hub.objects.get(sn=hub_sn)
                    policy_map, policy_items = self.before_send_down_policy_set(
                        instance=hub, item=item
                    )
                    # 下发策略集
                    sender = 'cmd-{}'.format(uuid.uuid1())
                    with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                        body = {
                            "action": "send_down_policyset",
                            "type": "cmd",
                            "policy_map": policy_map,
                            "policys": policy_items
                        }
                        msg_socket.send_single_message(receiver=hub.sn, body=body,
                                                       sender=sender)
                        recv = msg_socket.receive_data()
                    code = recv.get('code')
                    if code == 101:
                        # 集控脱网, 告警
                        record_alarm(
                            event="集控脱网", object_type='hub',
                            alert_source=hub, object=hub.sn,
                            level=3, status=3
                        )
                        raise ConnectHubTimeOut(
                            'connect hub [{}] time out'.format(hub.sn))
                    if code != 0:
                        raise HubError("hub [{}] unknown error".format(hub.sn))
            except (ConnectHubTimeOut, HubError):
                raise
            except Exception as ex:
                # TODO 除集控通讯外的其他异常处理
                raise
        msg = _('send down policy scheme success')
        return Response(data={'detail': msg})

    @action(methods=['POST'], detail=False, url_path='gather-policyset')
    def gather_policyset(self, request, *args, **kwargs):
        """策略集采集, 同步数据库(支持采集多个集控)
        POST /hubs/gather-policyset/
        {
            "hub": [hub1, hub2, ...]
        }
        """
        # TODO 采集策略集
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hub_sns = serializer.validated_data['hub']
        for hub_sn in hub_sns:
            hub = Hub.objects.get(sn=hub_sn)
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR,
                               sender=sender) as msg_socket:
                body = {
                    "action": "gather_policyset",
                    "type": "cmd"
                }
                msg_socket.send_single_message(receiver=hub_sn, body=body,
                                               sender=sender)
                recv = msg_socket.receive_data()
            code = recv.get('code')
            if code == 101:
                # 集控脱网, 告警
                record_alarm(
                    event="集控脱网", object_type='hub',
                    alert_source=hub,
                    object=hub_sn, level=3, status=3
                )
                raise ConnectHubTimeOut(
                    'connect hub [{}] time out'.format(hub_sn))
            if code != 0:
                raise HubError("hub [{}] unknown error".format(hub_sn))
            data = recv.get('data')
            # 去掉不需要的字段
            for i in ("action", "message", "code", "reason"):
                data.pop(i, None)
            try:
                with transaction.atomic():
                    self.after_gather_group(instance=hub,
                                            policy_data=data)
            except Exception as ex:
                # TODO 除集控通讯外的其他异常处理
                raise
        msg = _('gather policy set success')
        return Response(data={'detail': msg})

    @action(methods=['POST'], detail=False, url_path='recycle-policyset')
    def recycle_policyset(self, request, *args, **kwargs):
        """策略集回收, 同步数据库(支持采集多个集控)
        POST /hubs/recycle-policyset/
        {
            "hub": [hub1, hub2, ...]
        }
        """
        # TODO 回收策略集
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hub_sns = serializer.validated_data['hub']
        for hub_sn in hub_sns:
            try:
                with transaction.atomic():
                    # 删除下发策略
                    pass
                    # 回收策略
                    sender = 'cmd-{}'.format(uuid.uuid1())
                    with MessageSocket(*settings.NS_ADDR,
                                       sender=sender) as msg_socket:
                        body = {
                            "action": "cancel_policyset",
                            "type": "cmd"
                        }
                        msg_socket.send_single_message(receiver=hub_sn,
                                                       body=body,
                                                       sender=sender)
                        recv = msg_socket.receive_data()
                        code = recv.get('code')
                        if code == 101:
                            # 集控脱网, 告警
                            record_alarm(
                                event="集控脱网", object_type='hub',
                                alert_source=hub,
                                object=hub_sn, level=3, status=3
                            )
                            raise ConnectHubTimeOut(
                                'connect hub [{}] time out'.format(hub_sn))
                        if code != 0:
                            raise HubError(
                                "hub [{}] unknown error".format(hub_sn))
                        data = recv.get('data')
                        # 去掉不需要的字段
                        for i in ("action", "message", "code", "reason"):
                            data.pop(i, None)
            except (ConnectHubTimeOut, HubError):
                raise
            except Exception as ex:
                # TODO 除集控通讯外的其他异常处理
                raise
        msg = _('recycle policy set success')
        return Response(data={'detail': msg})

    # @action(methods=['POST'], detail=True, url_path='get-lampctrl-status')
    # def gather_lamp_ctrl_status(self, request, *args, **kwargs):
    #     """
    #     采集集控下的灯控状态(支持多灯采集)
    #     POST /hubs/{sn}/get-lamp-status/
    #     {
    #         "lampctrl": ["001", "002"]
    #     }
    #     """
    #     hub = self.get_object()
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     lampctrls = serializer.data.get('lampctrl')
    #
    #     sender = 'cmd-{}'.format(uuid.uuid1())
    #     with MessageSocket(settings.NS_ADDR, sender=sender) as msg_socket:
    #         body = {
    #             "action": "get_lamp_status",
    #             "type": "cmd",
    #             "lamp_sn": lampctrls
    #         }
    #         msg_socket.send_single_message(receiver=hub.sn, body=body,
    #                                        sender=sender)
    #         recv = msg_socket.receive_data()
    #         code = recv.get('code')
    #         if code == 101:
    #             # 集控脱网, 告警
    #             record_alarm(
    #                 event="集控脱网", object_type='hub', alert_source=hub,
    #                 object=hub.sn, level=3, status=3
    #             )
    #             raise ConnectHubTimeOut()
    #         if code != 0:
    #             raise HubError
    #         hub_status = recv.get('status')
    #         return Response(data=hub_status)

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

        return Response()

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

    @staticmethod
    def before_pattern_grouping(instance, serializer_data):
        """下发(模式)分组之前 数据库操作"""
        hub = instance
        group_num = serializer_data['group_num']
        memo = serializer_data['memo']
        group_num_rest = serializer_data['group_num_rest']
        memo_rest = serializer_data['memo_rest']
        seg = serializer_data['segmentation']
        sel = serializer_data['select']
        group_config = {group_num: [], group_num_rest: []}
        # # 删除已存在分组
        # hub.hub_group.filter_by().soft_delete()
        # 创建分组
        lampctrls = hub.hub_lampctrl.filter_by().order_by('sequence')
        for i, lampctrl in enumerate(lampctrls):
            if i % (seg + sel) in range(seg):
                # 未被选的lampctrl
                LampCtrlGroup.objects.create(
                    hub=hub,
                    lampctrl=lampctrl,
                    group_num=group_num_rest,
                    memo=memo_rest
                )
                group_config[group_num_rest].append(lampctrl.sn)
            else:
                # 被选的lampctrl
                LampCtrlGroup.objects.create(
                    hub=hub,
                    lampctrl=lampctrl,
                    group_num=group_num,
                    memo=memo
                )
                group_config[group_num].append(lampctrl.sn)
        return group_config

    @staticmethod
    def before_custom_grouping(instance, serializer_data):
        """下发(自定义)分组之前 数据库操作"""
        hub = instance
        configs = serializer_data['configs']
        group_config = defaultdict(list)
        # # 删除已存在分组
        # hub.hub_group.filter_by().soft_delete()
        # 创建分组
        for config in configs:
            lampctrl_sns = config['lampctrl']
            group_num = config['group_num']
            memo = config['memo']
            # 创建分组
            for lampctrl_sn in lampctrl_sns:
                lampctrl = LampCtrl.objects.get_or_404(sn=lampctrl_sn)
                LampCtrlGroup.objects.create(
                    hub=hub,
                    lampctrl=lampctrl,
                    group_num=group_num,
                    memo=memo
                )
                group_config[group_num].append(lampctrl_sn)
        return group_config

    @staticmethod
    def before_recycle_group(instance):
        """回收集控下的所有分组之前 数据库操作"""
        hub = instance
        # 删除所有自定义分组
        for i in hub.hub_group.filter_by(is_default=False):
            i.soft_delete()

    @staticmethod
    def after_gather_group(instance, custom_group, default_group):
        pass
        # hub = instance
        # # 采集集控分组后， 同步数据库， 以集控为准
        # # 删除数据库中所有分组
        # LampCtrlGroup.objects.filter_by(hub=hub).delete()
        # # 添加自定义分组
        # for group_num, lampctrls in custom_group.items():
        #     for lampctrl_sn in lampctrls:
        #         # TODO 灯控不存在
        #         if not LampCtrl.objects.filter_by(
        #                 sn=lampctrl_sn).exists():
        #             raise InvalidInputError(
        #                 "Please collect the hub configuration first")
        #         LampCtrlGroup.objects.create(
        #             hub=hub,
        #             lampctrl=lampctrl_sn,
        #             group_num=group_num,
        #             is_default=False
        #         )
        # # 添加默认分组
        # for group_num, lampctrls in default_group.items():
        #     for lampctrl_sn in lampctrls:
        #         # TODO 灯控不存在
        #         if not LampCtrl.objects.filter_by(
        #                 sn=lampctrl_sn).exists():
        #             raise InvalidInputError(
        #                 "Please collect the hub configuration first")
        #         LampCtrlGroup.objects.create(
        #             hub=hub,
        #             lampctrl=lampctrl_sn,
        #             group_num=group_num,
        #             is_default=True
        #         )

    @staticmethod
    def before_send_down_policy_set(instance, item):
        """下发策略方案之前 数据处理+数据库操作
        :param instance:
        :param item: 集控下发策略详细信息
        [
            {
                "hub": "hub_sn2"
                "group_num": "1",
                "policyset_id": "1"
            },
            {
                "hub": "hub_sn2"
                "group_num": "2",
                "policyset_id": "1"
            }
        ]
        """
        # 数据处理
        for im in item:
            group_num = im.get('group_num')
            policyset_id = im.get('policyset_id')
            policyset = PolicySet.objects.filter_by(id=policyset_id).first()

            policy_map = defaultdict(list)  # 策略-策略详情
            # policy map
            policy_ids = set(
                policyset.policys.filter_by().values_list('id', flat=True))
            for policy_id in policy_ids:
                policy_map[policy_id] = Policy.objects.get(id=policy_id).item

            policys = defaultdict(list)  # 分组-日期/策略
            # 没有分组 默认为全部 标记为100
            group_num = group_num or "100"
            for relation in policyset.policyset_relations.filter_by():
                policys[group_num].append(
                    dict(execute_date=relation.execute_date,
                         policy=relation.policy.id)
                )

            # TODO 不指定分组， 如何存策略集下发表
            # 数据库同步 100分组代表下发所有分组
            PolicySetSendDown.objects.create(
                hub=instance,
                policyset=policyset,
                group_num=int(group_num)
            )
            return policy_map, policys
