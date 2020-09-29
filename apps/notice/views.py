# Create your views here.

from notifications.signals import notify
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.notice.models import Notice
from apps.notice.serializers import NotificationSerializer
from apps.system.models import Users
from utils.constant import (
    JSON_NOTICE_SEND_USER_NOT_EXIST_VALIDATION_ERROR,
    JSON_NOTICE_TITLE_IS_NULL_VALIDATION_ERROR,
    JSON_NOTICE_CONTENT_IS_NULL_VALIDATION_ERROR,
    JSON_NOTICE_ID_NULL_VALIDATION_ERROR,
)
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
                return Notice.objects.filter(
                    deleted=False, recipient=user, unread=un_read
                ).order_by("-id")
            else:
                return Notice.objects.filter(deleted=False, recipient=user).order_by(
                    "-id"
                )

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
        json_result = {}
        if user:
            un_read_count = Notice.objects.filter(
                unread=True, deleted=False, recipient=user
            ).count()
            json_result["user_id"] = user.id
            json_result["user_name"] = user.user_name
            json_result["un_read_count"] = un_read_count
        return Response(json_result)


class CommentNoticeUpdateView(APIView):
    """更新通知状态"""

    def put(self, request, notice_id, *args, **kwargs):
        # 更新单条通知
        if notice_id:
            request.user.notifications.get(id=notice_id).mark_as_read()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                JSON_NOTICE_ID_NULL_VALIDATION_ERROR, status.HTTP_400_BAD_REQUEST
            )


class CommentNoticeSendView(APIView):
    def post(self, request, *args, **kwargs):
        error_list = []
        request_dict = request.data
        user_id = request_dict["recipient_id"]
        verb = request_dict["title"]
        description = request_dict["content"]
        if user_id is None:
            error_list.append(JSON_NOTICE_SEND_USER_NOT_EXIST_VALIDATION_ERROR)
        if verb is None:
            error_list.append(JSON_NOTICE_TITLE_IS_NULL_VALIDATION_ERROR)
        if description is None:
            error_list.append(JSON_NOTICE_CONTENT_IS_NULL_VALIDATION_ERROR)

        receive_user = Users.objects.filter(
            id=user_id, is_deleted=False, is_activate=True
        ).first()
        if receive_user is None:
            error_list.append(JSON_NOTICE_SEND_USER_NOT_EXIST_VALIDATION_ERROR)

        if receive_user and verb and description:
            notify.send(
                request.user, recipient=receive_user, verb=verb, description=description
            )
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                error_list,
                status=status.HTTP_400_BAD_REQUEST,
            )
