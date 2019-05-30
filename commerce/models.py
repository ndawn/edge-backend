import logging
import shutil

from django.core.exceptions import ObjectDoesNotExist as DoesNotExist
from django.db import models, IntegrityError
from accounts.models import User
from edge import config
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from utils.yadisk import upload_to_yadisk, delete_from_yadisk

import requests
import cloudinary
import cloudinary.uploader
import yadisk
from PIL import Image


DEFAULT_WEIGHT = 100

FILE_TYPE_CHOICES = {
    'image': 'Изображение',
}


logger = logging.getLogger()


class PriceMap(models.Model):
    class Meta:
        unique_together = (('usd', 'mode'), )
        verbose_name = 'Таблица цен'
        verbose_name_plural = 'Таблицы цен'

    MODE_CHOICES = {
        'monthly': 'Месяц',
        'weekly': 'Неделя',
    }

    mode = models.CharField(
        null=True,
        max_length=8,
        choices=MODE_CHOICES.items(),
        verbose_name='Тип',
    )

    usd = models.FloatField(
        default=0.0,
        verbose_name='Цена в долларах',
    )

    bought = models.FloatField(
        default=0.0,
        blank=True,
        verbose_name='Закупочная цена',
    )

    default = models.FloatField(
        default=0.0,
        blank=True,
        verbose_name='Цена',
    )

    discount = models.FloatField(
        default=0.0,
        blank=True,
        verbose_name='Цена со скидкой',
    )

    superior = models.FloatField(
        default=0.0,
        blank=True,
        verbose_name='Superior цена',
    )

    weight = models.FloatField(
        default=DEFAULT_WEIGHT,
        blank=True,
        verbose_name='Вес',
    )

    @staticmethod
    def dummy():
        return PriceMap.objects.get(usd=0.0)

    def __str__(self):
        return self.MODE_CHOICES.get(self.mode, '---') + ': $%.2f' % self.usd


class Category(models.Model):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    title = models.CharField(
        default='',
        max_length=32,
        verbose_name='Название',
    )

    description = models.TextField(
        default='',
        blank=True,
        verbose_name='Описание',
    )

    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Родительская категория',
    )

    slug = models.SlugField(
        blank=True,
        null=True,
        verbose_name='Код',
    )

    background = models.URLField(
        default=None,
        blank=True,
        null=True,
        verbose_name='Фоновое изображение',
    )

    def is_root(self):
        return self.parent is None

    def set_parent(self, other):
        if not isinstance(other, Category):
            raise IntegrityError('Parent must be a category')
        if self == other:
            raise IntegrityError('Category can\'t refer to itself')
        else:
            self.parent = other
            self.save()

    def get_root(self):
        if self.is_root():
            return self
        else:
            return self.parent.get_root()

    def self_tree(self):
        tree_list = []

        for category in self.category_set.all():
            tree_list.append({
                'category': category,
                'children': category.self_tree(),
            })

        return tree_list

    def get_parent_chain(self):
        return [self.title] + (self.parent.get_parent_chain() if self.parent is not None else [])

    def __str__(self):
        return ' -> '.join(reversed(self.get_parent_chain()))

    @staticmethod
    def tree():
        tree_list = []

        for category in Category.objects.filter(parent=None):
            tree_list.append({
                'category': category,
                'children': category.self_tree(),
            })

        return tree_list


class Publisher(models.Model):
    class Meta:
        verbose_name = 'Издатель'
        verbose_name_plural = 'Издатели'

    full_name = models.CharField(
        default='',
        null=True,
        blank=True,
        max_length=256,
        verbose_name='Полное название',
    )

    short_name = models.CharField(
        default='',
        null=True,
        blank=True,
        max_length=256,
        verbose_name='Краткое название',
    )

    def __str__(self):
        return 'Publisher: ' + self.full_name


class Item(models.Model):
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    title = models.CharField(
        default='Без названия',
        blank=True,
        max_length=512,
        verbose_name='Название',
    )

    origin_title = models.CharField(
        default='',
        null=True,
        blank=True,
        max_length=512,
        verbose_name='Оригинальное название',
    )

    description = models.TextField(
        default='',
        blank=True,
        verbose_name='Описание',
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория',
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Издатель',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Создан',
    )

    updated = models.DateTimeField(
        auto_now=True,
        blank=True,
        verbose_name='Обновлен',
    )

    def __str__(self):
        return f'Item: {self.title}'


