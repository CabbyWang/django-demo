#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/14
"""
import datetime
import re

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from hub.models import Hub
from django.conf import settings
from user.models import UserGroup, User, Permission
from utils.exceptions import InvalidInputError


class UserSerializer(serializers.ModelSerializer):
    user_group = serializers.PrimaryKeyRelatedField(required=True, queryset=UserGroup.objects.filter_by())
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.filter_by(),
                    message="用户名已存在")]
    )
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

    @staticmethod
    def validate_mobile(mobile):
        # 验证手机号码
        if not re.match(settings.REGEX_MOBILE, mobile):
            raise serializers.ValidationError('请输入有效的手机号码')
        return mobile

    @staticmethod
    def get_permission(obj):
        """
        获取用户权限(即用户拥有的集控列表)，与用户信息一同返回
        """
        permissions = obj.user_permission.all()
        return [p.hub.sn for p in permissions]

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'organization', 'email', 'mobile',
            'user_group', 'is_superuser', 'read_only_user', 'is_active',
            'receive_alarm', 'permission', 'updated_user'
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
                raise serializers.ValidationError("集控[{}]不存在".format(hub_sn))
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


class ChangePswSerializer(serializers.ModelSerializer):
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
            raise serializers.ValidationError("原密码错误")
        return password

    def validate_new_password(self, password):
        if password == self.initial_data['old_password']:
            raise serializers.ValidationError("新密码与原密码一致")
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
        return attrs

    class Meta:
        model = User
        fields = ("old_password", "new_password", "updated_user", "password_modified_time")
