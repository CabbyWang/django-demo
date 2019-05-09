from django.db import models

from hub.models import Hub
from lamp.models import LampCtrl
from user.models import User
from notify.models import Alert
from base.models import BaseModel


class WorkOrder(BaseModel):
    """
    工单表
    1. 自动告警生成
    2. 手工创建
    TYPES: 工单类型
    """
    # TODO 灯控合并到灯具类型中
    # TODO 将types提取出来到setting中
    TYPES = (
        (0, "其它"),
        (1, "集控"),
        (2, "灯具"),
        (3, "灯杆"),
        (4, "电缆"),
        (5, "控制箱")
    )
    STATUS = (('todo', '未处理'), ('doing', '处理中'), ('finished', '已处理'))

    alert = models.OneToOneField(Alert, related_name='alert_workorder',
                                 null=True, blank=True, help_text='告警编号')
    type = models.IntegerField(choices=TYPES, help_text='工单类型')
    obj_sn = models.CharField(max_length=32, null=True, blank=True,
                              help_text='对象编号')
    user = models.ForeignKey(User, related_name='user_workorder', null=True,
                             blank=True, verbose_name='处理人')
    memo = models.CharField(max_length=255, verbose_name='备注')
    status = models.CharField(choices=STATUS, default='todo',
                              max_length=16)  # to-do/doing/finished
    description = models.CharField(max_length=255, null=True, blank=True,
                                   help_text="处理结果描述")
    finished_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = '工单'
        verbose_name_plural = verbose_name
        ordering = ('-created_time', )
        db_table = "workorder"

    def __str__(self):
        return "WorkOrder[{}]: {}".format(self.id, self.memo)


class WorkorderImage(BaseModel):
    """
    工单图片表
    """
    IMAGE_TYPE = (u'无', u'维修问题描述图片', u'工单处理图片')

    order = models.ForeignKey(WorkOrder, related_name='workorder_image')
    file = models.ImageField(upload_to='workorder')
    image_type = models.IntegerField(choices=enumerate(IMAGE_TYPE), default=0)

    class Meta:
        verbose_name = '工单图片'
        verbose_name_plural = verbose_name
        db_table = "workorderimage"

    def __str__(self):
        return self.file.path


class WorkOrderAudio(BaseModel):
    """
    工单语音
    """
    order = models.OneToOneField(WorkOrder, related_name='workorder_audio')
    audio = models.FileField(upload_to='audio', verbose_name='工单语音')
    times = models.IntegerField(default=0)

    class Meta:
        verbose_name = '工单语音'
        verbose_name_plural = verbose_name
        ordering = ('-id', )
        db_table = "workorder_audio"


class Inspection(BaseModel):
    """
    巡检报告表
    """
    user = models.ForeignKey(User, related_name='user_inspection')
    hub = models.ForeignKey(Hub, related_name='hub_inspetion')
    memo = models.CharField(null=True, max_length=1023)

    class Meta:
        verbose_name = '巡检'
        verbose_name_plural = verbose_name
        ordering = ('-created_time', )
        db_table = "inspection"

    def __str__(self):
        return str(self.id)


class InspectionImage(BaseModel):
    """
    巡检报告图片表
    """
    inspection = models.ForeignKey(Inspection, related_name='inspection_image')
    file = models.ImageField(upload_to='inspection')

    class Meta:
        verbose_name = '巡检图片'
        verbose_name_plural = verbose_name
        db_table = "inspectionimage"

    def __str__(self):
        return self.file.path


class InspectionItem(BaseModel):
    """
    巡检报告具体项
    """
    STATUS_CHOICE = ((1, '正常'), (2, '故障'))

    inspection = models.ForeignKey(Inspection, related_name="inspection_item")
    hub = models.ForeignKey(Hub, related_name='hub_inspection_item')
    lampctrl = models.ForeignKey(LampCtrl,
                                 related_name='lampctrl_inspection_item')
    status = models.IntegerField(choices=STATUS_CHOICE)
    memo = models.CharField(max_length=1023, null=True, blank=True)

    class Meta:
        verbose_name = '巡检具体项'
        verbose_name_plural = verbose_name
        ordering = ('hub', 'lampctrl')
        db_table = "inspectionitem"

    def __str__(self):
        return str(self.id)
