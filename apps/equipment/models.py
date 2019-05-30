from datetime import datetime

from django.db import models

from base.models import BaseModel, Unit


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


class Hub(BaseModel):
    """
    集控数据模型
    """
    STATUS_CHOICE = ((1, '正常'), (2, '故障'), (3, '脱网'))

    sn = models.CharField(
        max_length=16, primary_key=True, verbose_name='编号',
        help_text='编号'
    )
    pole = models.ForeignKey(
        Pole, null=True, blank=True,
        related_name='pole_hub', verbose_name='灯杆'
    )
    unit = models.ForeignKey(
        Unit, null=True, blank=True, related_name='unit_hub',
        verbose_name='管理单元', help_text='管理单元'
    )
    status = models.IntegerField(
        choices=STATUS_CHOICE, verbose_name='状态', help_text='状态'
    )  # （1：正常，2：故障，3：脱网）
    rf_band = models.IntegerField(verbose_name='信道', help_text='信道')
    rf_addr = models.IntegerField(verbose_name='通讯模块逻辑地址',
                                  help_text='通讯模块逻辑地址')
    address = models.CharField(
        max_length=60, verbose_name='地址', help_text='地址'
    )
    new_address = models.CharField(
        max_length=255, null=True, blank=True,
        help_text='管控修改过的地址'
    )
    longitude = models.FloatField(
        max_length=8, verbose_name='经度', help_text='经度'
    )
    latitude = models.FloatField(
        max_length=8, verbose_name='纬度',
        help_text='纬度'
    )
    memo = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name='备注', help_text='备注'
    )
    registered_time = models.DateField(verbose_name='注册时间', help_text='注册时间')
    is_redirect = models.BooleanField(
        default=False, verbose_name='是否重定位',
        help_text='是否重定位'
    )
    version = models.CharField(max_length=16, verbose_name='集控版本号', help_text='集控版本号')

    class Meta:
        verbose_name = '集控'
        verbose_name_plural = verbose_name
        ordering = ('registered_time', )
        db_table = "hub"

    def __str__(self):
        return self.sn


class LampCtrl(BaseModel):
    """
    灯控
    """

    TYPE_CHOICE = ((1, '单路钠灯'), (2, '单路LED灯'), (3, '双路钠灯'), (4, '双路LED灯'), (5, '线路开关'))
    STATUS_CHOICE = ((1, '正常'), (2, '故障'), (3, '脱网'))
    SWITCH_CHOICE = ((0, '关'), (1, '开'))
    __model_fields = []  # 所有字段的字符列表

    sn = models.CharField(max_length=16, primary_key=True, help_text='灯控编号')
    hub = models.ForeignKey(Hub, related_name='hub_lampctrl', help_text='集控编号')
    sequence = models.IntegerField(help_text='序列号')
    status = models.SmallIntegerField(default=1, choices=STATUS_CHOICE,
                                      help_text='灯控状态(正常/故障/脱网)')
    switch_status = models.SmallIntegerField(default=0, choices=SWITCH_CHOICE,
                                             help_text='灯控状态(开关)')
    lamp_type = models.SmallIntegerField(default=1, choices=TYPE_CHOICE,
                                         help_text='灯具类型')
    is_repeated = models.BooleanField(default=False, help_text='是否是中继')
    rf_band = models.IntegerField(help_text='射频频率')
    rf_addr = models.IntegerField(help_text='射频地址')
    address = models.CharField(max_length=60, help_text='集控配置地址')
    new_address = models.CharField(max_length=255, null=True, blank=True,
                                   help_text='管控修改过的地址')
    longitude = models.FloatField(max_length=8, help_text='经度')
    latitude = models.FloatField(max_length=8, help_text='纬度')
    on_map = models.BooleanField(default=False, help_text='是否在地图上显示')
    memo = models.CharField(max_length=255, null=True, blank=True,
                            help_text='备注')
    version = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name='固件版本', help_text='固件版本'
    )
    # failure_date = models.DateField(null=True, blank=True, help_text='故障日期')
    registered_time = models.DateField(default=datetime.now, help_text='入网时间')
    is_redirect = models.BooleanField(default=False, verbose_name='是否重定位',
                                      help_text='是否重定位')

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
