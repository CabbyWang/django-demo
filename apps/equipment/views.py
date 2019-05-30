import zipfile
from pathlib import Path
from math import sqrt

from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import ugettext_lazy as _
from django.http import FileResponse
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, mixins, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from equipment.filters import CableFilter, CBoxFilter, LampFilter, PoleFilter, \
    LampCtrlFilter, HubFilter
from equipment.models import Cable, CBox, Lamp, Pole, LampCtrl, Hub
from equipment.permissions import IsSuperUserOrReadOnly, IsOwnHubOrSuperUser
from equipment.serializers import CableSerializer, CableBatchDeleteSerializer, \
    CBoxSerializer, CBoxBatchDeleteSerializer, CBoxImageSerializer, \
    CBoxDetailSerializer, LampSerializer, LampBatchDeleteSerializer, \
    LampImageSerializer, LampDetailSerializer, PoleSerializer, \
    PoleBatchDeleteSerializer, PoleImageSerializer, PoleDetailSerializer, \
    LampCtrlPartialUpdateSerializer, LampCtrlSerializer, HubDetailSerializer, \
    HubPartialUpdateSerializer
from group.models import LampCtrlGroup
from policy.models import PolicySetSendDown
from utils.exceptions import ObjectHasExisted, DeleteOnlineHubError
from utils.mixins import ListModelMixin, UploadModelMixin
from utils.permissions import IsAdminUser


