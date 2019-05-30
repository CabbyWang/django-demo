#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/14
"""
import requests
from datetime import datetime

from django.contrib.auth.backends import ModelBackend

from rest_framework import status
from rest_framework.response import Response

from rest_framework_jwt import views
from rest_framework_jwt.settings import api_settings

from user.models import User
from user.serializers import LoginSerializer


class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.filter_by(username=username).first()
            a = user.check_password(password)
            if user.check_password(password):
                return user
        except Exception as e:
            return None


jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class CustomObtainJSONWebToken(views.ObtainJSONWebToken):
    """
    用户登陆
    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        error = self.wechat_auth(request.data)
        if error:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=error)
        # return super(CustomObtainJSONWebToken, self).post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.object.get('user') or request.user
        token = serializer.object.get('token')
        response_data = jwt_response_payload_handler(token, user, request)
        response = Response(response_data)
        if api_settings.JWT_AUTH_COOKIE:
            expiration = (datetime.utcnow() +
                          api_settings.JWT_EXPIRATION_DELTA)
            response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                token,
                                expires=expiration,
                                httponly=True)
        return response

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