class Cover(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for size in config.SIZES:
            setattr(
                self,
                size,
                property(
                    lambda self: cloudinary.CloudinaryImage(self.id).build_url(transformation=config.SIZES[size])
                ),
            )

    _id = models.CharField(
        primary_key=True,
        max_length=32,
        verbose_name='ID',
    )

    version = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Версия',
    )

    signature = models.CharField(
        null=True,
        blank=True,
        max_length=40,
        verbose_name='Сигнатура',
    )

    format = models.CharField(
        null=True,
        blank=True,
        max_length=8,
        verbose_name='Тип файла',
    )

    width = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Ширина',
    )

    height = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Высота',
    )

    etag = models.CharField(
        null=True,
        blank=True,
        max_length=32,
        verbose_name='ETag',
    )

    phash = models.CharField(
        null=True,
        blank=True,
        max_length=16,
        verbose_name='pHash',
    )

    original_filename = models.CharField(
        null=True,
        blank=True,
        max_length=32,
        verbose_name='Оригинальное имя файла',
    )

    original_url = models.URLField(
        null=True,
        blank=True,
        verbose_name='URL оригинальной обложки',
    )

    hosted_url = models.URLField(
        null=True,
        blank=True,
        max_length=512,
        verbose_name='URL на стороннем ресурсе',
    )

    @property
    def id(self):
        return self._id

    @property
    def full(self):
        return cloudinary.CloudinaryImage(self.id).url

    def sizes(self):
        return {
            **{size: getattr(self, size) for size in config.SIZES},
            'full': self.full,
        }

    @staticmethod
    def is_similar(phash1, phash2):
        phash_distance = int(phash1, base=16) ^ int(phash2, base=16)
        phash_identity = 1 - bin(phash_distance).count('1') / 64

        return phash_identity > config.PHASH_IDENTITY_THRESHOLD

    @staticmethod
    def load(url):
        try:
            data = cloudinary.uploader.upload(
                url,
                folder=config.CLOUDINARY_COVER_FOLDER,
                phash=True,
                config=config.CLOUDINARY_CONFIG,
            )
        except cloudinary.api.Error:
            return Cover.dummy()
            # response = requests.get(url, stream=True)
            #
            # with open('/tmp/cloudinary_image', 'wb') as file:
            #     shutil.copyfileobj(response.raw, file)
            #
            # file = Image.open('/tmp/cloudinary_image')
            #
            # file # TODO: RESIZE
            #
            # data = cloudinary.uploader.upload(
            #     file,
            #     folder=config.CLOUDINARY_COVER_FOLDER,
            #     phash=True,
            #     config=config.CLOUDINARY_CONFIG,
            # )

        data['id'] = data['public_id']
        data['url'] = data['secure_url']

        del data['public_id']
        del data['resource_type']
        del data['created_at']
        del data['tags']
        del data['bytes']
        del data['type']
        del data['placeholder']

        if Cover.is_similar(data['phash'], config.DUMMY['prwld']['phash']) \
                or Cover.is_similar(data['phash'], config.DUMMY['mdtwn']['phash']):
            cloudinary.uploader.destroy(data['id'])

            return Cover.dummy()

        cover = Cover.objects.create(
            _id=data['id'],
            version=data['version'],
            signature=data['signature'],
            width=data['width'],
            height=data['height'],
            etag=data['etag'],
            phash=data['phash'],
            original_filename=data['original_filename'],
            original_url=url,
            hosted_url=data['url'],
        )

        logger.debug('Loaded cover: ' + data['id'])

        try:
            disk_data = upload_to_yadisk(data['url'], data['id'], '', data)

            cover.hosted_url = disk_data.file
            cover.save()
        except yadisk.exceptions.YaDiskError as exc:
            raise
            # logger.error(exc.__class__.__name__ + ' occured while uploading file to YaDisk')

        return cover

    @staticmethod
    def dummy():
        return Cover.objects.get(_id='dummy/dummy')


@receiver(pre_delete, sender=Cover)
def destroy_image(**kwargs):
    if 'instance' in kwargs:
        cloudinary.uploader.destroy(kwargs['instance'].id)
        delete_from_yadisk(kwargs['instance'].id, '')


