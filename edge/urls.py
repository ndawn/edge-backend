from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from accounts.views import UserViewSet
import accounts.auth_urls
import commerce.views
import commerce.urls
import parsers.urls
import parsers.views
import previews.views


router = routers.DefaultRouter()
router.register('user', UserViewSet)
router.register('pricemap', commerce.views.PriceMapViewSet)
router.register('category', commerce.views.CategoryViewSet)
router.register('publisher', commerce.views.PublisherViewSet)
router.register('item', commerce.views.ItemViewSet)
router.register('order', commerce.views.OrderViewSet)
router.register('parse_session', parsers.views.ParseSessionViewSet)
router.register('parse_publisher', previews.views.PublisherDataViewSet)
router.register('parse_category', previews.views.CategoryDataViewSet)
router.register('preview', previews.views.PreviewViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include(accounts.auth_urls)),
    path('api/commerce/', include(commerce.urls)),
    path('api/parsers/', include(parsers.urls)),
    path('api/', include(router.urls)),
]
