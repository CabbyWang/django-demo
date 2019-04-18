from django.db import models
from lamp.models import LampCtrl

from base.models import BaseModel


class PoleImage(BaseModel):
    """灯杆图片"""
    file = models.ImageField(upload_to='asset/pole/', verbose_name='灯杆图片')

    class Meta:
        verbose_name = '灯杆图片'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "pole_image"

    def __str__(self):
        return str(self.id)


class Pole(BaseModel):
    """ 灯杆 """
    sn = models.CharField(max_length=32, help_text='编号')
    vendor = models.CharField(max_length=32, help_text='厂家名称')
    model = models.CharField(max_length=32, help_text='型号')
    height = models.FloatField(help_text='高度')
    date = models.DateField(help_text='购买时间')
    longitude = models.FloatField(help_text='经度')
    latitude = models.FloatField(help_text='纬度')
    address = models.CharField(max_length=255, null=True, blank=True, help_text='安装地址')
    memo = models.CharField(max_length=255, null=True, blank=True, help_text='备注')
    is_used = models.BooleanField(default=False, help_text='是否已用')
    image = models.ForeignKey(PoleImage, null=True, blank=True)

    def __str__(self):
        return str(self.sn)

    class Meta:
        verbose_name = '灯杆'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "pole"


class LampImage(BaseModel):
    """灯具图片"""
    file = models.ImageField(upload_to='asset/lamp/', verbose_name='灯具图片')

    class Meta:
        verbose_name = '灯具图片'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "lamp_image"

    def __str__(self):
        return str(self.id)


class Lamp(BaseModel):
    """ 灯具 """
    sn = models.CharField(max_length=32, help_text='编号')
    vendor = models.CharField(max_length=32, help_text='厂家名称')
    model = models.CharField(max_length=32, help_text='型号')
    bearer = models.ForeignKey(Pole, related_name='pole_lamp', help_text='灯杆编号')
    controller = models.ForeignKey(LampCtrl, related_name='lampctrl_lamp', help_text='灯控编号')
    date = models.DateField(help_text='购买时间')
    address = models.CharField(max_length=255, null=True, blank=True, help_text='安装地址')
    memo = models.CharField(max_length=255, null=True, blank=True, help_text='备注')
    is_used = models.BooleanField(default=False, help_text='是否已用')
    image = models.ForeignKey(LampImage, null=True, blank=True)

    def __str__(self):
        return str(self.sn)

    class Meta:
        verbose_name = '灯具'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "lamp"


class CBoxImage(BaseModel):
    """控制箱图片"""
    file = models.ImageField(upload_to='asset/cbox/', verbose_name='控制箱图片')

    class Meta:
        verbose_name = '控制箱图片'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "cbox_image"

    def __str__(self):
        return str(self.id)


class CBox(BaseModel):
    """ 控制箱 """
    sn = models.CharField(max_length=32, help_text='编号')
    vendor = models.CharField(max_length=32, help_text='厂家名称')
    model = models.CharField(max_length=32, help_text='型号')
    date = models.DateField(help_text='购买时间')
    longitude = models.FloatField(help_text='经度')
    latitude = models.FloatField(help_text='纬度')
    address = models.CharField(max_length=255, null=True, blank=True, help_text='安装地址')
    memo = models.CharField(max_length=255, null=True, blank=True, help_text='备注')
    is_used = models.BooleanField(default=False, help_text='是否已用')
    image = models.ForeignKey(CBoxImage, null=True, blank=True)

    def __str__(self):
        return str(self.sn)

    class Meta:
        verbose_name = '控制箱'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "cbox"


class Cable(BaseModel):
    """ 电缆 """
    sn = models.CharField(max_length=32, help_text='编号')
    vendor = models.CharField(max_length=32, help_text='厂家名称')
    model = models.CharField(max_length=32, help_text='型号')
    length = models.FloatField(help_text='长度')
    date = models.DateField(help_text='购买时间')
    address = models.CharField(max_length=255, null=True, blank=True, help_text='安装地址')
    memo = models.CharField(max_length=255, null=True, blank=True, help_text='备注')

    def __str__(self):
        return str(self.sn)

    class Meta:
        verbose_name = '电缆'
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
        db_table = "cable"
