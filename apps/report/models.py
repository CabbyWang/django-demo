from django.db import models

from hub.models import Hub
from lamp.models import LampCtrl
from base.models import BaseModel


class DailyTotalConsumption(BaseModel):
    """
    日总能耗(对应总能耗曲线)
    """
    consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='日能耗')
    date = models.DateField(auto_now_add=True, help_text='日期')

    class Meta:
        verbose_name = '日总能耗'
        verbose_name_plural = verbose_name
        ordering = ('date', )
        db_table = "daily_total_consumption"


class HubDailyTotalConsumption(BaseModel):
    """
    集控日总能耗(暂时不用， 留着备用)
    """
    hub = models.ForeignKey(Hub, related_name="hub_daily_total_consumption",
                            help_text="集控")
    consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='日能耗')
    date = models.DateField(auto_now_add=True, help_text='日期')

    class Meta:
        verbose_name = '集控日总能耗'
        verbose_name_plural = verbose_name
        ordering = ('date', )
        db_table = "hub_daily_total_consumption"


class MonthTotalConsumption(BaseModel):
    """
    月总能耗（对应集控能耗对比图）
    """
    consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='月能耗')
    month = models.CharField(max_length=8, help_text='月(2018-06)')  # "2018-06"

    class Meta:
        verbose_name = '月总能耗'
        verbose_name_plural = verbose_name
        ordering = ('month',)
        db_table = "month_total_consumption"


class HubMonthTotalConsumption(BaseModel):
    """
    集控月总能耗（暂时不用， 留着备用）
    """
    hub = models.ForeignKey(Hub, related_name="hub_month_total_consumption",
                            help_text="集控")
    consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='月能耗')
    month = models.CharField(max_length=8, help_text='月(2018-06)')  # "2018-06"

    class Meta:
        verbose_name = '集控月总能耗'
        verbose_name_plural = verbose_name
        ordering = ('month',)
        db_table = "hub_month_total_consumption"


class DeviceConsumption(BaseModel):
    """
    设备能耗（对应集控能耗分解图）
    """
    hub = models.OneToOneField(Hub, related_name="hub_device_consumption", help_text="集控")
    hub_consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='集控能耗')
    lamps_consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='灯控能耗')
    loss_consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='线损能耗')

    class Meta:
        verbose_name = '设备能耗'
        verbose_name_plural = verbose_name
        ordering = ('hub',)
        db_table = "device_consumption"


class LampCtrlConsumption(BaseModel):
    """
    灯控能耗(对应路灯能耗图)
    """
    lampctrl = models.ForeignKey(LampCtrl, related_name="lampctrl_lamps_consumption", help_text="灯控")
    consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='灯控能耗')

    class Meta:
        verbose_name = '灯控能耗'
        verbose_name_plural = verbose_name
        ordering = ('lampctrl',)
        db_table = "lampctrl_consumption"
