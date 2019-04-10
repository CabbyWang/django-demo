# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-10 16:46
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
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('event', models.CharField(help_text='告警事件', max_length=64)),
                ('level', models.SmallIntegerField(choices=[(1, '正常'), (2, '故障'), (3, '脱网')], help_text='故障级别')),
                ('object_type', models.CharField(choices=[('hub', '集控'), ('lamp', '灯控')], help_text='告警设备类型', max_length=16)),
                ('object', models.CharField(help_text='产生告警的设备(集控/灯控)', max_length=64)),
                ('occurred_time', models.DateTimeField(auto_now_add=True, help_text='告警产生时间')),
                ('memo', models.CharField(blank=True, help_text='备注', max_length=255, null=True)),
                ('is_solved', models.BooleanField(default=False, help_text='是否解决')),
                ('solved_time', models.DateTimeField(auto_now=True, help_text='处理时间', null=True)),
            ],
            options={
                'verbose_name': '告警',
                'verbose_name_plural': '告警',
                'db_table': 'alert',
                'ordering': ('-occurred_time',),
            },
        ),
        migrations.CreateModel(
            name='AlertAudio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('audio', models.FileField(upload_to='audio', verbose_name='告警语音')),
                ('times', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': '告警语音',
                'verbose_name_plural': '告警语音',
                'db_table': 'alert_audio',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('event', models.CharField(help_text='操作事件', max_length=64)),
                ('object', models.CharField(help_text='操作对象', max_length=64)),
                ('memo', models.CharField(help_text='详情', max_length=255, null=True)),
            ],
            options={
                'verbose_name': '日志',
                'verbose_name_plural': '日志',
                'db_table': 'log',
                'ordering': ('created_time',),
            },
        ),
    ]
