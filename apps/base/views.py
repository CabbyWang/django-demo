from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from base.models import Unit
from base.serializers import UnitSerializer
from utils.mixins import ListModelMixin


class UnitViewSet(ListModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        获取所有管理单元
    """
    queryset = Unit.objects.filter_by()
    serializer_class = UnitSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
