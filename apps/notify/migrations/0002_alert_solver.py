# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-11 14:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notify', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='solver',
            field=models.ForeignKey(blank=True, db_column='solver', help_text='处理人员', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='solved_alert', to=settings.AUTH_USER_MODEL),
        ),
    ]
