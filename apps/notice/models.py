from django.db import models
from notifications.base.models import AbstractNotification


class Notice(AbstractNotification):
    category = models.IntegerField("消息类型", null=True, blank=True)

    class Meta:
        managed = True
        verbose_name = "消息类型"
        verbose_name_plural = verbose_name
        index_together = ("recipient", "unread")
