from previews.models import Preview, PublisherData, CategoryData
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from previews.serializers import PreviewSerializer, PublisherDataSerializer, CategoryDataSerializer


class PreviewViewSet(ModelViewSet):
    permission_classes = (IsAdminUser, )
    serializer_class = PreviewSerializer

    queryset = Preview.objects.all()


class PublisherDataViewSet(ModelViewSet):
    permission_classes = (IsAdminUser, )
    serializer_class = PublisherDataSerializer

    queryset = PublisherData.objects.all()


class CategoryDataViewSet(ModelViewSet):
    permission_classes = (IsAdminUser, )
    serializer_class = CategoryDataSerializer

    queryset = CategoryData.objects.all()
