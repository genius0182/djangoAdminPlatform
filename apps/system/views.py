import logging
import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from .serializers import (DictSerializer, DictTypeSerializer, RoleSerializer, DeptSerializer, MenuSerializer,
                          UserListSerializer, UserModifySerializer, UserCreateSerializer)
from .models import (Dict, DictType, Dept, Menu, Role, User)
from rest_framework.views import APIView
from rest_framework.decorators import action

logger = logging.getLogger('log')


class DeptViewSet(ModelViewSet):
    """
    部门-增删改查
    """
    perms_map = {'get': '*', 'post': 'dept_create',
                 'put': 'dept_update', 'delete': 'dept_delete'}
    queryset = Dept.objects.all()
    serializer_class = DeptSerializer
    pagination_class = None
    search_fields = ['name', 'method']
    ordering_fields = ['pk']
    ordering = ['pk']


class RoleViewSet(ModelViewSet):
    """
    角色-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['pk']
    ordering = ['pk']


class MenuViewSet(ModelViewSet):
    """

    """
    perms_map = {'get': '*', 'post': 'menu_create',
                 'put': 'menu_update', 'delete': 'menu_delete'}
    queryset = Role.objects.all()
    serializer_class = MenuSerializer
    pagination_class = None
    search_fields = ['title']
    ordering_fields = ['pk']
    ordering = ['pk']


class TestView(APIView):
    perms_map = {'get': 'test_view'}  # 单个API控权
    pass


class DictViewSet(ModelViewSet):
    """
    数据字典-增删改查
    """
    perms_map = {'get': '*', 'post': 'dict_create',
                 'put': 'dict_update', 'delete': 'dict_delete'}
    # queryset = Dict.objects.get_queryset(all=True) # 获取全部的,包括软删除的
    queryset = Dict.objects.all()
    filterset_fields = ['type', 'is_used', 'type__code']
    serializer_class = DictSerializer
    search_fields = ['name']
    ordering_fields = ['sort']
    ordering = ['sort']

    def paginate_queryset(self, queryset):
        """
        如果查询参数里没有page但有type或type__code时则不分页,否则请求分页
        """
        if self.paginator is None:
            return None
        elif (not self.request.query_params.get('page', None)) and (
                (self.request.query_params.get('type__code', None)) or (self.request.query_params.get('type', None))):
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(methods=['get'], detail=False, permission_classes=[], authentication_classes=[], url_name='correct_dict')
    def correct(self, request):
        for i in Dict.objects.all():
            i.save()
        return Response(status=status.HTTP_200_OK)
