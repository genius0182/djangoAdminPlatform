from rest_framework import serializers

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

