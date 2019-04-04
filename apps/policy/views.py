from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Policy, PolicySet, PolicySetSendDown, PolicySetRelation
from .serializers import (
    PolicySerializer, PolicySetSerializer
)


class PolicyViewSet(ModelViewSet):

    """
    策略
    list:
        获取所有策略
    retrieve:
        获取策略详细信息
    create:
        新建策略
    destroy:
        删除策略
    update:
        修改策略
    """

    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)


class PolicySetViewSet(ModelViewSet):

    """
    策略
    list:
        获取所有策略集
    retrieve:
        获取策略集详细信息
    create:
        新建策略集
    destroy:
        删除策略集
    update:
        修改策略集
        下发策略集
        采集策略方案
        回收策略方案（自定义方案）
    """

    queryset = PolicySet.objects.all()
    serializer_class = PolicySetSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
