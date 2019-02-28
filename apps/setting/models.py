from django.db import models


class SettingType(models.Model):
    """
    系统设置分类
    """
    name = models.CharField(max_length=255, unique=True)
    name_zhcn = models.CharField(max_length=255)

    class Meta:
        verbose_name = '系统设置分类'
        verbose_name_plural = verbose_name
        db_table = "setting_type"

    def __str__(self):
        return self.name


class Setting(models.Model):
    """
    系统设置
    """
    option = models.CharField(max_length=255, unique=True)
    option_zhcn = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    s_type = models.ForeignKey(SettingType, related_name='settings')

    class Meta:
        verbose_name = '系统设置'
        verbose_name_plural = verbose_name
        ordering = ('id', )
        db_table = "setting"
