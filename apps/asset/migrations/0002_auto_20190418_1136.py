# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-18 11:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lamp',
            name='address',
            field=models.CharField(blank=True, help_text='安装地址', max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='lamp',
            name='memo',
            field=models.CharField(blank=True, help_text='备注', max_length=1024, null=True),
        ),
    ]