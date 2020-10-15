import datetime
from django.test import TestCase
from rest_framework.test import APIClient
from apps.system.models import Users, Dept, Position, Role, Menu
# get_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SystemModuleTest(TestCase):
    @staticmethod
    def init_dept():
        Dept.objects.create(
            dept_id=1, dept_name="总公司", dept_sort=1, is_activate=True, is_deleted=False
        )
        Dept.objects.create(
            dept_id=2,
            dept_name="华南分部",
            pid=1,
            dept_sort=2,
            is_activate=True,
            is_deleted=False,
        )
        Dept.objects.create(
            dept_id=3,
            dept_name="华北分部",
            pid=1,
            dept_sort=3,
            is_activate=True,
            is_deleted=False,
        )
        Dept.objects.create(
            dept_id=4,
            dept_name="东北分部",
            pid=1,
            dept_sort=4,
            is_activate=True,
            is_deleted=False,
        )
        Dept.objects.create(
            dept_id=6,
            dept_name="开发部",
            pid=4,
            dept_sort=5,
            is_activate=True,
            is_deleted=False,
        )

    @staticmethod
    def init_position():
        Position.objects.create(
            position_id=1,
            position_name="SE",
            description="开发工程师",
            is_activate=True,
            is_deleted=False,
        )

    @staticmethod
    def init_Role():
        Role.objects.create(
            role_id=1,
            role_name="管理员",
            role_level=1,
            description="管理员",
            data_scope="自定义",
        )

    @staticmethod
    def init_User():
        Users.objects.create(
            id=1,
            user_name="admin",
            password="pbkdf2_sha256$216000$CRt1nNclyP9o$XCKOQGCNv2xdRHnPxAkDrOGZiNOMp9GkhQcq+MbDfUY=",
            phone="18888888888",
            email="201507802@qq.com",
            is_activate=True,
            is_deleted=False,
            dept_id=6,
            position_id=1,
        )

        Users.objects.create(
            id=2,
            user_name="devloper",
            password="pbkdf2_sha256$180000$TaRzUahqcmKe$danAeZ4p8Q5bs7rYiDNv2TWD7Io8I/1Wj/Y8OTd7NCw=",
            phone="18888888880",
            email="130022087221@qq.com",
            is_activate=True,
            is_deleted=False,
            dept_id=6,
            position_id=1,
            is_admin=True,
        )

    @staticmethod
    def init_menu():
        Menu.objects.create(
            menu_id=1,
            menu_name="root",
            router="root",
            sidebar=True,
            menu_type=0,
            is_activate=True,
            is_deleted=False,
        )
        Menu.objects.create(
            menu_id=2,
            pid=1,
            menu_type=1,
            menu_name="系统管理",
            menu_sort=3,
            router="system",
            sidebar=True,
            is_activate=True,
            is_deleted=False,
        )
        Menu.objects.create(
            menu_id=3,
            pid=2,
            menu_type=2,
            menu_name="角色管理",
            menu_sort=3,
            router="role",
            permission="role_list",
            sidebar=True,
            is_activate=True,
            is_deleted=False,
        )
        Menu.objects.create(
            menu_id=4,
            pid=2,
            menu_type=2,
            menu_name="菜单管理",
            menu_sort=5,
            router="menu",
            permission="menu_list",
            sidebar=True,
            is_activate=True,
            is_deleted=False,
        )

        Menu.objects.create(
            menu_id=5,
            pid=2,
            menu_type=2,
            menu_name="用户管理",
            menu_sort=10,
            router="user",
            permission="user_list",
            sidebar=True,
            is_activate=True,
            is_deleted=False,
        )
        Menu.objects.create(
            menu_id=6,
            pid=2,
            menu_type=2,
            menu_name="部门管理",
            menu_sort=6,
            router="dept",
            permission="dept_list",
            sidebar=True,
            is_activate=True,
            is_deleted=False,
        )
        Menu.objects.create(
            menu_id=7,
            pid=2,
            menu_type=2,
            menu_name="岗位管理",
            menu_sort=7,
            router="position",
            permission="position_list",
            sidebar=True,
            is_activate=True,
            is_deleted=False,
        )
        Menu.objects.create(
            menu_id=8,
            pid=5,
            menu_type=3,
            menu_name="用户新增",
            menu_sort=5,
            permission="user_add",
            sidebar=True,
            is_activate=True,
            is_deleted=False,
        )
        Menu.objects.create(
            menu_id=9,
            pid=5,
            menu_type=3,
            menu_name="用户编辑",
            menu_sort=5,
            permission="user_add",
            sidebar=True,
            is_activate=True,
            is_deleted=False,
        )
        Menu.objects.create(
            menu_id=10,
            pid=5,
            menu_type=3,
            menu_name="用户删除",
            menu_sort=5,
            permission="user_add",
            sidebar=True,
            is_activate=True,
            is_deleted=False,
        )

    def __init__(self, wrapped):
        super(SystemModuleTest, self).__init__(wrapped)
        self.token = None
        self.api_client = APIClient()

    def setUp(self) -> None:
        self.init_dept()
        self.init_position()
        self.init_Role()
        self.init_User()
        self.init_menu()

    def test_users_model(self):
        query_set = Users.objects.filter(user_name="admin").first()
        self.assertEqual(query_set.id, 1)

    def test_login_user_name_password(self):
        test_data = {
            "user_name": "devloper",
            "password": "KlJbQmYqrl/cpBIeeElPuBH/ul3Y0/o1qf/IobpaGgh2L3sCrm6KAtPHOuOtM2ooNcgHsnxVDFq3n7pbrvAexZgJk"
            "3SYruT108r5x0Z3pF2XDdSszRzOWweFoUnTGMXiMkfW/wJ9XE+C1q2+SUhOvLXmjosmDz5D2gYKdUm/ZAs=",
        }
        response = self.client.post(
            "/system/login/", data=test_data, content_type="application/json"
        )
        self.token = response.data["token"]
        self.assertEqual(response.status_code, 200)

    def test_query_user(self):
        if not self.token:
            self.test_login_user_name_password()
        self.api_client.credentials(HTTP_AUTHORIZATION="{0}".format(self.token))
        response = self.api_client.get("/system/user/", content_type="application/json")
        self.assertEqual(response.status_code, 200)
