import uuid

from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from communication.datahandle import after_gather_group, after_load_inventory, \
    before_custom_grouping, before_pattern_grouping, before_recycle_group, \
    before_update_group, before_send_down_policy_set, before_recycle_policy_set
from communication.serializers import GatherLampCtrlSerializer, \
    ControlLampSerializer, HubIsExistedSerializer, ControlAllSerializer, \
    PatternGroupSerializer, CustomGroupingSerializer, UpdateGroupSerializer, \
    SendDownPolicySetSerializer, DownloadHubLogSerializer
from equipment.models import Hub, LampCtrl
from equipment.serializers import HubDetailSerializer
from utils.alert import record_hub_disconnect, record_lamp_ctrl_trouble
from utils.exceptions import ConnectHubTimeOut, HubError, DMLError
from utils.msg_socket import MessageSocket


class CommunicateViewSet(mixins.ListModelMixin,
                         viewsets.GenericViewSet):

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
        if self.action == 'list':
            return HubDetailSerializer
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
        elif self.action == 'download_hub_log':
            return DownloadHubLogSerializer
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lampctrls = serializer.validated_data['lampctrl']

        ret_data = []
        error_lampctrls = []
        for hub, lampctrl_sns in lampctrls.items():
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "get_lamp_status",
                    "lamp_sn": lampctrl_sns
                }
                msg_socket.send_single_message(receiver=hub.sn, body=body,
                                               sender=sender)
                recv = msg_socket.receive_data()
            code = recv.get('code')
            if code == 101:
                # 集控脱网, 告警
                record_hub_disconnect(hub)
            if code != 0:
                error_lampctrls.extend(lampctrl_sns)
            if code == 0:
                lamp_status = recv.get('data')
                # 灯控状态返回值为{}时，采集失败
                for lampctrl_sn, l_status in lamp_status.items():
                    if not l_status:
                        error_lampctrls.append(lampctrl_sn)
                        record_lamp_ctrl_trouble(
                            LampCtrl.objects.filter_by(sn=lampctrl_sn).first()
                        )
                        continue
                    route_one, route_two = l_status.get('brightness', [0, 0])
                    electric_energy = l_status.get("electric_energy", {})
                    routes = dict(route_one=route_one, route_two=route_two)
                    ret_data.append({'lampctrl': lampctrl_sn, 'hub_sn': hub.sn,
                                     **routes, **electric_energy})
        if error_lampctrls:
            msg = _("gather lamp control '{error_lamps}' failed").format(
                error_lamps=','.join(error_lampctrls)
            )
            # msg = _("gather hub '{error_hubs}' status failed").format(
            #     error_hubs=','.join(error_hubs)
            # )
            return Response(
                status=status.HTTP_408_REQUEST_TIMEOUT,
                data=dict(
                    detail=msg,
                    message=msg,
                    error_lampctrls=error_lampctrls
                )
            )
        return Response(dict(message=ret_data, detail=ret_data))

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

        error_hubs = []
        for hub, lampctrl_sns in lampctrls.items():
            # 是否是控制所有灯控
            is_all = all(i in lampctrl_sns for i in LampCtrl.objects.filter(hub=hub).values_list('sn', flat=True))
            sender = 'cmd-{}'.format(uuid.uuid1())
            with MessageSocket(*settings.NS_ADDR, sender=sender) as msg_socket:
                body = {
                    "action": "lighten",
                    "detail": {
                        "hub_sn": hub.sn,
                        "lamp_sn": lampctrl_sns,
                        "action": action,
                        "all": is_all
                    }
                }
                msg_socket.send_single_message(receiver=hub.sn, body=body,
                                               sender=sender)
                recv = msg_socket.receive_data()
            code = recv.get('code')
            if code == 101:
                # 集控脱网, 告警
                record_hub_disconnect(hub)
            if code != 0:
                error_hubs.append(hub.sn)
            if code == 0:
                # 控灯成功 更新灯具状态
                if is_all:
                    LampCtrl.objects.filter(hub=hub).update(
                        switch_status=switch_status
                    )
                else:
                    LampCtrl.objects.filter(sn__in=lampctrl_sns).update(
                        switch_status=switch_status
                    )
        if error_hubs:
            msg = _("connect hub '{error_hubs}' time out").format(
                error_hubs=','.join(error_hubs)
            )
            raise HubError(msg)
        return Response(data={'detail': _("control lamps success")})

    @action(methods=['POST'], detail=False, url_path='load-inventory')
    def load_inventory(self, request, *args, **kwargs):
        """
        采集集控配置, 同步数据库(支持采集多个集控)
        POST /communicate/load-inventory/
        {
            "hub": [hub1, hub2, ...]
        }
        """
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
                record_hub_disconnect(hub)
            if code != 0:
                error_hubs.append(hub.sn)
            if code == 0:
                try:
                    with transaction.atomic():
                        after_load_inventory(
                            instance=hub,
                            inventory=recv.get('data')
                        )
                except Exception as ex:
                    raise DMLError(str(ex))

        if error_hubs:
            msg = _("gather hub '{error_hubs}' failed").format(
                error_hubs=','.join(error_hubs)
            )
            # raise HubError(msg)
            return Response(
                status=status.HTTP_408_REQUEST_TIMEOUT,
                data=dict(
                    detail=msg,
                    message=msg,
                    error_hubs=error_hubs
                )
            )
        return Response(data={'detail': _('gather success')})

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        ret_data = []
        error_hubs = []
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
                record_hub_disconnect(hub)
            if code != 0:
                error_hubs.append(hub.sn)
            if code == 0:
                hub_status = recv.get('data', {})
                ret_data.append({"hub": hub.sn, **hub_status})

        if error_hubs:
            msg = _("gather hub '{error_hubs}' status failed").format(
                error_hubs=','.join(error_hubs)
            )
            # raise HubError(msg)
            return Response(
                status=status.HTTP_408_REQUEST_TIMEOUT,
                data=dict(
                    detail=msg,
                    message=msg,
                    error_hubs=error_hubs
                )
            )
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
                record_hub_disconnect(hub)
                # msg = _("connect hub [{hub_sn}] time out")
                # raise ConnectHubTimeOut(msg.format(hub_sn=hub.sn))
                continue
            if code != 0:
                # msg = _("hub [{hub_sn}] unknown error")
                # raise HubError(msg.format(hub_sn=hub.sn))
                continue
            if code == 0:
                # 控灯成功 更新灯具状态
                switch_status = 0 if act == '0,0' else 1
                LampCtrl.objects.filter_by(hub=hub).update(
                    switch_status=switch_status
                )
        return Response(data={'detail': _('control lamps success')})

    @action(methods=['POST'], detail=False, url_path='custom-grouping')
    def custom_grouping(self, request, *args, **kwargs):
        """
        下发分组(自定义分组)
        POST /communicate/custom-grouping/
        {
            "hub": "001"
            "configs": [
                {
                    "lampctrl": ["001", "002"],
                    "group_num": 1,
                    "memo": ""
                },
                {
                    "lampctrl": ["003", "004"],
                    "group_num": 2,
                    "memo": ""
                }
            ]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hub = serializer.validated_data['hub']

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
                    record_hub_disconnect(hub)
                    msg = _("connect hub [{hub_sn}] time out")
                    raise ConnectHubTimeOut(msg.format(hub_sn=hub.sn))
                if code != 0:
                    if recv.get('reason') == 'group id duplicate':
                        msg = _('group number should be different with default groups')
                    else:
                        msg = _("hub [{hub_sn}] unknown error")
                    raise HubError(msg.format(hub_sn=hub.sn))
        except (ConnectHubTimeOut, HubError):
            raise
        except Exception as ex:
            raise DMLError(str(ex))
        return Response(data={'detail': _('group configuration success')})

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
        hub = serializer.validated_data['hub']

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
                    record_hub_disconnect(hub)
                    msg = _("connect hub [{hub_sn}] time out")
                    raise ConnectHubTimeOut(msg.format(hub_sn=hub.sn))
                if code != 0:
                    if recv.get('reason') == 'group id duplicate':
                        msg = _('group number should be different with default groups')
                    else:
                        msg = _("hub [{hub_sn}] unknown error")
                    raise HubError(msg.format(hub_sn=hub.sn))
        except (ConnectHubTimeOut, HubError):
            raise
        except Exception as ex:
            raise DMLError(str(ex))
        return Response(data={'detail': _('group configuration success')})

    @action(methods=['POST'], detail=False, url_path='recycle-group')
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
        error_hubs = []
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
                        record_hub_disconnect(hub)
                        msg = _("connect hub [{hub_sn}] time out")
                        raise ConnectHubTimeOut(msg.format(hub_sn=hub.sn))
                    if code != 0:
                        msg = _("hub [{hub_sn}] unknown error")
                        raise HubError(msg.format(hub_sn=hub.sn))
            except (ConnectHubTimeOut, HubError):
                error_hubs.append(hub.sn)
            except Exception as ex:
                error_hubs.append(hub.sn)
                # raise DMLError(str(ex))
        if error_hubs:
            msg = _("hub '{error_hubs}' recycle group config failed").format(
                error_hubs=','.join(error_hubs)
            )
            # raise HubError(msg)
            return Response(
                status=status.HTTP_408_REQUEST_TIMEOUT,
                data=dict(
                    detail=msg,
                    message=msg,
                    error_hubs=error_hubs
                )
            )
        return Response(data={'detail': _('recycle group config success')})

    @action(methods=['POST'], detail=False, url_path='gather-group')
    def gather_group(self, request, *args, **kwargs):
        """
        分组采集, 同步数据库(支持采集多个集控)
        POST /communicate/gather-group/
        {
            "hub": [hub1, hub2, ...]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        error_hubs = []
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
                record_hub_disconnect(hub)
                # msg = _("connect hub [{hub_sn}] time out")
                # raise ConnectHubTimeOut(msg.format(hub_sn=hub.sn))
            if code != 0:
                error_hubs.append(hub.sn)
                # msg = _("hub [{hub_sn}] unknown error")
                # raise HubError(msg.format(hub_sn=hub.sn))
            if code == 0:
                default_group = recv.get('data', {}).get('local_group_config')
                custom_group = recv.get('data', {}).get('slms_group_config')
                try:
                    with transaction.atomic():
                        after_gather_group(instance=hub,
                                           custom_group=custom_group,
                                           default_group=default_group)
                except Exception as ex:
                    # raise DMLError(str(ex))
                    error_hubs.append(hub.sn)
        if error_hubs:
            msg = _("hub '{error_hubs}' gather group config failed").format(
                error_hubs=','.join(error_hubs)
            )
            # raise HubError(msg)
            return Response(
                status=status.HTTP_408_REQUEST_TIMEOUT,
                data=dict(
                    detail=msg,
                    message=msg,
                    error_hubs=error_hubs
                )
            )
        return Response(
            data={'detail': _('gather group config success')})

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
                    record_hub_disconnect(hub)
                    msg = _("connect hub [{hub_sn}] time out")
                    raise ConnectHubTimeOut(msg.format(hub_sn=hub.sn))
                if code != 0:
                    if recv.get('reason') == 'group id duplicate':
                        msg = _('group number should be different with default groups')
                    else:
                        msg = _("hub [{hub_sn}] unknown error")
                    raise HubError(msg.format(hub_sn=hub.sn))
        except (ConnectHubTimeOut, HubError):
            raise
        except Exception as ex:
            raise DMLError(str(ex))
        return Response(data={'detail': _('group configuration success')})

    @action(methods=['POST'], detail=False, url_path='send-down-policyset')
    def send_down_policyset(self, request, *args, **kwargs):
        """
        下发策略集
        POST /communicate/send-down-policyset/
        {
            "policys": [
                {
                    "hub": "hub_sn1",
                    "group_num": null,
                    "policyset_id": "1"
                },
                {
                    "hub": "hub_sn2",
                    "group_num": "1",
                    "policyset_id": "1"
                },
                {
                    "hub": "hub_sn2",
                    "group_num": "2",
                    "policyset_id": "1"
                }
            ]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        policys = serializer.validated_data['policys']
        error_hubs = []
        for hub, item in policys.items():
            try:
                with transaction.atomic():
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
                        record_hub_disconnect(hub)
                        msg = _("connect hub [{hub_sn}] time out")
                        raise ConnectHubTimeOut(msg.format(hub_sn=hub.sn))
                    if code != 0:
                        msg = _("hub [{hub_sn}] unknown error")
                        raise HubError(msg.format(hub_sn=hub.sn))
            except (ConnectHubTimeOut, HubError):
                error_hubs.append(hub.sn)
                print('time out or hub error')
            except Exception as ex:
                error_hubs.append(hub.sn)
                print('exception -- > ', str(ex))
                # raise DMLError(str(ex))
        if error_hubs:
            msg = _("hub '{error_hubs}' send down policy scheme failed").format(
                error_hubs=','.join(error_hubs)
            )
            raise HubError(msg)
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        error_hubs = []
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
                record_hub_disconnect(hub)
                # msg = _("connect hub [{hub_sn}] time out")
                # raise ConnectHubTimeOut(msg.format(hub_sn=hub.sn))
            if code != 0:
                error_hubs.append(hub.sn)
                # msg = _("hub [{hub_sn}] unknown error")
                # raise HubError(msg.format(hub_sn=hub.sn))
            if code == 0:
                data = recv.get('data')
                policy_map = data.get('policy_map')
                policys = data.get('policys')
                # try:
                #     with transaction.atomic():
                #         # TODO 采集策略集后如何操作， 展示 or 存入数据库  最好是展示
                #         pass
                #         # after_gather_group(instance=hub,
                #         #                    policy_data=data)
                # except Exception as ex:
                #     error_hubs.append(hub.sn)
                #     # raise DMLError(str(ex))
        if error_hubs:
            msg = _("hub '{error_hubs}' gather policy set failed").format(
                error_hubs=','.join(error_hubs)
            )
            # raise HubError(msg)
            return Response(
                status=status.HTTP_408_REQUEST_TIMEOUT,
                data=dict(
                    detail=msg,
                    message=msg,
                    error_hubs=error_hubs
                )
            )
        msg = _('gather policy set success')
        # return Response(data={'detail': msg})
        return Response(data=data)

    @action(methods=['POST'], detail=False, url_path='recycle-policyset')
    def recycle_policyset(self, request, *args, **kwargs):
        """
        策略集回收, 同步数据库(支持采集多个集控)
        POST /communicate/recycle-policyset/
        {
            "hub": [hub1, hub2, ...]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hubs = serializer.validated_data['hub']
        error_hubs = []
        for hub in hubs:
            try:
                with transaction.atomic():
                    before_recycle_policy_set(instance=hub)
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
                        record_hub_disconnect(hub)
                        msg = _("connect hub [{hub_sn}] time out")
                        raise ConnectHubTimeOut(msg.format(hub_sn=hub.sn))
                    if code != 0:
                        msg = _("hub [{hub_sn}] unknown error")
                        raise HubError(msg.format(hub_sn=hub.sn))
            except (ConnectHubTimeOut, HubError):
                # raise
                error_hubs.append(hub.sn)
            except Exception as ex:
                error_hubs.append(hub.sn)
                # raise DMLError(str(ex))
        if error_hubs:
            msg = _("hub '{error_hubs}' recycle policy set failed").format(
                error_hubs=','.join(error_hubs)
            )
            raise HubError(msg)
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
