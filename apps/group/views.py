from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from equipment.models import LampCtrl
from equipment.serializers import LampCtrlSerializer
from group.filters import LampCtrlGroupFilter
from group.models import LampCtrlGroup
from group.serializers import GetLampCtrlserializer, LampCtrlGroupSerializer
from utils.mixins import ListModelMixin


class LampCtrlGroupViewSet(ListModelMixin,
                           viewsets.GenericViewSet):

    """灯控分组
    list:
        获取所有灯控分组
    """

    queryset = LampCtrlGroup.objects.filter_by()
    serializer_class = LampCtrlGroupSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = LampCtrlGroupFilter

    def get_serializer_class(self):
        if self.action == 'get_group_lamps':
            return GetLampCtrlserializer
        # if self.action == 'get_lampctrls_from_group':
        #     return GetLampCtrlserializer
        # if self.action == 'get_groups':
        #     return GetGroupserializer
        return LampCtrlGroupSerializer

    @action(methods=['GET'], detail=False, url_path='group-lamps')
    def get_group_lamps(self, request, *args, **kwargs):
        """获取某个分组内的灯具列表(未分组灯控归入0分组范畴)
        GET /lampctrlgroups/group-lamps/?hub=&group=&is_default=
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        hub = serializer.validated_data['hub']
        is_default = serializer.validated_data['is_default']
        group_num = serializer.validated_data['group_num']

        if not is_default and group_num == 0:
            # 获取自定义分组下未分组的灯具
            in_groups = LampCtrlGroup.objects.filter_by(hub=hub, is_default=False).values_list('lampctrl', flat=True)
            lampctrls = LampCtrl.objects.filter_by(hub=hub).exclude(sn__in=in_groups)
        else:
            in_groups = LampCtrlGroup.objects.filter_by(hub=hub, group_num=group_num, is_default=is_default).values_list('lampctrl', flat=True)
            lampctrls = LampCtrl.objects.filter_by(sn__in=in_groups)
        serializers = LampCtrlSerializer(lampctrls, many=True)
        return Response(serializers.data)

    # @action(methods=['GET'], detail=False, url_path='groups')
    # def get_groups(self, request, *args, **kwargs):
    #     """获取集控下的分组
    #     GET /lampctrlgroups/groups/?hub=&is_default=
    #     """
    #     serializer = self.get_serializer(data=request.query_params)
    #     serializer.is_valid(raise_exception=True)
    #     hub = serializer.validated_data['hub']
    #     is_default = serializer.validated_data['is_default']
    #     queryset = LampCtrlGroup.objects.filter_by(hub=hub, is_default=is_default)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)
