#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/5/9
"""
from rest_framework import serializers

from base.serializers import UnitSerializer
from equipment.models import PoleImage, Pole, LampImage, Lamp, CBoxImage, CBox, \
    Cable, LampCtrl, Hub


class PoleImageSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = PoleImage
        fields = ('id', 'file', 'created_time')


class PoleDetailSerializer(serializers.ModelSerializer):
    image = PoleImageSerializer(read_only=True)
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(write_only=True)
    is_deleted = serializers.BooleanField(write_only=True)

    class Meta:
        model = Pole
        fields = "__all__"


class PoleSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Pole
        fields = "__all__"


class PoleBatchDeleteSerializer(serializers.ModelSerializer):
    """批量删除灯杆格式检验"""
    sn = serializers.ListField(
        min_length=1,
        child=serializers.SlugRelatedField(
            queryset=Pole.objects.filter_by(),
            slug_field='sn'
        )
    )

    class Meta:
        model = Pole
        fields = ("sn", )


class LampImageSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = LampImage
        fields = ('id', 'file', 'created_time')


class LampDetailSerializer(serializers.ModelSerializer):
    image = LampImageSerializer(read_only=True)
    bearer = serializers.SlugRelatedField(
        queryset=Pole.objects.filter_by(),
        slug_field='sn'
    )
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(write_only=True)
    is_deleted = serializers.BooleanField(write_only=True)

    class Meta:
        model = Lamp
        fields = "__all__"


class LampSerializer(serializers.ModelSerializer):
    bearer = serializers.SlugRelatedField(
        queryset=Pole.objects.filter_by(),
        slug_field='sn'
    )

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    def validate(self, attrs):
        return attrs

    class Meta:
        model = Lamp
        fields = "__all__"


class LampBatchDeleteSerializer(serializers.ModelSerializer):
    """批量删除灯具格式检验"""
    sn = serializers.ListField(
        min_length=1,
        child=serializers.SlugRelatedField(
            queryset=Lamp.objects.filter_by(),
            slug_field='sn'
        )
    )

    class Meta:
        model = Lamp
        fields = ("sn", )


class CBoxImageSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = CBoxImage
        fields = ('id', 'file', 'created_time')


class CBoxDetailSerializer(serializers.ModelSerializer):
    image = CBoxImageSerializer(read_only=True)
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(write_only=True)
    is_deleted = serializers.BooleanField(write_only=True)

    class Meta:
        model = CBox
        fields = "__all__"


class CBoxSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = CBox
        fields = "__all__"


class CBoxBatchDeleteSerializer(serializers.ModelSerializer):
    """批量删除控制箱格式检验"""
    sn = serializers.ListField(
        min_length=1,
        child=serializers.SlugRelatedField(
            queryset=CBox.objects.filter_by(),
            slug_field='sn'
        )
    )

    class Meta:
        model = CBox
        fields = ("sn", )


class CableSerializer(serializers.ModelSerializer):
    sn = serializers.CharField(required=True)

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Cable
        fields = "__all__"


class CableBatchDeleteSerializer(serializers.ModelSerializer):
    """批量删除电缆格式检验"""
    sn = serializers.ListField(
        min_length=1,
        child=serializers.SlugRelatedField(
            queryset=Cable.objects.filter_by(),
            slug_field='sn'
        )
    )

    class Meta:
        model = Cable
        fields = ("sn", )


class LampCtrlSerializer(serializers.ModelSerializer):
    # failure_date = serializers.DateField(read_only=True, format='%Y-%m-%d')
    registered_time = serializers.DateField(read_only=True, format='%Y-%m-%d')
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    deleted_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    lamp_status = serializers.SerializerMethodField()
    hub_is_redirect = serializers.SerializerMethodField()
    real_address = serializers.SerializerMethodField()

    @staticmethod
    def get_lamp_status(instance):
        """
        lamp_status分四种状态， 正常开灯/正常熄灯/故障/脱网（正常分为两种状态）1/0/2/3
        """
        status = instance.status
        switch_status = instance.switch_status
        lamp_status = status
        if lamp_status == 1 and switch_status == 0:
            lamp_status = 0
        return lamp_status

    @staticmethod
    def get_real_address(instance):
        """获取lampctrl的真正地址"""
        address = instance.address
        new_address = instance.new_address or ''
        new_address = new_address.strip()
        return new_address or address

    @staticmethod
    def get_hub_is_redirect(instance):
        """集控是否重定位"""
        hub = instance.hub
        return hub.is_redirect
        # try:
        #     hub_instance = Hub.objects.get(sn=hub_sn)
        # except Hub.DoesNotExist:
        #     raise serializers.ValidationError("集控不存在")
        # return hub_instance.is_redirect

    class Meta:
        model = LampCtrl
        fields = "__all__"


class LampCtrlPartialUpdateSerializer(serializers.ModelSerializer):
    new_address = serializers.CharField()

    def validate(self, attrs):
        for k, v in attrs.items():
            if k == "new_address":
                continue
            attrs[k] = getattr(self.instance, k)
        return attrs

    class Meta:
        model = LampCtrl
        fields = "__all__"


class HubDetailSerializer(serializers.ModelSerializer):

    unit = UnitSerializer()
    lampctrls_num = serializers.SerializerMethodField()

    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_lampctrls_num(obj):
        return obj.hub_lampctrl.count()

    class Meta:
        model = Hub
        fields = "__all__"


class HubPartialUpdateSerializer(serializers.ModelSerializer):
    longitude = serializers.FloatField(max_value=180, min_value=0)
    latitude = serializers.FloatField(max_value=90, min_value=0)

    def validate(self, attrs):
        if all(i in attrs for i in ('longitude', 'latitude')):
            # 集控重定位, is_redirect=True
            attrs['is_redirect'] = True
        return attrs

    class Meta:
        model = Hub
        fields = "__all__"

