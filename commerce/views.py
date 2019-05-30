from commerce.models import PriceMap, Category, Publisher, Item, Order
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from commerce.serializers import (
    PriceMapSerializer,
    CategorySerializer,
    PublisherSerializer,
    ItemSerializer,
    OrderSerializer,
)


class PriceMapViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, )

    queryset = PriceMap.objects.all()
    serializer_class = PriceMapSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PublisherViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, )

    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, )

    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class CategoryTreeView(APIView):
    def get(self, request, format=None):
        roots = Category.objects.filter(parent=None)

        return Response([CategorySerializer(x).data for x in roots])
