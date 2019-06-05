# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-04 18:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('equipment', '0001_initial'),
        ('notify', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('memo', models.CharField(max_length=1023, null=True)),
                ('hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hub_inspetion', to='equipment.Hub')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_inspection', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '巡检',
                'verbose_name_plural': '巡检',
                'db_table': 'inspection',
                'ordering': ('-created_time',),
            },
        ),
        migrations.CreateModel(
            name='InspectionImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('file', models.ImageField(upload_to='inspection')),
                ('inspection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inspection_image', to='workorder.Inspection')),
            ],
            options={
                'verbose_name': '巡检图片',
                'verbose_name_plural': '巡检图片',
                'db_table': 'inspectionimage',
            },
        ),
        migrations.CreateModel(
            name='InspectionItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('status', models.IntegerField(choices=[(1, '正常'), (2, '故障')])),
                ('memo', models.CharField(blank=True, max_length=1023, null=True)),
                ('hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hub_inspection_item', to='equipment.Hub')),
                ('inspection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inspection_item', to='workorder.Inspection')),
                ('lampctrl', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lampctrl_inspection_item', to='equipment.LampCtrl')),
            ],
            options={
                'verbose_name': '巡检具体项',
                'verbose_name_plural': '巡检具体项',
                'db_table': 'inspectionitem',
                'ordering': ('hub', 'lampctrl'),
            },
        ),
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('type', models.IntegerField(choices=[(0, 'others'), (1, 'hub'), (2, 'lampctrl'), (3, 'lamp'), (4, 'pole'), (5, 'cable'), (6, 'cbox')], help_text='工单类型')),
                ('obj_sn', models.CharField(blank=True, help_text='对象编号', max_length=32, null=True)),
                ('memo', models.CharField(max_length=255, verbose_name='备注')),
                ('status', models.CharField(choices=[('todo', '未处理'), ('doing', '处理中'), ('finished', '已处理')], default='todo', max_length=16)),
                ('description', models.CharField(blank=True, help_text='处理结果描述', max_length=255, null=True)),
                ('finished_time', models.DateTimeField(blank=True, null=True)),
                ('alert', models.OneToOneField(blank=True, help_text='告警编号', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alert_workorder', to='notify.Alert')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_workorder', to=settings.AUTH_USER_MODEL, verbose_name='处理人')),
            ],
            options={
                'verbose_name': '工单',
                'verbose_name_plural': '工单',
                'db_table': 'workorder',
                'ordering': ('-created_time',),
            },
        ),
        migrations.CreateModel(
            name='WorkOrderAudio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('audio', models.FileField(upload_to='audio', verbose_name='工单语音')),
                ('times', models.IntegerField(default=0)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='workorder_audio', to='workorder.WorkOrder')),
            ],
            options={
                'verbose_name': '工单语音',
                'verbose_name_plural': '工单语音',
                'db_table': 'workorder_audio',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='WorkorderImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='是否删除', verbose_name='是否删除')),
                ('created_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, help_text='更新时间', null=True, verbose_name='更新时间')),
                ('deleted_time', models.DateTimeField(blank=True, db_index=True, help_text='删除时间', null=True, verbose_name='删除时间')),
                ('file', models.ImageField(upload_to='workorder')),
                ('image_type', models.IntegerField(choices=[(0, '无'), (1, '维修问题描述图片'), (2, '工单处理图片')], default=0)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workorder_image', to='workorder.WorkOrder')),
            ],
            options={
                'verbose_name': '工单图片',
                'verbose_name_plural': '工单图片',
                'db_table': 'workorderimage',
            },
        ),
    ]
