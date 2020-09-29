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
from utils.constant import (
    JSON_EMAIL_FORMAT_VALIDATION_ERROR,
    JSON_EMAIL_REGISTERED_VALIDATION_ERROR,
    JSON_PHONE_REGISTERED_VALIDATION_ERROR,
    JSON_PHONE_FORMAT_VALIDATION_ERROR,
    JSON_ACCOUNT_VALIDATION_ERROR,
    JSON_ROLE_VALIDATION_ERROR,
    JSON_MENU_VALIDATION_ERROR,
    JSON_DEPT_VALIDATION_ERROR,
    JSON_POSITION_VALIDATION_ERROR,
    JSON_DICT_VALIDATION_ERROR,
    JSON_DICT_TYPE_VALIDATION_ERROR,
    JSON_DICT_TYPE_CODE_VALIDATION_ERROR,
)
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

    dict_type_name = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    dict_type_id = None

    class Meta:
        model = DictType
        fields = "__all__"

    def validate_dict_type_name(self, dict_type_name):
        if "dict_type_id" not in self.initial_data.keys():
            if DictType.objects.filter(dict_type_name=dict_type_name).count() > 0:
                raise serializers.ValidationError(JSON_DICT_TYPE_VALIDATION_ERROR)
        else:
            self.dict_type_id = self.initial_data["dict_type_id"]
        if (
                DictType.objects.filter(
                    ~Q(dict_type_id=self.dict_type_id), dict_type_name=dict_type_name
                ).count()
                > 0
        ):
            raise serializers.ValidationError(JSON_DICT_TYPE_VALIDATION_ERROR)
        return dict_type_name

    def validate_code(self, code):
        if DictType.objects.filter(code=code):
            raise serializers.ValidationError(JSON_DICT_TYPE_CODE_VALIDATION_ERROR)
        else:
            self.code = self.initial_data["code"]
        if DictType.objects.filter(~Q(code=self.code), code=code).count() > 0:
            raise serializers.ValidationError(JSON_DICT_TYPE_CODE_VALIDATION_ERROR)
        return code


class DictSerializer(serializers.ModelSerializer):
    """
    数据字典序列化
    """

    dict_name = serializers.CharField(required=True)

    dict_id = None

    # fullname = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Dict
        fields = "__all__"

    def validate_dict_name(self, dict_name):
        if "dict_id" not in self.initial_data.keys():
            if Dict.objects.filter(dict_name=dict_name).count() > 0:
                raise serializers.ValidationError(JSON_DICT_VALIDATION_ERROR)
        else:
            self.dict_id = self.initial_data["dict_id"]
        if (
                Dict.objects.filter(~Q(dict_id=self.dict_id), dict_name=dict_name).count()
                > 0
        ):
            raise serializers.ValidationError(JSON_DICT_VALIDATION_ERROR)
        return dict_name


class PositionSerializer(serializers.ModelSerializer):
    """
    职位/岗位序列化
    """

    position_name = serializers.CharField(required=True)

    position_id = None

    class Meta:
        model = Position
        fields = "__all__"

    def validate_position_name(self, position_name):
        if "position_id" not in self.initial_data.keys():
            if Position.objects.filter(position_name=position_name).count() > 0:
                raise serializers.ValidationError(JSON_POSITION_VALIDATION_ERROR)
        else:
            self.position_id = self.initial_data["position_id"]
        if (
                Position.objects.filter(
                    ~Q(position_id=self.position_id), position_name=position_name
                ).count()
                > 0
        ):
            raise serializers.ValidationError(JSON_POSITION_VALIDATION_ERROR)
        return position_name


class DeptSerializer(serializers.ModelSerializer):
    """
    部门序列化
    """

    dept_name = serializers.CharField(required=True)

    dept_id = None

    class Meta:
        model = Dept
        fields = "__all__"

    def validate_dept_name(self, dept_name):
        if "dept_id" not in self.initial_data.keys():
            if Dept.objects.filter(dept_name=dept_name).count() > 0:
                raise serializers.ValidationError(JSON_DEPT_VALIDATION_ERROR)
        else:
            self.dept_id = self.initial_data["dept_id"]
        if (
                Dept.objects.filter(~Q(dept_id=self.dept_id), dept_name=dept_name).count()
                > 0
        ):
            raise serializers.ValidationError(JSON_DEPT_VALIDATION_ERROR)
        return dept_name


