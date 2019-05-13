import datetime

from django.db import models
from django.db.models.manager import Manager
from django.contrib.auth.models import UserManager, AbstractUser
from django.http import Http404


# class MyQuerySet(models.query.QuerySet):
#
#     def soft_delete(self):
#         a = 1
#         pass


class MyManager(Manager):

    def filter_by(self, *args, **kwargs):
        """
        Returns a new QuerySet instance with the args ANDed to the existing
        set.
        is_deleted is False.
        """
        kwargs['is_deleted'] = False
        return super(MyManager, self).filter(*args, **kwargs)

    def get_or_404(self, *args, **kwargs):
        """
        Get an object or http404
        """
        try:
            return super(MyManager, self).get(*args, **kwargs)
        except:
            raise Http404


    # def get_query_set(self):
    #     return MyQuerySet(self.model, using=self._db)


class MyUserManage(UserManager):

    def filter_by(self, *args, **kwargs):
        """
        Returns a new QuerySet instance with the args ANDed to the existing
        set.
        is_deleted is False.
        """
        kwargs['is_deleted'] = False
        return super(MyUserManage, self).filter(*args, **kwargs)


class BaseModel(models.Model):

    is_deleted = models.BooleanField(
        default=False, verbose_name='是否删除', help_text='是否删除'
    )
    created_time = models.DateTimeField(
        auto_now_add=True, verbose_name='创建时间', help_text='创建时间'
    )
    updated_time = models.DateTimeField(
        auto_now=True, null=True, blank=True, verbose_name='更新时间',
        help_text='更新时间'
    )
    deleted_time = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name='删除时间',
        help_text='删除时间'
    )

    objects = MyManager()

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_time = datetime.datetime.now()
        self.save()

    @classmethod
    def fields(cls):
        return [i.name for i in cls._meta.fields]

    class Meta:
        abstract = True


class MyAbstractUser(AbstractUser):

    is_deleted = models.BooleanField(
        default=False, verbose_name='是否删除', help_text='是否删除'
    )
    created_time = models.DateTimeField(
        auto_now_add=True, verbose_name='创建时间', help_text='创建时间'
    )
    updated_time = models.DateTimeField(
        auto_now=True, null=True, blank=True, verbose_name='更新时间',
        help_text='更新时间'
    )
    deleted_time = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name='删除时间',
        help_text='删除时间'
    )

    objects = MyUserManage()

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_time = datetime.datetime.now()
        self.save()

    class Meta:
        abstract = True


class Unit(BaseModel):
    """
    管理单元
    """
    name = models.CharField(max_length=32, verbose_name="名称", unique=True)

    class Meta:
        verbose_name = "管理单元"
        verbose_name_plural = verbose_name
        ordering = ('name',)
        db_table = "unit"

    def __str__(self):
        return self.name
