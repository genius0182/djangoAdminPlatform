import django.utils.timezone as timezone
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models

from utils.baseModel import SoftModel


class Position(SoftModel):
    """
    职位/岗位
    """

    position_id = models.AutoField("岗位表主键ID", primary_key=True)
    position_name = models.CharField("名称", max_length=32, unique=True)
    description = models.CharField("描述", max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = "职位/岗位"
        verbose_name_plural = verbose_name
        ordering = ["position_id"]

    def __str__(self):
        return self.position_name


class Dept(SoftModel):
    """
    部门
    """

    dept_id = models.AutoField("部门表主键ID", primary_key=True)
    pid = models.BigIntegerField("上级部门ID", null=True, db_index=True)
    sub_count = models.IntegerField("子部门数目", default=0)
    dept_name = models.CharField("名称", max_length=255)
    dept_sort = models.IntegerField("排序", default=999)

    class Meta:
        managed = True
        verbose_name = "部门"
        verbose_name_plural = verbose_name
        ordering = ["dept_id"]

    def __str__(self):
        return self.dept_name


class Menu(SoftModel):
    """
    菜单
    """

    menu_id = models.AutoField("菜单表主键ID", primary_key=True)
    pid = models.BigIntegerField("上级菜单ID", null=True, db_index=True)
    menu_type = models.IntegerField("菜单类型, 0:root,1:目录，2:菜单，3:是按钮", null=True)
    menu_name = models.CharField("组件名称", max_length=255, null=True, unique=True)
    menu_sort = models.IntegerField("排序", null=True)
    sidebar = models.BooleanField("是否显示在侧边栏", default=True)
    router = models.CharField("router名称", max_length=255, null=True, blank=True)
    permission = models.CharField("权限", max_length=255, null=True)

    class Meta:
        managed = True
        verbose_name = "部门"
        verbose_name_plural = verbose_name
        ordering = ["menu_sort"]

    def __str__(self):
        return self.menu_name


class Role(SoftModel):
    """
    角色
    """

    data_type_choices = (
        ("全部", "全部"),
        ("自定义", "自定义"),
        ("同级及以下", "同级及以下"),
        ("本级及以下", "本级及以下"),
        ("本级", "本级"),
        ("仅本人", "仅本人"),
    )
    role_id = models.AutoField("角色表主键ID", primary_key=True)
    role_name = models.CharField("角色", max_length=255, unique=True)
    role_level = models.IntegerField("角色级别", null=True)
    description = models.CharField("描述", max_length=255, blank=True, null=True)
    data_scope = models.CharField(
        "数据权限", max_length=255, choices=data_type_choices, default="本级及以下"
    )
    menus = models.ManyToManyField(Menu, blank=True, verbose_name="角色菜单关联")

    depts = models.ManyToManyField(Dept, blank=True, verbose_name="角色部门关联")

    class Meta:
        managed = True
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        ordering = ["role_id"]

    def __str__(self):
        return self.role_name


class Users(AbstractBaseUser):
    """
    用户
    """

    id = models.AutoField("用户表主键ID", primary_key=True)
    user_name = models.CharField(
        "用户名", max_length=255, null=True, blank=True, unique=True
    )
    USERNAME_FIELD = "user_name"
    nick_name = models.CharField("昵称", max_length=255, null=True, blank=True)
    gender = models.CharField("性别 1:男,2:女", max_length=2, null=True)
    phone = models.CharField("手机号", max_length=255, null=True, blank=True, unique=True)
    email = models.CharField("邮箱", max_length=255, null=True, blank=True, unique=True)
    avatar_name = models.CharField(
        "头像地址", max_length=1000, null=True, blank=True, db_index=True
    )
    avatar_path = models.CharField("头像真实路径", max_length=1000, null=True, blank=True)
    is_admin = models.BooleanField(
        default=False, verbose_name="是否为admin帐号", help_text="是否为admin帐号"
    )
    pwd_reset_time = models.DateTimeField(
        default=timezone.now,
        verbose_name="修改密码时间",
        help_text="修改密码时间",
        null=True,
        blank=True,
    )

    create_by = models.CharField(
        null=True, blank=True, verbose_name="创建者", help_text="创建者", max_length=50
    )
    update_by = models.CharField(
        null=True, blank=True, verbose_name="创建者", help_text="创建者", max_length=50
    )
    create_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="创建时间",
        help_text="创建时间",
        null=True,
        blank=True,
    )
    update_at = models.DateTimeField(
        auto_now=True, verbose_name="修改时间", help_text="修改时间", null=True, blank=True
    )
    is_deleted = models.BooleanField(
        default=False, verbose_name="删除标记", help_text="删除标记"
    )
    is_activate = models.BooleanField(
        default=False, verbose_name="状态：1启用、0禁用", help_text="状态：1启用、0禁用"
    )

    dept = models.ForeignKey(
        Dept, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="部门"
    )
    position = models.ForeignKey(
        Position, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="职位/岗位"
    )
    roles = models.ManyToManyField(Role, blank=True, verbose_name="用户角色关联")

    objects = BaseUserManager()

    class Meta:
        managed = True
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name
        unique_together = ("user_name", "phone", "email")
        ordering = ["id"]

    def __str__(self):
        return self.user_name


class DictType(SoftModel):
    """
    数据字典类型
    """

    dict_type_id = models.AutoField("数据字典类型表主键ID", primary_key=True)
    dict_type_name = models.CharField("名称", max_length=30)
    code = models.CharField("代号", unique=True, max_length=30)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父"
    )

    class Meta:
        managed = True
        verbose_name = "字典类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.dict_type_name


class Dict(SoftModel):
    """
    数据字典
    """

    dict_id = models.AutoField("数据字典表主键ID", primary_key=True)
    dict_name = models.CharField("名称", max_length=1000)
    code = models.CharField("编号", max_length=30, null=True, blank=True)
    fullname = models.CharField("全名", max_length=1000, null=True, blank=True)
    description = models.TextField("描述", blank=True, null=True)
    other = models.TextField("其它信息", blank=True, null=True)
    dict_type = models.ForeignKey(DictType, on_delete=models.CASCADE, verbose_name="类型")
    sort = models.IntegerField("排序", default=1)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父"
    )

    class Meta:
        managed = True
        verbose_name = "字典"
        verbose_name_plural = verbose_name
        unique_together = ("dict_name", "dict_type")

    def __str__(self):
        return self.dict_name

    def save(self, *args, **kwargs):
        """
        冗余一个字段,方便调用
        """
        if self.code and self.code not in self.dict_name:
            self.fullname = self.code + "-" + self.dict_name
        super().save(*args, **kwargs)
