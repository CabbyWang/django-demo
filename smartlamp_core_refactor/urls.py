"""smartlamp_core_refactor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include

# from django.contrib import admin

from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from user.auth import CustomObtainJSONWebToken
from user.views import UserGroupViewSet, UserViewSet
from hub.views import HubViewSet

import xadmin
xadmin.autodiscover()

obtain_jwt_token = CustomObtainJSONWebToken.as_view()

router = routers.DefaultRouter()

# 用户组
router.register('user-groups', UserGroupViewSet, basename='user-groups')

# 用户
router.register('users', UserViewSet, basename='users')

# 用户权限(集控)
# router.register('permissions', PermissionViewSet, basename='permissions')

# 集控
router.register('hubs', HubViewSet, basename='hubs')


urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^', include(router.urls)),
    # url(r'^admin/', admin.site.urls),
    url(r'^login/', obtain_jwt_token),
    url(r'api_docs/', include_docs_urls(title="smartlamp")),
]
