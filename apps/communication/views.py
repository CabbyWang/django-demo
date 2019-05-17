import uuid
from collections import defaultdict

from django.conf import settings
from django.db import transaction
from django.http import StreamingHttpResponse
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from communication.datahandle import after_gather_group, after_load_inventory, \
    before_custom_grouping, before_pattern_grouping, before_recycle_group, \
    before_update_group, before_send_down_policy_set
from communication.serializers import GatherLampCtrlSerializer, \
    ControlLampSerializer, HubIsExistedSerializer, ControlAllSerializer, \
    PatternGroupSerializer, CustomGroupingSerializer, UpdateGroupSerializer, \
    SendDownPolicySetSerializer
from equipment.models import Hub, LampCtrl
from group.models import LampCtrlGroup
from policy.models import PolicySetSendDown, PolicySet, Policy
from utils.alert import record_alarm
from utils.data_handle import record_inventory
from utils.exceptions import ConnectHubTimeOut, HubError, DMLError, \
    UnknownError
from utils.msg_socket import MessageSocket


class CommunicateViewSet(viewsets.ModelViewSet):

    """
    集控通讯
    get_lamp_ctrl_status:
        采集灯控状态
    control_lamp:
        控灯
    load_inventory:
        采集集控配置
    gather_hub_status:
        采集集控状态
    gather_group:
        分组采集
    update_group:
        修改分组配置(不能修改默认分组)
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

    queryset = Hub.objects.filter_by()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.action == 'get_lamp_ctrl_status':
            return GatherLampCtrlSerializer
        elif self.action == 'control_lamp':
            return ControlLampSerializer
        elif self.action == 'control_all':
            return ControlAllSerializer
        elif self.action == 'pattern_grouping':
            return PatternGroupSerializer
        elif self.action == 'custom_grouping':
            return CustomGroupingSerializer
        elif self.action == 'update_group':
            return UpdateGroupSerializer
        elif self.action == 'send_down_policyset':
            return SendDownPolicySetSerializer
        elif self.action == 'recycle_policyset':
            return HubIsExistedSerializer
        return HubIsExistedSerializer

    @action(methods=['POST'], detail=False, url_path='get-lamp-ctrl-status')
    def get_lamp_ctrl_status(self, request, *args, **kwargs):
        """
        采集灯控状态(支持多灯采集)
        POST /communicate/get-lamp-ctrl-status/
        {
            "lampctrl": ["001", "002"]
        }
        """
        # TODO 灯控根据集控分类
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lampctrls = serializer.validated_data['lampctrl']

        ret_data = []

        for hub_sn, lampctrl_sns in lampctrls.items():
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "get_lamp_status",
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

    @action(methods=['POST'], detail=False, url_path='control-lamp')
    def control_lamp(self, request, *args, **kwargs):
        """
        控灯
        POST /communicate/control-lamp/
        {
            "lampctrl": ["001", "002", "003"],
            "action": "0,80"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lampctrls = serializer.validated_data['lampctrl']
        action = serializer.validated_data['action']
        switch_status = 0 if action == "0,0" else 1

        for hub_sn, lampctrl_sns in lampctrls.items():
            # 是否是控制所有灯控
            hub = Hub.objects.get(sn=hub_sn)
            is_all = all(i in lampctrl_sns for i in LampCtrl.objects.filter(hub=hub).values_list('sn', flat=True))
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "lighten",
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

    @action(methods=['POST'], detail=False, url_path='load-inventory')
    def load_inventory(self, request, *args, **kwargs):
        """
        采集集控配置, 同步数据库(支持采集多个集控)
        POST /communicate/load-inventory/
        {
            "hub": [hub1, hub2, ...]
        }
        """
        # TODO 采集集控配置
        # _logger.info("load inventory")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']

        error_hubs = []
        for hub in hubs:
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "load_inventory"
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
            try:
                with transaction.atomic():
                    after_load_inventory(
                        instance=hub,
                        inventory=recv.get('inventory')
                    )
            except Exception as ex:
                raise DMLError(str(ex))

        if error_hubs:
            return Response(status=status.HTTP_408_REQUEST_TIMEOUT,
                            data={'detail': '集控[{}]采集失败'.format(
                                ','.join(error_hubs))})

        return Response(data={'detail': '采集配置成功'})

    @action(methods=['POST'], detail=False, url_path='get-hub-status')
    def gather_hub_status(self, request, *args, **kwargs):
        """
        采集集控的状态(开关、电压电流功率等)，直接返回给前端，不入库
        (不支持同时采集多个集控的状态)
        POST /communicate/get-hub-status/
        {
            "hub": ["001", "002"]
        }
        """
        # TODO 支持采集多个集控?
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        ret_data = []
        for hub in hubs:
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "get_hub_status"
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
            ret_data.append(hub_status)
        return Response(data=ret_data)

    @action(methods=['POST'], detail=False, url_path='control-all')
    def control_all(self, request, *args, **kwargs):
        """
        全开全关（控制集控下所有灯控）
        POST /communicate/control-all/
        {
            "hub": ["1001", "1002", "1003"]
            "action": "open" # open/close 全开/全关
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        act = serializer.validated_data['action']

        for hub in hubs:
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "lighten",
                    "detail": {
                        "hub_sn": hub.sn,
                        "lamp_sn": [],
                        "action": act,
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
                    event="集控脱网", object_type='hub', alert_source=hub,
                    object=hub.sn, level=3, status=3
                )
                raise ConnectHubTimeOut(
                    'connect hub [{}] time out'.format(hub.sn))
            if code != 0:
                raise HubError("hub [{}] unknown error".format(hub.sn))
            if code == 0:
                # 控灯成功 更新灯具状态
                LampCtrl.objects.filter_by(hub=hub).update(switch_status=1)
        return Response(data={'detail': 'control lamps success'})

    @action(methods=['POST'], detail=False, url_path='download-log')
    def download_hub_log(self, request, *args, **kwargs):
        """
        下载集控日志
        POST /communicate/download-log/
        {
            "hub": ["001"]
        }
        """
        # TODO 大文件下载问题? 更换文件下载方式 支持多个下载?
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        for hub in hubs:
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "get_hub_log"
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
            break  # 暂时只取第一个下载, 后续作优化

        return resp

    @action(methods=['POST'], detail=False, url_path='custom-grouping')
    def custom_grouping(self, request, *args, **kwargs):
        """
        下发分组(自定义分组)
        POST /communicate/custom-grouping/
        "{
            "hub": "001"
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hub_sn = serializer.validated_data['hub']
        hub = Hub.objects.get(sn=hub_sn)

        try:
            with transaction.atomic():
                group_config = before_custom_grouping(
                    instance=hub, serializer_data=serializer.validated_data
                )
                sender = 'cmd-{}'.format(uuid.uuid1())
                with MessageSocket(*settings.NS_ADDR,
                                   sender=sender) as msg_socket:
                    body = {
                        "action": "send_down_group_config",
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
            raise DMLError(str(ex))
        return Response(data={'detail': 'group configuration success'})

    @action(methods=['POST'], detail=False, url_path='pattern-grouping')
    def pattern_grouping(self, request, *args, **kwargs):
        """
        下发分组(按模式分组)
        POST /communicate/pattern-grouping/
        {
            "hub": "001",
            "group_num": 1,
            "memo": "",
            "group_num_rest": 2,
            "memo_rest": "",
            "segmentation": 1,
            "select": 1
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hub_sn = serializer.validated_data['hub']
        hub = Hub.objects.get(sn=hub_sn)

        # 先更新数据库再下发
        try:
            with transaction.atomic():
                group_config = before_pattern_grouping(
                    instance=hub, serializer_data=serializer.validated_data
                )

                sender = 'cmd-{}'.format(uuid.uuid1())
                with MessageSocket(*settings.NS_ADDR,
                                   sender=sender) as msg_socket:
                    body = {
                        "action": "send_down_group_config",
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
            raise DMLError(str(ex))
        return Response(data={'detail': 'group configuration success'})

    @action(methods=['POST'], detail=True, url_path='recycle-group')
    def recycle_group(self, request, *args, **kwargs):
        """
        回收集控下的所有分组
        POST /communicate/recycle-group/
        {
            "hub": ["001"]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        for hub in hubs:
            try:
                with transaction.atomic():
                    before_recycle_group(instance=hub)
                    sender = 'cmd-{}'.format(uuid.uuid1())
                    with MessageSocket(*settings.NS_ADDR,
                                       sender=sender) as msg_socket:
                        body = {
                            "action": "cancel_group_config",
                        }
                        msg_socket.send_single_message(
                            receiver=hub.sn,
                            body=body,
                            sender=sender
                        )
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
                raise DMLError(str(ex))
        return Response(data={'detail': 'recycle group config success'})

    @action(methods=['POST'], detail=False, url_path='gather-group')
    def gather_group(self, request, *args, **kwargs):
        """
        分组采集, 同步数据库(支持采集多个集控)
        POST /communicate/gather-group/
        {
            "hub": [hub1, hub2, ...]
        }
        """
        # TODO 采集分组
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        for hub in hubs:
            hub = Hub.objects.get(sn=hub.sn)
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR,
                               sender=sender) as msg_socket:
                body = {
                    "action": "gather_group_config",
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
                default_group = recv.get('local_group_config')
                custom_group = recv.get('slms_group_config')
                try:
                    with transaction.atomic():
                        after_gather_group(instance=hub,
                                           custom_group=custom_group,
                                           default_group=default_group)
                except Exception as ex:
                    # TODO 除集控通讯外的其他异常处理
                    raise
        return Response(
            data={'detail': 'gather group config success'})

    @action(methods=['POST'], detail=False, url_path='update-group')
    def update_group(self, request, *args, **kwargs):
        """
        修改分组配置(不能修改默认分组)
        POST /communicate/update-group/
        {
            "hub": "001",
            "lampctrl": ["001"],
            "group_num": 1
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hub = serializer.validated_data['hub']

        try:
            with transaction.atomic():
                group_config = before_update_group(
                    instance=hub, serializer_data=serializer.validated_data
                )
                sender = 'cmd-{}'.format(uuid.uuid1())
                with MessageSocket(*settings.NS_ADDR,
                                   sender=sender) as msg_socket:
                    body = {
                        "action": "send_down_group_config",
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
            raise DMLError(str(ex))
        return Response(data={'detail': 'group configuration success'})

    @action(methods=['POST'], detail=False, url_path='send-down-policyset')
    def send_down_policyset(self, request, *args, **kwargs):
        """
        下发策略集
        POST /communicate/send-down-policyset/
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
                    policy_map, policy_items = before_send_down_policy_set(
                        instance=hub, item=item
                    )
                    # 下发策略集
                    sender = 'cmd-{}'.format(uuid.uuid1())
                    with MessageSocket(*settings.NS_ADDR,
                                       sender=sender) as msg_socket:
                        body = {
                            "action": "send_down_policyset",
                            "policy_map": policy_map,
                            "policys": policy_items
                        }
                        msg_socket.send_single_message(receiver=hub.sn,
                                                       body=body,
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
                raise DMLError(str(ex))
        msg = _('send down policy scheme success')
        return Response(data={'detail': msg})

    @action(methods=['POST'], detail=False, url_path='gather-policyset')
    def gather_policyset(self, request, *args, **kwargs):
        """
        策略集采集, 同步数据库(支持采集多个集控)
        POST /communicate/gather-policyset/
        {
            "hub": [hub1, hub2, ...]
        }
        """
        # TODO 采集策略集
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        for hub in hubs:
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR,
                               sender=sender) as msg_socket:
                body = {
                    "action": "gather_policyset"
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
            data = recv.get('data')
            # 去掉不需要的字段
            for i in ("action", "message", "code", "reason"):
                data.pop(i, None)
            try:
                with transaction.atomic():
                    # TODO 采集策略集后如何操作， 展示 or 存入数据库  最好是展示
                    pass
                    # after_gather_group(instance=hub,
                    #                    policy_data=data)
            except Exception as ex:
                # TODO 除集控通讯外的其他异常处理
                raise
        msg = _('gather policy set success')
        return Response(data={'detail': msg})

    @action(methods=['POST'], detail=False, url_path='recycle-policyset')
    def recycle_policyset(self, request, *args, **kwargs):
        """
        策略集回收, 同步数据库(支持采集多个集控)
        POST /communicate/recycle-policyset/
        {
            "hub": [hub1, hub2, ...]
        }
        """
        # TODO 回收策略集
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        for hub in hubs:
            try:
                with transaction.atomic():
                    # TODO 删除下发策略
                    pass
                    # 回收策略
                    sender = 'cmd-{}'.format(uuid.uuid1())
                    with MessageSocket(*settings.NS_ADDR,
                                       sender=sender) as msg_socket:
                        body = {
                            "action": "cancel_policyset"
                        }
                        msg_socket.send_single_message(receiver=hub.sn,
                                                       body=body,
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
                            raise HubError(
                                "hub [{}] unknown error".format(hub.sn))
            except (ConnectHubTimeOut, HubError):
                raise
            except Exception as ex:
                # TODO 除集控通讯外的其他异常处理
                raise
        msg = _('recycle policy set success')
        return Response(data={'detail': msg})

    @action(methods=['PUT'], detail=False, url_path='change-cycle-time')
    def change_cycle_time(self, request, *args, **kwargs):
        """
        修改集控采集周期
        PUT /communicate/change_cycle_time/
        {
            "cycle_time": 2*3600,
            "hubs": ['hub_sn1', 'hub_sn2', 'hub_sn3']  # 为空时， 修改全部集控
        }
        """

        return Response()