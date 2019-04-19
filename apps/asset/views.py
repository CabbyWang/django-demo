from django.utils.translation import ugettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated

from asset.filters import PoleFilter, LampFilter, CBoxFilter, CableFilter
from .models import Pole, Lamp, CBox, Cable
from .serializers import (
    PoleSerializer, LampSerializer, CBoxSerializer, CableSerializer,
    CBoxImageSerializer, PoleImageSerializer, LampImageSerializer,
    PoleDetailSerializer, LampDetailSerializer, CBoxDetailSerializer,
    PoleBatchDeleteSerializer, LampBatchDeleteSerializer,
    CBoxBatchDeleteSerializer, CableBatchDeleteSerializer)
from .permissions import IsSuperUserOrReadOnly
from utils.mixins import ListModelMixin, UploadModelMixin
from utils.exceptions import ObjectHasExisted


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
            raise ObjectHasExisted(detail='pole [{}] has been existed'.format(sn))
        serializer.save()

    def perform_update(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        instance = serializer.instance
        if Pole.objects.filter_by(sn=sn).exclude(id=instance.id).exists():
            raise ObjectHasExisted(
                detail='pole [{}] has been existed'.format(sn))
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
        a = serializer.is_valid(raise_exception=False)
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
            raise ObjectHasExisted(detail='lamp [{}] has been existed'.format(sn))
        serializer.save()

    def perform_update(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        instance = serializer.instance
        if Lamp.objects.filter_by(sn=sn).exclude(id=instance.id).exists():
            raise ObjectHasExisted(detail='lamp [{}] has been existed'.format(sn))
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
            raise ObjectHasExisted(detail='cbox [{}] has been existed'.format(sn))
        serializer.save()

    def perform_update(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        instance = serializer.instance
        if CBox.objects.filter_by(sn=sn).exclude(id=instance.id).exists():
            raise ObjectHasExisted(detail='cbox [{}] has been existed'.format(sn))
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
            raise ObjectHasExisted(detail='cable [{}] has been existed'.format(sn))
        serializer.save()

    def perform_update(self, serializer):
        sn = serializer.validated_data.get('sn')
        # 判断sn是否存在
        instance = serializer.instance
        if Cable.objects.filter_by(sn=sn).exclude(id=instance.id).exists():
            raise ObjectHasExisted(detail='cable [{}] has been existed'.format(sn))
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
