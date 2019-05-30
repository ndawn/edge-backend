from abc import ABC, abstractmethod

from parsers.previews.extractors import ModelExtractor
from commerce.models import Item, Variant
from previews.models import Preview


class ItemExtractor(ModelExtractor, ABC):
    model = Item

    @abstractmethod
    def get_title(self):
        pass

    @abstractmethod
    def get_origin_title(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

    @abstractmethod
    def get_category(self):
        pass

    @abstractmethod
    def get_publisher(self):
        pass


class VariantExtractor(ModelExtractor, ABC):
    model = Variant

    @abstractmethod
    def get_title(self):
        pass

    @abstractmethod
    def get_origin_title(self):
        pass

    @abstractmethod
    def get_bought(self):
        pass

    @abstractmethod
    def get_price(self):
        pass

    @abstractmethod
    def get_weight(self):
        pass

    @abstractmethod
    def get_image(self):
        pass


class PreviewExtractor(ModelExtractor, ABC):
    model = Preview

    @abstractmethod
    def get_mode(self):
        pass

    @abstractmethod
    def get_origin_url(self):
        pass

    @abstractmethod
    def get_price_map(self):
        pass

    @abstractmethod
    def get_release_date(self):
        pass
