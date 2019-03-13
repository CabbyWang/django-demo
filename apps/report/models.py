from django.db import models

from hub.models import Hub
from base.models import BaseModel


class TotalPowerConsumption(BaseModel):
    """
    集控总能耗
    """
    power_consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='总能耗')
    date = models.DateField(auto_now_add=True, help_text='记录时间')

    class Meta:
        verbose_name = '集控总能耗'
        verbose_name_plural = verbose_name
        ordering = ('date', )
        db_table = "totalpowerconsumption"


class Consumption(BaseModel):
    """
    集控当天能耗表
    """
    hub = models.ForeignKey(Hub, related_name='hub_consumption', help_text='集控编号')
    consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='能耗')
    date = models.DateField(auto_now_add=True, help_text='记录时间')

    class Meta:
        verbose_name = "集控日能耗"
        verbose_name_plural = verbose_name
        db_table = "consumption"
