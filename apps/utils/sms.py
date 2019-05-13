#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/13
"""
import copy

import requests
from django.conf import settings

from equipment.models import Hub
from setting.models import Setting
from user.models import Permission, User


# TODO 把SMS和Alert完全分离出来 或者再抽象一层


class SMSMetaClass(type):
    """
        元类
    """

    def __new__(cls, name, bases, attrs):
        try:
            sms_type = Setting.objects.get(option="sms_type").value  # 流量通(llt) 互亿无线(hy)
        except Setting.DoesNotExist:
            print('sms_type未配置或出错')
        except Exception:
            pass

        try:
            attrs['account'] = Setting.objects.get(option='{}_sms_account'.format(sms_type)).value
            attrs['password'] = Setting.objects.get(option='{}_sms_pswd'.format(sms_type)).value
            attrs['send_sms'] = attrs.get('_send_sms_{}'.format(sms_type))
        except:
            # TODO 异常处理，可能是配置问题 可能其他问题
            pass
        return type.__new__(cls, name, bases, attrs)


class SMS(object):
    """
        短信类
    """

    __metaclass__ = SMSMetaClass

    @staticmethod
    def get_message(**kwargs):
        """

        :param kwargs: alert_id object_type object event alert_source level
        :return:
        """
        # template = "{}"    # 请及时/处理"
        template = "【天恒智能】 {}"    # 请及时处理"
        # template = "【天恒智能】%s"    # 告警已解除"

        kw = copy.deepcopy(kwargs)
        object_type = '集控' if kwargs.get('object_type') == 'hub' else '节点'
        level = kwargs.get('level')
        if str(level) == '1':
            level = '警告'
        elif str(level) == '2':
            level = '故障'
        elif str(level) == '3':
            level = '严重故障'
        kw.update(object_type=object_type)
        text = "告警编号{alert_id}，{object_type}{object} {event}" \
               "告警源{alert_source}，级别：{level}".format(**kw)
        message = template.format(text)
        return message

    def send_msgs(self, **kwargs):
        message = self.get_message(**kwargs)
        for mobile in kwargs.get("mobiles"):
            self.send_sms(mobile, message)

    def _send_sms_llt(self, mobile, message):
        """发送短信(流量通)"""
        payload = {
            "account": self.account,
            "pswd": self.password,
            "mobile": mobile,
            "msg": message,
            "needstatus": True
        }
        print(requests.get('http://118.31.188.220/msg/HttpBatchSendSM', params=payload).content)

    def _send_sms_hy(self, mobile, message):
        """发送短信(互亿无线)"""
        # TODO 互亿无线接口需要修改(python2 to python3)
        return
        # data = {'account': self.account, 'password': self.password, 'content': message, 'mobile': mobile, 'format': 'json'}
        # req = urllib2.urlopen(
        #     url='http://106.ihuyi.com/webservice/sms.php?method=Submit',
        #     data=urllib.urlencode(data)
        # )
        # content = req.read()
        # print(content)
        # return content


def get_receivers(hub_sn):
    """
    根据集控sn获取负责该集控的联系人
    :param hub_sn: 集控编号
    :return: 能接收到告警的mobile列表
    """
    print('hub_sn = {}'.format(hub_sn))
    hub = Hub.objects.filter_by(sn=hub_sn).first()
    if not hub:
        return []
    return list(filter(lambda x: x,
                hub.users.filter_by().values_list('mobile', flat=True)))


def send_alert_sms(**kw):
    """发送告警短信"""
    if not settings.ENABLE_ALERT_SMS:
        return
    params = copy.deepcopy(kw)
    hub_sn = params.get('alert_source')
    receivers = get_receivers(hub_sn=hub_sn)
    params['alert_id'] = params.get('id')
    params['mobiles'] = receivers
    try:
        sms = SMS()
        sms.send_msgs(**kw)

    except Exception as ex:
        print(str(ex))
        print('error occured when send message')
