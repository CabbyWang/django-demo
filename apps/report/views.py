from functools import reduce

from django.db.models import Count, Sum
from django.utils.translation import ugettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.decorators import action

# from report.filters import DeviceConsumptionFilter, \
#     HubMonthTotalConsumptionFilter
from setting.models import Setting
from utils.exceptions import InvalidInputError
from utils.mixins import ListModelMixin
from .models import LampCtrlConsumption
from .serializers import LampCtrlConsumptionSerializer


## TODO 是否需要将报表模块集中到一个viewset中


# class DailyTotalConsumptionViewSet(ListModelMixin,
#                                    viewsets.GenericViewSet):
#     """
#     日能耗
#     list:
#         获取日能耗列表(对应总能耗曲线图)
#     """
#
#     queryset = DailyTotalConsumption.objects.filter_by()
#     serializer_class = DailyTotalConsumptionSerializer
#     authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
#
#
# class HubDailyTotalConsumptionViewSet(ListModelMixin,
#                                       viewsets.GenericViewSet):
#     """
#     集控日能耗（暂时用不上， 备用）
#     list:
#         获取集控日能耗列表
#     """
#
#     queryset = HubDailyTotalConsumption.objects.filter_by()
#     serializer_class = HubDailyTotalConsumptionSerializer
#     authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
#
#
# class MonthPowerConsumptionViewSet(ListModelMixin,
#                                    viewsets.GenericViewSet):
#
#     """
#     月能耗
#     list:
#         获取月能耗列表(对应集控能耗对比图)
#     """
#
#     queryset = MonthTotalConsumption.objects.filter_by()
#     serializer_class = MonthTotalConsumptionSerializer
#     authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
#
#
# class DeviceConsumptionViewSet(ListModelMixin,
#                                mixins.RetrieveModelMixin,
#                                viewsets.GenericViewSet):
#
#     """
#     设备能耗
#     list:
#         获取所有设备的能耗分布列表(对应集控能耗分解图)
#     retrieve:
#         获取单个集控的能耗分布(对应集控能耗分解图)
#     """
#
#     queryset = DeviceConsumption.objects.filter_by()
#     serializer_class = DeviceConsumptionSerializer
#     authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
#     lookup_field = "hub_id"
#     filter_backends = (DjangoFilterBackend, )
#     filter_class = DeviceConsumptionFilter
#
#
# class HubMonthPowerConsumptionViewSet(ListModelMixin,
#                                       viewsets.GenericViewSet):
#
#     """
#     集控月能耗
#     list:
#         获取集控月能耗列表(对应集控能耗图)
#     """
#
#     queryset = HubMonthTotalConsumption.objects.filter_by()
#     serializer_class = HubMonthTotalConsumptionSerializer
#     authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
#     filter_backends = (DjangoFilterBackend,)
#     filter_class = HubMonthTotalConsumptionFilter
#
#
# class LampCtrlConsumptionViewSet(ListModelMixin,
#                                  viewsets.GenericViewSet):
#
#     """
#     灯控能耗
#     list:
#         所有灯控能耗列表(对应路灯能耗图)
#     """
#
#     queryset = LampCtrlConsumption.objects.filter_by()
#     serializer_class = LampCtrlConsumptionSerializer
#     authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)


