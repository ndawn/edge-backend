from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import RegisterView, TestView


urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('test/', TestView.as_view()),
    path('register/', RegisterView.as_view()),
]
