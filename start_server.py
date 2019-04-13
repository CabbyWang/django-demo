#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 
"""
import os
# import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartlamp.settings")

import django

django.setup()

from twisted.internet import reactor, task

from network_service.server import ServerFactory
from network_service.config import LISTEN_PORT

# BASE_DIR = os.path.dirname(__file__)

# sys.path.append(os.path.join(BASE_DIR, "network_service"))


if __name__ == '__main__':
    factory = ServerFactory()

    task1 = task.LoopingCall(factory.check_users_online)  # 加入一个循环任务，循环检测心跳
    task1.start(61, now=False)  # 每隔61秒检查一次心跳

    reactor.listenTCP(LISTEN_PORT, factory)
    reactor.run()
