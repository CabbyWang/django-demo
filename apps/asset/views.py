from django.utils.translation import ugettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from asset.filters import PoleFilter, LampFilter, CBoxFilter, CableFilter
from .models import Pole, Lamp, CBox, Cable
from .serializers import (
    PoleSerializer, LampSerializer, CBoxSerializer, CableSerializer,
    CBoxImageSerializer, PoleImageSerializer, LampImageSerializer,
    PoleDetailSerializer, LampDetailSerializer, CBoxDetailSerializer,
    PoleBatchDeleteSerializer, LampBatchDeleteSerializer,
    CBoxBatchDeleteSerializer, CableBatchDeleteSerializer)
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
    upload_images:
        上传灯杆图片
    """

    queryset = Pole.objects.filter_by()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
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
        sn = serializer.data.get('sn')
        # 判断sn是否存在
        if Pole.objects.filter_by(sn=sn).exists():
            raise ObjectHasExisted(detail='pole [{}] has been existed'.format(sn))
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
    upload_images:
        上传灯具图片
    """

    queryset = Lamp.objects.filter_by()
    serializer_class = LampSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
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
        sn = serializer.data.get('sn')
        # 判断sn是否存在
        if Lamp.objects.filter_by(sn=sn).exists():
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
    upload_images:
        上传控制箱图片
    """

    queryset = CBox.objects.filter_by()
    serializer_class = CBoxSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
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
        sn = serializer.data.get('sn')
        # 判断sn是否存在
        if CBox.objects.filter_by(sn=sn).exists():
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
    filter_backends = (DjangoFilterBackend,)
    filter_class = CableFilter
    lookup_field = 'sn'

    def get_serializer_class(self):
        if self.action == 'batch_delete':
            return CableBatchDeleteSerializer
        return CableSerializer

    def perform_create(self, serializer):
        sn = serializer.data.get('sn')
        # 判断sn是否存在
        if Cable.objects.filter_by(sn=sn).exists():
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
