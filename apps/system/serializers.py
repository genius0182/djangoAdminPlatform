import re

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        token = "Bearer " + str(refresh.access_token)
        user_serializer = UserLoginSerializer(self.user)

        data["token"] = token
        data["user"] = user_serializer.data

        data["perms"] = perms

        data.pop("refresh")
        data.pop("access")
        return data


class DictTypeSerializer(serializers.ModelSerializer):
    """
    数据字典类型序列化
    """

    class Meta:
        model = DictType
        fields = "__all__"


class DictSerializer(serializers.ModelSerializer):
    """
    数据字典序列化
    """

    # fullname = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Dict
        fields = "__all__"


class PositionSerializer(serializers.ModelSerializer):
    """
    职位/岗位序列化
    """

    class Meta:
        model = Position
        fields = "__all__"


class DeptSerializer(serializers.ModelSerializer):
    """
    部门序列化
    """

    class Meta:
        model = Dept
        fields = "__all__"


class MenuSerializer(serializers.ModelSerializer):
    """
    菜单序列化
    """

    class Meta:
        model = Menu
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化
    """

    # menus = MenuSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = "__all__"


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

    phone = serializers.CharField(max_length=11, read_only=True)
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
            "is_admin",
            "roles",
            "position",
        ]

    @staticmethod
    def validate_phone(phone):
        re_phone = r"^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        if not re.match(re_phone, phone):
            raise serializers.ValidationError("手机号码不合法")
        return phone


class UserCreateSerializer(serializers.ModelSerializer):
    """
    创建用户序列化
    """

    user_name = serializers.CharField(required=True)
    phone = serializers.CharField(max_length=11, read_only=True)
    dept = serializers.PrimaryKeyRelatedField(queryset=Dept.objects.all())
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all())

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
            "is_admin",
            "dept",
            "position",
        ]

    @staticmethod
    def validate_username(user_name):
        if Users.objects.filter(user_name=user_name):
            raise serializers.ValidationError(user_name + " 账号已存在")
        return user_name

    @staticmethod
    def validate_phone(phone):
        re_phone = r"^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        if not re.match(re_phone, phone):
            raise serializers.ValidationError("手机号码不合法")
        if Users.objects.filter(phone=phone):
            raise serializers.ValidationError("手机号已经被注册")
        return phone
