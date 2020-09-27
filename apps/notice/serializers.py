# author:hao.lu
# create_date: 9/25/2020 10:29 AM
# file : serializers.py
# IDE: PyCharm

from notifications.models import Notification
# ! -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.system.models import Users


#
# class GenericNotificationRelatedField(serializers.RelatedField):
#     User = get_user_model()
#
#     def to_representation(self, value):
#         if isinstance(value, Invite):
#             serializer = InviteSerializer(value)
#         if isinstance(value, Users):
#             serializer = UserListSerializer(value)
#         return serializer.data
#
class NotificationSerializer(serializers.Serializer):
    recipient = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    level = serializers.CharField(max_length=20)
    verb = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255)
    timestamp = serializers.DateTimeField(read_only=True)
    public = serializers.BooleanField(read_only=True)
    # serializers.StringRelatedField(source="dept")
    unread = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        # fields = "__all__"
        fields = [
            "recipient",
            "verb",
            "timestamp",
            "public",
            "level",
            "unread",
            "description",
        ]
    # target = GenericNotificationRelatedField(read_only=True)
