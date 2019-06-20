from django.db import models
# from django.conf import settings

from equipment.models import Hub, LampCtrl
from user.models import User
from notify.models import Alert
from base.models import BaseModel
from utils.settings import WORK_ORDER_TYPES


class WorkOrder(BaseModel):
    """
    工单表
    1. 自动告警生成
    2. 手工创建
    TYPES: 工单类型
    """
    # TODO 灯控合并到灯具类型中
    # TODO 将types提取出来到setting中
    STATUS = (('todo', '未处理'), ('doing', '处理中'), ('finished', '已处理'))

    alert = models.OneToOneField(Alert, related_name='alert_workorder',
                                 null=True, blank=True, help_text='告警编号')
    type = models.IntegerField(
        choices=WORK_ORDER_TYPES, help_text='工单类型'
    )
    obj_sn = models.CharField(max_length=32, null=True, blank=True,
                              help_text='对象编号')
    user = models.ForeignKey(User, related_name='user_workorder', null=True,
                             blank=True, verbose_name='处理人')
    memo = models.CharField(max_length=255, verbose_name='备注')
    status = models.CharField(choices=STATUS, default='todo',
                              max_length=16, verbose_name='工单状态')  # to-do/doing/finished
    description = models.CharField(max_length=255, null=True, blank=True,
                                   help_text="处理结果描述")
    finished_time = models.DateTimeField(null=True, blank=True, help_text="完成时间")

    class Meta:
        verbose_name = '工单'
        verbose_name_plural = verbose_name
        ordering = ('-created_time', )
        db_table = "workorder"

    def __str__(self):
        return "WorkOrder[{}]: {}".format(self.id, self.memo)

    def not_listen_audio(self):
        try:
            audio = self.workorder_audio
            return audio if audio.times < 2 else None
        except models.ObjectDoesNotExist:
            return


class WorkorderImage(BaseModel):
    """
    工单图片表
    """
    IMAGE_TYPE = (u'无', u'维修问题描述图片', u'工单处理图片')

    order = models.ForeignKey(WorkOrder, related_name='workorder_image', verbose_name='工单编号')
    file = models.ImageField(upload_to='workorder', verbose_name='工单图片')
    image_type = models.IntegerField(choices=enumerate(IMAGE_TYPE), default=0, verbose_name='工单类型')

    class Meta:
        verbose_name = '工单图片'
        verbose_name_plural = verbose_name
        db_table = "workorder_image"

    def __str__(self):
        return self.file.path


class WorkOrderAudio(BaseModel):
    """
    工单语音
    """
    order = models.OneToOneField(WorkOrder, related_name='workorder_audio', verbose_name='工单编号')
    audio = models.FileField(upload_to='audio', verbose_name='工单语音')
    times = models.IntegerField(default=0, verbose_name='被听次数')

    class Meta:
        verbose_name = '工单语音'
        verbose_name_plural = verbose_name
        ordering = ('-id', )
        db_table = "workorder_audio"


class Inspection(BaseModel):
    """
    巡检报告表
    """
    user = models.ForeignKey(User, related_name='user_inspection', verbose_name='巡检人')
    hub = models.ForeignKey(Hub, db_column='hub_sn', related_name='hub_inspetion', verbose_name='集控编号')
    memo = models.CharField(null=True, max_length=1023, verbose_name='备注')

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
    inspection = models.ForeignKey(Inspection, related_name='inspection_image', verbose_name='巡检编号')
    file = models.ImageField(upload_to='inspection', verbose_name='巡检图片')

    class Meta:
        verbose_name = '巡检图片'
        verbose_name_plural = verbose_name
        db_table = "inspection_image"

    def __str__(self):
        return self.file.path


class InspectionItem(BaseModel):
    """
    巡检报告具体项
    """
    STATUS_CHOICE = ((1, '正常'), (2, '故障'))

    inspection = models.ForeignKey(Inspection, related_name="inspection_item", verbose_name='巡检编号')
    # hub = models.ForeignKey(Hub, db_column='hub_sn', related_name='hub_inspection_item', verbose_name='集控编号')
    lampctrl = models.ForeignKey(LampCtrl, db_column='lampctrl_sn',
                                 related_name='lampctrl_inspection_item', verbose_name='灯控编号')
    status = models.IntegerField(choices=STATUS_CHOICE, verbose_name='状态')
    memo = models.CharField(max_length=1023, null=True, blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '巡检具体项'
        verbose_name_plural = verbose_name
        ordering = ('lampctrl', )
        db_table = "inspection_item"

    def __str__(self):
        return str(self.id)
