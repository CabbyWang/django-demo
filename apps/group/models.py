from django.db import models

from base.models import BaseModel
from equipment.models import Hub, LampCtrl


class LampCtrlGroup(BaseModel):
    """
    灯控分组
    """
    hub = models.ForeignKey(Hub, db_column='hub_sn', related_name='hub_group', help_text='集控编号')
    lampctrl = models.ForeignKey(LampCtrl, db_column='lampctrl_sn', related_name='lampctrl_group', help_text='灯控编号')
    group_num = models.IntegerField(help_text='分组编号')
    memo = models.CharField(max_length=255, null=True, blank=True, help_text='备注')
    is_default = models.BooleanField(default=False, help_text='是否为默认分组')

    class Meta:
        verbose_name = '灯控分组'
        verbose_name_plural = verbose_name
        ordering = ('hub_id', 'lampctrl_id')
        db_table = 'lampctrl_group'

    def __str__(self):
        return str(self.group_num)
