#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/30
"""
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Alert
from workorder.models import WorkOrder


@receiver(pre_delete, sender=Alert)
def delete_work_order(sender, instance=None, using=None, **kwargs):
    """删除Alert时， 同步删除Alert相对应的WorkOrder"""
    WorkOrder.objects.filter_by(alert=instance).delete()
