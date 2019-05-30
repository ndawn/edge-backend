from rest_framework import serializers
from previews.models import Preview, PublisherData, CategoryData
from commerce.serializers import PriceMapSerializer, PublisherSerializer, CategorySerializer


class PreviewSerializer(serializers.HyperlinkedModelSerializer):
    price_map = PriceMapSerializer(many=False, read_only=True)

    class Meta:
        model = Preview
        fields = (
            'url',
            'id',
            'variant_id',
            'mode',
            'origin_url',
            'price_map',
            'release_date',
            'cover_origin',
        )


class PublisherDataSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    publisher = PublisherSerializer()

    class Meta:
        model = PublisherData
        fields = (
            'id',
            'address',
            'default',
            'publisher',
        )

    def get_address(self, obj):
        return obj.site.address


class CategoryDataSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    category = CategorySerializer

    class Meta:
        model = CategoryData
        fields = (
            'id',
            'address',
            'default',
            'category',
        )

    def get_address(self, obj):
        return obj.site.address
