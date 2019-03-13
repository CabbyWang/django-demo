#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/28
"""
import os
import sys
import django


sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartlamp_core_refactor.settings")
django.setup()

from django.contrib.auth import get_user_model


User = get_user_model()


# TODO 使用django中的createsuperuser创建用户， 密码会二次加密(待解决)
def create_superuser(username='admin', password='smartlamp'):
    if User.objects.filter(username=username).exists():
        # 用户名存在
        user = User.objects.get(username=username)
        user.is_superuser = True
        user.is_staff = True
        user.set_password(password)
        user.save()
    else:
        User.objects.create(username=username, password=password,
                            is_superuser=True, is_staff=True)


if __name__ == '__main__':
    create_superuser()
