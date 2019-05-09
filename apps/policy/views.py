from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from policy.filters import PolicyFilter, PolicySetFilter
from .models import Policy, PolicySet
from .serializers import (
    PolicySerializer, PolicySetSerializer
)
from utils.mixins import ListModelMixin
from utils.exceptions import InvalidInputError


class PolicyViewSet(ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):

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

    queryset = Policy.objects.filter_by()
    serializer_class = PolicySerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = PolicyFilter

    def perform_destroy(self, instance):
        if instance.policy_relations.exists:
            raise InvalidInputError('the policy is using, can not be deleted')
        instance.soft_delete()


class PolicySetViewSet(ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):

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
    """

    queryset = PolicySet.objects.filter_by()
    serializer_class = PolicySetSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = PolicySetFilter

    def perform_destroy(self, instance):
        if instance.policyset_send_down_policysets.exists():
            msg = _('the policyset is using, can not be deleted')
            raise InvalidInputError(msg)
        instance.policyset_relations.update(is_deleted=True)
        instance.soft_delete()
