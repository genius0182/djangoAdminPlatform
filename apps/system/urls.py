from django.urls import path, include
from rest_framework import routers

from .views import DictViewSet, TestView, RoleViewSet, DeptViewSet, MenuViewSet, UserViewSet, TestRoleView

router = routers.DefaultRouter()
router.register('dict', DictViewSet, basename="dict")
router.register('user', UserViewSet, basename="user")
router.register('dept', DeptViewSet, basename="dept")
router.register('menu', MenuViewSet, basename="menu")
router.register('role', RoleViewSet, basename="role")
# router.register('roleTest', TestRoleView.as_view(), basename="test")

urlpatterns = [
    path('', include(router.urls)),
    path('test/', TestView.as_view()),
    path('roleTest/', TestRoleView.as_view())
]
