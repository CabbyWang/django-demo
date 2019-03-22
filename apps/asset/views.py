

from rest_framework import viewsets, mixins, status

from .models import Pole, Lamp, CBox, Cable
from .serializers import (
    PoleSerializer, LampSerializer, CBoxSerializer,
    CableSerializer
)
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
    retrieve:
        获取灯杆详细信息

    """

    queryset = Pole.objects.all()
    serializer_class = PoleSerializer


class LampViewSet(ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  UploadModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        获取灯杆列表信息
    retrieve:
        获取灯杆详细信息
    update:

    """

    queryset = Lamp.objects.all()
    serializer_class = LampSerializer


class CBoxViewSet(ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  UploadModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        获取灯杆列表信息
    retrieve:
        获取灯杆详细信息

    """

    queryset = CBox.objects.all()
    serializer_class = CBoxSerializer


class CableViewSet(ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  UploadModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        获取灯杆列表信息
    retrieve:
        获取灯杆详细信息

    """

    queryset = Cable.objects.all()
    serializer_class = CableSerializer
