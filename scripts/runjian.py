#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/29
"""


# 1、登录接口
# 2、获取灯杆动态数据接口
# 3、控制灯杆接口
# 4、获取告警信息接口
import json

import requests


class Api(object):

    def __init__(self):
        self._token = None
        self._cookie = None

    def get_token_cookie(self):
        """登录接口"""
        login_url = "https://solariot.iot2.creekspring.com/api/v1/auth/login"
        hearders = {"content-type": "application/json"}
        body = {"username": "thzn", "password": "12345678"}
        res = requests.post(login_url, data=json.dumps(body),
                            headers=hearders)
        status_code = res.status_code
        if status_code != 200:
            # 登录失败
            print('login failed...')
            return
        cookie = res.headers.get('set-cookie')
        ret_data = res.json()
        token = ret_data.get('accessToken')
        return token, cookie

    def get_device_data(self):
        """获取设备详细信息接口"""
        url = "https://solariot.iot2.creekspring.com/api/v2/solar-motes/pagi"
        params = dict(
            projectId=1332,
            pageNo=1,
            pageSize=10,
            isDisabled=True,
            name=None,
            groupId=None
        )
        headers = {
            "content-type": "application/json",
            "authorization": "Bearer {}".format(self._token),
            "cookie": self._cookie
        }
        res = requests.get(url, params=params, headers=headers)
        if res.status_code == 401:
            self._token, self._cookie = self.get_token_cookie()
            self.get_device_data()
        elif res.status_code == 200:
            ret_data = res.json()
            print(ret_data)

    def control_device(self):
        """开启/关闭设备接口  1:开启 2:关闭 3:调光"""
        url = "https://solariot.iot2.creekspring.com/api/v2/device-downs/switch-control/44608"
        data = {"switchState": 1, "brightness": 44}
        headers = {
            "content-type": "application/json",
            "Authorization": "Bearer {}".format(self._token),
            "cookie": self._cookie
        }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        if res.status_code == 401:
            self._token, self._cookie = self.get_token_cookie()
            self.control_device()
        elif res.status_code == 200:
            ret_data = res.json()
            print(ret_data)

    def get_alert_data(self):
        """获取告警信息接口"""
        url = "https://solariot.iot2.creekspring.com/api/v2/solar-alerts/pagi"
        params = dict(
            projectId=1332,
            pageNo=1,
            pageSize=10,
            name=None,
            alertStatus=None,
            beginDate=None,
            endDate=None
        )
        headers = {
            # "content-type": "application/json",
            "authorization": "Bearer {}".format(self._token),
            "cookie": self._cookie
        }
        res = requests.get(url, params=params, headers=headers)
        if res.status_code == 401:
            self._token, self._cookie = self.get_token_cookie()
            self.get_alert_data()
        elif res.status_code == 200:
            ret_data = res.json()
            print(ret_data)


if __name__ == '__main__':
    api = Api()
    # api.get_alert_data()
    # api.get_device_data()
    api.control_device()
