# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-17 10:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0003_auto_20190412_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='event',
            field=models.CharField(help_text='操作事件', max_length=1024),
        ),
        migrations.AlterField(
            model_name='log',
            name='memo',
            field=models.CharField(help_text='详情', max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='log',
            name='object',
            field=models.CharField(help_text='操作对象', max_length=255),
        ),
    ]