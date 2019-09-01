from rest_framework import serializers
from previews.models import Preview, PublisherData, CategoryData
from commerce.serializers import PriceMapSerializer, PublisherSerializer, CategorySerializer
from parsers.serializers import SiteSerializer


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
    publisher = PublisherSerializer(read_only=True)

    class Meta:
        model = PublisherData
        fields = (
            'id',
            'default',
            'publisher',
        )


class CategoryDataSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = CategoryData
        fields = (
            'id',
            'default',
            'category',
        )
