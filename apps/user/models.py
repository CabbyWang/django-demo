from django.db import models
from django.contrib.auth.models import AbstractUser

from equipment.models import Hub
from base.models import BaseModel, MyAbstractUser


class UserGroup(BaseModel):
    """
    用户组
    """
    name = models.CharField(max_length=32, verbose_name='用户组名', help_text='用户组名')
    memo = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注', help_text='备注')

    class Meta:
        verbose_name = "用户组"
        verbose_name_plural = verbose_name
        ordering = ('created_time', )
        db_table = "usergroup"

    def __str__(self):
        return self.name

    def exists_users(self):
        return self.users.filter(is_deleted=False)


class User(MyAbstractUser):
    """
    用户
    """
    # TODO 用户名username需要重写， unique改为False 逻辑删除后 允许添加被删除的同名用户
    username = models.CharField(max_length=32)
    hubs = models.ManyToManyField(Hub, related_name='users', through='Permission')
    mobile = models.CharField(max_length=11, verbose_name="电话")
    is_read_only = models.BooleanField(default=False, verbose_name="只读用户")
    is_receive_alarm = models.BooleanField(default=False, verbose_name="接收告警")
    password_modified_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="密码修改时间")
    user_group = models.ForeignKey(UserGroup, related_name='users', null=True, blank=True, verbose_name="用户组")
    updated_user = models.ForeignKey("self", null=True, blank=True, verbose_name="修改者")
    organization = models.CharField(max_length=255, null=True, blank=True, verbose_name="组织")
    memo = models.CharField(max_length=255, null=True, blank=True, verbose_name="备注")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ('created_time', )
        db_table = "user"

    def __str__(self):
        return self.username


class Permission(BaseModel):
    """
    用户权限
    """
    user = models.ForeignKey(User, related_name='user_permission')
    hub = models.ForeignKey(Hub, related_name='hub_permision')

    class Meta:
        verbose_name = "用户权限"
        verbose_name_plural = verbose_name
        ordering = ('created_time',)
        db_table = "permission"

    def __str__(self):
        return self.user.username
