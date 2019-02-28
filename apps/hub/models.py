from django.db import models


class Unit(models.Model):
    """
    管理单元
    """
    name = models.CharField(max_length=32, verbose_name="名称", unique=True)

    class Meta:
        verbose_name = "管理单元"
        verbose_name_plural = verbose_name
        db_table = "unit"

    def __str__(self):
        return self.name


class Hub(models.Model):
    """
    集控数据模型
    """
    STATUS_CHOICE = ((1, '正常'), (2, '故障'), (3, '脱网'))

    sn = models.CharField(max_length=16, primary_key=True, verbose_name='编号', help_text='编号')
    unit = models.ForeignKey(Unit, related_name='unit_hub', null=True, blank=True, verbose_name='管理单元', help_text='管理单元')
    status = models.IntegerField(choices=STATUS_CHOICE, verbose_name='状态', help_text='状态')    # （1：正常，2：故障，3：脱网）
    rf_band = models.IntegerField(verbose_name='信道', help_text='信道')
    rf_addr = models.IntegerField(verbose_name='通讯模块逻辑地址', help_text='通讯模块逻辑地址')
    address = models.CharField(max_length=60, verbose_name='地址', help_text='地址')
    longitude = models.FloatField(max_length=8, verbose_name='经度', help_text='经度')
    latitude = models.FloatField(max_length=8, verbose_name='纬度', help_text='纬度')
    memo = models.CharField(max_length=255, blank=True, null=True, verbose_name='备注', help_text='备注')
    registered_time = models.DateField(verbose_name='注册时间', help_text='注册时间')
    is_redirect = models.BooleanField(default=False, verbose_name='是否为中继', help_text='是否为中继')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除', help_text='是否删除')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    updated_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间', help_text='更新时间')
    deleted_time = models.DateTimeField(db_index=True, null=True, blank=True, verbose_name='删除时间', help_text='删除时间')

    class Meta:
        verbose_name = '集控'
        verbose_name_plural = verbose_name
        ordering = ('registered_time', )
        db_table = "hub"

    def __str__(self):
        return self.sn


class HubStatus(models.Model):
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
