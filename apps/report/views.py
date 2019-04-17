from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from report.filters import DeviceConsumptionFilter, \
    HubMonthTotalConsumptionFilter
from utils.mixins import ListModelMixin
from .models import (
    DailyTotalConsumption, HubDailyTotalConsumption, MonthTotalConsumption,
    HubMonthTotalConsumption, DeviceConsumption, LampCtrlConsumption
)
from .serializers import (
    DailyTotalConsumptionSerializer, HubDailyTotalConsumptionSerializer,
    MonthTotalConsumptionSerializer, HubMonthTotalConsumptionSerializer,
    DeviceConsumptionSerializer, LampCtrlConsumptionSerializer
)


## TODO 是否需要将报表模块集中到一个viewset中


class DailyTotalConsumptionViewSet(ListModelMixin,
                                   viewsets.GenericViewSet):
    """
    日能耗
    list:
        获取日能耗列表(对应总能耗曲线图)
    """

    queryset = DailyTotalConsumption.objects.filter_by()
    serializer_class = DailyTotalConsumptionSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)


class HubDailyTotalConsumptionViewSet(ListModelMixin,
                                      viewsets.GenericViewSet):
    """
    集控日能耗（暂时用不上， 备用）
    list:
        获取集控日能耗列表
    """

    queryset = HubDailyTotalConsumption.objects.filter_by()
    serializer_class = HubDailyTotalConsumptionSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)


class MonthPowerConsumptionViewSet(ListModelMixin,
                                   viewsets.GenericViewSet):

    """
    月能耗
    list:
        获取月能耗列表(对应集控能耗对比图)
    """

    queryset = MonthTotalConsumption.objects.filter_by()
    serializer_class = MonthTotalConsumptionSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)


class DeviceConsumptionViewSet(ListModelMixin,
                               mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):

    """
    设备能耗
    list:
        获取所有设备的能耗分布列表(对应集控能耗分解图)
    retrieve:
        获取单个集控的能耗分布(对应集控能耗分解图)
    """

    queryset = DeviceConsumption.objects.filter_by()
    serializer_class = DeviceConsumptionSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = "hub_id"
    filter_backends = (DjangoFilterBackend, )
    filter_class = DeviceConsumptionFilter


class HubMonthPowerConsumptionViewSet(ListModelMixin,
                                      viewsets.GenericViewSet):

    """
    集控月能耗
    list:
        获取集控月能耗列表(对应集控能耗图)
    """

    queryset = HubMonthTotalConsumption.objects.filter_by()
    serializer_class = HubMonthTotalConsumptionSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend,)
    filter_class = HubMonthTotalConsumptionFilter


class LampCtrlConsumptionViewSet(ListModelMixin,
                                 viewsets.GenericViewSet):

    """
    灯控能耗
    list:
        所有灯控能耗列表(对应路灯能耗图)
    """

    queryset = LampCtrlConsumption.objects.filter_by()
    serializer_class = LampCtrlConsumptionSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
