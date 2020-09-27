import re

from django.core.cache import cache
from django.db.models import Q
from jwt import decode as jwt_decode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenVerifySerializer,
)

from server.settings import SECRET_KEY
from utils.constant import E_MAIL_REGULAR, PHONE_REGULAR
from .models import Dict, DictType, Dept, Menu, Role, Users, Position
from .rbac_perm import get_permission_list


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    token验证
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        perms = get_permission_list(self.user)
        access_token = refresh.access_token
        token = "Bearer " + str(access_token)
        cache.set(self.user.user_name + "__token", str(access_token), 60 * 60 * 24)
        user_serializer = UserListSerializer(self.user)

        data["token"] = token
        data["user"] = user_serializer.data

        data["perms"] = perms

        data.pop("refresh")
        data.pop("access")

        return data


class MyTokenVerifySerializer(TokenVerifySerializer):
    """
    token验证
    """

    def validate(self, attrs):
        """
        attrs['token']: 是请求的token
        settings.SECRET_KEY: setting.py默认的key 除非在配置文件中修改了
        algorithms: 加密的方法
        """
        decoded_data = jwt_decode(attrs["token"], SECRET_KEY, algorithms=["HS256"])
        return decoded_data


class DictTypeSerializer(serializers.ModelSerializer):
    """
    数据字典类型序列化
    """

    class Meta:
        model = DictType
        fields = "__all__"

    # TODO 字典类型名称


class DictSerializer(serializers.ModelSerializer):
    """
    数据字典序列化
    """

    # fullname = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Dict
        fields = "__all__"

    # TODO 字典名称


class PositionSerializer(serializers.ModelSerializer):
    """
    职位/岗位序列化
    """

    class Meta:
        model = Position
        fields = "__all__"

    # TODO 职位名称


class DeptSerializer(serializers.ModelSerializer):
    """
    部门序列化
    """

    class Meta:
        model = Dept
        fields = "__all__"

    # TODO 校验部门名称


class MenuSerializer(serializers.ModelSerializer):
    """
    菜单序列化
    """

    menu_id = None

    class Meta:
        model = Menu
        fields = "__all__"

    def validate_menu_name(self, menu_name):
        if self.menu_id is None:
            self.menu_id = self.initial_data["menu_id"]
        if (
                Users.objects.filter(~Q(menu_id=self.menu_id), menu_name=menu_name).count()
                > 0
        ):
            raise serializers.ValidationError("菜单名称已经存在")
        return menu_name


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化
    """

    # menus = MenuSerializer(many=True, read_only=True)
    role_id = None

    class Meta:
        model = Role
        fields = "__all__"

    def validate_role_name(self, role_name):
        if self.role_id is None:
            self.role_id = self.initial_data["role_id"]
        if (
                Users.objects.filter(~Q(role_id=self.role_id), role_name=role_name).count()
                > 0
        ):
            raise serializers.ValidationError("角色名称已经存在")
        return role_name


class UserLoginSerializer(serializers.ModelSerializer):
    """
    用户列表序列化
    """

    dept = DeptSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = Users
        fields = [
            "id",
            "phone",
            "email",
            "nick_name",
            "gender",
            "dept",
            "user_name",
            "is_admin",
            "avatar_name",
            "avatar_path",
            "pwd_reset_time",
            "is_activate",
            "is_deleted",
            "update_at",
            "create_at",
            "create_by",
            "update_by",
            "roles",
            "position",
        ]


class UserListSerializer(serializers.ModelSerializer):
    """
    用户列表序列化
    """

    dept_name = serializers.StringRelatedField(source="dept")
    position_name = serializers.StringRelatedField(source="position")
    roles_name = serializers.StringRelatedField(source="roles", many=True)

    class Meta:
        model = Users
        fields = [
            "id",
            "phone",
            "email",
            "nick_name",
            "gender",
            "dept",
            "dept_name",
            "user_name",
            "is_admin",
            "avatar_name",
            "avatar_path",
            "pwd_reset_time",
            "is_activate",
            "is_deleted",
            "update_at",
            "create_at",
            "create_by",
            "update_by",
            "roles",
            "roles_name",
            "position",
            "position_name",
        ]


class UserModifySerializer(serializers.ModelSerializer):
    """
    用户编辑序列化
    """

    user_id = None
    phone = serializers.CharField(max_length=11, required=True)
    email = serializers.CharField(max_length=255, required=True)
    dept = serializers.PrimaryKeyRelatedField(queryset=Dept.objects.all())
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all())
    roles = serializers.PrimaryKeyRelatedField(many=True, queryset=Role.objects.all())

    class Meta:
        model = Users
        fields = [
            "id",
            "user_name",
            "nick_name",
            "gender",
            "phone",
            "email",
            "dept",
            "avatar_path",
            "avatar_name",
            "is_activate",
            "is_admin",
            "roles",
            "position",
        ]

    def validate_user_name(self, user_name):
        if self.user_id is None:
            self.user_id = self.initial_data["id"]
        if Users.objects.filter(~Q(id=self.user_id), user_name=user_name).count() > 0:
            raise serializers.ValidationError(user_name + " 账号已存在")
        return user_name

    def validate_phone(self, phone):
        re_phone = PHONE_REGULAR
        if self.user_id is None:
            self.user_id = self.initial_data["id"]
        if not re.match(re_phone, phone):
            raise serializers.ValidationError("手机号码不合法")
        if Users.objects.filter(~Q(id=self.user_id), phone=phone).count() > 0:
            raise serializers.ValidationError("手机号已经被注册")
        return phone

    def validate_email(self, email):
        re_email = E_MAIL_REGULAR
        if self.user_id is None:
            self.user_id = self.initial_data["id"]
        if not re.match(re_email, email):
            raise serializers.ValidationError("邮箱格式不合法")
        if Users.objects.filter(~Q(id=self.user_id), email=email).count() > 0:
            raise serializers.ValidationError("邮箱已经被注册")
        return email


class UserCreateSerializer(serializers.ModelSerializer):
    """
    创建用户序列化
    """

    user_name = serializers.CharField(required=True)
    phone = serializers.CharField(max_length=11, required=True)
    dept = serializers.PrimaryKeyRelatedField(queryset=Dept.objects.all())
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all())
    roles = serializers.PrimaryKeyRelatedField(many=True, queryset=Role.objects.all())

    class Meta:
        model = Users
        fields = [
            "id",
            "user_name",
            "nick_name",
            "gender",
            "phone",
            "email",
            "dept",
            "is_activate",
            "is_admin",
            "avatar_path",
            "avatar_name",
            "is_admin",
            "position",
            "roles",
        ]

    def validate_user_name(self, user_name):
        if Users.objects.filter(user_name=user_name):
            raise serializers.ValidationError(user_name + " 账号已存在")
        return user_name

    def validate_phone(self, phone):
        re_phone = PHONE_REGULAR
        if not re.match(re_phone, phone):
            raise serializers.ValidationError("手机号码不合法")
        if Users.objects.filter(phone=phone):
            raise serializers.ValidationError("手机号已经被注册")
        return phone

    def validate_email(self, email):
        re_email = E_MAIL_REGULAR
        if not re.match(re_email, email):
            raise serializers.ValidationError("邮箱格式不合法")
        if Users.objects.filter(email=email):
            raise serializers.ValidationError("邮箱已经被注册")
        return email
