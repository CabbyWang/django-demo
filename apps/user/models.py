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
        db_table = "user_group"

    def __str__(self):
        return self.name

    def exists_users(self):
        return self.users.filter(is_deleted=False)


class User(MyAbstractUser):
    """
    用户
    """
    # TODO 用户名username需要重写， unique改为False 逻辑删除后 允许添加被删除的同名用户
    username = models.CharField(max_length=32, verbose_name="用户名")
    hubs = models.ManyToManyField(Hub, related_name='users', through='Permission')
    mobile = models.CharField(max_length=11, verbose_name="电话")
    is_read_only = models.BooleanField(default=False, verbose_name="是否只读用户")
    is_receive_alarm = models.BooleanField(default=False, verbose_name="是否接收告警")
    password_modified_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="密码修改时间")
    user_group = models.ForeignKey(UserGroup, related_name='users', null=True, blank=True, verbose_name="用户组编号")
    updated_user = models.ForeignKey("self", db_column='updated_user', null=True, blank=True, verbose_name="修改者")
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
    user = models.ForeignKey(User, related_name='user_permission', verbose_name="用户编号")
    hub = models.ForeignKey(Hub, db_column='hub_sn', related_name='hub_permision', verbose_name="集控编号")

    class Meta:
        verbose_name = "用户权限"
        verbose_name_plural = verbose_name
        ordering = ('created_time',)
        db_table = "permission"

    def __str__(self):
        return self.user.username
