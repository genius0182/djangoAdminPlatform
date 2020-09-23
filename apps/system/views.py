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

from apps.system.service import MenuBuildService, DeptBuildService
from utils.pagination import MyPagination
from utils.querySetUtil import get_child_queryset2
from .models import Dict, Dept, Role, Users, Position, Menu
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
    PositionSerializer,
)

logger = logging.getLogger("log")

menu_build_service = MenuBuildService()
dept_build_service = DeptBuildService()


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


class PositionViewSet(ModelViewSet):
    """
    部门-增删改查
    """

    perms_map = {
        "get": "*",
        "post": "position_create",
        "put": "position_update",
        "delete": "position_delete",
    }
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    pagination_class = None
    search_fields = ["position_name", "method"]
    ordering_fields = ["pk"]
    ordering = ["pk"]
    _paginator = MyPagination()

    def get_queryset(self, *args, **kwargs):
        position_name = self.request.query_params.get("position_name", None)
        if position_name:
            return Position.objects.filter(
                is_deleted=False,
                is_activate=True,
                position_name__contains=position_name,
            )
        else:
            return Position.objects.filter(is_deleted=False, is_activate=True)

    def paginate_queryset(self, queryset):
        """
        如果查询参数里没有page但有type或type__code时则不分页,否则请求分页
        """
        if self.paginator is None:
            return None
        elif not self.request.query_params.get("page", None):
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)


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
    search_fields = ["dept_name", "method"]
    ordering_fields = ["pk"]
    ordering = ["pk"]

    _paginator = MyPagination()

    def paginate_queryset(self, queryset):
        """
        如果查询参数里没有page但有type或type__code时则不分页,否则请求分页
        """
        if self.paginator is None:
            return None
        elif not self.request.query_params.get("page", None):
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(
        methods=["get"],
        detail=False,
        perms_map={"get": "*"},
        url_path="build",
    )
    def build(self, request, *args, **kwargs):
        dept_name = request.query_params.get("dept_name", None)
        result = dept_build_service.get_dept_all(dept_name)
        return Response(result)


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
    search_fields = ["role_name"]
    ordering_fields = ["pk"]
    ordering = ["pk"]
    _paginator = MyPagination()

    def get_queryset(self, *args, **kwargs):
        role_name = self.request.query_params.get("role_name", None)
        if role_name:
            return Role.objects.filter(
                is_deleted=False, is_activate=True, role_name__contains=role_name
            )
        else:
            return Role.objects.filter(is_deleted=False, is_activate=True)

    def paginate_queryset(self, queryset):
        """
        如果查询参数里没有page但有type或type__code时则不分页,否则请求分页
        """
        if self.paginator is None:
            return None
        elif not self.request.query_params.get("page", None):
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)


class MenuViewSet(ModelViewSet):
    """"""

    perms_map = {
        "get": "*",
        "post": "menu_create",
        "put": "menu_update",
        "delete": "menu_delete",
    }
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    pagination_class = None
    search_fields = ["title"]
    ordering_fields = ["pk"]
    ordering = ["pk"]

    # _paginator = MyPagination()
    #
    # def paginate_queryset(self, queryset):
    #     """
    #     如果查询参数里没有page但有type或type__code时则不分页,否则请求分页
    #     """
    #     if self.paginator is None:
    #         return None
    #     elif not self.request.query_params.get("page", None):
    #         return None
    #     return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(
        methods=["get"],
        detail=False,
        # permission_classes=[IsAuthenticated],  # perms_map={'put':'change_password'}
        perms_map={"get": "*"},
        url_path="build",
    )
    def build(self, request):
        user_id = request.query_params.get("user_id", None)
        logger.debug("user_id={}".format(user_id))
        users = Users.objects.filter(
            id=user_id, is_activate=True, is_deleted=False
        ).first()
        result = menu_build_service.get_role_menus(users)
        return Response(result)

    @action(
        methods=["get"],
        detail=False,
        perms_map={"get": "*"},
        url_path="all",
    )
    def all(self, request):
        menu_name = request.query_params.get("menu_name", None)
        result = menu_build_service.get_all_menus(menu_name)

        return Response(result)


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
    search_fields = ["dict_name"]
    ordering_fields = ["sort"]
    ordering = ["sort"]
    _paginator = MyPagination()

    def get_queryset(self, *args, **kwargs):
        dict_name = self.request.query_params.get("dict_name", None)
        if dict_name:
            return Dict.objects.filter(
                is_deleted=False, is_activate=True, dict_name__contains=dict_name
            )
        else:
            return Dict.objects.filter(is_deleted=False, is_activate=True)

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
    _paginator = MyPagination()

    def paginate_queryset(self, queryset):
        """
        如果查询参数里没有page但有type或type__code时则不分页,否则请求分页
        """
        if self.paginator is None:
            return None
        elif not self.request.query_params.get("page", None):
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_queryset(self):
        queryset = self.queryset
        if hasattr(self.get_serializer_class(), "setup_eager_loading"):
            queryset = self.get_serializer_class().setup_eager_loading(queryset)  # 性能优化
        dept = self.request.query_params.get("dept", None)  # 该部门及其子部门所有员工
        user_name = self.request.query_params.get("user_name", None)
        if dept is not None:
            dept_query_set = get_child_queryset2(Dept.objects.get(pk=dept))
            queryset = queryset.filter(dept__in=dept_query_set)
        if user_name:
            queryset = queryset.filter(user_name=user_name)
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
