from django.db import models

from hub.models import Hub


class LampCtrl(models.Model):
    """
    灯控
    """

    TYPE_CHOICE = ((1, '单路钠灯'), (2, '单路LED灯'), (3, '双路钠灯'), (4, '双路LED灯'))
    STATUS_CHOICE = ((1, '正常'), (2, '故障'), (3, '脱网'))
    SWITCH_CHOICE = ((0, '关'), (1, '开'))
    __model_fields = []  # 所有字段的字符列表

    sn = models.CharField(max_length=16, primary_key=True, help_text='灯控编号')
    hub = models.ForeignKey(Hub, related_name='hub_lampctrl', help_text='集控编号')
    sequence = models.IntegerField(help_text='序列号')
    status = models.SmallIntegerField(default=1, choices=STATUS_CHOICE, help_text='灯控状态(正常/故障/脱网)')
    switch_status = models.SmallIntegerField(default=0, choices=SWITCH_CHOICE, help_text='灯控状态(开关)')
    lamp_type = models.SmallIntegerField(default=1, choices=TYPE_CHOICE, help_text='灯具类型')
    is_repeated = models.BooleanField(default=False, help_text='是否是中继')
    rf_band = models.IntegerField(help_text='信道')
    rf_addr = models.IntegerField(help_text='通讯模块逻辑地址')
    address = models.CharField(max_length=60, help_text='集控配置地址')
    new_address = models.CharField(max_length=255, help_text='管控修改过的地址')
    longitude = models.FloatField(max_length=8, help_text='经度')
    latitude = models.FloatField(max_length=8, help_text='纬度')
    on_map = models.BooleanField(default=False, help_text='是否在地图上显示')
    memo = models.CharField(max_length=255, null=True, blank=True, help_text='备注')
    failure_date = models.DateField(null=True, blank=True, help_text='故障日期')
    registered_time = models.DateField(help_text='入网时间')
    is_deleted = models.BooleanField(default=False, help_text='是否删除')
    created_time = models.DateTimeField(auto_now_add=True, help_text='修改时间')
    updated_time = models.DateTimeField(auto_now=True, null=True, blank=True, help_text='删除时间')
    deleted_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = '灯控'
        verbose_name_plural = verbose_name
        ordering = ('hub', 'sequence')
        db_table = "lampctrl"
        unique_together = ('hub', 'sequence')

    def __str__(self):
        return self.sn

    @classmethod
    def model_fields(cls):
        """获取Lamp中的字段列表
        ['sn', 'sequence']
        """
        if not cls.__model_fields:
            cls.__model_fields = [i.name for i in cls._meta.fields]
        return cls.__model_fields


class LampCtrlGroup(models.Model):
    """
    灯控分组
    """
    hub = models.ForeignKey(Hub, related_name='hub_group', help_text='集控编号')
    lampctrl = models.ForeignKey(LampCtrl, related_name='lampctrl_group', help_text='灯控编号')
    group_num = models.IntegerField(help_text='分组编号')
    memo = models.CharField(max_length=255, null=True, help_text='备注')
    is_default = models.BooleanField(default=False, help_text='是否为默认分组')

    class Meta:
        verbose_name = '灯控分组'
        verbose_name_plural = verbose_name
        ordering = ('hub_id', 'lampctrl_id')
        db_table = 'lampctrl_group'

    def __str__(self):
        return self.group_num


# class LampCtrlGroup(models.Model):
#     """分组"""
#     hub = models.ForeignKey(Hub, related_name='hub_group', help_text='集控编号')
#     group = models.IntegerField()
#     memo = models.CharField(max_length=255, null=True)
#     is_default = models.BooleanField(default=False)
#
#     class Meta:
#         verbose_name = '灯控分组'
#         verbose_name_plural = verbose_name
#         ordering = ('id', )
#         db_table = 'lampctrl_group'
#
#     def __str__(self):
#         return self.group_num


class LampCtrlStatus(models.Model):
    """
    灯控状态历史
    """
    lampctrl = models.ForeignKey(LampCtrl, related_name='lampctrl_status', help_text='灯控编号')
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
