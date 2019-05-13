from django.db import models

from equipment.models import Hub, LampCtrl
from base.models import BaseModel


class LampCtrlConsumption(BaseModel):
    """
    灯控每日能耗表
    """
    lampctrl = models.ForeignKey(LampCtrl, related_name='lampctrl_consumption')
    hub = models.ForeignKey(Hub, related_name='hub_consumption')
    consumption = models.DecimalField(max_digits=32, decimal_places=1)
    date = models.DateField()

    class Meta:
        verbose_name = "路灯每日能耗表"
        verbose_name_plural = verbose_name
        db_table = "lamp_consumption"