class Variant(models.Model):
    class Meta:
        verbose_name = 'Вариация'
        verbose_name_plural = 'Вариации'

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )

    title = models.CharField(
        default='Без названия',
        blank=True,
        max_length=512,
        verbose_name='Название',
    )

    origin_title = models.CharField(
        default='',
        null=True,
        blank=True,
        max_length=512,
        verbose_name='Оригинальное название',
    )

    bought = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name='Закупочная цена'
    )

    price = models.FloatField(
        default=0,
        blank=True,
        verbose_name='Цена',
    )

    stock_quantity = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name='Количество в наличии',
    )

    weight = models.FloatField(
        default=DEFAULT_WEIGHT,
        blank=True,
        verbose_name='Вес',
    )

    image = models.OneToOneField(
        Cover,
        on_delete=models.SET(Cover.dummy),
        null=True,
        blank=True,
        verbose_name='Обложка',
    )

    active = models.BooleanField(
        default=False,
        blank=True,
        verbose_name='Активен',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Создан',
    )

    updated = models.DateTimeField(
        auto_now=True,
        blank=True,
        verbose_name='Обновлен',
    )

    @property
    def cover(self):
        return self.image

    @cover.setter
    def cover(self, cover):
        old_cover, self.image = self.image, cover

        if isinstance(old_cover, Cover) and old_cover.id != 'dummy/dummy':
            try:
                old_cover.delete()
            except Cover.DoesNotExist:
                pass


class VariantIdentifier(models.Model):
    class Meta:
        verbose_name = 'Идентификатор вариации'
        verbose_name_plural = 'Идентификаторы вариации'

    identifier = models.CharField(
        primary_key=True,
        max_length=16,
        verbose_name='Идентификатор',
    )

    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )


class CartManager(models.Manager):
    def get_cart(self, user):
        return self.get_or_create(user=user, is_submitted=False, defaults={'user': user})[0]

    def create_from_anonymous(self, anonymous, user):
        for cart_item in anonymous:
            item_id = cart_item['item']['id']
            item_queryset = Item.objects.in_bulk([item_id])
            item = item_queryset.get(item_id)

            if item and item.quantity:
                if item.quantity >= cart_item['quantity']:
                    quantity = cart_item['quantity']
                else:
                    quantity = item.quantity

                CartItem.objects.create(
                    item=item,
                    quantity=quantity,
                    cart=self.get_cart(user),
                )
        return self.get_cart(user)


class Cart(models.Model):
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    objects = CartManager()

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    is_submitted = models.BooleanField(
        default=False,
        verbose_name='Закрыта',
    )

    closed = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        verbose_name='Закрыта',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Создана',
    )

    updated = models.DateTimeField(
        auto_now=True,
        blank=True,
        verbose_name='Обновлена',
    )

    def clear(self):
        self.cartitem_set.delete()


class CartItem(models.Model):
    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'

        unique_together = ('cart', 'item')

    item = models.ForeignKey(
        Variant,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )

    quantity = models.IntegerField(
        default=1,
        null=True,
        blank=True,
        verbose_name='Количество',
    )

    cart = models.ForeignKey(
        Cart,
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Корзина',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Создан',
    )

    updated = models.DateTimeField(
        auto_now=True,
        blank=True,
        verbose_name='Обновлен',
    )


class PaymentMethod(models.Model):
    class Meta:
        verbose_name = 'Метод оплаты'
        verbose_name_plural = 'Методы оплаты'

    name = models.CharField(
        default='',
        blank=True,
        max_length=32,
        verbose_name='Название',
    )

    description = models.TextField(
        default='',
        blank=True,
        verbose_name='Описание',
    )


class DeliveryMethod(models.Model):
    class Meta:
        verbose_name = 'Метод доставки'
        verbose_name_plural = 'Методы доставки'

    name = models.CharField(
        default='',
        blank=True,
        max_length=32,
        verbose_name='Название',
    )

    description = models.TextField(
        default='',
        blank=True,
        verbose_name='Описание',
    )


class OrderStatus(models.Model):
    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказа'

    name = models.CharField(
        default='',
        blank=True,
        max_length=64,
        verbose_name='Название',
    )

    description = models.CharField(
        default='',
        blank=True,
        max_length=128,
        verbose_name='Описание',
    )


class Order(models.Model):
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Пользователь',
    )

    cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Корзина',
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Метод оплаты',
    )

    delivery_method = models.ForeignKey(
        DeliveryMethod,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Метод доставки',
    )

    track_code = models.CharField(
        blank=True,
        null=True,
        max_length=32,
        verbose_name='Код отслеживания',
    )

    status = models.ForeignKey(
        OrderStatus,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Статус',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Создан',
    )

    updated = models.DateTimeField(
        auto_now=True,
        blank=True,
        verbose_name='Обновлен',
    )
