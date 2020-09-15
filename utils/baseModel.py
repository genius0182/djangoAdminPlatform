import django.utils.timezone as timezone
from django.db import models


class BaseModel(models.Model):
    """
    基本表
    """

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

    class Meta:
        abstract = True


class SoftModel(BaseModel):
    """
    软删除基本表
    """

    class Meta:
        abstract = True

    def delete(self, using=None, soft=True, *args, **kwargs):
        """
        这里需要真删除的话soft=False即可
        """
        if soft:
            self.is_deleted = True
            self.save(using=using)
        else:

            return super(SoftModel, self).delete(using=using, *args, **kwargs)
