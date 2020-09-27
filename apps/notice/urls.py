# author:hao.lu
# create_date: 9/25/2020 10:21 AM
# file : urls.py
# IDE: PyCharm

# ! -*- coding: utf-8 -*-

from django.urls import path, include
from rest_framework import routers

from apps.notice.views import CommentNoticeUpdateView, CommentNoticeListView

router = routers.DefaultRouter()
router.register("list", CommentNoticeListView, basename="list")
urlpatterns = [
    path("", include(router.urls)),
    # 通知列表
    # path("list/", CommentNoticeListView.as_view()),
    # 更新通知状态
    path("update/", CommentNoticeUpdateView.as_view()),
]
