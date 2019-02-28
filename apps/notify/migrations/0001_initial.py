# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-02-28 16:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(help_text='告警事件', max_length=64)),
                ('level', models.SmallIntegerField(choices=[(1, '正常'), (2, '故障'), (3, '脱网')], help_text='故障级别')),
                ('object_type', models.CharField(choices=[('hub', '集控'), ('lamp', '灯控')], help_text='告警设备类型', max_length=16)),
                ('object', models.CharField(help_text='产生告警的设备(集控/灯控)', max_length=64)),
                ('occurred_time', models.DateTimeField(auto_now_add=True, help_text='告警产生时间')),
                ('memo', models.CharField(blank=True, help_text='备注', max_length=255, null=True)),
                ('is_solved', models.BooleanField(default=False, help_text='是否解决')),
                ('solved_time', models.DateTimeField(auto_now=True, help_text='处理时间', null=True)),
                ('remain_times', models.IntegerField(default=5, help_text='告警剩余次数')),
            ],
            options={
                'verbose_name': '告警',
                'verbose_name_plural': '告警',
                'db_table': 'alert',
                'ordering': ('-occurred_time',),
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(help_text='操作事件', max_length=64)),
                ('object', models.CharField(help_text='操作对象', max_length=64)),
                ('memo', models.CharField(help_text='详情', max_length=255, null=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='操作时间')),
            ],
            options={
                'verbose_name': '日志',
                'verbose_name_plural': '日志',
                'db_table': 'log',
                'ordering': ('created_time',),
            },
        ),
    ]
