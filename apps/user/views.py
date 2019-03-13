import re
import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from hub.models import Hub
from user.filters import UserGroupFilter, UserFilter
from user.models import UserGroup, Permission
from user.serializers import (
    UserSerializer, AssignPermissionSerializer, PermissionSerializer,
    UserGroupCreateSerializer, UserGroupDetailSerializer, UpdateGroupSerializer,
    ChangePswSerializer
)
from user.permissions import IsOwnerOrPriority, IsPriority, IsOwner
from utils.paginator import CustomPagination
from utils.mixins import ListModelMixin
from utils.permissions import IsSuperUser


User = get_user_model()


class UserGroupViewSet(ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """
    用户组列表页
    list:
        查看所有用户组
    retrieve:
        查看用户组详情
    create:
        创建一个用户组(权限需要：admin, 管理员)
    update:
        修改用户组信息
    destory:
        删除用户组
    assign_permission:
        修改用户组权限
    """

    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = UserGroupFilter

    def get_permissions(self):
        if self.action in ('create', 'update', 'destory', 'assign_permission'):
            return [IsAuthenticated(), IsSuperUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserGroup.objects.all()
        # 非管理员用户只能看到自己的用户组
        user = self.request.user
        return user.user_group.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserGroupCreateSerializer
        if self.action == 'assign_permission':
            return AssignPermissionSerializer
        return UserGroupDetailSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 用户组中有用户，不允许删除
        if instance.users.filter(is_deleted=False).exists():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE,
                            data={'code': 1, 'message': '用户组不为空，不允许删除'})
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['PUT'], detail=True, url_path='permission')
    def assign_permission(self, request, *args, **kwargs):
        """
        为用户组下的用户批量分配或修改权限，用户组下的用户权限都会被覆盖
        权限需要：admin, 管理员
        {
            "permission": ["hub1", "hub2"]
        }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        users = instance.users.all()
        hubs = serializer.validated_data['permission']
        hubs = Hub.objects.filter(sn__in=hubs)
        try:
            with transaction.atomic():
                for user in users:
                    Permission.objects.filter(user=user).delete()
                    for hub in hubs:
                        Permission.objects.create(user=user, hub=hub)
        except Exception as ex:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': str(ex)})
        return Response()


class UserViewSet(ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    用户列表页
    list:
        查看所有用户
    retrieve:
        获取用户详细信息(个人信息) 获取用户的所有权限()
    create:
        创建用户
    destory:
        删除用户
    set_superuser:
        设置管理员(IsSuperUser)
    cancel_superuser:
        取消管理员(IsPriority)
    set_readonly:
        设置只读用户(IsPriority)
    cancel_readonly:
        取消只读用户(IsPriority)
    set_alert:
        设置接收告警(IsPriority)
    cancel_alert:
        取消接收告警(IsPriority)
    update_group:
        修改用户所属用户组
    enable:
        启用用户(IsPriority)
    disable:
        禁用用户(IsPriority)
    change_password:
        修改用户密码（IsOwn）
    check_password_interval:
        检查上次修改密码时间()
    reset_password:
        重置密码（IsOwnerOrPriority）
    assign_permission:
        为用户分配权限（IsSuperUser）
    """

    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    queryset = User.objects.filter(is_deleted=False)
    # serializer_class = UserSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilter

    def get_queryset(self):
        if self.action == 'list':
            return User.objects.filter(is_deleted=False).exclude(username='admin')
        elif self.action == 'create':
            return User.objects.all()
        elif self.action == 'update':
            return User.objects.all()
        return User.objects.filter(is_deleted=False)

    def get_permissions(self):
        if self.action in ('create', 'destory', 'set_superuser', 'update_group',
                           'assign_permission'):
            return [IsAuthenticated(), IsSuperUser()]
        if self.action in ('cancel_superuser', 'set_readonly',
                           'cancel_readonly', 'set_alert', 'cancel_alert',
                           'enable', 'disable'
                           ):
            return [IsAuthenticated(), IsPriority()]
        if self.action == 'change_password':
            return [IsAuthenticated(), IsOwner()]
        if self.action == 'reset_password':
            return [IsAuthenticated(), IsOwnerOrPriority()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'create', 'destory'):
            return UserSerializer
        if self.action == 'update_group':
            return UpdateGroupSerializer
        if self.action == 'change_password':
            return ChangePswSerializer
        if self.action == 'assign_permission':
            return AssignPermissionSerializer
        return UserSerializer

    def perform_create(self, serializer):
        """已删除用户中有相同用户名"""
        validated_data = serializer.validated_data
        username = validated_data['username']
        # 删除被删除用户
        self.get_queryset().filter(username=username).delete()
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        删除用户
        支持批量删除: DELETE /users/1,2,3/
        权限需要：IsSuper + Priority
        """
        users = kwargs.get('pk')
        # TODO 是否需要验证pk传过来的格式
        for user_id in users.split(','):
            user = User.objects.get(id=user_id)
            if user.username == request.user.username:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'message': '不能删除自己'}
                )
            if user.is_superuser and request.user.username != 'admin':
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'message': '不能删除管理员用户'}
                )
            user.is_deleted = True
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['PUT'], detail=True, url_path='set-superuser')
    def set_superuser(self, request, *args, **kwargs):
        """设置管理员"""
        instance = self.get_object()
        instance.is_superuser = True
        instance.save()
        return Response()

    @action(methods=['PUT'], detail=True, url_path='cancel-superuser')
    def cancel_superuser(self, request, *args, **kwargs):
        """取消管理员"""
        instance = self.get_object()
        instance.is_superuser = False
        instance.save()
        return Response()

    @action(methods=['PUT'], detail=True, url_path='set-readonly')
    def set_readonly(self, request, *args, **kwargs):
        """设置为只读用户"""
        instance = self.get_object()
        instance.read_only_user = True
        instance.save()
        return Response()

    @action(methods=['PUT'], detail=True, url_path='cancel-readonly')
    def cancel_readonly(self, request, *args, **kwargs):
        """取消只读"""
        instance = self.get_object()
        instance.read_only_user = False
        instance.save()
        return Response()

    @action(methods=['PUT'], detail=True, url_path='set-alert')
    def set_alert(self, request, *args, **kwargs):
        """设置接收告警"""
        instance = self.get_object()
        instance.receive_alarm = True
        instance.save()
        return Response()

    @action(methods=['PUT'], detail=True, url_path='cancel-alert')
    def cancel_alert(self, request, *args, **kwargs):
        """取消接收告警"""
        instance = self.get_object()
        instance.receive_alarm = False
        instance.save()
        return Response()

    @action(methods=['PUT'], detail=True, url_path='group')
    def update_group(self, request, *args, **kwargs):
        """修改用户所属用户组
        PUT /users/{id}/group/
        {
            "user_group": 1
        }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['PUT'], detail=True, url_path='enable')
    def enable(self, request, *args, **kwargs):
        """启用用户
        PUT /users/{id}/enable/
        """
        instance = self.get_object()
        instance.is_active = True
        instance.save()
        return Response()

    @action(methods=['PUT'], detail=True, url_path='disable')
    def disable(self, request, *args, **kwargs):
        """禁用用户
        PUT /users/{id}/disable/
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response()

    @action(methods=['PUT'], detail=True, url_path='password')
    def change_password(self, request, *args, **kwargs):
        """修改用户密码
        PUT /users/{id}/password/
        {
            "old_password": "",
            "new_password": ""
        }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path='password-interval')
    def check_password_interval(self, request, *args, **kwargs):
        """检查上次修改密码时间
        GET /users/{id}/password-interval/
        """
        user = request.user
        psw_modified_time = user.password_modified_time
        if psw_modified_time + settings.MODIFY_PSW_INTERVAL < datetime.datetime.now():
            return Response(data={'code': 2, 'message': '已经一个月未修改密码，请及时修改'})
        return Response()

    @action(methods=['PUT'], detail=True, url_path='reset-password')
    def reset_password(self, request, *args, **kwargs):
        """重置密码
        PUT /users/{id}/reset-password/
        """
        instance = self.get_object()
        instance.set_password(settings.DEFAULT_PASSWORD)
        instance.updated_user = request.user
        instance.save()
        return Response()

    @action(methods=['PUT'], detail=True, url_path='permission')
    def assign_permission(self, request, *args, **kwargs):
        """
        为用户分配或修改权限
        PUT /users/{id}/permission/
        {
            "permission": ["hub1", "hub2"]
        }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        hubs = serializer.validated_data['permission']
        hubs = Hub.objects.filter(sn__in=hubs)
        try:
            with transaction.atomic():
                Permission.objects.filter(user=instance).delete()
                for hub in hubs:
                    Permission.objects.create(user=instance, hub=hub)
        except Exception as ex:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={'message': str(ex)})
        return Response()
