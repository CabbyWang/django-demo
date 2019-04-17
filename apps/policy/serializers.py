#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/4/4
"""
from django.db import transaction

from rest_framework import serializers

from .models import Policy, PolicySet, PolicySetRelation, PolicySetSendDown


class PolicySerializer(serializers.ModelSerializer):
    # ('时控', '经纬度', '光控', '回路控制')
    name = serializers.CharField(max_length=255)
    type = serializers.ChoiceField([(0, '时控'), (1, '经纬度'), (2, '光控'), (3, '回路控制')])
    item = serializers.ListField(allow_empty=True)
    creator = serializers.CharField(
        write_only=True,
        default=serializers.CurrentUserDefault()
    )
    is_used = serializers.SerializerMethodField()

    @staticmethod
    def get_is_used(instance):
        return PolicySetRelation.objects.filter_by(policy=instance).exists()

    def validate_item(self, item):
        """验证item"""
        if 'type' not in self.initial_data:
            return item
        type = self.initial_data['type']
        type0 = ('action', 'minute', 'hour')
        type1 = ('action', 'longitude', 'latitude', 's_type', 'offset')
        type2 = ('action', 'detect_period', 'lower_bound', 'higher_bound',
                 'tolerance')
        type3 = ('action', 'minute', 'hour', 'second')
        for im in item:
            if type == 0 and not all(i in im for i in type0):
                raise serializers.ValidationError('item格式错误')
            if type == 1 and not all(i in im for i in type1):
                raise serializers.ValidationError('item格式错误')
            if type == 2 and not all(i in im for i in type2):
                raise serializers.ValidationError('item格式错误')
            if type == 3 and not all(i in im for i in type3):
                raise serializers.ValidationError('item格式错误')
        return item

    class Meta:
        model = Policy
        fields = ('name', 'type', 'item', 'is_used', 'creator', 'created_time',
                  'updated_time')


class PolicySetRelationSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='policy.id')
    name = serializers.ReadOnlyField(source='policy.name')
    type = serializers.ReadOnlyField(source='policy.type')
    item = serializers.ReadOnlyField(source='policy.item')

    class Meta:
        model = PolicySetRelation
        fields = ('id', 'name', 'type', 'item', 'execute_date')


class PolicySetSerializer(serializers.ModelSerializer):

    policys = PolicySetRelationSerializer(
        source='policyset_relations', many=True, read_only=True)
    name = serializers.CharField(max_length=255)
    creator = serializers.CharField(
        write_only=True,
        default=serializers.CurrentUserDefault()
    )
    created_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True,
                                             format='%Y-%m-%d %H:%M:%S')
    is_used = serializers.SerializerMethodField()

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
            id = policy.get('id')
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
                id = policy.get('id')
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
        fields = ('policys', 'name', 'memo', 'creator', 'created_time',
                  'updated_time', 'is_used')
