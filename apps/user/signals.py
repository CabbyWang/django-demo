#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/27
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth import get_user_model

User = get_user_model()


# @receiver(post_save, sender=User)
# def create_user(sender, instance=None, created=False, **kwargs):
#     if created:
#         password = instance.password
#         instance.set_password(password)
#         instance.save()
