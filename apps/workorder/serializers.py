#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/8
"""
import datetime

from rest_framework import serializers

from asset.models import Pole, Lamp, Cable, CBox
from hub.models import Hub
from lamp.models import LampCtrl
from notify.models import Alert
from user.views import User
from .models import WorkOrder, WorkorderImage, WorkOrderAudio, Inspection, InspectionImage, InspectionItem
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

    order = serializers.PrimaryKeyRelatedField(required=True, queryset=WorkOrder.objects.filter_by())

    class Meta:
        model = WorkorderImage
        fields = ("id", "file", "created_time",
                  "updated_time", "order", "is_deleted")


class WorkOrderDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    # workorder_image = WorkOrderImageSerializer(many=True)
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    finished_time = serializers.DateTimeField(read_only=True,
                                              format='%Y-%m-%d %H:%M:%S')

    audio = serializers.SerializerMethodField()
    workorder_image = serializers.SerializerMethodField()

    def get_workorder_image(self, instance):
        queryset = instance.workorder_image.filter_by()
        return WorkOrderImageSerializer(
            queryset, many=True, context={'request': self.context['request']}
        ).data

    @staticmethod
    def get_audio(instance):
        # 返回语音文件路径，或None
        try:
            order_audio = instance.workorder_audio
            if order_audio.is_deleted:
                return
            return order_audio.audio.path
        except:
            return

    class Meta:
        model = WorkOrder
        fields = "__all__"


class WorkOrderSerializer(serializers.ModelSerializer):
    TYPES = (
        (0, "其它"),
        (1, "集控"),
        (2, "灯控"),
        (3, "灯杆"),
        (4, "灯具"),
        (5, "电缆"),
        (6, "控制箱"),
    )
    STATUS = (('todo', '未处理'), ('doing', '处理中'), ('finished', '已处理'))

    alert = serializers.PrimaryKeyRelatedField(required=False,
                                               queryset=Alert.objects.filter_by(),
                                               allow_null=True,
                                               help_text='告警编号')
    type = serializers.ChoiceField(choices=TYPES, help_text='工单类型')
    obj_sn = serializers.CharField(required=False, max_length=32,
                                   allow_blank=True, help_text='对象编号')
    # lampctrl = serializers.PrimaryKeyRelatedField(required=False,
    #                                               queryset=LampCtrl.objects.filter_by(),
    #                                               allow_null=True)
    # sequence = serializers.IntegerField(required=False,
    #                                     allow_null=True)
    user = serializers.PrimaryKeyRelatedField(required=False,
                                              queryset=User.objects.filter_by(),
                                              allow_null=True,
                                              help_text='用户id')
    memo = serializers.CharField(max_length=255)
    status = serializers.ChoiceField(choices=STATUS,
                                     default='todo')  # to-do/doing/finished
    finished_time = serializers.DateTimeField(required=False, allow_null=True)
    description = serializers.CharField(required=False, max_length=255,
                                        allow_blank=True)

    @staticmethod
    def validate_alert(alert):
        if WorkOrder.objects.filter_by(alert=alert).exists():
            # raise serializers.ValidationError("该告警已生成工单")
            raise InvalidInputError('the alert [{}] has generated a work order'.format(alert.event))
        return alert

    def validate_obj_sn(self, obj_sn):
        w_type = self.initial_data.get("type")
        # 判断集控是否存在
        if w_type == 1 and obj_sn and not Hub.objects.filter_by(sn=obj_sn).exists():
            raise serializers.ValidationError("hub [{}] not exist".format(obj_sn))
        # 判断灯控是否存在
        elif w_type == 2 and obj_sn and not LampCtrl.objects.filter_by(sn=obj_sn).exists():
            raise serializers.ValidationError("lamp control [{}] not exist".format(obj_sn))
        # 判断灯杆是否存在
        elif w_type == 3 and obj_sn and not Pole.objects.filter_by(sn=obj_sn).exists():
            raise serializers.ValidationError("pole [{}] not exist".format(obj_sn))
        # 判断灯具是否存在
        elif w_type == 4 and obj_sn and not Lamp.objects.filter_by(sn=obj_sn).exists():
            raise serializers.ValidationError("lamp [{}] not exist".format(obj_sn))
        # 判断电缆是否存在
        elif w_type == 5 and obj_sn and not Cable.objects.filter_by(sn=obj_sn).exists():
            raise serializers.ValidationError("cable [{}] not exist".format(obj_sn))
        # 判断控制箱是否存在
        elif w_type == 6 and obj_sn and not CBox.objects.filter_by(sn=obj_sn).exists():
            raise serializers.ValidationError("control box [{}] not exist".format(obj_sn))
        return obj_sn

    # def validate(self, attrs):
    #     w_type = self.initial_data['type']
    #     if w_type == 1:
    #         工单类型为“集控”
    #         hub = Hub.objects.get(sn=self.initial_data['obj_sn'])
    #         lamp = LampCtrl.objects.filter_by(hub=hub).first()
    #         灯控编号存在
    #         if lamp:
    #             # 自动填充sequence
    #             attrs['sequence'] = lamp.sequence
    #     return attrs

    class Meta:
        model = WorkOrder
        fields = "__all__"


class ConfirmOrderSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(required=False, read_only=True)
    memo = serializers.CharField(required=False, read_only=True)

    def validate(self, attrs):
        request = self.context["request"]
        # 只有被指派人才可以确认工单
        if self.instance.user != request.user:
            # raise serializers.ValidationError("只有被指派人才可以确认工单")
            raise InvalidInputError("只有被指派人才可以确认工单")
        # 工单处于完成状态， 不能确认工单
        if self.instance.status == 'finished':
            # raise serializers.ValidationError("工单已经处于完成状态")
            raise InvalidInputError("工单已经处于完成状态")
        # 工单处于处理中状态， 不能再次确认工单
        if self.instance.status == 'doing':
            # raise serializers.ValidationError("工单已经在处理中")
            raise InvalidInputError("工单已经在处理中")
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

    class Meta:
        model = InspectionImage
        fields = ("id", "file", "created_time", "updated_time")


class InspectionItemSerializer(serializers.ModelSerializer):
    STATUS_CHOICE = ((1, '正常'), (2, '故障'))

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    inspection = serializers.PrimaryKeyRelatedField(queryset=Inspection.objects.filter_by())
    hub = serializers.PrimaryKeyRelatedField(queryset=Hub.objects.filter_by())
    lampctrl = serializers.PrimaryKeyRelatedField(queryset=LampCtrl.objects.filter_by())
    status = serializers.ChoiceField(choices=STATUS_CHOICE)
    memo = serializers.CharField(required=True, max_length=1023, allow_blank=True)

    sequence = serializers.SerializerMethodField()
    real_address = serializers.SerializerMethodField()

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
