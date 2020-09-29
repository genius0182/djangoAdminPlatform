# author:hao.lu
# create_date: 9/25/2020 10:21 AM
# file : urls.py
# IDE: PyCharm

# ! -*- coding: utf-8 -*-

from django.urls import path, include
from rest_framework import routers

from apps.notice.views import (
    CommentNoticeUpdateView,
    CommentNoticeListView,
    CommentNoticeSendView,
)

router = routers.DefaultRouter()
router.register("list", CommentNoticeListView, basename="list")
urlpatterns = [
    path("", include(router.urls)),
    # 更新通知状态
    path("markRead/<notice_id>/", CommentNoticeUpdateView.as_view()),
    path("noticeSend/", CommentNoticeSendView.as_view()),
]
