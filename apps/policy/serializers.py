#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/4
"""
import datetime

from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from user.models import User
from .models import Policy, PolicySet, PolicySetRelation, PolicySetSendDown
from utils.validators import UniqueValidator
from utils.sunrise_sunset import calculate_sunrise_sunset


class PolicySerializer(serializers.ModelSerializer):
    # ('时控', '经纬度', '光控', '回路控制')
    name = serializers.CharField(
        max_length=255,
        validators=[
            UniqueValidator(
                queryset=Policy.objects.filter_by(),
                message="policy name already exists")]
    )
    # type = serializers.ChoiceField(
    #     write_only=True,
    #     choices=[(0, '时控'), (1, '经纬度'), (2, '光控'), (3, '回路控制')],
    #     error_messages={
    #         'invalid_choice': _("the value of 'type' should be in (0,1,2,3)")
    #     }
    # )
    item = serializers.ListField(min_length=1)
    creator = serializers.SlugRelatedField(
        # write_only=True,
        slug_field='username',
        queryset=User.objects.filter_by(),
        default=serializers.CurrentUserDefault()
    )
    is_used = serializers.SerializerMethodField()
    format_item = serializers.SerializerMethodField()

    def get_format_item(self, instance):
        """用于前端画图， 将时间转换为分钟"""
        date = self.context.get('request').query_params.get('date')
        items = instance.item
        ret_data = []
        for item in items:
            tp = item.get('type')
            if tp == 2:
                # 光控
                continue
            elif tp in (0, 3):
                # 时控 回路控制
                minutes = int(item.get('hour')) * 60 + int(item.get('minute'))
                ret_data.append(dict(
                    action=item.get('action'),
                    minutes=minutes
                ))
            elif tp == 1:
                # 经纬控
                if not date:
                    continue
                ss = calculate_sunrise_sunset(
                    longitude=item.get('longitude'),
                    latitude=item.get('latitude'),
                    date=date
                )
                time = ss.get('runrise') if item.get('s_type') == 'sunrise' else ss.get('runset')
                time += datetime.timedelta(minutes=item.get('offset', 0))
                minutes = time.hour * 60 + time.minute
                ret_data.append(dict(
                    action=item.get('action'),
                    minutes=minutes
                ))
        return ret_data

    @staticmethod
    def get_is_used(instance):
        return PolicySetRelation.objects.filter_by(policy=instance).exists()

    @staticmethod
    def validate_item(item):
        """验证item"""
        type0 = ('action', 'minute', 'hour')
        type1 = ('action', 'longitude', 'latitude', 's_type', 'offset')
        type2 = ('action', 'detect_period', 'lower_bound', 'higher_bound',
                 'tolerance')
        type3 = ('action', 'minute', 'hour', 'second')
        # item格式错误
        msg = _('item format error')
        for im in item:
            if 'type' not in im:
                raise serializers.ValidationError(msg)
            type = im['type']
            if type == 0 and not all(i in im for i in type0):
                raise serializers.ValidationError(msg)
            if type == 1 and not all(i in im for i in type1):
                raise serializers.ValidationError(msg)
            if type == 2 and not all(i in im for i in type2):
                raise serializers.ValidationError(msg)
            if type == 3 and not all(i in im for i in type3):
                raise serializers.ValidationError(msg)
        return item

    class Meta:
        model = Policy
        fields = ('id', 'name', 'item', 'format_item', 'is_used',
                  'creator', 'created_time', 'updated_time')


class PolicySetRelationSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='policy.id')
    name = serializers.ReadOnlyField(source='policy.name')
    type = serializers.ReadOnlyField(source='policy.type')
    item = serializers.ReadOnlyField(source='policy.item')
    creator = serializers.ReadOnlyField(source='policy.creator.username')
    memo = serializers.ReadOnlyField(source='policy.memo')

    class Meta:
        model = PolicySetRelation
        fields = (
            'id', 'name', 'creator', 'memo', 'type', 'item', 'execute_date'
        )


class PolicySetSerializer(serializers.ModelSerializer):

    # policys = PolicySetRelationSerializer(
    #     source='policyset_relations',
    #     many=True,
    #     read_only=True)
    policys = serializers.SerializerMethodField()
    name = serializers.CharField(
        max_length=255,
        validators=[
            UniqueValidator(
                queryset=PolicySet.objects.filter_by(),
                message="policyset name already exists")]
    )
    creator = serializers.SlugRelatedField(
        # write_only=True,
        slug_field='username',
        queryset=User.objects.filter_by(),
        default=serializers.CurrentUserDefault()
    )
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    is_used = serializers.SerializerMethodField()

    def validate(self, attrs):
        """验证policys 格式如下
        [
            {
                "policy_id": 1,
                "execute_date": "2019-05-06"
            },
            {
                "policy_id": 1,
                "execute_date": "2019-05-07"
            }
        ]
        """
        policys = self.initial_data.get('policys')
        if not policys or not isinstance(policys, list):
            msg = _("'invalid input'")
            raise serializers.ValidationError(msg)
        for item in policys:
            if 'execute_date' not in item or 'policy_id' not in item:
                msg = _("'invalid input'")
                raise serializers.ValidationError(msg)
            policy_id = item['policy_id']
            if not Policy.objects.filter_by(id=policy_id).exists():
                msg = _('policy id [{policy_id}] does not exist')
                raise serializers.ValidationError(msg.format(policy_id))
        return attrs

    @staticmethod
    def get_policys(obj):
        qs = obj.policyset_relations.filter(is_deleted=False)
        serializer = PolicySetRelationSerializer(qs, many=True)
        return serializer.data

    @staticmethod
    def get_is_used(instance):
        return PolicySetSendDown.objects.filter_by(policyset=instance).exists()

    class Meta:
        model = PolicySet
        fields = ("id", "name", "policys", "creator", "memo", "created_time",
                  "updated_time")
        depth = 1

    @transaction.atomic
    def update(self, instance, validated_data):
        PolicySetRelation.objects.filter_by(policyset=instance).delete()
        policys = self.initial_data.get("policys")
        for policy in policys:
            id = policy.get('policy_id')
            execute_date = policy.get('execute_date')
            new_policy = Policy.objects.get(id=id)
            PolicySetRelation.objects.create(
                policyset=instance,
                policy=new_policy,
                execute_date=execute_date
            )

        instance.__dict__.update(**validated_data)
        instance.save()
        return instance

    @transaction.atomic
    def create(self, validated_data):
        policyset = PolicySet.objects.create(**validated_data)
        if "policys" in self.initial_data:
            policys = self.initial_data.get("policys")
            for policy in policys:
                id = policy.get('policy_id')
                new_policy = Policy.objects.get(id=id)
                execute_date = policy.get('execute_date')
                PolicySetRelation.objects.create(
                    policyset=policyset,
                    policy=new_policy,
                    execute_date=execute_date
                )
        return policyset

    class Meta:
        model = PolicySet
        fields = ('id', 'policys', 'name', 'memo', 'creator', 'created_time',
                  'updated_time', 'is_used')
