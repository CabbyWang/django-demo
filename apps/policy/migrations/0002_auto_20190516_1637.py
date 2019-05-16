# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-05-16 16:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('policy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='policyset',
            name='creator',
            field=models.ForeignKey(blank=True, db_column='creator', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_policysets', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='policyset',
            name='policys',
            field=models.ManyToManyField(through='policy.PolicySetRelation', to='policy.Policy'),
        ),
        migrations.AddField(
            model_name='policy',
            name='creator',
            field=models.ForeignKey(blank=True, db_column='creator', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_policys', to=settings.AUTH_USER_MODEL),
        ),
    ]
