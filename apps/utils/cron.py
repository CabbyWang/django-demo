#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/12
"""

"""
django-crontab

1. add all defined jobs from CRONJOBS to crontab.
    `python manage.py crontab add`
2. show current active jobs of this project.
    `python manage.py crontab show`
3. removing all defined jobs.
    `python manage.py crontab remove`
"""

from status.models import HubStatus
from lamp.models import LampCtrlStatus


def calculate_energy():
    """
    根据HubStatus和LampCtrlStauts表计算出能耗， 填充report相关表
    DailyTotalConsumption, HubDailyTotalConsumption, MonthTotalConsumption,
    HubMonthTotalConsumption, DeviceConsumption, LampCtrlConsumption
    """
    # TODO 定时任务 填充report相关表
    pass
