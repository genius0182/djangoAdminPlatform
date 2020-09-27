# Create your views here.

from notifications.models import Notification
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.notice.serializers import NotificationSerializer


class CommentNoticeListView(ModelViewSet):
    """通知列表"""
    # 上下文的名称
    # context_object_name = 'notices'

    # 未读通知的查询集
    # def get(self, request, *args, **kwargs):
    #     # notification = request.user.notifications
    #     notification = Notification.objects.filter(unread=True,deleted=False,recipient=request.user)
    #     serializer = NotificationSerializer(notification)
    #     return Response(serializer.data)
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer()

    def get_queryset(self):
        return self.request.user.notifications.unread()


class CommentNoticeUpdateView(APIView):
    """更新通知状态"""

    # 处理 get 请求
    def get(self, request, *args, **kwargs):
        # 获取未读消息
        notice_id = request.query_params.get("notice_id", None)
        # user_id = request.query_params.get("user_id", None)
        # 更新单条通知
        if notice_id:
            # user = Users.objects.get(id=user_id)
            request.user.notifications.get(id=notice_id).mark_as_read()
        # 更新全部通知
        else:
            request.user.notifications.mark_all_as_read()

        return Response(status=status.HTTP_200_OK)
