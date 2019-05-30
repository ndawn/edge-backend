from rest_framework import serializers
from edge.config import SIZES
from commerce.models import (
    PriceMap,
    Category,
    Publisher,
    Item,
    Cover,
    Variant,
    Cart,
    CartItem,
    PaymentMethod,
    DeliveryMethod,
    OrderStatus,
    Order,
)


class PriceMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceMap
        fields = (
            'id',
            'mode',
            'usd',
            'bought',
            'default',
            'discount',
            'superior',
            'weight',
        )


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id',
            'title',
            'description',
            'children',
            'slug',
            'background',
        )

    # def get_parent(self, obj):
    #     return CategorySerializer(obj.parent).data if not obj.is_root() else None

    def get_children(self, obj):
        return [CategorySerializer(x).data for x in obj.category_set.all()]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = (
            'id',
            'full_name',
            'short_name',
        )


class ParserPublisherSerializer(serializers.ModelSerializer):
    parser_data = serializers.SerializerMethodField()

    class Meta:
        model = Publisher
        fields = (
            'id',
            'full_name',
            'short_name',
        )


class CoverSizesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cover
        fields = (
            'full',
            *SIZES.keys(),
        )


class CoverSerializer(serializers.ModelSerializer):
    sizes = CoverSizesSerializer(many=False, read_only=True)

    class Meta:
        model = Cover
        fields = (
            'id',
            'version',
            'signature',
            'width',
            'height',
            'etag',
            'phash',
            'sizes',
            'original_filename',
            'original_cover_url',
        )


class VariantSerializer(serializers.ModelSerializer):
    cover = CoverSerializer(many=False, read_only=True)

    class Meta:
        model = Variant
        fields = (
            'id',
            'bought',
            'price',
            'stock_quantity',
            'weight',
            'cover',
            'active',
            'created',
            'updated',
        )


class ItemSerializer(serializers.ModelSerializer):
    publisher = PublisherSerializer(many=False, read_only=True)
    variant_set = VariantSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = (
            'id',
            'title',
            'description',
            'category',
            'publisher',
            'variant_set',
            'created',
            'updated',
        )


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = (
            'id',
            'user',
            'is_submitted',
            'date_closed',
            'created',
            'updated',
        )


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = (
            'id',
            'item',
            'quantity',
            'cart_id',
            'created',
            'updated',
        )


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = (
            'id',
            'name',
            'description',
        )


class DeliveryMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = (
            'id',
            'name',
            'description',
        )


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = (
            'id',
            'name',
            'description',
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'cart',
            'payment_method',
            'delivery_method',
            'track_code',
            'status',
            'created',
            'updated',
        )
