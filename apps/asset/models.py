from django.db import models
from lamp.models import LampCtrl

from base.models import BaseModel


class Pole(BaseModel):
    """ 灯杆 """
    sn = models.CharField(max_length=32, primary_key=True, db_index=True, help_text='编号')
    vendor = models.CharField(max_length=32, help_text='厂家名称')
    model = models.CharField(max_length=32, help_text='型号')
    height = models.FloatField(help_text='高度')
    date = models.DateField(help_text='购买时间')
    longitude = models.FloatField(help_text='经度')
    latitude = models.FloatField(help_text='纬度')
    address = models.CharField(max_length=32, null=True, blank=True, help_text='安装地址')
    memo = models.CharField(max_length=64, null=True, blank=True, help_text='备注')
    is_used = models.BooleanField(default=False, help_text='是否已用')
    image = models.ImageField(upload_to='asset/pole/', null=True, blank=True, default=None)

    def __str__(self):
        return str(self.sn)

    class Meta:
        verbose_name = '灯杆'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "pole"


class Lamp(BaseModel):
    """ 灯具 """
    sn = models.CharField(max_length=32, primary_key=True, db_index=True, help_text='编号')
    vendor = models.CharField(max_length=32, help_text='厂家名称')
    model = models.CharField(max_length=32, help_text='型号')
    bearer = models.ForeignKey(Pole, related_name='pole_lamp', help_text='灯杆编号')
    controller = models.ForeignKey(LampCtrl, related_name='lampctrl_lamp', help_text='灯控编号')
    date = models.DateField(help_text='购买时间')
    address = models.CharField(max_length=32, null=True, blank=True, help_text='安装地址')
    memo = models.CharField(max_length=64, null=True, blank=True, help_text='备注')
    is_used = models.BooleanField(default=False, help_text='是否已用')
    image = models.ImageField(upload_to='asset/lamp/', null=True, blank=True, default=None)

    def __str__(self):
        return str(self.sn)

    class Meta:
        verbose_name = '灯具'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "lamp"


class CBox(BaseModel):
    """ 控制箱 """
    sn = models.CharField(max_length=32, primary_key=True, db_index=True, help_text='编号')
    vendor = models.CharField(max_length=32, help_text='厂家名称')
    model = models.CharField(max_length=32, help_text='型号')
    date = models.DateField(help_text='购买时间')
    longitude = models.FloatField(help_text='经度')
    latitude = models.FloatField(help_text='纬度')
    address = models.CharField(max_length=32, null=True, blank=True, help_text='安装地址')
    memo = models.CharField(max_length=64, null=True, blank=True, help_text='备注')
    is_used = models.BooleanField(default=False, help_text='是否已用')
    image = models.ImageField(upload_to='asset/cbox/', null=True, blank=True, default=None)

    def __str__(self):
        return str(self.sn)

    class Meta:
        verbose_name = '控制箱'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "cbox"


class Cable(BaseModel):
    """ 电缆 """
    sn = models.CharField(max_length=32, primary_key=True, db_index=True, help_text='编号')
    vendor = models.CharField(max_length=32, help_text='厂家名称')
    model = models.CharField(max_length=32, help_text='型号')
    length = models.FloatField(help_text='长度')
    date = models.DateField(help_text='购买时间')
    address = models.CharField(max_length=32, null=True, blank=True, help_text='安装地址')
    memo = models.CharField(max_length=64, null=True, blank=True, help_text='备注')

    def __str__(self):
        return str(self.sn)

    class Meta:
        verbose_name = '电缆'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "cable"