class PoleViewSet(ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  UploadModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        获取灯杆列表信息
    create:
        创建灯杆信息
    update:
        修改灯杆信息
    destroy:
        删除灯杆
    batch_delete:
        批量删除
    pole_use_status:
        灯杆使用状态
    upload_images:
        上传灯杆图片
    """

    queryset = Pole.objects.filter_by()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsSuperUserOrReadOnly)
    filter_backends = (DjangoFilterBackend, )
    filter_class = PoleFilter
    lookup_field = 'sn'

    def get_serializer_class(self):
        if self.action == 'list':
            return PoleDetailSerializer
        if self.action == 'upload_images':
            return PoleImageSerializer
        if self.action == 'batch_delete':
            return PoleBatchDeleteSerializer
        return PoleSerializer

    def perform_create(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        if Pole.objects.filter_by(sn=sn).exists():
            msg = _("pole '{sn}' already exist")
            raise ObjectHasExisted(detail=msg.format(sn=sn))
        serializer.save()

    def perform_update(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        instance = serializer.instance
        if Pole.objects.filter_by(sn=sn).exclude(id=instance.id).exists():
            msg = _("pole '{sn}' already exist")
            raise ObjectHasExisted(detail=msg.format(sn=sn))
        serializer.save()

    @action(methods=['POST'], detail=False, url_path='images')
    def upload_images(self, request, *args, **kwargs):
        """上传灯杆图片"""
        return super(PoleViewSet, self).create(request, *args, **kwargs)

    @action(methods=['DELETE'], detail=False, url_path='batch')
    def batch_delete(self, request, *args, **kwargs):
        """批量删除
        DELETE /poles/batch/
        {
            "sn": ["1", "2"]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        sns = serializer.data.get('sn')
        for pole_sn in sns:
            pole = Pole.objects.filter_by(sn=pole_sn).first()
            if pole:
                pole.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(methods=['GET'], detail=False, url_path='use-status')
    def pole_use_status(self, request, *args, **kwargs):
        """灯杆使用状态
        GET /poles/use-status/
        """
        # TODO 是否需要使用serializer
        is_used = Pole.objects.filter_by(is_used=True).count()
        not_used = Pole.objects.filter_by(is_used=False).count()
        total = is_used + not_used
        return Response(data=dict(
            used_count=is_used,
            not_used_count=not_used,
            total_count=total,
            use_status='{:.0%}'.format(
                float(is_used) / total if total else 0)
        ))


class LampViewSet(ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  UploadModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        获取灯具列表信息
    create:
        创建灯具信息
    update:
        修改灯具信息
    destroy:
        删除灯具
    lamp_use_status:
        灯具使用状态
    upload_images:
        上传灯具图片
    """

    queryset = Lamp.objects.filter_by()
    serializer_class = LampSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsSuperUserOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filter_class = LampFilter
    lookup_field = 'sn'

    def get_serializer_class(self):
        if self.action == 'list':
            return LampDetailSerializer
        if self.action == 'upload_images':
            return LampImageSerializer
        if self.action == 'batch_delete':
            return LampBatchDeleteSerializer
        return LampSerializer

    def perform_create(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        if Lamp.objects.filter_by(sn=sn).exists():
            msg = _("lamp '{sn}' already exist")
            raise ObjectHasExisted(detail=msg.format(sn=sn))
        serializer.save()

    def perform_update(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        instance = serializer.instance
        if Lamp.objects.filter_by(sn=sn).exclude(id=instance.id).exists():
            msg = _("lamp '{sn}' already exist")
            raise ObjectHasExisted(detail=msg.format(sn=sn))
        serializer.save()

    @action(methods=['POST'], detail=False, url_path='images')
    def upload_images(self, request, *args, **kwargs):
        """上传灯杆图片"""
        return super(LampViewSet, self).create(request, *args, **kwargs)

    @action(methods=['DELETE'], detail=False, url_path='batch')
    def batch_delete(self, request, *args, **kwargs):
        """批量删除
        DELETE /lamps/batch/
        {
            "sn": ["1", "2"]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sns = serializer.data.get('sn')
        for lamp_sn in sns:
            lamp = Lamp.objects.filter_by(sn=lamp_sn).first()
            if lamp:
                lamp.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(methods=['GET'], detail=False, url_path='use-status')
    def lamp_use_status(self, request, *args, **kwargs):
        """灯具使用状态
        GET /lamps/use-status/
        """
        # TODO 是否需要使用serializer
        is_used = Lamp.objects.filter_by(is_used=True).count()
        not_used = Lamp.objects.filter_by(is_used=False).count()
        total = is_used + not_used
        return Response(data=dict(
            used_count=is_used,
            not_used_count=not_used,
            total_count=total,
            use_status='{:.0%}'.format(
                float(is_used) / total if total else 0)
        ))


class CBoxViewSet(ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  UploadModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        获取控制箱列表信息
    create:
        创建控制箱信息
    update:
        修改控制箱信息
    destroy:
        删除控制箱
    cbox_use_status:
        控制箱使用状态
    upload_images:
        上传控制箱图片
    """

    queryset = CBox.objects.filter_by()
    serializer_class = CBoxSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsSuperUserOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filter_class = CBoxFilter
    lookup_field = 'sn'

    def get_serializer_class(self):
        if self.action == 'list':
            return CBoxDetailSerializer
        if self.action == 'upload_images':
            return CBoxImageSerializer
        if self.action == 'batch_delete':
            return CBoxBatchDeleteSerializer
        return CBoxSerializer

    def perform_create(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        if CBox.objects.filter_by(sn=sn).exists():
            msg = _("control box '{sn}' already exist")
            raise ObjectHasExisted(detail=msg.format(sn=sn))
        serializer.save()

    def perform_update(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        instance = serializer.instance
        if CBox.objects.filter_by(sn=sn).exclude(id=instance.id).exists():
            msg = _("control box '{sn}' already exist")
            raise ObjectHasExisted(detail=msg.format(sn=sn))
        serializer.save()

    @action(methods=['POST'], detail=False, url_path='images')
    def upload_images(self, request, *args, **kwargs):
        """上传灯杆图片"""
        return super(CBoxViewSet, self).create(request, *args, **kwargs)

    @action(methods=['DELETE'], detail=False, url_path='batch')
    def batch_delete(self, request, *args, **kwargs):
        """批量删除
        DELETE /cboxs/batch/
        {
            "sn": ["1", "2"]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sns = serializer.data.get('sn')
        for cbox_sn in sns:
            cbox = CBox.objects.filter_by(sn=cbox_sn).first()
            if cbox:
                cbox.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(methods=['GET'], detail=False, url_path='use-status')
    def cbox_use_status(self, request, *args, **kwargs):
        """控制箱使用状态
        GET /cboxs/use-status/
        """
        # TODO 是否需要使用serializer
        is_used = CBox.objects.filter_by(is_used=True).count()
        not_used = CBox.objects.filter_by(is_used=False).count()
        total = is_used + not_used
        return Response(data=dict(
            used_count=is_used,
            not_used_count=not_used,
            total_count=total,
            use_status='{:.0%}'.format(
                float(is_used) / total if total else 0)
        ))


class CableViewSet(ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   UploadModelMixin,
                   viewsets.GenericViewSet):
    """
    list:
        获取电缆列表信息
    retrieve:
        获取电缆详细信息
    create:
        创建电缆信息
    update:
        修改电缆信息
    destroy:
        删除电缆
    """

    queryset = Cable.objects.filter_by()
    serializer_class = CableSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsSuperUserOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filter_class = CableFilter
    lookup_field = 'sn'

    def get_serializer_class(self):
        if self.action == 'batch_delete':
            return CableBatchDeleteSerializer
        return CableSerializer

    def perform_create(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        if Cable.objects.filter_by(sn=sn).exists():
            msg = _("cable '{sn}' already exist")
            raise ObjectHasExisted(detail=msg.format(sn=sn))
        serializer.save()

    def perform_update(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        instance = serializer.instance
        if Cable.objects.filter_by(sn=sn).exclude(id=instance.id).exists():
            msg = _("cable '{sn}' already exist")
            raise ObjectHasExisted(detail=msg.format(sn=sn))
        serializer.save()

    @action(methods=['DELETE'], detail=False, url_path='batch')
    def batch_delete(self, request, *args, **kwargs):
        """批量删除
        DELETE /cables/batch/
        {
            "sn": ["1", "2"]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sns = serializer.data.get('sn')
        for cable_sn in sns:
            cable = Cable.objects.filter_by(sn=cable_sn).first()
            if cable:
                cable.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.soft_delete()


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
        修改灯控地址(修改地址/单灯重定位)
    get_light_rate:
        灯控投运率
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
        return Response(data=dict(
            name="灯控投运率",
            total=total,
            normal=normal,
            trouble=trouble,
            offline=offline,
            putin_rate=putin_rate
        ))


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
    """
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
                "odd_even": False,
                "points": [[116.203048, 39.801835],  [116.226478, 39.82416],  [116.256912, 39.873809]],
                "sequence": [1, 2, 3, 4, 5, 7]
            }
        奇偶:
            {
                "odd_even": True,
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
        is_odd_even = request_data.get('odd_even')
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
