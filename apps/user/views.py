import re
import datetime

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from equipment.models import Hub
from user.filters import UserGroupFilter, UserFilter
from user.models import UserGroup, Permission
from user.serializers import (
    UserSerializer, AssignPermissionSerializer, PermissionSerializer,
    UserGroupDetailSerializer, UpdateGroupSerializer, ChangePswSerializer,
    UserGroupSerializer, UserDetailSerializer, SetReadonlySerializer,
    SetReceiveAlarmSerializer, SetActiveSerializer, ChangeProfileSerializer)
from user.permissions import IsOwnerOrPriority, IsPriority, IsOwner
from utils.paginator import CustomPagination
from utils.mixins import ListModelMixin
from utils.permissions import IsSuperUser, IsAdminUser


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
    destroy:
        删除用户组
    assign_permission:
        修改用户组权限
    """

    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = UserGroupFilter
    ordering_fields = ('created_time', 'name')

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy', 'assign_permission'):
            return [IsAuthenticated(), IsSuperUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserGroup.objects.filter_by()
        # 非管理员用户只能看到自己的用户组
        user = self.request.user
        return UserGroup.objects.filter(id=user.user_group.id)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserGroupDetailSerializer
        if self.action == 'assign_permission':
            return AssignPermissionSerializer
        return UserGroupSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 用户组中有用户，不允许删除
        if instance.users.filter(is_deleted=False).exists():
            # 用户组不为空，不允许删除
            msg = _("can't delete user group that has users")
            raise serializers.ValidationError(msg)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.soft_delete()

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
        hubs = Hub.objects.filter_by(sn__in=hubs)
        try:
            with transaction.atomic():
                for user in users:
                    Permission.objects.filter_by(user=user).delete()
                    for hub in hubs:
                        Permission.objects.create(user=user, hub=hub)
        except Exception as ex:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={'detail': str(ex), 'message': str(ex)}
            )
        return Response()


class UserViewSet(ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
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
    destroy:
        删除用户(IsPriority)
    set_superuser:
        设置管理员(IsSuperUser)
    cancel_superuser:
        取消管理员(IsPriority)
    set_read_only:
        设置是否为只读用户(IsPriority)
    set_receive_alarm:
        设置是否接收告警短信(IsPriority)
    set_active:
        设置是否激活用户(IsPriority)
    change_profile:
        修改个人信息(IsOwn)
    update_group:
        修改用户所属用户组
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
    queryset = User.objects.filter_by()
    # serializer_class = UserSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filter_class = UserFilter

    def get_queryset(self):
        if self.action == 'list':
            return User.objects.filter_by().exclude(username='admin')
        elif self.action == 'create':
            return User.objects.filter_by()
        elif self.action == 'update':
            return User.objects.filter_by()
        return User.objects.filter_by()

    def get_permissions(self):
        if self.action in ('update', ):
            return [IsAuthenticated(), IsAdminUser()]
        if self.action in (
            'create', 'set_superuser', 'update_group',
            'assign_permission'
        ):
            return [IsAuthenticated(), IsSuperUser()]
        if self.action in (
            'cancel_superuser', 'set_read_only',
            'set_receive_alarm', 'set_active', 'destroy'
        ):
            return [IsAuthenticated(), IsPriority()]
        if self.action in ('change_profile', 'change_password'):
            return [IsAuthenticated(), IsOwner()]
        if self.action == 'reset_password':
            return [IsAuthenticated(), IsOwnerOrPriority()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserDetailSerializer
        if self.action == 'update_group':
            return UpdateGroupSerializer
        if self.action == 'change_password':
            return ChangePswSerializer
        if self.action == 'change_profile':
            return ChangeProfileSerializer
        # if self.action == 'reset_password':
        #     return ResetPswSerializer
        if self.action == 'assign_permission':
            return AssignPermissionSerializer
        if self.action == 'set_read_only':
            return SetReadonlySerializer
        if self.action == 'set_receive_alarm':
            return SetReceiveAlarmSerializer
        if self.action == 'set_active':
            return SetActiveSerializer
        return UserSerializer

    def get_object(self):
        if self.action in ('change_profile', 'change_password'):
            return self.request.user
        return super(UserViewSet, self).get_object()

    def perform_create(self, serializer):
        """已删除用户中有相同用户名, 直接覆盖"""
        validated_data = serializer.validated_data
        username = validated_data['username']
        # 删除被删除用户
        User.objects.filter(username=username).delete()
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
            user = User.objects.filter_by(id=user_id).first()
            if not user:
                continue
            if user.username == request.user.username:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'detail': '不能删除自己'}
                )
            if user.is_superuser and request.user.username != 'admin':
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'detail': '不能删除管理员用户'}
                )
            user.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['PUT'], detail=True, url_path='hf')
    def xxx(self, request, *args, **kwargs):
        """恢复已删除用户
        PUT /users/{id}/group/
        {
            "is_deleted": 1
        }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['PUT'], detail=True, url_path='set-superuser')
    def set_superuser(self, request, *args, **kwargs):
        """设置管理员"""
        # TODO 修改实现方式， 参考set_ready_only
        instance = self.get_object()
        if instance.is_read_only:
            # 只读用户不能设置为管理员
            msg = _("read_only users can't be set to superuser")
            raise serializers.ValidationError(msg)
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

    @action(methods=['PUT'], detail=True, url_path='read-only')
    def set_read_only(self, request, *args, **kwargs):
        """设置是否为只读用户
        PUT /users/{id}/read-only/
        {
            "is_read_only": true
        }
        """
        return super(UserViewSet, self).update(request, *args, **kwargs)

    @action(methods=['PUT'], detail=True, url_path='receive-alarm')
    def set_receive_alarm(self, request, *args, **kwargs):
        """设置是否接收告警短信
        PUT /users/{id}/receive-alarm/
        {
            "is_receive_alarm": true
        }
        """
        return super(UserViewSet, self).update(request, *args, **kwargs)

    @action(methods=['PUT'], detail=True, url_path='active')
    def set_active(self, request, *args, **kwargs):
        """设置是否激活用户
        PUT /users/{id}/active/
        {
            "is_active": true
        }
        """
        return super(UserViewSet, self).update(request, *args, **kwargs)

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

    @action(methods=['PUT'], detail=False, url_path='profile')
    def change_profile(self, request, *args, **kwargs):
        """
        修改个人信息(IsOwn)
        PUT /users/profile/
        {
            "mobile": "",
            "email" "",
            "organization": ""
        }
        """
        return super(UserViewSet, self).update(request, *args, **kwargs)

    @action(methods=['PUT'], detail=False, url_path='password')
    def change_password(self, request, *args, **kwargs):
        """修改用户密码
        PUT /users/password/
        {
            "old_password": "",
            "new_password": ""
        }
        """
        return super(UserViewSet, self).update(request, *args, **kwargs)

    @action(methods=['GET'], detail=True, url_path='password-interval')
    def check_password_interval(self, request, *args, **kwargs):
        """检查上次修改密码时间
        GET /users/{id}/password-interval/
        """
        user = request.user
        psw_modified_time = user.password_modified_time
        if psw_modified_time + settings.MODIFY_PSW_INTERVAL < datetime.datetime.now():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail': '已经一个月未修改密码，请及时修改'})
        return Response()

    @action(methods=['PUT'], detail=True, url_path='reset-password')
    def reset_password(self, request, *args, **kwargs):
        """重置密码
        PUT /users/{id}/reset-password/
        """
        default_psw = settings.DEFAULT_PASSWORD
        instance = self.get_object()
        instance.set_password(default_psw)
        instance.updated_user = request.user
        instance.save()
        return Response(data={"password": default_psw})

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
        hubs = Hub.objects.filter_by(sn__in=hubs)
        try:
            with transaction.atomic():
                Permission.objects.filter_by(user=instance).delete()
                for hub in hubs:
                    Permission.objects.create(user=instance, hub=hub)
        except Exception as ex:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={'detail': str(ex)})
        return Response()
