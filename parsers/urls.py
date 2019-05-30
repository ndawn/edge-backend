from django.urls import path
from parsers.views import ParseView


urlpatterns = [
    path('run/', ParseView.as_view()),
]
