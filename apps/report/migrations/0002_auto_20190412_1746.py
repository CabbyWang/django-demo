# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-12 17:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0001_initial'),
        ('lamp', '0001_initial'),
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyTotalConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('consumption', models.DecimalField(decimal_places=1, help_text='日能耗', max_digits=32)),
                ('date', models.DateField(auto_now_add=True, help_text='日期')),
            ],
            options={
                'verbose_name': '日总能耗',
                'verbose_name_plural': '日总能耗',
                'db_table': 'daily_total_consumption',
                'ordering': ('date',),
            },
        ),
        migrations.CreateModel(
            name='DeviceConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('hub_consumption', models.DecimalField(decimal_places=1, help_text='集控能耗', max_digits=32)),
                ('lamps_consumption', models.DecimalField(decimal_places=1, help_text='灯控能耗', max_digits=32)),
                ('loss_consumption', models.DecimalField(decimal_places=1, help_text='线损能耗', max_digits=32)),
                ('hub', models.OneToOneField(help_text='集控', on_delete=django.db.models.deletion.CASCADE, related_name='hub_device_consumption', to='hub.Hub')),
            ],
            options={
                'verbose_name': '设备能耗',
                'verbose_name_plural': '设备能耗',
                'db_table': 'device_consumption',
                'ordering': ('hub',),
            },
        ),
        migrations.CreateModel(
            name='HubDailyTotalConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('consumption', models.DecimalField(decimal_places=1, help_text='日能耗', max_digits=32)),
                ('date', models.DateField(auto_now_add=True, help_text='日期')),
                ('hub', models.ForeignKey(help_text='集控', on_delete=django.db.models.deletion.CASCADE, related_name='hub_daily_total_consumption', to='hub.Hub')),
            ],
            options={
                'verbose_name': '集控日总能耗',
                'verbose_name_plural': '集控日总能耗',
                'db_table': 'hub_daily_total_consumption',
                'ordering': ('date',),
            },
        ),
        migrations.CreateModel(
            name='HubMonthTotalConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('consumption', models.DecimalField(decimal_places=1, help_text='月能耗', max_digits=32)),
                ('month', models.CharField(help_text='月(2018-06)', max_length=8)),
                ('hub', models.ForeignKey(help_text='集控', on_delete=django.db.models.deletion.CASCADE, related_name='hub_month_total_consumption', to='hub.Hub')),
            ],
            options={
                'verbose_name': '集控月总能耗',
                'verbose_name_plural': '集控月总能耗',
                'db_table': 'hub_month_total_consumption',
                'ordering': ('month',),
            },
        ),
        migrations.CreateModel(
            name='LampCtrlConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('consumption', models.DecimalField(decimal_places=1, help_text='灯控能耗', max_digits=32)),
                ('lampctrl', models.ForeignKey(help_text='灯控', on_delete=django.db.models.deletion.CASCADE, related_name='lampctrl_lamps_consumption', to='lamp.LampCtrl')),
            ],
            options={
                'verbose_name': '灯控能耗',
                'verbose_name_plural': '灯控能耗',
                'db_table': 'lampctrl_consumption',
                'ordering': ('lampctrl',),
            },
        ),
        migrations.CreateModel(
            name='MonthTotalConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('consumption', models.DecimalField(decimal_places=1, help_text='月能耗', max_digits=32)),
                ('month', models.CharField(help_text='月(2018-06)', max_length=8)),
            ],
            options={
                'verbose_name': '月总能耗',
                'verbose_name_plural': '月总能耗',
                'db_table': 'month_total_consumption',
                'ordering': ('month',),
            },
        ),
        migrations.RemoveField(
            model_name='consumption',
            name='hub',
        ),
        migrations.DeleteModel(
            name='TotalPowerConsumption',
        ),
        migrations.DeleteModel(
            name='Consumption',
        ),
    ]
