import ast

from django.db import models

from hub.models import Hub
from base.models import BaseModel


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
    item = ListField(default=[])
    memo = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')
    creator = models.CharField(max_length=16, blank=True, null=True)
    type = models.IntegerField(choices=enumerate(POLICY_TYPE), verbose_name='策略类型')

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
    name = models.CharField(max_length=255)
    memo = models.CharField(max_length=255, null=True, blank=True)
    creator = models.CharField(max_length=16, blank=True, null=True)

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
    policy = models.ForeignKey(Policy, related_name='policy_relations')
    policyset = models.ForeignKey(PolicySet, related_name='policyset_relations')
    execute_date = models.DateField()

    class Meta:
        verbose_name = '策略集映射'
        verbose_name_plural = verbose_name
        ordering = ('execute_date', )
        db_table = "policyset_relation"


class PolicySetSendDown(BaseModel):
    """
    策略下发
    """
    policyset = models.ForeignKey(PolicySet, related_name='policyset_send_down_policysets')
    hub = models.ForeignKey(Hub, related_name='hub_send_down_policysets')
    group_id = models.CharField(max_length=16)

    class Meta:
        verbose_name = '策略集下发'
        verbose_name_plural = verbose_name
        ordering = ('created_time', )
        db_table = "policyset_send_down"
