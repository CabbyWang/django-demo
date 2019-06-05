#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/30
"""
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from .models import Alert
from workorder.models import WorkOrder


@receiver(pre_delete, sender=Alert)
def delete_work_order(sender, instance=None, using=None, **kwargs):
    """删除Alert时， 同步删除Alert相对应的WorkOrder"""
    WorkOrder.objects.filter_by(alert=instance).delete()


@receiver(post_save, sender=Alert)
def generate_alert_audio(sender, instance, created, **kwargs):
    """产生告警时, 生成告警语音"""
    if created:
        body = dict(
            id=instance.id,
            event=instance.event,
            object_type=instance.object_type,
            alert_source=instance.alert_source,
            object=instance.object,
            level=instance.level
        )
        from utils.tts import AlertTTS
        tts = AlertTTS()
        try:
            tts.generate_audio(body=body)
        except:
            # TODO log error: 生成语音失败
            pass


@receiver(post_save, sender=Alert)
def create_work_order(sender, instance, created, **kwargs):
    """产生告警时, 生成告警对应工单"""
    if created:
        WorkOrder.objects.create(
            alert=instance,
            type=1 if instance.object_type == 'hub' else 2,
            obj_sn=instance.object,
            memo='{}，由告警自动生成'.format(instance.event),
            status='todo'
        )


@receiver(post_save, sender=Alert)
def send_alert_sms(sender, instance, created, **kwargs):
    """产生告警时，发送告警短信"""
    if created:
        body = dict(
            id=instance.id,
            event=instance.event,
            object_type=instance.object_type,
            alert_source=instance.alert_source,
            object=instance.object,
            level=instance.level
        )
        from utils import sms
        sms.send_alert_sms(**body)
