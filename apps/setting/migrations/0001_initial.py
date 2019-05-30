# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-05-29 09:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('option', models.CharField(max_length=255, unique=True, verbose_name='设置名')),
                ('name', models.CharField(max_length=255, verbose_name='设置名(显示)')),
                ('value', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': '系统设置',
                'verbose_name_plural': '系统设置',
                'db_table': 'setting',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='SettingType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('option', models.CharField(max_length=255, unique=True, verbose_name='设置类型名')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': '系统设置分类',
                'verbose_name_plural': '系统设置分类',
                'db_table': 'setting_type',
            },
        ),
        migrations.AddField(
            model_name='setting',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='setting.SettingType'),
        ),
    ]
