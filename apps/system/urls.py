from django.urls import path, include
from rest_framework import routers

from .views import (
    DictViewSet,
    DictTypeViewSet,
    TestView,
    RoleViewSet,
    DeptViewSet,
    MenuViewSet,
    UserViewSet,
    TestRoleView,
    MyTokenObtainPairView,
    PositionViewSet,
    LogoutView,
)

router = routers.DefaultRouter()
router.register("dict", DictViewSet, basename="dict")
router.register("dicttype", DictTypeViewSet, basename="dict")
router.register("user", UserViewSet, basename="user")
router.register("dept", DeptViewSet, basename="dept")
router.register("menu", MenuViewSet, basename="menu")
router.register("role", RoleViewSet, basename="role")
router.register("position", PositionViewSet, basename="position")

urlpatterns = [
    path("", include(router.urls)),
    path("test/", TestView.as_view()),
    # path("build/", BuildMenuView.as_view()),
    # path("allMenu/", MenuAllView.as_view()),
    path("roleTest/", TestRoleView.as_view()),
    path("login/", MyTokenObtainPairView.as_view()),
    path("logout/", LogoutView.as_view()),
]
