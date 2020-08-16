from rest_framework import serializers
import re
from .models import (Dict, DictType, Dept, Menu, Role, User)


class DictTypeSerializer(serializers.ModelSerializer):
    """
    数据字典类型序列化
    """

    class Meta:
        model = DictType
        fields = '__all__'


class DictSerializer(serializers.ModelSerializer):
    """
    数据字典序列化
    """

    # fullname = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Dict
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化
    """

    class Meta:
        model = Role
        fields = '__all__'


class DeptSerializer(serializers.ModelSerializer):
    """
    部门序列化
    """

    class Meta:
        model = Dept
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    """
    菜单序列化
    """

    class Meta:
        model = Menu
        fields = '__all__'


class UserListSerializer(serializers.ModelSerializer):
    """
    用户列表序列化
    """
    dept_name = serializers.StringRelatedField(source='dept')
    roles_name = serializers.StringRelatedField(source='roles', many=True)

    class Meta:
        model = User
        fields = ['id', 'phone', 'email', 'nick_name', 'gender', 'dept'
                                                                 'username', 'is_admin', 'avatar_name', 'avatar_path',
                  'pwd_reset_time', 'roles_name', 'dept_name']

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('superior', 'dept')
        queryset = queryset.prefetch_related('roles', )
        return queryset


class UserModifySerializer(serializers.ModelSerializer):
    """
    用户编辑序列化
    """
    phone = serializers.CharField(max_length=11, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'nick_name', 'gender', 'phone', 'email', 'dept',
                  'avatar_path', 'avatar_name', 'is_admin', 'roles']

    @staticmethod
    def validate_phone(phone):
        re_phone = r'^1[358]\d{9}$|^147\d{8}$|^176\d{8}$'
        if not re.match(re_phone, phone):
            raise serializers.ValidationError('手机号码不合法')
        return phone


class UserCreateSerializer(serializers.ModelSerializer):
    """
    创建用户序列化
    """
    username = serializers.CharField(required=True)
    phone = serializers.CharField(max_length=11, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'nick_name', 'gender', 'phone', 'email', 'dept',
                  'avatar_path', 'avatar_name', 'is_admin', 'roles']

    @staticmethod
    def validate_username(username):
        if User.objects.filter(username=username):
            raise serializers.ValidationError(username + ' 账号已存在')
        return username

    @staticmethod
    def validate_phone(phone):
        re_phone = r'^1[358]\d{9}$|^147\d{8}$|^176\d{8}$'
        if not re.match(re_phone, phone):
            raise serializers.ValidationError('手机号码不合法')
        if User.objects.filter(phone=phone):
            raise serializers.ValidationError('手机号已经被注册')
        return phone
