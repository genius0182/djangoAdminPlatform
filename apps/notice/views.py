# Create your views here.

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.notice.models import Notice
from apps.notice.serializers import NotificationSerializer
from utils.pagination import MyPagination


class CommentNoticeListView(ModelViewSet):
    """通知列表"""

    serializer_class = NotificationSerializer
    _paginator = MyPagination()

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        un_read = self.request.query_params.get("un_read", None)
        if user:
            if un_read:
                return Notice.objects.filter(deleted=False, recipient=user, unread=un_read).order_by("-id")
            else:
                return Notice.objects.filter(deleted=False, recipient=user).order_by("-id")

    def paginate_queryset(self, queryset):
        """
        如果查询参数里没有page但有type或type__code时则不分页,否则请求分页
        """
        if self.paginator is None:
            return None
        elif not self.request.query_params.get("page", None):
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(
        methods=["get"],
        detail=False,
        # permission_classes=[IsAuthenticated],  # perms_map={'put':'change_password'}
        # perms_map={"get": "*"},
        url_path="count",
    )
    def count(self, request):
        user = self.request.user
        if user:
            un_read_count = Notice.objects.filter(
                unread=True, deleted=False, recipient=user
            ).count()
            json_result = {
                "user_id": user.id,
                "user_name": user.user_name,
                "un_read_count": un_read_count,
            }
        return Response(json_result)


class CommentNoticeUpdateView(APIView):
    """更新通知状态"""

    def put(self, request, notice_id, *args, **kwargs):
        # 更新单条通知
        if notice_id:
            request.user.notifications.get(id=notice_id).mark_as_read()
        # 更新全部通知
        else:
            return Response(data="")

        return Response(status=status.HTTP_200_OK)
