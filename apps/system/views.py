import logging

from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from notifications.signals import notify
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenViewBase, TokenObtainPairView

from apps.system.rbac_perm import RbacPermission
from apps.system.service import MenuBuildService, DeptBuildService
from utils.constant import DEFAULT_PASSWORD
from utils.crypto_util import rsa_decode
from utils.pagination import MyPagination
from utils.querySetUtil import get_child_queryset2
from .models import Dict, DictType, Dept, Role, Users, Position, Menu
from .serializers import (
    MyTokenObtainPairSerializer,
    DictSerializer,
    DictTypeSerializer,
    RoleSerializer,
    DeptSerializer,
    MenuSerializer,
    UserListSerializer,
    UserModifySerializer,
    UserCreateSerializer,
    PositionSerializer,
    MyTokenVerifySerializer,
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


class MyTokenVerifyView(TokenViewBase):
    serializer_class = MyTokenVerifySerializer


class TestView(APIView):
    perms_map = {"get": "test_view"}  # 单个API控权

    def get(self, request, *args, **kwargs):
        notify.send(request.user, recipient=request.user, verb="通知test")
        return Response(status=status.HTTP_200_OK)


class TestRoleView(APIView):
    # @cache_response(key_func="role_func")
    def get(self, request, *args, **kwargs):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def role_func(self, view_instance, view_method, request, args, kwargs):
        return "role_{}".format(request.user.id)


class LogoutView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):  # 可将token加入黑名单
        serializer = UserListSerializer(data=request.data)
        if serializer:
            serializer.is_valid(raise_exception=False)
            user_name = serializer.data["user_name"]
            cache.delete(user_name + "__token")
            cache.delete(user_name + "__perms")
        return Response(status=status.HTTP_200_OK)


class PositionViewSet(ModelViewSet):
    """
    岗位-增删改查
    """

    perms_map = {
        "get": "*",
        "post": "position_add",
        "put": "position_edit",
        "delete": "position_del",
    }
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    pagination_class = None
    search_fields = ["position_name", "method"]
    ordering_fields = ["position_id"]
    ordering = ["-position_id"]
    _paginator = MyPagination()

    def get_queryset(self, *args, **kwargs):
        position_name = self.request.query_params.get("position_name", None)
        if position_name:
            return Position.objects.filter(
                is_deleted=False,
                position_name__contains=position_name,
            ).order_by("-position_id")
        else:
            return Position.objects.filter(is_deleted=False).order_by("-position_id")

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
        "post": "dept_add",
        "put": "dept_edit",
        "delete": "dept_del",
    }
    queryset = Dept.objects.all()
    serializer_class = DeptSerializer
    pagination_class = None
    search_fields = ["dept_name", "method"]
    # ordering_fields = ["pk"]
    # ordering = ["pk"]

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
        "post": "role_add",
        "put": "role_edit",
        "delete": "role_del",
    }
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = None
    search_fields = ["role_name"]
    # ordering_fields = ["role_id"]
    # ordering = ["-role_id"]
    _paginator = MyPagination()

    def get_queryset(self, *args, **kwargs):
        role_name = self.request.query_params.get("role_name", None)
        if role_name:
            return Role.objects.filter(
                is_deleted=False, role_name__contains=role_name
            ).order_by("-role_id")
        else:
            return Role.objects.filter(is_deleted=False).order_by("-role_id")

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
        "post": "menu_add",
        "put": "menu_edit",
        "delete": "menu_del",
    }
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    pagination_class = None
    search_fields = ["title"]

    # ordering_fields = ["pk"]
    # ordering = ["pk"]

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


class DictTypeViewSet(ModelViewSet):
    """
    数据字典类型-增删改查
    """

    perms_map = {
        "get": "*",
        "post": "dict_type_add",
        "put": "dict_type_edit",
        "delete": "dict_type_del",
    }
    queryset = DictType.objects.all()
    serializer_class = DictTypeSerializer
    pagination_class = None
    search_fields = ["dict_type_name"]
    ordering_fields = ["code"]
    ordering = ["-code"]
    _paginator = MyPagination()

    def get_queryset(self, *args, **kwargs):
        dict_type_name = self.request.query_params.get("dict_type_name", None)
        if dict_type_name:
            return DictType.objects.filter(
                is_deleted=False,
                dict_type_name__contains=dict_type_name,
            ).order_by("-dict_type_id")
        else:
            return DictType.objects.filter(is_deleted=False).order_by("-dict_type_id")

    def paginate_queryset(self, queryset):
        """
        如果查询参数里没有page但有type或type__code时则不分页,否则请求分页
        """
        if self.paginator is None:
            return None
        elif not self.request.query_params.get("page", None):
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)


class DictViewSet(ModelViewSet):
    """
    数据字典-增删改查
    """

    perms_map = {
        "get": "*",
        "post": "dict_add",
        "put": "dict_edit",
        "delete": "dict_del",
    }
    # queryset = Dict.objects.get_queryset(all=True) # 获取全部的,包括软删除的
    queryset = Dict.objects.all().order_by("-dict_id")
    filter_set_fields = ["type", "is_used", "type__code"]
    serializer_class = DictSerializer
    search_fields = ["dict_name"]
    ordering_fields = ["sort"]
    ordering = ["-sort"]
    _paginator = MyPagination()

    def get_queryset(self, *args, **kwargs):
        dict_name = self.request.query_params.get("dict_name", None)
        if dict_name:
            return Dict.objects.filter(is_deleted=False, dict_name__contains=dict_name)
        else:
            return Dict.objects.filter(is_deleted=False)

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
        "post": "user_add",
        "put": "user_edit",
        "delete": "user_del",
    }
    queryset = Users.objects.all().order_by("-id")
    serializer_class = UserListSerializer
    # filter_set_class = UserFilter
    search_fields = ["user_name", "phone", "email"]
    ordering_fields = ["-id"]
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
            queryset = queryset.filter(user_name__contains=user_name, is_deleted=False)
        return queryset

    def get_serializer_class(self):
        # 根据请求类型动态变更serializer
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "list":
            return UserListSerializer
        return UserModifySerializer

    def create(self, request, *args, **kwargs):

        password = request.data["password"] if "password" in request.data else None
        if password:
            password = make_password(rsa_decode(password))
        else:
            # 创建用户默认添加密码
            password = make_password(DEFAULT_PASSWORD)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(password=password)
        return Response(serializer.data)

    @action(
        methods=["put"],
        detail=False,
        permission_classes=[RbacPermission],
        url_path="change_password",
    )
    def change_password(self, request):
        """
        修改密码
        """
        user = request.user

        old_password = (
            rsa_decode(request.data["old_password"])
            if request.data["old_password"]
            else None
        )
        if old_password and check_password(old_password, user.password):
            new_password1 = (
                rsa_decode(request.data["new_password1"])
                if request.data["new_password1"]
                else None
            )
            new_password2 = (
                rsa_decode(request.data["new_password2"])
                if request.data["new_password2"]
                else None
            )
            if new_password1 and new_password2 and (new_password1 == new_password2):
                user.set_password(new_password2)
                user.save()
                return Response("密码修改成功!", status=status.HTTP_200_OK)
            else:
                return Response("新密码两次输入不一致!", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("旧密码错误!", status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["put"],
        detail=True,
        permission_classes=[RbacPermission],
        url_path="reset_password",
    )
    def reset_password(self, request, pk=None):
        if pk:
            user = Users.objects.get(id=pk)
            password = make_password(DEFAULT_PASSWORD)
            user.set_password(password)
            user.save()
            return Response("密码修改成功!", status=status.HTTP_200_OK)
