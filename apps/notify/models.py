from django.db import models

from hub.models import Hub
from user.models import User

from base.models import BaseModel


class Log(BaseModel):
    """
    日志
    """
    user = models.ForeignKey(User, related_name='user_log', help_text='操作人员用户名')
    event = models.CharField(max_length=64, help_text='操作事件')
    object = models.CharField(max_length=64, help_text='操作对象')
    memo = models.CharField(max_length=255, null=True, help_text='详情')

    class Meta:
        verbose_name = '日志'
        verbose_name_plural = verbose_name
        ordering = ('created_time',)
        db_table = "log"

    def __str__(self):
        return self.event


class Alert(BaseModel):
    """
    告警
    """
    ALERT_LEVEL = ((1, '正常'), (2, '故障'), (3, '脱网'))
    OBJECT_TYPE = (('hub', '集控'), ('lamp', '灯控'))

    event = models.CharField(max_length=64, help_text='告警事件')
    level = models.SmallIntegerField(choices=ALERT_LEVEL, help_text='故障级别')
    alert_source = models.ForeignKey(Hub, related_name='hub_alert', help_text='告警源(集控)')
    object_type = models.CharField(max_length=16, choices=OBJECT_TYPE, help_text='告警设备类型')
    object = models.CharField(max_length=64, help_text='产生告警的设备(集控/灯控)')
    occurred_time = models.DateTimeField(auto_now_add=True, help_text='告警产生时间')
    memo = models.CharField(max_length=255, null=True, blank=True, help_text='备注')
    is_solved = models.BooleanField(default=False, help_text='是否解决')
    solver = models.ForeignKey(User, related_name='solved_alert', null=True, blank=True, help_text='处理人员')
    solved_time = models.DateTimeField(auto_now=True, null=True, blank=True, help_text='处理时间')
    # audio = models.ForeignKey(AlertAudio, related_name='audio_alert', help_text='告警语音')
    # times = models.IntegerField(default=0, help_text='告警被听次数')

    class Meta:
        verbose_name = '告警'
        verbose_name_plural = verbose_name
        ordering = ('-occurred_time', )
        db_table = "alert"

    def __str__(self):
        return self.event


class AlertAudio(BaseModel):
    """
    告警语音
    """
    alert = models.OneToOneField(Alert, related_name='alert_audio')
    audio = models.FileField(upload_to='audio', verbose_name='告警语音')
    times = models.IntegerField(default=0)

    class Meta:
        verbose_name = '告警语音'
        verbose_name_plural = verbose_name
        # unique_together = ('alert_id', 'audio')
        ordering = ('-id', )
        db_table = "alert_audio"
