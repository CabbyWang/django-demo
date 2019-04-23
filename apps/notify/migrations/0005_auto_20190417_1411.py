# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-17 14:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0004_auto_20190417_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='level',
            field=models.SmallIntegerField(choices=[(1, '告警'), (2, '故障'), (3, '严重故障')], help_text='故障级别'),
        ),
    ]
