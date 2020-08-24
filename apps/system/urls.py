from django.urls import path, include
from .views import DictViewSet, TestView, RoleViewSet, DeptViewSet, MenuViewSet, UserViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('dict', DictViewSet, basename="dict")
router.register('user', UserViewSet, basename="user")
router.register('dept', DeptViewSet, basename="dept")
router.register('menu', MenuViewSet, basename="menu")
router.register('role', RoleViewSet, basename="role")

urlpatterns = [
    path('', include(router.urls)),
    path('test/', TestView.as_view())
]
