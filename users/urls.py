from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    path("create", views.CustomerCreateAPIView.as_view()),
    path("update/<int:customer_pk>", views.CustomerUpdateAPIView.as_view()),
    path('token/obtain', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]