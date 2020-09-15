import logging

from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenViewBase, TokenObtainPairView

from utils.querySetUtil import get_child_queryset2
from .models import Dict, Dept, Role, Users
# from .filters import UserFilter
from .rbac_perm import get_permission_list
from .serializers import (
    MyTokenObtainPairSerializer,
    DictSerializer,
    RoleSerializer,
    DeptSerializer,
    MenuSerializer,
    UserListSerializer,
    UserModifySerializer,
    UserCreateSerializer,
)

logger = logging.getLogger("log")


class MyTokenObtainPairView(TokenObtainPairView):
    """
    自定义得到token user_name: 账号或者密码 password: 密码或者验证码
    """

    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenViewBase):
    """
    自定义刷新token refresh: 刷新token的元素
    """

    serializer_class = TokenRefreshSerializer


class TestRoleView(APIView):
    @cache_response(key_func="role_func")
    def get(self, request, *args, **kwargs):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def role_func(self, view_instance, view_method, request, args, kwargs):
        return "role_{}".format(request.user.id)


class DeptViewSet(ModelViewSet):
    """
    部门-增删改查
    """

    perms_map = {
        "get": "*",
        "post": "dept_create",
        "put": "dept_update",
        "delete": "dept_delete",
    }
    queryset = Dept.objects.all()
    serializer_class = DeptSerializer
    pagination_class = None
    search_fields = ["name", "method"]
    ordering_fields = ["pk"]
    ordering = ["pk"]


class RoleViewSet(ModelViewSet):
    """
    角色-增删改查
    """

    perms_map = {
        "get": "*",
        "post": "role_create",
        "put": "role_update",
        "delete": "role_delete",
    }
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = None
    search_fields = ["name"]
    ordering_fields = ["pk"]
    ordering = ["pk"]


class MenuViewSet(ModelViewSet):
    """"""

    perms_map = {
        "get": "*",
        "post": "menu_create",
        "put": "menu_update",
        "delete": "menu_delete",
    }
    queryset = Role.objects.all()
    serializer_class = MenuSerializer
    pagination_class = None
    search_fields = ["title"]
    ordering_fields = ["pk"]
    ordering = ["pk"]


class TestView(APIView):
    perms_map = {"get": "test_view"}  # 单个API控权
    pass


class DictViewSet(ModelViewSet):
    """
    数据字典-增删改查
    """

    perms_map = {
        "get": "*",
        "post": "dict_create",
        "put": "dict_update",
        "delete": "dict_delete",
    }
    # queryset = Dict.objects.get_queryset(all=True) # 获取全部的,包括软删除的
    queryset = Dict.objects.all()
    filter_set_fields = ["type", "is_used", "type__code"]
    serializer_class = DictSerializer
    search_fields = ["name"]
    ordering_fields = ["sort"]
    ordering = ["sort"]

    def paginate_queryset(self, queryset):
        """
        如果查询参数里没有page但有type或type__code时则不分页,否则请求分页
        """
        if self.paginator is None:
            return None
        elif (not self.request.query_params.get("page", None)) and (
                (self.request.query_params.get("type__code", None))
                or (self.request.query_params.get("type", None))
        ):
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[],
        authentication_classes=[],
        url_name="correct_dict",
    )
    def correct(self, request):
        for i in Dict.objects.all():
            i.save()
        return Response(status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    """
    用户管理-增删改查
    """

    perms_map = {
        "get": "*",
        "post": "user_create",
        "put": "user_update",
        "delete": "user_delete",
    }
    queryset = Users.objects.all()
    serializer_class = UserListSerializer
    # filter_set_class = UserFilter
    search_fields = ["user_name", "phone", "email"]
    ordering_fields = ["-pk"]

    def get_queryset(self):
        queryset = self.queryset
        if hasattr(self.get_serializer_class(), "setup_eager_loading"):
            queryset = self.get_serializer_class().setup_eager_loading(queryset)  # 性能优化
        dept = self.request.query_params.get("dept", None)  # 该部门及其子部门所有员工
        if dept is not None:
            dept_query_set = get_child_queryset2(Dept.objects.get(pk=dept))
            queryset = queryset.filter(dept__in=dept_query_set)
        return queryset

    def get_serializer_class(self):
        # 根据请求类型动态变更serializer
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "list":
            return UserListSerializer
        return UserModifySerializer

    def create(self, request, *args, **kwargs):
        # 创建用户默认添加密码
        password = request.data["password"] if "password" in request.data else None
        if password:
            password = make_password(password)
        else:
            password = make_password("123456")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(password=password)
        return Response(serializer.data)

    @action(
        methods=["put"],
        detail=False,
        permission_classes=[IsAuthenticated],  # perms_map={'put':'change_password'}
        url_name="change_password",
    )
    def password(self, request, pk=None):
        """
        修改密码
        """
        user = request.user
        old_password = request.data["old_password"]
        if check_password(old_password, user.password):
            new_password1 = request.data["new_password1"]
            new_password2 = request.data["new_password2"]
            if new_password1 == new_password2:
                user.set_password(new_password2)
                user.save()
                return Response("密码修改成功!", status=status.HTTP_200_OK)
            else:
                return Response("新密码两次输入不一致!", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("旧密码错误!", status=status.HTTP_400_BAD_REQUEST)

    # perms_map={'get':'*'}, 自定义action控权
    @action(
        methods=["get"],
        detail=False,
        url_name="my_info",
        permission_classes=[IsAuthenticated],
    )
    def info(self, request, pk=None):
        """
        初始化用户信息
        """
        user = request.user
        perms = get_permission_list(user)
        data = {
            "id": user.id,
            "user_name": user.user_name,
            "nick_name": user.nick_name,
            "roles": user.roles.values_list("name", flat=True),
            # 'avatar': request._request._current_scheme_host + '/media/' + str(user.image),
            "avatar_path": user.avatar_path,
            "perms": perms,
        }
        return Response(data)
