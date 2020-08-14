from django.db import models
from utils.baseModel import SoftModel, BaseModel
from django.db.models import JSONField
from django.contrib.auth.models import AbstractUser
import django.utils.timezone as timezone


class Dept(SoftModel):
    """
    部门
    """

    pid = models.BigIntegerField('上级部门ID', null=True, db_index=True)
    sub_count = models.IntegerField('子部门数目', default=0)
    name = models.CharField('名称', max_length=255)
    dept_sort = models.IntegerField('排序', default=999)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name


class Menu(SoftModel):
    """
    菜单
    """
    pid = models.BigIntegerField('上级菜单ID', null=True, db_index=True)
    sub_count = models.IntegerField('子菜单个数', default=0)
    type = models.IntegerField('菜单类型', null=True)
    title = models.CharField('菜单标题', max_length=255, null=True, unique=True)
    name = models.CharField('组件名称', max_length=255, null=True, unique=True)
    component = models.CharField('组件', max_length=255, null=True)
    menu_sort = models.IntegerField('排序', null=True)
    icon = models.CharField('图标', max_length=255, null=True)
    path = models.CharField('链接地址', max_length=255, null=True)
    i_frame = models.BooleanField('是否外链', default=False)
    cache = models.BooleanField('是否缓存', default=False)
    hidden = models.BooleanField('是否隐藏', default=False)
    permission = models.CharField('权限', max_length=255, null=True)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = verbose_name
        ordering = ['menu_sort']
        unique_together = ('title', 'name')

    def __str__(self):
        return self.name



class Role(SoftModel):
    """
    角色
    """
    data_type_choices = (
        ('全部', '全部'),
        ('自定义', '自定义'),
        ('同级及以下', '同级及以下'),
        ('本级及以下', '本级及以下'),
        ('本级', '本级'),
        ('仅本人', '仅本人')
    )
    name = models.CharField('角色', max_length=255, unique=True)
    level = models.IntegerField('角色级别', null=True)
    description = models.CharField('描述', max_length=255, blank=True, null=True)
    data_scope = models.CharField('数据权限', max_length=255,
                                  choices=data_type_choices, default='本级及以下')
    perms = models.ManyToManyField(Menu, blank=True, verbose_name='角色菜单关联')

    depts = models.ManyToManyField(
        Dept, blank=True, verbose_name='角色部门关联')

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name


class User(SoftModel):
    """
    用户
    """
    username = models.CharField('用户名', max_length=255, null=True, blank=True, unique=True)
    nick_name = models.CharField('昵称', max_length=255, null=True, blank=True)
    gender = models.CharField('性别', max_length=2, null=True)
    phone = models.CharField('手机号', max_length=255, null=True, blank=True, unique=True)
    email = models.CharField('邮箱', max_length=255, null=True, blank=True, unique=True)
    avatar_name = models.CharField('头像地址', max_length=1000, null=True, blank=True, db_index=True)
    avatar_path = models.CharField('头像真实路径', max_length=1000, null=True, blank=True)
    is_admin = models.BooleanField(default=False, verbose_name='是否为admin帐号', help_text='是否为admin帐号')
    pwd_reset_time = models.DateTimeField(default=timezone.now, verbose_name='修改密码时间', help_text='修改密码时间')
    dept = models.ForeignKey(
        Dept, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='部门')
    roles = models.ManyToManyField(Role, blank=True, verbose_name='用户角色关联')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
        unique_together = ('username', 'phone', 'email')
        ordering = ['id']

    def __str__(self):
        return self.username


class DictType(SoftModel):
    """
    数据字典类型
    """
    name = models.CharField('名称', max_length=30)
    code = models.CharField('代号', unique=True, max_length=30)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL, verbose_name='父')

    class Meta:
        verbose_name = '字典类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Dict(SoftModel):
    """
    数据字典
    """
    name = models.CharField('名称', max_length=1000)
    code = models.CharField('编号', max_length=30, null=True, blank=True)
    fullname = models.CharField('全名', max_length=1000, null=True, blank=True)
    description = models.TextField('描述', blank=True, null=True)
    other = JSONField('其它信息', blank=True, null=True)
    type = models.ForeignKey(DictType, on_delete=models.CASCADE, verbose_name='类型')
    sort = models.IntegerField('排序', default=1)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='父')

    class Meta:
        verbose_name = '字典'
        verbose_name_plural = verbose_name
        unique_together = ('name',  'type')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        冗余一个字段,方便调用
        """
        if self.code and self.code not in self.name:
            self.fullname = self.code + '-' + self.name
        super().save(*args, **kwargs)
