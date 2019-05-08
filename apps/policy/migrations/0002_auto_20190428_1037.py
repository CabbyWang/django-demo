# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-28 10:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policy', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policysetsenddown',
            name='group_id',
        ),
        migrations.AddField(
            model_name='policysetsenddown',
            name='group_num',
            field=models.IntegerField(default=0, help_text='分组编号'),
            preserve_default=False,
        ),
    ]