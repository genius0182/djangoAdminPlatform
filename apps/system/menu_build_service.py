"""
    Copyright [2020-2021] [hao.lu and shuai.liu]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from apps.system.models import Menu
from apps.system.serializers import MenuSerializer


class MenuBuildSevice:
    def build(self, user):
        all_menu = None
        roles = user.roles.filter(is_activate=True)
        for role in roles:
            temp_menu = role.menus.filter(is_activate=True, sidebar=True, menu_type__in=[0, 1, 2]).order_by(
                "menu_sort")
            if all_menu is None:
                all_menu = temp_menu
            else:
                all_menu = all_menu | temp_menu

        result = self.get_parent_menu_all(all_menu)
        return result

    def get_parent_menu_all(self, menus):
        # chilren_list = []
        parent_dict = {}
        parent_list = []
        for menu in menus:
            parent_menus = Menu.objects.filter(is_activate=True, sidebar=True, menu_id=menu.pid).first()
            if len(parent_dict) == 0 or parent_menus.menu_id not in parent_dict.keys():
                parent_dict["parent" + str(parent_menus.menu_id)] = MenuSerializer(parent_menus).data
                parent_dict[parent_menus.menu_id] = [MenuSerializer(menu).data]
                parent_list.append(parent_dict)
            else:
                child_list = parent_dict[parent_menus.menu_id]
                child_list.append(MenuSerializer(menu).data)
            if not self.is_exist(parent_list, parent_dict):
                parent_dict["parent"] = MenuSerializer(parent_menus).data
                parent_list.append(parent_dict)
        result = self.get_parent(parent_list)
        return result

    def get_parent(self, parent_list):
        result_dict = {}
        root_flag = False
        for parent_dict in parent_list:
            parent_menus = Menu.objects.filter(is_activate=True, sidebar=True,
                                               menu_id=parent_dict["parent"]["pid"]).first()
            if parent_menus.pid is None:
                root_flag = True
            if len(result_dict) == 0:
                result_dict[parent_menus.menu_id] = [MenuSerializer(parent_menus).data]
                result_dict["parent"] = MenuSerializer(parent_menus).data
                parent_list.append(result_dict)
            else:
                child_list = result_dict[parent_menus.menu_id]
                child_list.append(MenuSerializer(parent_menus).data)
            if not self.is_exist(parent_list, result_dict):
                result_dict["parent"] = MenuSerializer(parent_menus).data
                parent_list.append(result_dict)
        if root_flag:
            return parent_list
        else:
            return self.get_parent(parent_list)

    def is_exist(self, result_list, result_dict):
        return [True if menu["parent"]["menu_id"] == result_dict["parent"]["menu_id"] else False for menu in
                result_list]
