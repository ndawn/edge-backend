from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from accounts.views import UserViewSet
import accounts.urls
import commerce.urls
import commerce.views
import parsers.urls
import parsers.views
import previews.urls
import previews.views


router = routers.DefaultRouter()
router.register('user', UserViewSet)
router.register('pricemap', commerce.views.PriceMapViewSet)
router.register('category', commerce.views.CategoryViewSet)
router.register('publisher', commerce.views.PublisherViewSet)
router.register('item', commerce.views.ItemViewSet)
router.register('order', commerce.views.OrderViewSet)
router.register('parse_session', parsers.views.ParseSessionViewSet)
router.register('preview', previews.views.PreviewViewSet)
router.register('site', parsers.views.SiteViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include(accounts.urls)),
    path('commerce/', include(commerce.urls)),
    path('parsers/', include(parsers.urls)),
    path('previews/', include(previews.urls)),
] + router.urls
