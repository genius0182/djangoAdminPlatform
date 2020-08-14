from django.urls import path, include
from .views import DictViewSet, TestView
from rest_framework import routers

router = routers.DefaultRouter()
router.register('dict', DictViewSet, basename="dict")

urlpatterns = [
    path('', include(router.urls)),
    path('test/', TestView.as_view())
]
