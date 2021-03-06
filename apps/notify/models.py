from datetime import datetime

from django.db import models
from rest_framework.request import Request
from django.utils.translation import ugettext_lazy as _

from equipment.models import Hub
from user.models import User

from base.models import BaseModel


class Log(BaseModel):
    """
    日志
    """
    STATUS = ('success', 'fail')

    # user = models.ForeignKey(User, null=True, blank=True, related_name='user_log', help_text='操作人员用户名')
    username = models.CharField(max_length=64, help_text='操作人员用户名')
    event = models.CharField(max_length=1024, help_text='操作事件')
    object = models.CharField(max_length=255, help_text='操作对象')
    status = models.IntegerField(choices=enumerate(STATUS), verbose_name='操作状态')
    memo = models.CharField(max_length=1024, null=True, blank=True, help_text='详情')

    class Meta:
        verbose_name = '日志'
        verbose_name_plural = verbose_name
        ordering = ('-created_time',)
        db_table = "log"

    def __str__(self):
        return self.event


class Alert(BaseModel):
    """
    告警
    """
    # TODO 告警事件（event）是否需要变为可选类型
    ALERT_LEVEL = ((1, '告警'), (2, '故障'), (3, '严重故障'))
    OBJECT_TYPE = (('hub', '集控'), ('lamp', '灯控'))

    event = models.CharField(max_length=64, help_text='告警事件')
    level = models.SmallIntegerField(choices=ALERT_LEVEL, help_text='故障级别')
    alert_source = models.ForeignKey(Hub, db_column='alert_source', related_name='hub_alert', help_text='告警源(集控)')
    object_type = models.CharField(max_length=16, choices=OBJECT_TYPE, help_text='告警设备类型')
    object = models.CharField(max_length=64, help_text='产生告警的设备(集控/灯控)')
    memo = models.CharField(max_length=255, null=True, blank=True, help_text='备注')
    occurred_time = models.DateTimeField(default=datetime.now, help_text='发生时间')
    is_solved = models.BooleanField(default=False, help_text='是否解决')
    solver = models.ForeignKey(User, db_column='solver', related_name='solved_alert', null=True, blank=True, help_text='处理人员')
    solved_time = models.DateTimeField(auto_now=True, help_text='处理时间')

    class Meta:
        verbose_name = '告警'
        verbose_name_plural = verbose_name
        ordering = ('-created_time', )
        db_table = "alert"

    def __str__(self):
        return self.event

    def not_listen_audio(self):
        try:
            audio = self.alert_audio
            return audio if audio.times < 2 else None
        except models.ObjectDoesNotExist:
            return


class AlertAudio(BaseModel):
    """
    告警语音
    """
    alert = models.OneToOneField(Alert, related_name='alert_audio', verbose_name='告警编号')
    audio = models.FileField(upload_to='audio', verbose_name='告警语音')
    times = models.IntegerField(default=0, verbose_name='被听次数')

    class Meta:
        verbose_name = '告警语音'
        verbose_name_plural = verbose_name
        ordering = ('-id', )
        db_table = "alert_audio"
