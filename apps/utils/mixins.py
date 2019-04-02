#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/14
"""
import os

from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin as _ListModelMixin

from utils.paginator import CustomPagination


class UploadModelMixin(object):
    """
    Upload Image Mixin
    """
    def upload(self, request, *args, **kwargs):
        image_uri = self.perform_upload(request)
        return Response(status=status.HTTP_200_OK, data={"image": image_uri})

    def perform_upload(self, request):
        asset_type = request.path.strip("/").split("/")[1]
        _, image = request.FILES.items()[0]
        image_content = image.read()
        image_name = image.name
        image_dir = os.path.join(settings.MEDIA_ROOT, "asset", asset_type)
        if not os.path.exists(image_dir):
            os.mkdir(image_dir)
        path = os.path.join(image_dir, image_name)
        with open(path, "wb") as f:
            f.write(image_content)
        return os.path.join("asset", asset_type, image_name)


class UploadModelMixin2(object):
    """
    Upload Image mixin.
    """

    def upload(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        image_uri = self.perform_upload(request)
        return Response(status=status.HTTP_200_OK, data={"image": image_uri})

    def perform_upload(self, request):
        asset_type = request.path.strip("/").split("/")[1]
        _, image = request.FILES.items()[0]
        image_content = image.read()
        image_name = image.name
        image_dir = os.path.join(settings.MEDIA_ROOT, "asset", asset_type)
        if not os.path.exists(image_dir):
            os.mkdir(image_dir)
        path = os.path.join(image_dir, image_name)
        with open(path, "wb") as f:
            f.write(image_content)
        return os.path.join("asset", asset_type, image_name)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class ListModelMixin(_ListModelMixin):
    """
    List a queryset.
    If all = 'true', no paging.
    """

    def list(self, request, *args, **kwargs):
        self.pagination_class = None
        if request.query_params.get('all') != 'true':
            self.pagination_class = CustomPagination
        return super(ListModelMixin, self).list(request, *args, **kwargs)
