#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/23
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LampCtrlStatus, LampCtrlLatestStatus


@receiver(post_save, sender=LampCtrlStatus)
def update_lamp_ctl_lst_status(sender, instance=None, created=False, **kwargs):
    """每次保存数据到LampCtrlStatus表时， 同步更新LampCtrlLatestStatus表"""
    if created:
        lampctrl = instance.lampctrl
        LampCtrlLatestStatus.objects.update_or_create(
            lampctrl=lampctrl,
            hub=instance.hub,
            defaults=dict(
                route_one=instance.route_one,
                route_two=instance.route_two,
                voltage=instance.voltage,
                current=instance.current,
                power=instance.power,
                consumption=instance.consumption
            )
        )
