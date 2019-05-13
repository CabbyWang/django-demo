from django.db import models

from base.models import BaseModel
from equipment.models import Hub, LampCtrl


class HubStatus(BaseModel):
    """
    集控状态历史记录
    """
    sn = models.ForeignKey(Hub, related_name='hub_hubstatus', help_text='集控编号')
    A_voltage = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='A相电压')
    A_current = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='A相电流')
    A_power = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='A相功率')
    A_power_consumption = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='A相能耗')
    B_voltage = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='B相电压')
    B_current = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='B相电流')
    B_power = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='B相功率')
    B_power_consumption = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='B相能耗')
    C_voltage = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='C相电压')
    C_current = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='C相电流')
    C_power = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='C相功率')
    C_power_consumption = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='C相能耗')
    voltage = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='总电压')
    current = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='总电流')
    power = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='总功率')
    power_consumption = models.DecimalField(max_digits=32, decimal_places=1, default=0, help_text='总能耗')
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '集控状态历史'
        verbose_name_plural = verbose_name
        ordering = ('time', )
        db_table = "hubstatus"


class LampCtrlStatus(BaseModel):
    """
    灯控状态历史
    """
    lampctrl = models.ForeignKey(LampCtrl, related_name='lampctrl_status', help_text='灯控编号')
    route_one = models.IntegerField(null=True)
    route_two = models.IntegerField(null=True)
    voltage = models.DecimalField(max_digits=32, decimal_places=1, help_text='电压')
    current = models.DecimalField(max_digits=32, decimal_places=1, help_text='电流')
    power = models.DecimalField(max_digits=32, decimal_places=1, help_text='功率')
    power_consumption = models.DecimalField(max_digits=32, decimal_places=1, help_text='能耗')
    time = models.DateTimeField(auto_now_add=True, help_text='上报时间')

    class Meta:
        verbose_name = '灯控状态历史'
        verbose_name_plural = verbose_name
        ordering = ('time', )
        db_table = "lampstatus"
