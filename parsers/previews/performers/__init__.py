from datetime import datetime
from abc import ABC, abstractmethod

from commerce.models import Category, Publisher
from parsers.models import ParseSession


__all__ = ['previewsworld', 'ItemParsePerformer']


class ItemParsePerformer(ABC):
    _session_meta = None

    def __init__(self,
                 catalog_date=None,
                 urls=None,
                 publishers=None,
                 publisher_ids=None,
                 categories=None,
                 category_ids=None):
        self.session = ParseSession.objects.create(type='previews', meta=self._session_meta)

        self.catalog_date = self.urls = self.publishers = None

        if urls is not None:
            self.urls = urls
        elif catalog_date is not None:
            if catalog_date.__class__ is not datetime:
                raise ValueError('Catalog date must be datetime object')

            self.catalog_date = catalog_date
        else:
            self.catalog_date = self.get_last_available_date()

        if categories:
            self.categories = categories
        elif category_ids:
            self.categories = [Category.objects.get(pk=pk) for pk in category_ids]
        else:
            self.categories = self.get_default_categories()

        if publishers:
            self.publishers = publishers
        elif publisher_ids:
            self.publishers = [Publisher.objects.get(pk=pk) for pk in publisher_ids]
        else:
            self.publishers = self.get_default_publishers()

    @abstractmethod
    def get_tasks(self):
        pass

    @staticmethod
    @abstractmethod
    def get_default_publishers():
        pass

    @staticmethod
    @abstractmethod
    def get_default_categories():
        pass

    @staticmethod
    @abstractmethod
    def get_last_available_date():
        pass
