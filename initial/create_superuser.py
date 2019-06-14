#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/28
"""
import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, base_dir)

sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartlamp.settings")
django.setup()

from django.contrib.auth import get_user_model


User = get_user_model()


def create_superuser(username='admin', password='smartlamp'):
    # TODO
    # password = User.set_password(raw_password=password)
    user, _ = User.objects.update_or_create(
        username=username,
        defaults=dict(
            is_superuser=True,
            is_staff=True,
            password=password
        )
    )
    user.set_password(password)
    user.save()


if __name__ == '__main__':
    create_superuser()
