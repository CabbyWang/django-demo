from django.db import models

from equipment.models import Hub, LampCtrl
from base.models import BaseModel


class LampCtrlConsumption(BaseModel):
    """
    灯控每日能耗表
    """
    lampctrl = models.ForeignKey(LampCtrl, db_column='lampctrl_sn', related_name='lampctrl_consumption', verbose_name='灯控编号')
    hub = models.ForeignKey(Hub, db_column='hub_sn', related_name='hub_lampctrlconsumption', verbose_name='集控编号')
    consumption = models.DecimalField(max_digits=32, decimal_places=2, verbose_name='能耗')
    date = models.DateField(verbose_name='日期')

    class Meta:
        verbose_name = "路灯每日能耗表"
        verbose_name_plural = verbose_name
        db_table = "lamp_ctrl_consumption"


class HubConsumption(BaseModel):
    """
    集控每日能耗表
    """
    hub = models.ForeignKey(Hub, db_column='hub_sn', related_name='hub_consumption', verbose_name='集控编号')
    consumption = models.DecimalField(max_digits=32, decimal_places=2, verbose_name='能耗')
    date = models.DateField(verbose_name='日期')

    class Meta:
        verbose_name = "集控每日能耗表"
        verbose_name_plural = verbose_name
        db_table = "hub_consumption"

