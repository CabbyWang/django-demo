#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/14
"""
import requests

from django.contrib.auth.backends import ModelBackend

from rest_framework import status
from rest_framework.response import Response

from rest_framework_jwt import views

from user.models import User


class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username, is_deleted=False)
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class CustomObtainJSONWebToken(views.ObtainJSONWebToken):
    """
    用户登陆
    """

    def post(self, request, *args, **kwargs):
        error = self.wechat_auth(request.data)
        if error:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=error)
        return super(CustomObtainJSONWebToken, self).post(request, *args, **kwargs)

    @staticmethod
    def wechat_auth(request_data):
        """
        微信验证 code2Session
        """
        if 'appid' not in request_data:
            return
        appid, js_code = request_data.get('appid'), request_data.get('js_code')
        secret, grant_type = request_data.get('secret'), request_data.get(
            'grant_type')
        kw_url = "https://api.weixin.qq.com/sns/jscode2session?appid={appid}" \
                 "&secret={secret}&js_code={js_code}&grant_type={grant_type}"
        url = kw_url.format(
            appid=appid,
            secret=secret,
            js_code=js_code,
            grant_typ=grant_type
        )
        res = requests.get(url, verify=False)
        ret_json = res.json()
        errcode, errMsg = ret_json.get("errcode"), ret_json.get("errMsg")
        if not errcode:
            # 验证成功
            return
        return {'errcode': errcode, 'errMsg': errMsg}