class MenuSerializer(serializers.ModelSerializer):
    """
    菜单序列化
    """

    menu_name = serializers.CharField(required=True)

    menu_id = None

    class Meta:
        model = Menu
        fields = "__all__"

    def validate_menu_name(self, menu_name):
        if "menu_id" not in self.initial_data.keys():
            if Menu.objects.filter(menu_name=menu_name).count() > 0:
                raise serializers.ValidationError(JSON_MENU_VALIDATION_ERROR)
        else:
            self.menu_id = self.initial_data["menu_id"]
        if (
                Menu.objects.filter(~Q(menu_id=self.menu_id), menu_name=menu_name).count()
                > 0
        ):
            raise serializers.ValidationError(JSON_MENU_VALIDATION_ERROR)
        return menu_name


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化
    """

    role_name = serializers.CharField(required=True)
    # menus = MenuSerializer(many=True, read_only=True)
    role_id = None

    class Meta:
        model = Role
        fields = "__all__"

    def validate_role_name(self, role_name):
        if "role_id" not in self.initial_data.keys():
            if Role.objects.filter(role_name=role_name).count() > 0:
                raise serializers.ValidationError(JSON_ROLE_VALIDATION_ERROR)
        else:
            self.role_id = self.initial_data["role_id"]
        if (
                Role.objects.filter(~Q(role_id=self.role_id), role_name=role_name).count()
                > 0
        ):
            raise serializers.ValidationError(JSON_ROLE_VALIDATION_ERROR)
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
    user_name = serializers.CharField(required=True)
    phone = serializers.CharField(max_length=255, required=True)
    email = serializers.CharField(max_length=255, required=True)
    dept = serializers.PrimaryKeyRelatedField(queryset=Dept.objects.all())
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all())
    roles = serializers.PrimaryKeyRelatedField(many=True, queryset=Role.objects.all())
    dept_name = serializers.StringRelatedField(source="dept")
    position_name = serializers.StringRelatedField(source="position")
    roles_name = serializers.StringRelatedField(source="roles", many=True)

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
            "roles_name",
            "position_name",
            "dept_name",
        ]

    def validate_user_name(self, user_name):
        if self.user_id is None:
            self.user_id = self.initial_data["id"]
        if Users.objects.filter(~Q(id=self.user_id), user_name=user_name).count() > 0:
            raise serializers.ValidationError(JSON_ACCOUNT_VALIDATION_ERROR)
        return user_name

    def validate_phone(self, phone):
        re_phone = PHONE_REGULAR
        if self.user_id is None:
            self.user_id = self.initial_data["id"]
        if not re.match(re_phone, phone):
            raise serializers.ValidationError(JSON_PHONE_FORMAT_VALIDATION_ERROR)
        if Users.objects.filter(~Q(id=self.user_id), phone=phone).count() > 0:
            raise serializers.ValidationError(JSON_PHONE_REGISTERED_VALIDATION_ERROR)
        return phone

    def validate_email(self, email):
        re_email = E_MAIL_REGULAR
        if self.user_id is None:
            self.user_id = self.initial_data["id"]
        if not re.match(re_email, email):
            raise serializers.ValidationError(JSON_EMAIL_FORMAT_VALIDATION_ERROR)
        if Users.objects.filter(~Q(id=self.user_id), email=email).count() > 0:
            raise serializers.ValidationError(JSON_EMAIL_REGISTERED_VALIDATION_ERROR)
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
            raise serializers.ValidationError(JSON_ACCOUNT_VALIDATION_ERROR)
        return user_name

    def validate_phone(self, phone):
        re_phone = PHONE_REGULAR
        if not re.match(re_phone, phone):
            raise serializers.ValidationError(JSON_PHONE_FORMAT_VALIDATION_ERROR)
        if Users.objects.filter(phone=phone):
            raise serializers.ValidationError(JSON_PHONE_REGISTERED_VALIDATION_ERROR)
        return phone

    def validate_email(self, email):
        re_email = E_MAIL_REGULAR
        if not re.match(re_email, email):
            raise serializers.ValidationError(JSON_EMAIL_FORMAT_VALIDATION_ERROR)
        if Users.objects.filter(email=email):
            raise serializers.ValidationError(JSON_EMAIL_REGISTERED_VALIDATION_ERROR)
        return email
