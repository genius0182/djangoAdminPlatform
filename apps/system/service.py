# author:hao.lu
# create_date: 9/17/2020 3:25 PM
# file : service.py
# IDE: PyCharm

import logging

# ! -*- coding: utf-8 -*-
from apps.system.models import Menu, Dept
from apps.system.serializers import MenuSerializer, DeptSerializer

logger = logging.getLogger("log")


class MenuBuildService:
    """
    构建menu树型结构类
    """

    def get_role_menus(self, user):
        """
        根据权限返回菜单项，不包括按钮级别
        Args:
            user: 用户对象

        Returns: 树型结构菜单

        """
        roles = user.roles.all().distinct()
        all_sql_menus = None
        result = []
        if not user.is_admin:
            for role in roles:
                temp_menus = (
                    role.menus.filter(is_deleted=False, menu_type__in=[0, 1, 2])
                        .distinct()
                        .order_by("menu_sort")
                )
                # 合并queryset
                if all_sql_menus is None:
                    all_sql_menus = temp_menus
                else:
                    all_sql_menus = all_sql_menus | temp_menus
        else:
            all_sql_menus = Menu.objects.filter(
                is_deleted=False, menu_type__in=[0, 1, 2]
            ).order_by("menu_sort")

        if all_sql_menus and len(all_sql_menus) > 0:
            all_menus = self.handler_menus_data(all_sql_menus)
            result = self.get_menus_child_all(all_menus)
        return result

    def get_all_menus(self, menu_name):
        """
        构建全部菜单的树型结构
        Returns: 树型结构菜单

        """
        if menu_name:
            all_sql_menus = Menu.objects.filter(
                is_deleted=False, menu_name__contains=menu_name
            ).order_by("menu_sort")
            all_menus = self.handler_menus_data(all_sql_menus)
            result = self.get_query_menus_child_all(all_menus)
        else:
            all_sql_menus = Menu.objects.filter(is_deleted=False).order_by("menu_sort")
            all_menus = self.handler_menus_data(all_sql_menus)
            result = self.get_menus_child_all(all_menus)

        return result

    @staticmethod
    def handler_menus_data(menus):
        result = [MenuSerializer(menu).data for menu in menus]
        return result

    def get_query_menus_child_all(self, menus):
        """
        根据查询后的结果,递归构建菜单
        Args:
            menus: 根据查询后的菜单结果

        Returns: 树型结构的菜单

        """
        root_list = []
        for menu in menus:
            result = menu
            root_list.append(result)
        for root in root_list:
            root_child = self.get_child(menus, root["menu_id"])
            if root_child:
                root["children"] = root_child
        return root_list

    def get_menus_child_all(self, menus):
        """
        递归构建菜单，从root开始逐层向下构建
        Args:
            menus: 菜单集合

        Returns: 树型结构菜单

        """

        root_list = []
        for menu in menus:
            if menu["pid"] is None:
                result = menu
                root_list.append(result)
        for root in root_list:
            root_child = self.get_child(menus, root["menu_id"])
            if root_child:
                root["children"] = root_child

        return root_list

    def get_child(self, menus, menu_id):
        """
        获取菜单子节点
        Args:
            menus: 菜单集合
            menu_id: 菜单ID

        Returns: 子节点树型结构

        """
        child_list = []
        for menu in menus:
            if menu["pid"] == menu_id:
                child_result = menu
                child_list.append(child_result)
            for child_menu in child_list:
                child = self.get_child(menus, child_menu["menu_id"])
                if child:
                    child_menu["children"] = child
        return child_list


class DeptBuildService:
    def get_dept_all(self, dept_name):
        if dept_name:
            dept_sql_list = Dept.objects.filter(
                is_deleted=False, dept_name__contains=dept_name
            ).order_by("dept_sort")
            dept_list = self.handler_dept_list_data(dept_sql_list)
            result = self.get_query_dept_child_all(dept_list)
        else:
            dept_sql_list = Dept.objects.filter(is_deleted=False).order_by("dept_sort")
            dept_list = self.handler_dept_list_data(dept_sql_list)
            result = self.get_dept_child_all(dept_list)
        return result

    @staticmethod
    def handler_dept_list_data(dept_list):
        result = [DeptSerializer(dept).data for dept in dept_list]
        return result

    def get_query_dept_child_all(self, dept_list):
        """
        根据查询后的结果递归构建部门
        Args:
            dept_list: 部门集合

        Returns: 树型结构部门

        """
        root_list = []
        for dept in dept_list:
            result = dept
            root_list.append(result)
        for root in root_list:
            root_child = self.get_query_child(root["dept_id"])
            if root_child:
                root["children"] = root_child
        return root_list

    def get_dept_child_all(self, dept_list):
        """
        递归构建部门，从root开始逐层向下构建
        Args:
            dept_list: 部门集合

        Returns: 树型结构部门

        """
        root_list = []
        for dept in dept_list:
            if dept["pid"] is None:
                result = dept
                root_list.append(result)
        for root in root_list:
            root_child = self.get_child(dept_list, root["dept_id"])
            if root_child:
                root["children"] = root_child
        return root_list

    def get_child(self, dept_list, dept_id):
        """
        获取部门子节点
        Args:
            dept_list: 部门集合
            dept_id: 部门ID

        Returns: 子节点树型结构

        """
        child_list = []
        for dept in dept_list:
            if dept["pid"] == dept_id:
                child_result = dept
                child_list.append(child_result)
            for child_dept in child_list:
                child = self.get_child(dept_list, child_dept["dept_id"])
                if child:
                    child_dept["children"] = child
        return child_list

    def get_query_child(self, dept_id):
        child_list = []
        children = Dept.objects.filter(is_deleted=False, pid=dept_id).order_by(
            "dept_sort"
        )
        if children:
            child_list = [DeptSerializer(child).data for child in children]
            for child_dept in child_list:
                child = self.get_query_child(child_dept["dept_id"])
                if child:
                    child_dept["children"] = child
        return child_list
