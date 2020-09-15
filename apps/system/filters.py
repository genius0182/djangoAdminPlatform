from django_filters import rest_framework as filters

from .models import Users


class UserFilter(filters.FilterSet):
    class Meta:
        model = Users
        fields = {
            "name": ["exact", "contains"],
            # 'enabled': ['exact'],
        }
