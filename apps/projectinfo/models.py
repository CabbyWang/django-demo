from django.db import models

from base.models import BaseModel


class ProjectInfo(BaseModel):

    name = models.CharField(max_length=16, help_text='公司名称')
    city = models.CharField(max_length=16, help_text='城市名称')
    longitude = models.FloatField(max_length=8, help_text='经度')
    latitude = models.FloatField(max_length=8, help_text='纬度')
    zoom_level = models.IntegerField(default=17, help_text='缩放级别')

    class Meta:
        verbose_name = '项目信息'
        verbose_name_plural = verbose_name
        ordering = ('id', )
        db_table = "projectinfo"

    def __str__(self):
        return self.name
