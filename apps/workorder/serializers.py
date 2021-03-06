#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/8
"""
import datetime

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from equipment.models import Pole, Lamp, Cable, CBox
from equipment.models import Hub, LampCtrl
from notify.models import Alert
from user.views import User
from .models import (
    WorkOrder, WorkorderImage, WorkOrderAudio,
    Inspection, InspectionImage, InspectionItem
)
from utils.exceptions import InvalidInputError


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class WorkOrderImageSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    order = serializers.PrimaryKeyRelatedField(
        required=True, queryset=WorkOrder.objects.filter_by()
    )

    class Meta:
        model = WorkorderImage
        fields = ("id", "file", "created_time",
                  "updated_time", "order", "is_deleted")


class AudioSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkOrderAudio
        fields = ("id", "audio")
        read_only_fields = ('audio', )


class WorkOrderDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    finished_time = serializers.DateTimeField(read_only=True,
                                              format='%Y-%m-%d %H:%M:%S')

    workorder_audio = AudioSerializer(source='not_listen_audio')
    workorder_image = serializers.SerializerMethodField()

    def get_workorder_image(self, instance):
        queryset = instance.workorder_image.filter_by()
        return WorkOrderImageSerializer(
            queryset, many=True, context={'request': self.context['request']}
        ).data

    class Meta:
        model = WorkOrder
        fields = "__all__"


class WorkOrderSerializer(serializers.ModelSerializer):
    TYPES = (
        (0, "其它"),
        (1, "集控"),
        (2, "灯具"),
        (3, "灯杆"),
        (4, "电缆"),
        (5, "控制箱")
    )
    STATUS = (('todo', '未处理'), ('doing', '处理中'), ('finished', '已处理'))

    alert = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Alert.objects.filter_by(),
        allow_null=True,
        help_text='告警编号'
    )
    type = serializers.ChoiceField(
        required=True, choices=TYPES, help_text='工单类型'
    )
    obj_sn = serializers.CharField(required=False, max_length=32,
                                   allow_blank=True, help_text='对象编号')
    user = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=User.objects.filter_by(),
        allow_null=True,
        help_text='用户id'
    )
    memo = serializers.CharField(max_length=255)
    status = serializers.ChoiceField(choices=STATUS,
                                     default='todo')  # to-do/doing/finished
    finished_time = serializers.DateTimeField(required=False, allow_null=True)
    description = serializers.CharField(
        required=False, max_length=255,
        allow_blank=True
    )

    @staticmethod
    def validate_alert(alert):
        if WorkOrder.objects.filter_by(alert=alert).exists():
            # raise serializers.ValidationError("该告警已生成工单")
            msg = _('the alert [{event}] has generated a work order'.format(
                event=alert.event))
            raise InvalidInputError(msg)
        return alert

    def validate_obj_sn(self, obj_sn):
        w_type = self.initial_data.get("type")
        # 判断集控是否存在
        if w_type == 1  and not Hub.objects.filter_by(
                sn=obj_sn).exists():
            raise InvalidInputError("hub [{}] does not exist".format(obj_sn))
        # # 判断灯控或灯具是否存在
        elif w_type == 2 and obj_sn and not LampCtrl.objects.filter_by(
                sn=obj_sn).exists() and not Lamp.objects.filter_by(
                sn=obj_sn).exists():
            raise serializers.ValidationError(
                "lamp or lamp control [{}] does not exist".format(obj_sn))
        # 判断灯杆是否存在
        elif w_type == 3 and obj_sn and not Pole.objects.filter_by(
                sn=obj_sn).exists():
            raise InvalidInputError("pole [{}] does not exist".format(obj_sn))
        # 判断电缆是否存在
        elif w_type == 4 and obj_sn and not Cable.objects.filter_by(
                sn=obj_sn).exists():
            raise InvalidInputError("cable [{}] does not exist".format(obj_sn))
        # 判断控制箱是否存在
        elif w_type == 5 and obj_sn and not CBox.objects.filter_by(
                sn=obj_sn).exists():
            raise InvalidInputError(
                "control box [{}] does not exist".format(obj_sn))
        return obj_sn

    def validate(self, attrs):
        if attrs['type'] != 0 and 'obj_sn' not in attrs:
            raise InvalidInputError('field "obj_sn" is required')
        return attrs

    class Meta:
        model = WorkOrder
        fields = "__all__"


class ConfirmOrderSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(required=False, read_only=True)
    memo = serializers.CharField(required=False, read_only=True)

    def validate(self, attrs):
        request = self.context["request"]
        # 没有处理人，要先指派工单
        if not self.instance.user:
            msg = _("Please assign work order first")
            raise serializers.ValidationError(msg)
            pass
        # 只有被指派人才可以确认工单
        if self.instance.user != request.user:
            msg = _("Only the user who has been assigned can confirm work order")
            raise serializers.ValidationError(msg)
        # 工单处于完成状态， 不能确认工单
        if self.instance.status == 'finished':
            msg = _("The work order has been finished")
            raise serializers.ValidationError(msg)
        # 工单处于处理中状态， 不能再次确认工单
        if self.instance.status == 'doing':
            msg = _("The work order's status is doing")
            raise serializers.ValidationError(msg)
        attrs["status"] = 'doing'
        return attrs

    class Meta:
        model = WorkOrder
        fields = "__all__"


class ReassignOrderSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(required=False, read_only=True)
    memo = serializers.CharField(required=False, read_only=True)

    user = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=User.objects.filter_by()
    )

    def validate(self, attrs):
        # 工单处于完成状态， 不能重新指派
        if self.instance.status == 'finished':
            raise serializers.ValidationError("工单已经处于完成状态")
        # 重新指派工单只允许修改被指派人(user)
        for k, v in attrs.items():
            if k == "user":
                continue
            attrs[k] = getattr(self.instance, k)
        attrs["status"] = 'todo'
        return attrs

    class Meta:
        model = WorkOrder
        fields = "__all__"


class FinishOrderSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(required=False, read_only=True)
    memo = serializers.CharField(required=False, read_only=True)

    description = serializers.CharField(max_length=255)

    def validate(self, attrs):
        request = self.context["request"]
        # 只有管理员可以确认完成工单
        if not request.user.is_superuser:
            # raise serializers.ValidationError("只有管理员可以确认完成工单")
            raise InvalidInputError('only superuser can finish the work order')
        # 工单处于完成状态， 不需要再次完成工单
        if self.instance.status == 'finished':
            # raise serializers.ValidationError("工单已经处于完成状态")
            raise InvalidInputError('work order has been finished')
        attrs["finished_time"] = datetime.datetime.now()
        attrs["status"] = 'finished'
        return attrs

    class Meta:
        model = WorkOrder
        fields = "__all__"


class ReopenOrderSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(required=False, read_only=True)
    memo = serializers.CharField(required=False, read_only=True)

    def validate(self, attrs):
        # 工单处于开启状态， 不需要重新开启工单
        if self.instance.status != 'finished':
            # raise serializers.ValidationError("工单已经处于开启状态")
            raise InvalidInputError("work order has been opened")
        # 重新开启工单后， status为doing， finished_time为空
        attrs["finished_time"] = None
        attrs["status"] = 'doing'
        attrs["description"] = None
        return attrs

    class Meta:
        model = WorkOrder
        fields = "__all__"


class WorkOrderAudioSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkOrderAudio
        fields = '__all__'


class InspectionImageSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    inspection = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Inspection.objects.filter_by()
    )

    class Meta:
        model = InspectionImage
        fields = ("id", "file", "inspection", "created_time", "updated_time")


class InspectionItemSerializer(serializers.ModelSerializer):
    STATUS_CHOICE = ((1, '正常'), (2, '故障'))

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    inspection = serializers.PrimaryKeyRelatedField(queryset=Inspection.objects.filter_by())
    # inspection = serializers.IntegerField(required=False, read_only=True)
    # inspection = serializers.PrimaryKeyRelatedField(queryset=Inspection.objects.filter_by(), required=False, read_only=True)
    # hub = serializers.PrimaryKeyRelatedField(queryset=Hub.objects.filter_by())
    lampctrl = serializers.PrimaryKeyRelatedField(queryset=LampCtrl.objects.filter_by())
    status = serializers.ChoiceField(choices=STATUS_CHOICE)
    memo = serializers.CharField(required=True, max_length=1023, allow_blank=True)

    sequence = serializers.SerializerMethodField(read_only=True)
    real_address = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_sequence(instance):
        return instance.lampctrl.sequence

    @staticmethod
    def get_real_address(instance):
        lampctrl = instance.lampctrl
        address = lampctrl.address
        new_address = lampctrl.new_address or ''
        new_address = new_address.strip()
        return new_address or address

    class Meta:
        model = InspectionItem
        fields = "__all__"


class InspectionSerializer(serializers.ModelSerializer):
    inspection_image = InspectionImageSerializer(read_only=True, many=True)
    inspection_item = InspectionItemSerializer(read_only=True, many=True)

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter_by(),
                                              write_only=True)
    hub = serializers.PrimaryKeyRelatedField(queryset=Hub.objects.filter_by())
    memo = serializers.CharField(required=False, allow_blank=True, max_length=1023)

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Inspection
        fields = "__all__"

    def validate(self, attrs):
        """验证inspection_item 格式如下
        [
            {
                "lampctrl": "000000000001",
                "status": 1,
                "memo": ""
            },
            {
                "lampctrl": "000000000001",
                "status": 1,
                "memo": ""
            }
        ]
        """
        isp_items = self.initial_data.get('inspection_item')
        if not isp_items or not isinstance(isp_items, list):
            msg = _("'invalid input'")
            raise serializers.ValidationError(msg)
        for item in isp_items:
            if 'lampctrl' not in item or 'status' not in item:
                msg = _("'invalid input'")
                raise serializers.ValidationError(msg)
            lampctrl_sn = item['lampctrl']
            if not LampCtrl.objects.filter_by(sn=lampctrl_sn).exists():
                msg = _("lampctrl '{lampctrl_sn}' does not exist")
                raise serializers.ValidationError(msg.format(lampctrl_sn=lampctrl_sn))
        return attrs

    def create(self, validated_data):
        inspection = Inspection.objects.create(**validated_data)
        if "inspection_item" in self.initial_data:
            isp_items = self.initial_data.get('inspection_item')
            for item in isp_items:
                lampctrl_sn = item.get('lampctrl')
                lampctrl = LampCtrl.objects.get(sn=lampctrl_sn)
                status = item.get('status')
                memo = item.get('memo')
                InspectionItem.objects.create(
                    inspection=inspection,
                    lampctrl=lampctrl,
                    status=status,
                    memo=memo
                )
        return inspection


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class InspectionDetailSerializer(serializers.ModelSerializer):
    inspection_image = InspectionImageSerializer(read_only=True, many=True)
    inspection_item = InspectionItemSerializer(read_only=True, many=True)
    user = UserSerializer()

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Inspection
        fields = "__all__"