class ReportViewSet(ListModelMixin,
                    viewsets.GenericViewSet):

    """
    报表
    get_energy_saving:
        节能率
    get_current_power:
        瞬时功率
    get_total_consumption:
        总能耗曲线(所有集控每日累计总能耗)
    get_month_consumption:
        集控能耗对比图(所有集控相邻几个月份之间累计总能耗)
    get_device_consumption:
        集控能耗分解图(集控的路灯能耗和线损能耗)
    get_consumption:
        集控能耗图(集控某几个月份的能耗情况)
    get_lamp_ctrl_consumption:
        路灯能耗图(集控下各灯控的能耗情况)
    """

    queryset = LampCtrlConsumption.objects.filter_by()
    serializer_class = LampCtrlConsumptionSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    @action(methods=['GET'], detail=False, url_path='energy-saving')
    def get_energy_saving(self, request, *args, **kwargs):
        """节能率
        GET /reports/energy-saving/
        {
            "energy_saving_rate": 100.0%,
            "energy_saving": 11,
            "real_consumption": 11
        }
        """
        try:
            setting = Setting.objects.get(option='daily_consumption')
            daily_consumption = float(setting.value)
        except Setting.DoesNotExist:
            # raise serializers.ValidationError('每日能耗未配置')
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'code': 2, 'message': "每日能耗未配置"})
        days = LampCtrlConsumption.objects.values('date').annotate().count()
        # 预期总能耗
        expect_consumption = daily_consumption * days
        # 实际总能耗
        hub_csp = LampCtrlConsumption.objects.values('hub').annotate(csp=Sum('consumption'))
        real_consumption = int('{:.0f}'.format(sum(float(item.get('csp', 0)) for item in hub_csp)))  # 不保留小数点
        energy_saving = int('{:.0f}'.format(expect_consumption - real_consumption))  # 不保留小数点
        if expect_consumption == 0:
            energy_saving_rate = '{:.0%}'.format(0)
        else:
            energy_saving_rate = '{:.0%}'.format(energy_saving / expect_consumption)
        return Response(data=dict(
            energy_saving_rate=energy_saving_rate,
            energy_saving=energy_saving,
            real_consumption=real_consumption
        ))

    @action(methods=['GET'], detail=False, url_path='current-power')
    def get_current_power(self, request, *args, **kwargs):
        """瞬时功率
        GET /reports/current-power/
        {
            "current_power": 200
        }
        """
        # TODO 瞬时功率的获取 不保留小数点
        return Response(data=dict(current_power=2100))

    @action(methods=['GET'], detail=False, url_path='total-consumption')
    def get_total_consumption(self, request, *args, **kwargs):
        """
        总能耗曲线(所有集控每日累计总能耗)
        GET /reports/total-consumption/
        :return:
        [
            {
                "expected_consumption": 5000,
                "consumption": 4000,
                "date": "2019-04-15"
            },
            {
                "expected_consumption": 6000,
                "consumption": 5000,
                "date": "2019-04-16"
            }
        ]
        """
        try:
            setting = Setting.objects.get(option='daily_consumption')
            daily_consumption = float(setting.value)
        except Setting.DoesNotExist:
            # 每日能耗未配置
            msg = _('the option ["DAILY_CONSUMPTION"] has not been set')
            raise InvalidInputError(msg)
        date_consumption = LampCtrlConsumption.objects.values('date').annotate(sum_csp=Sum('consumption'))
        # sum(map(lambda x: x.get('sum_scp'), date_consumption))
        ret_data = []
        for i, data in enumerate(date_consumption):
            days = i + 1
            date = data.get('date')
            real_consumption = data.get('sum_csp')
            tem = dict(
                expected_consumption=daily_consumption * days,
                real_consumption=real_consumption,
                date=date
            )
            ret_data.append(tem)
        return Response(data=ret_data)

    @action(methods=['GET'], detail=False, url_path='month-consumption')
    def get_month_consumption(self, request, *args, **kwargs):
        """集控能耗对比图(所有集控相邻几个月份之间累计总能耗)
        GET /reports/month-consumption/
        :return:
        [
            {
                "consumption": 5000,
                "month": "2019-03"
            },
            {
                "consumption": 5000,
                "month": "2019-04"
            }
        ]
        """
        # TODO 实现
        # from django.db.models import
        # LampCtrlConsumption.objects.values('date__month')
        data = [
            {
                "consumption": 5000,
                "month": "2019-03"
            },
            {
                "consumption": 5000,
                "month": "2019-04"
            }
        ]
        return Response(data=data)

    @action(methods=['GET'], detail=False, url_path='device-consumption')
    def get_device_consumption(self, request, *args, **kwargs):
        """集控能耗分解图(集控的路灯能耗和线损能耗)
        GET /reports/device-consumption/
        :return:
        [
            {
                "hub": "hub_sn1",
                "hub_consumption": 5000,
                "lamps_consumption": 4000,
                "loss_consumption": 1000
            },
            {
                "hub": "hub_sn2",
                "hub_consumption": 5000,
                "lamps_consumption": 4000,
                "loss_consumption": 1000
            }
        ]
        """
        # TODO 实现
        data = [
            {
                "hub": "hub_sn1",
                "hub_consumption": 5000,
                "lamps_consumption": 4000,
                "loss_consumption": 1000
            },
            {
                "hub": "hub_sn2",
                "hub_consumption": 5000,
                "lamps_consumption": 4000,
                "loss_consumption": 1000
            }
        ]
        return Response(data=data)

    @action(methods=['GET'], detail=False, url_path='hub-month-consumption')
    def get_consumption(self, request, *args, **kwargs):
        """集控能耗图(集控某几个月份的能耗情况)
        GET /reports/hub-month-consumption/?hub=&month=
        [
            {
                "consumption": 5000,
                "month": "2019-03"
            },
            {
                "consumption": 5000,
                "month": "2019-04"
            }
        ]
        """
        # TODO 实现
        # TODO 必须提供集控编号
        data = [
            {
                "consumption": 5000,
                "month": "2019-03"
            },
            {
                "consumption": 5000,
                "month": "2019-04"
            }
        ]
        return Response(data=data)

    @action(methods=['GET'], detail=False, url_path='lampctrl_consumption')
    def get_lamp_ctrl_consumption(self, request, *args, **kwargs):
        """路灯能耗图(集控下各灯控的能耗情况)
        GET /reports/lampctrl_consumption/?hub=
        [
            {
                "lampctrl": "001",
                "consumption": 150
            },
            {
                "lampctrl": "002",
                "consumption": 160
            }
        ]
        """
        # TODO 实现
        # TODO 必须提供集控编号
        data = [
            {
                "lampctrl": "001",
                "consumption": 150
            },
            {
                "lampctrl": "002",
                "consumption": 160
            }
        ]
        return Response(data=data)
