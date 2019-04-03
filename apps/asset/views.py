

from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Pole, Lamp, CBox, Cable
from .serializers import (
    PoleSerializer, LampSerializer, CBoxSerializer, CableSerializer,
    CBoxImageSerializer, PoleImageSerializer, LampImageSerializer,
    PoleDetailSerializer, LampDetailSerializer, CBoxDetailSerializer)
from utils.mixins import ListModelMixin, UploadModelMixin


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
    upload_images:
        上传灯杆图片
    """

    queryset = Pole.objects.all()
    serializer_class = PoleSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.action == 'list':
            return PoleDetailSerializer
        if self.action == 'upload_images':
            return PoleImageSerializer
        return PoleSerializer

    @action(methods=['POST'], detail=False, url_path='images')
    def upload_images(self, request, *args, **kwargs):
        """上传灯杆图片"""
        return super(PoleViewSet, self).create(request, *args, **kwargs)


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

    queryset = Lamp.objects.all()
    serializer_class = LampSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.action == 'list':
            return LampDetailSerializer
        if self.action == 'upload_images':
            return LampImageSerializer
        return LampSerializer

    @action(methods=['POST'], detail=False, url_path='images')
    def upload_images(self, request, *args, **kwargs):
        """上传灯杆图片"""
        return super(LampViewSet, self).create(request, *args, **kwargs)


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

    queryset = CBox.objects.all()
    serializer_class = CBoxSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.action == 'list':
            return CBoxDetailSerializer
        if self.action == 'upload_images':
            return CBoxImageSerializer
        return CBoxSerializer

    @action(methods=['POST'], detail=False, url_path='images')
    def upload_images(self, request, *args, **kwargs):
        """上传灯杆图片"""
        return super(CBoxViewSet, self).create(request, *args, **kwargs)


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

    queryset = Cable.objects.all()
    serializer_class = CableSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
