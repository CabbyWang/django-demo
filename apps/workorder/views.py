import enum
import os

# from django.conf import settings

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from workorder.filters import WorkOrderFilter, InspectionFilter
from .models import (
    WorkOrder, WorkorderImage, WorkOrderAudio,
    Inspection, InspectionImage, InspectionItem
)
from .serializers import (WorkOrderSerializer, WorkOrderImageSerializer,
                          WorkOrderDetailSerializer, ConfirmOrderSerializer,
                          ReassignOrderSerializer, FinishOrderSerializer,
                          ReopenOrderSerializer, WorkOrderAudioSerializer,
                          InspectionSerializer, InspectionItemSerializer,
                          InspectionImageSerializer,
                          InspectionDetailSerializer)
from utils.mixins import ListModelMixin
from utils.settings import WorkOrderType


# TODO 创建工单和重新指派工单后需要生成语音


class WorkOrderViewSet(ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """
    工单
    list:
        获取工单信息
    retrieve:
        获取工单详细信息
    create:
        创建工单
    get_malfunction_status:
        获取资产故障情况
    confirm_order:
        确认工单
    reassign_order:
        重新指派工单
    finish_order:
        完成工单
    reopen_order:
        重新开启工单
    upload_images:
        上传工单图片
    """

    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend, )
    filter_class = WorkOrderFilter

    def get_queryset(self):
        """
        普通用户只能看到自己的工单
        """
        if not self.request.user.is_superuser:
            return WorkOrder.objects.filter_by(user_id=self.request.user.id)
        return WorkOrder.objects.filter_by()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return WorkOrderDetailSerializer
        if self.action == "confirm_order":
            return ConfirmOrderSerializer
        if self.action == "reassign_order":
            return ReassignOrderSerializer
        if self.action == 'finish_order':
            return FinishOrderSerializer
        if self.action == 'reopen_order':
            return ReopenOrderSerializer
        if self.action == 'upload_images':
            return WorkOrderImageSerializer
        return WorkOrderSerializer

    @action(methods=['GET'], detail=False, url_path="malfunction-status")
    def get_malfunction_status(self, request, *args, **kwargs):
        """
        资产故障情况
        GET /workorders/malfunction-status/
        """
        ret = []
        for order in WorkOrderType:
            d = dict(
                name=order.name,
                value=WorkOrder.objects.filter_by(type=order.value).count()
            )
            ret.append(d)
        return Response(data=ret)

    @action(methods=['POST'], detail=True, url_path="confirm")
    def confirm_order(self, request, *args, **kwargs):
        """
        确认工单
        POST /workorders/{id}/confirm/
        """
        return super(WorkOrderViewSet, self).update(request, *args, **kwargs)

    @action(methods=['POST'], detail=True, url_path='reassign')
    def reassign_order(self, request, *args, **kwargs):
        """
        重新指派工单
        POST /workorders/{id}/reassign/
        {
            "user": 2
        }
        """
        return super(WorkOrderViewSet, self).update(request, *args, **kwargs)

    @action(methods=['POST'], detail=True, url_path='finish')
    def finish_order(self, request, *args, **kwargs):
        """
        完成工单(管理员)
        POST /workorders/{id}/finish/
        {
            "description": "xxx"
        }
        """
        return super(WorkOrderViewSet, self).update(request, *args, **kwargs)

    @action(methods=['POST'], detail=True, url_path='reopen')
    def reopen_order(self, request, *args, **kwargs):
        """
        重新开启工单
        POST /workorders/{id}/reopen/
        """
        return super(WorkOrderViewSet, self).update(request, *args, **kwargs)

    @action(methods=['POST'], detail=True, url_path='images')
    def upload_images(self, request, *args, **kwargs):
        """上传工单图片"""
        # TODO 这里直接改动request.data 是否可行？ 是否有其他方式？ 研究一下
        order_id = kwargs.get('pk')
        request.data['order'] = order_id
        return super(WorkOrderViewSet, self).create(request, *args, **kwargs)


class WorkOrderImageViewSet(mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """
    工单图片
    destroy:
        删除工单图片
    """

    queryset = WorkorderImage.objects.filter_by()
    serializer_class = WorkOrderImageSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # lookup_field = 'order_id'

    # TODO 删除工单图片后， 需要删除图片文件? 可以保留
    def perform_destroy(self, instance):
        instance.soft_delete()


class WorkOrderAudioViewSet(mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """
    工单语音
    destroy:
        删除工单语音(通过workorder_id删除)
    """
    queryset = WorkOrderAudio.objects.filter_by()
    serializer_class = WorkOrderAudioSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = 'order_id'

    def perform_destroy(self, instance):
        instance.times += 1
        instance.save()


class InspectionViewSet(ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """
    巡检
    list:
        获取巡检信息
    retrieve:
        获取巡检详细信息
    create:
        创建巡检报告
    destroy:
        删除巡检报告
    update:
        修改巡检报告
    upload_images:
        上传巡检图片
    """

    queryset = Inspection.objects.filter_by()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    filter_backends = (DjangoFilterBackend,)
    filter_class = InspectionFilter

    # TODO 删除巡检报告，使用逻辑删除？ 相关联表如何处理, 手动操作还是研究delete实现?

    def get_serializer_class(self):
        if self.action == 'upload_images':
            return InspectionImageSerializer
        if self.action in ('list', 'retrieve'):
            return InspectionDetailSerializer
        return InspectionSerializer

    @action(methods=['POST'], detail=True, url_path='images')
    def upload_images(self, request, *args, **kwargs):
        """上传巡检图片"""
        # TODO 这里直接改动request.data 是否可行？ 是否有其他方式？ 研究一下
        inspection_id = kwargs.get('pk')
        request.data['inspection'] = inspection_id
        return super(InspectionViewSet, self).create(request, *args, **kwargs)


class InspectionImageViewSet(mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):
    """
    巡检图片
    destroy:
        删除巡检图片
    """
    queryset = InspectionImage.objects.filter_by()
    serializer_class = InspectionImageSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # lookup_field = "inspection_id"


class InspectionItemViewSet(mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """
    巡检项
    create:
        添加巡检项
    """
    queryset = InspectionItem.objects.filter_by()
    serializer_class = InspectionItemSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
