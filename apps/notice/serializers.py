# author:hao.lu
# create_date: 9/25/2020 10:29 AM
# file : serializers.py
# IDE: PyCharm

# ! -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.notice.models import Notice


class NotificationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    recipient = serializers.PrimaryKeyRelatedField(read_only=True)
    recipient_name = serializers.StringRelatedField(source="recipient")
    level = serializers.CharField(max_length=20)
    verb = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255)
    timestamp = serializers.DateTimeField(read_only=True)
    public = serializers.BooleanField(read_only=True)
    deleted = serializers.BooleanField(read_only=True)
    unread = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notice
        fields = [
            "id",
            "recipient",
            "recipient_name",
            "verb",
            "timestamp",
            "public",
            "level",
            "unread",
            "deleted",
            "description",
        ]
