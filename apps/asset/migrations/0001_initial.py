# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-02 17:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lamp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cable',
            fields=[
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('sn', models.CharField(help_text='编号', max_length=32, primary_key=True, serialize=False)),
                ('vendor', models.CharField(help_text='厂家名称', max_length=32)),
                ('model', models.CharField(help_text='型号', max_length=32)),
                ('length', models.FloatField(help_text='长度')),
                ('date', models.DateField(help_text='购买时间')),
                ('address', models.CharField(blank=True, help_text='安装地址', max_length=32, null=True)),
                ('memo', models.CharField(blank=True, help_text='备注', max_length=64, null=True)),
            ],
            options={
                'verbose_name': '电缆',
                'verbose_name_plural': '电缆',
                'db_table': 'cable',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='CBox',
            fields=[
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('sn', models.CharField(help_text='编号', max_length=32, primary_key=True, serialize=False)),
                ('vendor', models.CharField(help_text='厂家名称', max_length=32)),
                ('model', models.CharField(help_text='型号', max_length=32)),
                ('date', models.DateField(help_text='购买时间')),
                ('longitude', models.FloatField(help_text='经度')),
                ('latitude', models.FloatField(help_text='纬度')),
                ('address', models.CharField(blank=True, help_text='安装地址', max_length=32, null=True)),
                ('memo', models.CharField(blank=True, help_text='备注', max_length=64, null=True)),
                ('is_used', models.BooleanField(default=False, help_text='是否已用')),
            ],
            options={
                'verbose_name': '控制箱',
                'verbose_name_plural': '控制箱',
                'db_table': 'cbox',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='CBoxImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('image', models.ImageField(upload_to='asset/cbox/', verbose_name='控制箱图片')),
            ],
            options={
                'verbose_name': '控制箱图片',
                'verbose_name_plural': '控制箱图片',
                'db_table': 'cbox_image',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='Lamp',
            fields=[
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('sn', models.CharField(help_text='编号', max_length=32, primary_key=True, serialize=False)),
                ('vendor', models.CharField(help_text='厂家名称', max_length=32)),
                ('model', models.CharField(help_text='型号', max_length=32)),
                ('date', models.DateField(help_text='购买时间')),
                ('address', models.CharField(blank=True, help_text='安装地址', max_length=32, null=True)),
                ('memo', models.CharField(blank=True, help_text='备注', max_length=64, null=True)),
                ('is_used', models.BooleanField(default=False, help_text='是否已用')),
            ],
            options={
                'verbose_name': '灯具',
                'verbose_name_plural': '灯具',
                'db_table': 'lamp',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='LampImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('image', models.ImageField(upload_to='asset/lamp/', verbose_name='灯具图片')),
            ],
            options={
                'verbose_name': '灯具图片',
                'verbose_name_plural': '灯具图片',
                'db_table': 'lamp_image',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='Pole',
            fields=[
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('sn', models.CharField(help_text='编号', max_length=32, primary_key=True, serialize=False)),
                ('vendor', models.CharField(help_text='厂家名称', max_length=32)),
                ('model', models.CharField(help_text='型号', max_length=32)),
                ('height', models.FloatField(help_text='高度')),
                ('date', models.DateField(help_text='购买时间')),
                ('longitude', models.FloatField(help_text='经度')),
                ('latitude', models.FloatField(help_text='纬度')),
                ('address', models.CharField(blank=True, help_text='安装地址', max_length=32, null=True)),
                ('memo', models.CharField(blank=True, help_text='备注', max_length=64, null=True)),
                ('is_used', models.BooleanField(default=False, help_text='是否已用')),
            ],
            options={
                'verbose_name': '灯杆',
                'verbose_name_plural': '灯杆',
                'db_table': 'pole',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='PoleImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('image', models.ImageField(upload_to='asset/pole/', verbose_name='灯杆图片')),
            ],
            options={
                'verbose_name': '灯杆图片',
                'verbose_name_plural': '灯杆图片',
                'db_table': 'pole_image',
                'ordering': ['-created_time'],
            },
        ),
        migrations.AddField(
            model_name='pole',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.PoleImage'),
        ),
        migrations.AddField(
            model_name='lamp',
            name='bearer',
            field=models.ForeignKey(help_text='灯杆编号', on_delete=django.db.models.deletion.CASCADE, related_name='pole_lamp', to='asset.Pole'),
        ),
        migrations.AddField(
            model_name='lamp',
            name='controller',
            field=models.ForeignKey(help_text='灯控编号', on_delete=django.db.models.deletion.CASCADE, related_name='lampctrl_lamp', to='lamp.LampCtrl'),
        ),
        migrations.AddField(
            model_name='lamp',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.LampImage'),
        ),
        migrations.AddField(
            model_name='cbox',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.CBoxImage'),
        ),
    ]
