# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-12 18:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0002_auto_20190410_1646'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alert',
            options={'ordering': ('-created_time',), 'verbose_name': '告警', 'verbose_name_plural': '告警'},
        ),
        migrations.RemoveField(
            model_name='alert',
            name='occurred_time',
        ),
    ]