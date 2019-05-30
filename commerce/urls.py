from django.urls import path
from commerce.views import CategoryTreeView


urlpatterns = [
    path('category/tree/', CategoryTreeView.as_view()),
]
