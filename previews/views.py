from previews.models import Preview, PublisherData, CategoryData
from previews.serializers import PreviewSerializer, PublisherDataSerializer, CategoryDataSerializer

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser


class PreviewViewSet(ModelViewSet):
    permission_classes = (IsAdminUser, )
    serializer_class = PreviewSerializer

    queryset = Preview.objects.all()


class PublisherDataListView(ListAPIView):
    permission_classes = (IsAdminUser, )
    serializer_class = PublisherDataSerializer

    queryset = PublisherData.objects.all()

    def list(self, request, site_id, *args, **kwargs):
        queryset = self.get_queryset().filter(site_id=site_id)
        serializer = PublisherDataSerializer(queryset, many=True)
        return Response(serializer.data)


class CategoryDataListView(ListAPIView):
    permission_classes = (IsAdminUser, )
    serializer_class = CategoryDataSerializer

    queryset = CategoryData.objects.all()

    def list(self, request, site_id, *args, **kwargs):
        queryset = self.get_queryset().filter(site_id=site_id)
        serializer = CategoryDataSerializer(queryset, many=True)
        return Response(serializer.data)
