from django.contrib import admin
from previews.models import Site, PublisherData, CategoryData


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('address', )


@admin.register(PublisherData)
class PublisherDataAdmin(admin.ModelAdmin):
    list_display = ('site', 'publisher', 'full_name', 'short_name', 'singles_category_code', 'tp_category_code', 'default')


@admin.register(CategoryData)
class CategoryDataAdmin(admin.ModelAdmin):
    list_display = ('site', 'category', 'identifier', 'name')
