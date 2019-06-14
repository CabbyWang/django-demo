from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, viewsets, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from policy.filters import PolicyFilter, PolicySetFilter
from .models import Policy, PolicySet
from .serializers import (
    PolicySerializer, PolicySetSerializer,
    PolicySetDetailSerializer)
from utils.mixins import ListModelMixin


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
        # 只能删除自己创建的策略
        is_admin = self.request.user.username == 'admin'
        if not is_admin and instance.creator != self.request.user:
            msg = _('you can only delete your own policy')
            raise serializers.ValidationError(msg)
        if instance.policy_relations.filter_by().exists():
            msg = _("you cant't delete the policy in use")
            raise serializers.ValidationError(msg)
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

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PolicySetDetailSerializer
        return PolicySetSerializer

    def perform_destroy(self, instance):
        # 只能删除自己创建的策略
        is_admin = self.request.user.username == 'admin'
        if not is_admin and instance.creator != self.request.user:
            msg = _("you can only delete your own policyset")
            raise serializers.ValidationError(msg)
        if instance.policyset_send_down_policysets.filter_by().exists():
            msg = _("you cant't delete the policy in use")
            raise serializers.ValidationError(msg)
        instance.policyset_relations.update(is_deleted=True)
        instance.soft_delete()
