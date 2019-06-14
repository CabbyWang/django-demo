from django.db import models
from django.contrib.auth import get_user_model

from base.models import BaseModel


User = get_user_model()


class SettingType(BaseModel):
    """
    系统设置分类
    """
    option = models.CharField(max_length=255, unique=True,
                              verbose_name='设置类型名')
    name = models.CharField(max_length=255, verbose_name='设置类型名(显示)')

    class Meta:
        verbose_name = '系统设置分类'
        verbose_name_plural = verbose_name
        db_table = "setting_type"

    def __str__(self):
        return self.name


class Setting(BaseModel):
    """
    系统设置
    """
    option = models.CharField(max_length=255, unique=True,
                              verbose_name='设置名')
    name = models.CharField(max_length=255, verbose_name='设置名(显示)')
    value = models.CharField(max_length=255, verbose_name='值')
    type = models.ForeignKey(SettingType, db_column='type', related_name='settings', verbose_name='设置类型')

    class Meta:
        verbose_name = '系统设置'
        verbose_name_plural = verbose_name
        ordering = ('id', )
        db_table = "setting"


# class LogFile(BaseModel):
#     """
#     下载文件记录
#     """
#     user = models.ForeignKey(User)
#     file = models.FileField(max_length=255, null=True, blank=True)
#
#     class Meta:
#         verbose_name = '下载文件记录'
#         verbose_name_plural = verbose_name
#         ordering = ('id',)
#         db_table = "log_file"
