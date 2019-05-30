"""smartlamp URL Configuration

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
from django.conf import settings
from django.views.static import serve

from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from base.views import UnitViewSet
from communication.views import CommunicateViewSet
from equipment.views import HubViewSet, LampCtrlViewSet, PoleViewSet, \
    LampViewSet, CBoxViewSet, CableViewSet
from group.views import LampCtrlGroupViewSet
from report.views import ReportViewSet
from status.views import StatusViewSet, LampCtrlStatusViewSet, HubLogViewSet
from user.auth import CustomObtainJSONWebToken
from user.views import UserGroupViewSet, UserViewSet
from setting.views import SettingViewSet
from projectinfo.views import ProjectInfoViewSet
from notify.views import LogViewSet, AlertViewSet, AlertAudioViewSet
from policy.views import PolicyViewSet, PolicySetViewSet
from workorder.views import (
    WorkOrderViewSet, WorkOrderImageViewSet, WorkOrderAudioViewSet,
    InspectionViewSet, InspectionImageViewSet, InspectionItemViewSet
)

import xadmin

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

# 管理单元
router.register('units', UnitViewSet, base_name='units')

# 设置
router.register('settings', SettingViewSet, base_name='settings')

# 灯控
router.register('lampctrls', LampCtrlViewSet, base_name='lampctrls')

# 灯控状态
router.register('lampctrlstatus', LampCtrlStatusViewSet, base_name='lampctrlstatus')

# 项目信息
router.register('projectinfo', ProjectInfoViewSet, base_name='projectinfo')

# 灯杆
router.register('poles', PoleViewSet, base_name='poles')

# 灯具
router.register('lamps', LampViewSet, base_name='lamps')

# 控制箱
router.register('cboxs', CBoxViewSet, base_name='cboxs')

# 电缆
router.register('cables', CableViewSet, base_name='cables')

# 日志
router.register('logs', LogViewSet, base_name='logs')

# 告警
router.register('alerts', AlertViewSet, base_name='alerts')

# 告警语音
router.register('alertaudios', AlertAudioViewSet, base_name='alertaudios')

# 策略
router.register('policies', PolicyViewSet, base_name='policies')

# 策略集
router.register('policysets', PolicySetViewSet, base_name='policysets')

# 工单
router.register('workorders', WorkOrderViewSet, base_name='workorders')

# 工单图片
router.register('workorderimages', WorkOrderImageViewSet, base_name='workorderimages')

# 工单语音
router.register('workorderaudios', WorkOrderAudioViewSet, base_name='workorderaudios')

# 巡检
router.register('inspections', InspectionViewSet, base_name='inspections')

# 巡检图片
router.register('inspection-images', InspectionImageViewSet, base_name='inspection-images')

# 巡检项
router.register('inspection-items', InspectionItemViewSet, base_name='inspection-items')

# 报表
router.register('reports', ReportViewSet, base_name='reports')

# 状态
router.register('status', StatusViewSet, base_name='status')

# 灯控分组
router.register('lampctrlgroups', LampCtrlGroupViewSet, base_name='lampctrlgroups')

# 集控通讯
router.register('communicate', CommunicateViewSet, base_name='communicate')

# 获取集控日志
router.register('hub-log', HubLogViewSet, base_name='hub-log')


urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^', include(router.urls)),
    # url(r'^admin/', admin.site.urls),
    url(r'^login/', obtain_jwt_token),
    url(r'api_docs/', include_docs_urls(title="smartlamp",
                                        authentication_classes=[],
                                        permission_classes=[])),
    url(r'^(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR})
]
