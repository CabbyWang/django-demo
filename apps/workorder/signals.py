#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/6/4
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import WorkOrder


@receiver(post_save, sender=WorkOrder)
def generate_work_order_audio(sender, instance, created, **kwargs):
    """生成工单时, 生成工单语音"""
    if created:
        body = dict(id=instance.id, message=instance.memo)
        from utils.tts import WorkorderTTS
        tts = WorkorderTTS()
        try:
            tts.generate_audio(body=body)
        except:
            # TODO log error: 生成语音失败
            pass
