from django.db import models

from hub.models import Hub
from lamp.models import LampCtrl
from user.models import User
from notify.models import Alert


class WorkOrder(models.Model):
    """
    工单表
    1. 自动告警生成
    2. 手工创建
    TYPES: 工单类型
    """
    TYPES = (
        (1, "集控"),
        (2, "灯杆"),
        (3, "灯具"),
        (4, "电缆"),
        (5, "控制箱"),
        (6, "其它"),
    )
    STATUS = (('todo', '未处理'), ('doing', '处理中'), ('finished', '已处理'))

    alert = models.ForeignKey(Alert, related_name='alert_workorder', null=True, blank=True, help_text='告警编号')
    w_type = models.IntegerField(choices=TYPES, help_text='工单类型')
    obj_sn = models.CharField(max_length=32, null=True, blank=True, help_text='')
    lampctrl = models.ForeignKey(LampCtrl, related_name='lampctrl_workorder', null=True, blank=True)
    sequence = models.IntegerField(null=True, blank=True)  # 维修历史根据逻辑号查，因为sn号可能会改变
    user = models.ForeignKey(User, related_name='user_workorder', null=True, blank=True)
    message = models.CharField(null=True, blank=True, max_length=255)
    status = models.CharField(choices=STATUS, default='todo', max_length=16)    # to-do/doing/finished
    created_time = models.DateTimeField(auto_now_add=True)
    finished_time = models.DateTimeField(default=None, null=True)
    # deleted_time = models.DateTimeField(db_index=True, null=True, blank=True)
    memo = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ('-created_time', )
        db_table = "workorder"


class WorkorderImage(models.Model):
    """
    工单图片表
    """
    IMAGE_TYPE = (u'无', u'维修问题描述图片', u'工单处理图片')

    order = models.ForeignKey(WorkOrder, related_name='workorder_image')
    # memo = models.CharField(max_length=255, null=True)
    image = models.ImageField(upload_to='workorder')
    image_type = models.IntegerField(choices=enumerate(IMAGE_TYPE))
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workorderimage"


class Inspection(models.Model):
    """
    巡检报告表
    """
    user = models.ForeignKey(User, related_name='user_inspection')
    hub = models.ForeignKey(Hub, related_name='hub_inspetion', null=False)
    memo = models.CharField(null=True, max_length=1023)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_time', )
        db_table = "inspection"


class InspectionImage(models.Model):
    """
    巡检报告图片表
    """
    inspection = models.ForeignKey(Inspection, related_name='inspection_image')
    # memo = models.CharField(max_length=255, null=True)
    image = models.ImageField(upload_to='inspection')
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inspectionimage"


class InspectionItem(models.Model):
    """
    巡检报告具体项
    """
    STATUS_CHOICE = ((1, '正常'), (2, '故障'))

    hub = models.ForeignKey(Hub, related_name='hub_inspection_item')
    lamp = models.ForeignKey(LampCtrl, related_name='lampctrl_inspection_item')
    sequence = models.IntegerField()
    status = models.IntegerField(choices=STATUS_CHOICE)
    memo = models.CharField(max_length=1023, null=True, blank=True)
    inspection_id = models.IntegerField()

    class Meta:
        ordering = ('hub', 'sequence')
        db_table = "inspectionitem"
