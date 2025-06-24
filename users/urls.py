from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views

urlpatterns = [
    path("create", views.CustomerCreateAPIView.as_view()),
    path("update", views.CustomerUpdateAPIView.as_view()),
    path("get-verification-code", views.get_verification_code),
    path("reset-password", views.reset_password),
    path('token/obtain', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

]