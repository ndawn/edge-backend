from django.contrib import admin
from commerce.models import PriceMap, Category, Publisher


@admin.register(PriceMap)
class PriceMapAdmin(admin.ModelAdmin):
    list_display = ('mode', 'usd', 'bought', 'default', 'discount', 'superior', 'weight')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('slug', '__str__')


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'short_name')
