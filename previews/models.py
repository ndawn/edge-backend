from django.db import models
from commerce.models import Category, Publisher, Variant, PriceMap
from parsers.models import Site, ParseSession


class Preview(models.Model):
    class Meta:
        verbose_name = 'Предзаказ'
        verbose_name_plural = 'Предзаказы'

    MODE_CHOICES = {
        'monthly': 'Месяц',
        'weekly': 'Неделя',
    }

    variant = models.OneToOneField(
        Variant,
        on_delete=models.CASCADE,
        unique=False,
        blank=True,
        verbose_name='Товар',
    )

    mode = models.CharField(
        null=True,
        max_length=8,
        choices=MODE_CHOICES.items(),
        verbose_name='Тип',
    )

    origin_url = models.URLField(
        default='',
        blank=True,
        verbose_name='Ссылка на оригинальный товар',
    )

    price_map = models.ForeignKey(
        PriceMap,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Таблица цен',
    )

    release_date = models.DateField(
        null=True,
        verbose_name='Дата выхода',
    )

    session = models.ForeignKey(
        ParseSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Сессия загрузки',
    )

    upc = models.CharField(
        null=True,
        max_length=20,
    )


class PublisherData(models.Model):
    class Meta:
        verbose_name = 'Информация об издателе'
        verbose_name_plural = 'Информация об издателях'

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        verbose_name='Сайт',
    )

    publisher = models.OneToOneField(
        Publisher,
        on_delete=models.CASCADE,
        verbose_name='Издатель',
    )

    full_name = models.CharField(
        null=True,
        blank=True,
        max_length=32,
        verbose_name='Полное название',
    )

    short_name = models.CharField(
        null=True,
        blank=True,
        max_length=16,
        verbose_name='Сокращенное название',
    )

    singles_category_code = models.CharField(
        null=True,
        blank=True,
        max_length=16,
        verbose_name='Код категории синглов',
    )

    tp_category_code = models.CharField(
        null=True,
        blank=True,
        max_length=16,
        verbose_name='Код категории сборников',
    )

    default = models.BooleanField(
        default=False,
        blank=True,
        verbose_name='По умолчанию для этого сайта',
    )

    def __str__(self):
        return self.publisher.short_name + ' @ ' + self.site.address


class CategoryData(models.Model):
    class Meta:
        verbose_name = 'Информация о категории'
        verbose_name_plural = 'Информация о категориях'

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        verbose_name='Сайт',
    )

    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
    )

    identifier = models.CharField(
        null=True,
        blank=True,
        max_length=16,
        verbose_name='ID категории',
    )

    name = models.CharField(
        null=True,
        blank=True,
        max_length=32,
        verbose_name='Название категории',
    )

    default = models.BooleanField(
        default=False,
        blank=True,
        verbose_name='По умолчанию для этого сайта',
    )

    def __str__(self):
        return self.category.name + ' @ ' + self.site.address
