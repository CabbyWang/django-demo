import math

from django.db.models import Sum, F
from django.db import connection
from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.decorators import action

from setting.models import Setting
from status.models import HubLatestStatus, LampCtrlLatestStatus
from utils.mixins import ListModelMixin
from .models import LampCtrlConsumption, HubConsumption
from .serializers import LampCtrlConsumptionSerializer, \
    DailyConsumptionSerializer, HubIsExistedSerializer, NeedHubSerializer, \
    GetConsumptionSerializer


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

    def get_serializer_class(self):
        if self.action == 'get_total_consumption':
            return DailyConsumptionSerializer
        if self.action == 'get_device_consumption':
            return HubIsExistedSerializer
        if self.action == 'get_consumption':
            return GetConsumptionSerializer
        if self.action == 'get_lamp_ctrl_consumption':
            return NeedHubSerializer
        return LampCtrlConsumptionSerializer

    @action(methods=['GET'], detail=False, url_path='energy-saving')
    def get_energy_saving(self, request, *args, **kwargs):
        """节能率
        1. 集控有能耗，使用集控能耗作为总能耗(HubConsumption)
        2. 集控无能耗，使用集控下灯控总能耗作为总能耗(LampCtrlConsumption)
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
            # 未初始化数据
            msg = _("you may have not initialized settings")
            raise serializers.ValidationError(msg)
        # 集控投运天数
        days = len(HubConsumption.objects.values_list('date', flat=True).distinct())
        # 预期总能耗
        expect_consumption = daily_consumption * days
        # 实际总能耗
        hub_total = HubConsumption.objects.aggregate(total=Sum('consumption') / 1000)['total'] or 0
        lampctrl_total = LampCtrlConsumption.objects.aggregate(total=Sum('consumption') / 1000)['total'] or 0
        real_consumption = hub_total if hub_total else lampctrl_total
        real_consumption = round(real_consumption)  # 不保留小数点
        energy_saving = round(expect_consumption - real_consumption)  # 不保留小数点
        # energy_saving_rate = '0%' if not expect_consumption else '{:.0%}'.format(energy_saving / expect_consumption)
        energy_saving_rate = '0%' if not expect_consumption else '{}%'.format(math.floor(energy_saving / expect_consumption * 100))
        return Response(data=dict(
            energy_saving_rate=energy_saving_rate,
            energy_saving=energy_saving,
            real_consumption=real_consumption
        ))

    @action(methods=['GET'], detail=False, url_path='current-power')
    def get_current_power(self, request, *args, **kwargs):
        """瞬时功率
        1. 集控最新状态表(HubLatestStatus)
        2. 灯控最新状态表(LampCtrlLatestStatus)
        集控功率可以使用；灯控功率估计报不上来， 通过电流电压值进行计算
        GET /reports/current-power/
        {
            "current_power": 200
        }
        """
        # TODO 考虑 是否需要区分权限
        cur_power = 0
        # 计算在线的集控
        for hub_lst_status in HubLatestStatus.objects.filter_by(hub__status=1):
            # TODO 验证集控装三相电后，是否能把power报上来，报不上来则使用voltage*current
            if hub_lst_status.power == 0:
                # 集控上报功率为0，说明没有装三相电， 使用灯控功率计算
                cur_power += LampCtrlLatestStatus.objects.filter_by(lampctrl__status=1).aggregate(total=Sum(F('voltage')*F('current')))['total'] or 0
            else:
                # 集控上报功率不为0，说明装有三相电， 使用集控功率计算
                cur_power += HubLatestStatus.objects.aggregate(Sum('power'))['power__sum']
        # 不保留小数点
        cur_power = round(cur_power / 1000)
        return Response(data=dict(current_power=cur_power))

    @action(methods=['GET'], detail=False, url_path='total-consumption')
    def get_total_consumption(self, request, *args, **kwargs):
        """
        总能耗曲线(所有集控每日累计总能耗)(HubConsumption)
        GET /reports/total-consumption/
        :return:
        [
            {
                "expected_consumption": 5000, # KW
                "real_consumption": 4000,
                "date": "2019-04-15"
            },
            {
                "expected_consumption": 6000,
                "real_consumption": 5000,
                "date": "2019-04-16"
            }
        ]
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        daily_consumption = serializer.validated_data['daily_consumption']

        date_csps = HubConsumption.objects.values_list('date').annotate(csp=Sum('consumption'))
        ret = []
        tem_csp = 0
        for i, (date, csp) in enumerate(sorted(date_csps, key=lambda x: x[0])):
            days = i + 1
            expected_consumption = daily_consumption * days
            tem_csp += csp
            ret.append(dict(
                real_consumption=round(float(tem_csp) / 1000, 2),
                date=date.strftime('%Y-%m-%d'),
                expected_consumption=expected_consumption
            ))
        return Response(data=ret)

    @action(methods=['GET'], detail=False, url_path='month-consumption')
    def get_month_consumption(self, request, *args, **kwargs):
        """集控能耗对比图(所有集控相邻几个月份之间累计总能耗)
        GET /reports/month-consumption/?start_month=&end_month=
        [
            {
                "consumption": 5000,  # KW
                "month": "2019-03"
            },
            {
                "consumption": 5000,
                "month": "2019-04"
            }
        ]
        """
        params = request.query_params
        start_month = params.get('start_month')
        end_month = params.get('end_month')

        query_param = ''
        if start_month:
            query_param += ' and DATE_FORMAT(date,"%Y-%m") >= "{}"'.format(
                start_month)
        if end_month:
            query_param += ' and DATE_FORMAT(date,"%Y-%m") <= "{}"'.format(
                end_month)

        sql = "select sum(consumption), DATE_FORMAT(date,'%Y-%m') as mon from hub_consumption WHERE 1=1 {} GROUP BY mon".format(
            query_param)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        ret = []
        for consumption, month in result:
            tem = dict(
                consumption=round(float(consumption) / 1000, 2),
                month=month
            )
            ret.append(tem)
        return Response(data=ret)

    @action(methods=['GET'], detail=False, url_path='device-consumption')
    def get_device_consumption(self, request, *args, **kwargs):
        """集控能耗分解图(集控的路灯能耗和线损能耗)
        GET /reports/device-consumption/?hub=
        :return:
        [
            {
                "hub": "hub_sn1",
                "hub_consumption": 5000,  # KW
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
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        hub = serializer.validated_data['hub']
        ret_data = []
        if hub:
            hub_consumption = HubConsumption.objects.filter_by(hub=hub).aggregate(csp=Sum('consumption'))['csp'] or 0
            lamps_consumption = LampCtrlConsumption.objects.filter_by(hub=hub).aggregate(csp=Sum('consumption'))['csp'] or 0
            hub_consumption = round(float(hub_consumption) / 1000, 2)
            lamps_consumption = round(float(lamps_consumption) / 1000, 2)
            loss_consumption = round(hub_consumption - lamps_consumption, 2)
            ret_data.append(dict(
                hub=hub.sn,
                hub_consumption=hub_consumption,
                lamps_consumption=lamps_consumption,
                loss_consumption=loss_consumption
            ))
            return Response(data=ret_data)
        hub_csps = HubConsumption.objects.values_list('hub').annotate(csp=Sum('consumption'))
        lampctrl_csps = dict(LampCtrlConsumption.objects.values_list('hub').annotate(csp=Sum('consumption')))
        for hub_sn, hub_consumption in hub_csps:
            lamps_consumption = lampctrl_csps.get(hub_sn, 0)
            hub_consumption = round(float(hub_consumption) / 1000, 2)
            lamps_consumption = round(float(lamps_consumption) / 1000, 2)
            loss_consumption = round(hub_consumption - lamps_consumption, 2)
            ret_data.append(dict(
                hub=hub_sn,
                hub_consumption=hub_consumption,
                lamps_consumption=lamps_consumption,
                loss_consumption=loss_consumption
            ))
        return Response(data=ret_data)

    @action(methods=['GET'], detail=False, url_path='hub-month-consumption')
    def get_consumption(self, request, *args, **kwargs):
        """集控能耗图(集控某几个月份的能耗情况)
        GET /reports/hub-month-consumption/?hub=&month=
        [
            {
                "consumption": 5000,  # KW
                "month": "2019-03"
            },
            {
                "consumption": 5000,
                "month": "2019-04"
            }
        ]
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        hub = serializer.validated_data['hub']
        months = serializer.validated_data['month']

        query_param = 'and DATE_FORMAT(date,"%Y-%m") in ("{}")'.format(
            '","'.join(months.split(','))) if months else ''
        sql = """select sum(consumption), DATE_FORMAT(date,'%Y-%m') as mon from hub_consumption WHERE hub_id='{hub_sn}' {query_param} GROUP BY  mon;
                      """.format(hub_sn=hub.sn, query_param=query_param)

        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        ret = []
        for consumption, month in result:
            tem = dict(
                consumption=round(float(consumption) / 1000, 2),
                month=month
            )
            ret.append(tem)
        return Response(data=ret)

    @action(methods=['GET'], detail=False, url_path='lampctrl_consumption')
    def get_lamp_ctrl_consumption(self, request, *args, **kwargs):
        """路灯能耗图(集控下各灯控的能耗情况)
        GET /reports/lampctrl_consumption/?hub=
        [
            {
                "lampctrl": "001",
                "consumption": 150  # KW
            },
            {
                "lampctrl": "002",
                "consumption": 160
            }
        ]
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        hub = serializer.validated_data['hub']

        data = list(LampCtrlConsumption.objects.filter_by(hub=hub).values('lampctrl').annotate(consumption=Sum('consumption') / 1000))
        # 保留两位小数
        for i in data:
            i['consumption'] = round(i.get('consumption', 0), 2)
        return Response(data=data)
