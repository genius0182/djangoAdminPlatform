from django.core.cache import cache
from jwt import decode as jwt_decode
from rest_framework.permissions import BasePermission

from server.settings import SECRET_KEY
from utils.querySetUtil import get_child_queryset2
from .models import Menu


def get_permission_list(user):
    """
    获取权限列表,可用redis存取
    """
    if user.is_admin:
        perms_list = ["admin"]
    else:
        perms = Menu.objects.none()
        roles = user.roles.all()
        if roles:
            for i in roles:
                perms = perms | i.menus.all()
        perms_list = perms.values_list("permission", flat=True)
        # filter null value
        perms_list = list(filter(lambda a: (a), perms_list))
        perms_list = list(set(perms_list))
    cache.set(user.user_name + "__perms", perms_list)
    # cache.persist(user.user_name)
    return perms_list


class RbacPermission(BasePermission):
    """
    基于角色的权限校验类
    """

    def has_permission(self, request, view):
        """
        权限校验逻辑
        :param request:
        :param view:
        :return:
        """
        if not request.user:
            return False
        else:
            perms = cache.get(request.user.user_name + "__perms")
        token = cache.get(request.user.user_name + "__token")
        if token:
            try:
                decoded_data = jwt_decode(token, SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_data.get("user_id")
                if request.user.id != user_id:
                    return False
            except Exception:
                return False
        else:
            return False
        if not perms:
            perms = get_permission_list(request.user)
        if perms:
            if "admin" in perms:
                return True
            elif not hasattr(view, "perms_map"):
                return True
            else:
                perms_map = view.perms_map
                _method = request._request.method.lower()
                action = view.action
                if perms_map:
                    for key in perms_map:
                        if key == _method or key == "*":
                            if action and (action in perms or perms_map[key] == "*"):
                                return True
                            elif action in ["create", "update", "delete", "list"] and (
                                    perms_map[key] in perms or perms_map[key] == "*"
                            ):
                                return True
                return False
        else:
            return False

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if not request.user:
            return False
        # if hasattr(obj, "dept"):
        #     has_obj_perm(request.user, obj)
        return True


def has_obj_perm(user, obj):
    """
    数据权限控权
    返回对象的是否可以操作
    需要控数据权限的表需有belong_dept, create_by, update_by字段(部门, 创建人, 编辑人)
    传入user, obj实例
    """
    roles = user.roles
    data_range = roles.values_list("datas", flat=True)
    if "全部" in data_range:
        return True
    elif "自定义" in data_range:
        if roles.depts.exists():
            if obj.belong_dept not in roles.depts:
                return False
    elif "同级及以下" in data_range:
        if user.dept.parent:
            belong_depts = get_child_queryset2(user.dept.parent)
            if obj.belong_dept not in belong_depts:
                return False
    elif "本级及以下" in data_range:
        belong_depts = get_child_queryset2(user.dept)
        if obj.belong_dept not in belong_depts:
            return False
    elif "本级" in data_range:
        if obj.belong_dept is not user.dept:
            return False
    return True
