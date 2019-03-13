# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-03-13 08:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hub',
            fields=[
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('sn', models.CharField(help_text='编号', max_length=16, primary_key=True, serialize=False, verbose_name='编号')),
                ('status', models.IntegerField(choices=[(1, '正常'), (2, '故障'), (3, '脱网')], help_text='状态', verbose_name='状态')),
                ('rf_band', models.IntegerField(help_text='信道', verbose_name='信道')),
                ('rf_addr', models.IntegerField(help_text='通讯模块逻辑地址', verbose_name='通讯模块逻辑地址')),
                ('address', models.CharField(help_text='地址', max_length=60, verbose_name='地址')),
                ('longitude', models.FloatField(help_text='经度', max_length=8, verbose_name='经度')),
                ('latitude', models.FloatField(help_text='纬度', max_length=8, verbose_name='纬度')),
                ('memo', models.CharField(blank=True, help_text='备注', max_length=255, null=True, verbose_name='备注')),
                ('registered_time', models.DateField(help_text='注册时间', verbose_name='注册时间')),
                ('is_redirect', models.BooleanField(default=False, help_text='是否为中继', verbose_name='是否重定位')),
            ],
            options={
                'verbose_name': '集控',
                'verbose_name_plural': '集控',
                'db_table': 'hub',
                'ordering': ('registered_time',),
            },
        ),
        migrations.CreateModel(
            name='HubStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('A_voltage', models.DecimalField(decimal_places=1, default=0, help_text='A相电压', max_digits=32)),
                ('A_current', models.DecimalField(decimal_places=1, default=0, help_text='A相电流', max_digits=32)),
                ('A_power', models.DecimalField(decimal_places=1, default=0, help_text='A相功率', max_digits=32)),
                ('A_power_consumption', models.DecimalField(decimal_places=1, default=0, help_text='A相能耗', max_digits=32)),
                ('B_voltage', models.DecimalField(decimal_places=1, default=0, help_text='B相电压', max_digits=32)),
                ('B_current', models.DecimalField(decimal_places=1, default=0, help_text='B相电流', max_digits=32)),
                ('B_power', models.DecimalField(decimal_places=1, default=0, help_text='B相功率', max_digits=32)),
                ('B_power_consumption', models.DecimalField(decimal_places=1, default=0, help_text='B相能耗', max_digits=32)),
                ('C_voltage', models.DecimalField(decimal_places=1, default=0, help_text='C相电压', max_digits=32)),
                ('C_current', models.DecimalField(decimal_places=1, default=0, help_text='C相电流', max_digits=32)),
                ('C_power', models.DecimalField(decimal_places=1, default=0, help_text='C相功率', max_digits=32)),
                ('C_power_consumption', models.DecimalField(decimal_places=1, default=0, help_text='C相能耗', max_digits=32)),
                ('voltage', models.DecimalField(decimal_places=1, default=0, help_text='总电压', max_digits=32)),
                ('current', models.DecimalField(decimal_places=1, default=0, help_text='总电流', max_digits=32)),
                ('power', models.DecimalField(decimal_places=1, default=0, help_text='总功率', max_digits=32)),
                ('power_consumption', models.DecimalField(decimal_places=1, default=0, help_text='总能耗', max_digits=32)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('sn', models.ForeignKey(help_text='集控编号', on_delete=django.db.models.deletion.CASCADE, related_name='hub_hubstatus', to='hub.Hub')),
            ],
            options={
                'verbose_name': '集控状态历史',
                'verbose_name_plural': '集控状态历史',
                'db_table': 'hubstatus',
                'ordering': ('time',),
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='名称')),
            ],
            options={
                'verbose_name': '管理单元',
                'verbose_name_plural': '管理单元',
                'db_table': 'unit',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='hub',
            name='unit',
            field=models.ForeignKey(blank=True, help_text='管理单元', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='unit_hub', to='hub.Unit', verbose_name='管理单元'),
        ),
    ]
