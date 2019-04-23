# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-18 10:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workorder', '0003_auto_20190417_0959'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workorder',
            old_name='message',
            new_name='memo',
        ),
        migrations.AlterField(
            model_name='workorder',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_workorder', to=settings.AUTH_USER_MODEL, verbose_name='处理人'),
        ),
    ]
