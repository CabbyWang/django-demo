import ast

from django.db import models

from equipment.models import Hub
from base.models import BaseModel
from group.models import LampCtrlGroup
from user.models import User


class ListField(models.TextField):

    description = "A ListFiled"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, conn, context):
        if not value:
            value = []
        if isinstance(value, list):
            return value
        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if not value:
            return value
        return str(value)


class Policy(BaseModel):
    """
    策略
    """
    POLICY_TYPE = ('时控', '经纬度', '光控', '回路控制')

    name = models.CharField(max_length=255, verbose_name='策略名称')
    item = ListField(default=[], verbose_name='策略项')
    memo = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')
    creator = models.ForeignKey(User, db_column='creator',
                                related_name='user_policys',
                                blank=True, null=True, verbose_name='创建人')

    class Meta:
        verbose_name = "策略"
        verbose_name_plural = verbose_name
        ordering = ('-created_time', )
        db_table = "policy"

    def __str__(self):
        return self.name


class PolicySet(BaseModel):
    """
    策略集
    """
    policys = models.ManyToManyField(Policy, through='PolicySetRelation')
    name = models.CharField(max_length=255, verbose_name='策略集名称')
    memo = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')
    creator = models.ForeignKey(User, db_column='creator',
                                related_name='user_policysets',
                                blank=True, null=True, verbose_name='创建人')

    def get_policys(self, obj):
        return obj.policyset_relations.filter(is_deleted=False)

    class Meta:
        verbose_name = '策略集'
        verbose_name_plural = verbose_name
        ordering = ('-created_time', )
        db_table = "policyset"

    def __str__(self):
        return self.name


class PolicySetRelation(BaseModel):
    """
    策略集映射
    """
    policy = models.ForeignKey(Policy, related_name='policy_relations', verbose_name='策略编号')
    policyset = models.ForeignKey(
        PolicySet, related_name='policyset_relations', verbose_name='策略集编号'
    )
    execute_date = models.DateField(verbose_name='执行时间')

    class Meta:
        verbose_name = '策略集映射'
        verbose_name_plural = verbose_name
        ordering = ('execute_date', )
        db_table = "policyset_relation"


class PolicySetSendDown(BaseModel):
    """
    策略下发
    """
    policyset = models.ForeignKey(
        PolicySet,
        related_name='policyset_send_down_policysets',
        verbose_name='策略集编号'
    )
    hub = models.ForeignKey(Hub, db_column='hub_sn', related_name='hub_send_down_policysets', verbose_name='集控编号')
    group_num = models.IntegerField(help_text='分组编号')

    class Meta:
        verbose_name = '策略集下发'
        verbose_name_plural = verbose_name
        ordering = ('created_time', )
        db_table = "policyset_send_down"
