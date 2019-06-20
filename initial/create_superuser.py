#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/28
"""
import os
import sys
from pathlib import Path


# the base_dir should be added into system path.
cur_file = Path(__file__).cwd()
base_dir = cur_file.parent
sys.path.insert(0, str(base_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartlamp.settings")

import django
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
