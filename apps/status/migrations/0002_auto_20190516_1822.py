# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-05-16 18:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hublateststatus',
            name='time',
        ),
        migrations.AddField(
            model_name='hubstatus',
            name='report_time',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='上报时间', verbose_name='上报时间'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lampctrlstatus',
            name='report_time',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='上报时间', verbose_name='上报时间'),
            preserve_default=False,
        ),
    ]