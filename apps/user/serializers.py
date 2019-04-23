#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/14
"""
import datetime
import re

from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _

from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer, \
    jwt_payload_handler, jwt_encode_handler
from rest_framework.validators import UniqueValidator

from hub.models import Hub
from django.conf import settings
from user.models import UserGroup, User, Permission
from utils.exceptions import InvalidInputError


class LoginSerializer(JSONWebTokenSerializer):

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    # raise serializers.ValidationError(msg)
                    raise InvalidInputError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                # raise serializers.ValidationError(msg)
                raise InvalidInputError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            # raise serializers.ValidationError(msg)
            raise InvalidInputError(msg)


class UserSerializer(serializers.ModelSerializer):
    user_group = serializers.PrimaryKeyRelatedField(required=True, queryset=UserGroup.objects.filter_by())
    # TODO 尝试重写serializers.ValidationError定制化提示信息
    # username = serializers.CharField(
    #     required=True,
    #     validators=[UniqueValidator(queryset=User.objects.filter_by(),
    #                 message="用户名已存在")]
    # )
    password = serializers.CharField(
        required=True,
        min_length=8,
        style={'input_type': 'password'},
        write_only=True,
        error_messages={
            "min_length": "密码长度不能小于8位"
        },
    )
    mobile = serializers.CharField()
    email = serializers.CharField(
        required=True,
    )
    updated_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    permission = serializers.SerializerMethodField()
    username = serializers.CharField(required=True)

    @staticmethod
    def validate_username(username):
        # 验证用户名
        if User.objects.filter_by(username=username).exists():
            raise InvalidInputError('用户名已存在')
        return username

    @staticmethod
    def validate_mobile(mobile):
        # 验证手机号码
        if not re.match(settings.REGEX_MOBILE, mobile):
            raise InvalidInputError('请输入有效的手机号码')
        return mobile

    @staticmethod
    def get_permission(obj):
        """
        获取用户权限(即用户拥有的集控列表)，与用户信息一同返回
        """
        permissions = obj.user_permission.all()
        return [p.hub.sn for p in permissions]

    def create(self, validated_data):
        instance = super(UserSerializer, self).create(validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'organization', 'email', 'mobile',
            'user_group', 'is_superuser', 'is_read_only', 'is_active',
            'is_receive_alarm', 'permission', 'updated_user'
        )


class UserDetailSerializer(UserSerializer):
    user_group = serializers.SlugRelatedField(
        queryset=UserGroup.objects.filter_by(),
        slug_field='name'
    )


class UserGroupDetailSerializer(serializers.ModelSerializer):
    users = UserSerializer(required=False, many=True)

    class Meta:
        model = UserGroup
        fields = ("id", "name", 'memo', 'users')


class UserGroupSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(
    #     required=True,
    #     validators=[
    #         UniqueValidator(queryset=UserGroup.objects.filter_by(),
    #                         message="用户组名已存在")
    #     ]
    # )
    name = serializers.CharField(required=True)

    @staticmethod
    def validate_name(name):
        if UserGroup.objects.filter_by(name=name).exists():
            raise InvalidInputError('user group name [{}] has been existed'.format(name))
        return name

    class Meta:
        model = UserGroup
        fields = ("name", "memo")


class AssignPermissionSerializer(serializers.Serializer):
    permission = serializers.ListField()

    @staticmethod
    def validate_permission(hubs):
        for hub_sn in hubs:
            if not Hub.objects.filter_by(sn=hub_sn).exists():
                raise InvalidInputError("集控[{}]不存在".format(hub_sn))
        return hubs


class PermissionSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    hub_sn = serializers.CharField(required=True)

    class Meta:
        model = Permission
        fields = ('id', 'user_id', 'hub_sn')


class UpdateGroupSerializer(serializers.ModelSerializer):
    user_group = serializers.PrimaryKeyRelatedField(required=True, queryset=UserGroup.objects.filter_by())

    class Meta:
        model = UserGroup
        fields = ("user_group", )


class ChangeProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


class MyBaseSerializer(serializers.ModelSerializer):
    """
    单独设置权限序列化类(基类)
    """
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)
    mobile = serializers.CharField(required=False, allow_blank=True)
    user_group = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = '__all__'


class ChangePswSerializer(MyBaseSerializer):
    old_password = serializers.CharField(required=True, min_length=8, write_only=True)
    new_password = serializers.CharField(required=True, min_length=8, write_only=True)
    updated_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    password_modified_time = serializers.HiddenField(
        default=datetime.datetime.now()
    )

    def validate_old_password(self, password):
        request = self.context['request']
        user = request.user
        if not user.check_password(password):
            raise InvalidInputError("原密码错误")
        return password

    def validate_new_password(self, password):
        if password == self.initial_data['old_password']:
            raise InvalidInputError("新密码与原密码一致")
        return password

    def update(self, instance, validated_data):

        instance = super(ChangePswSerializer, self).update(instance, validated_data)

        # TODO 是否可以通过signal来完成
        password = validated_data['password']
        instance.set_password(password)
        instance.save()
        return instance

    def validate(self, attrs):
        attrs['password'] = attrs['new_password']
        for k, v in attrs.items():
            if k in ('password', 'new_password', 'old_password'):
                continue
            attrs[k] = getattr(self.instance, k)
        return attrs


class ChangeProfileSerializer(MyBaseSerializer):

    mobile = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    organization = serializers.CharField(required=True)

    def validate(self, attrs):
        for k, v in attrs.items():
            if k in ('mobile', 'email', 'organization'):
                continue
            attrs[k] = getattr(self.instance, k)
        return attrs


class SetReadonlySerializer(MyBaseSerializer):
    """设置是否为只读用户"""

    is_read_only = serializers.BooleanField(required=True)

    def validate(self, attrs):
        for k, v in attrs.items():
            if k == 'is_read_only':
                continue
            attrs[k] = getattr(self.instance, k)
        return attrs


class SetReceiveAlarmSerializer(MyBaseSerializer):
    """设置是否接受告警语音"""

    is_receive_alarm = serializers.BooleanField(required=True)

    def validate(self, attrs):
        for k, v in attrs.items():
            if k == 'is_receive_alarm':
                continue
            attrs[k] = getattr(self.instance, k)
        return attrs


class SetActiveSerializer(MyBaseSerializer):
    """设置是否被激活"""

    is_active = serializers.BooleanField(required=True)

    def validate(self, attrs):
        for k, v in attrs.items():
            if k == 'is_active':
                continue
            attrs[k] = getattr(self.instance, k)
        return attrs
