from django.urls import path
from previews.views import PublisherDataListView, CategoryDataListView


urlpatterns = [
    path('publisher/<site_id>/', PublisherDataListView.as_view()),
    path('category/<site_id>/', CategoryDataListView.as_view()),
]
