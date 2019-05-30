from datetime import datetime
import logging

from parsers.previews.extractors.base import ItemExtractor, VariantExtractor, PreviewExtractor
from edge import config
from django.core.exceptions import ObjectDoesNotExist
from commerce.models import PriceMap, Publisher, Cover


logger = logging.getLogger()


class PreviewsworldItemExtractor(ItemExtractor):
    def get_title(self):
        if 'title' in self.cached_data:
            return self.cached_data['title']

        title = getattr(self.tree.select_one('.Title'), 'text', None)

        if title is not None:
            self.cached_data['title'] = title

        return title

    def get_origin_title(self):
        if 'title' in self.cached_data:
            return self.cached_data['title']

        title = getattr(self.tree.select_one('.Title'), 'text', None)

        if title is not None:
            self.cached_data['title'] = title

        return title

    def get_description(self):
        description = self.tree.select_one('.Text')

        if description is not None:
            attribute_buffer = description.select_one('.ItemCode')

            if attribute_buffer is not None:
                attribute_buffer.extract()

            attribute_buffer = description.select_one('.Creators')

            if attribute_buffer is not None:
                attribute_buffer.extract()

            for li in description.select('li'):
                li.extract()

            for b in description.select('b'):
                b.extract()

            attribute_buffer = description.select_one('.ReleaseDate')

            if attribute_buffer is not None:
                release_date_string = attribute_buffer.extract().text

                if 'release_date_string' not in self.cached_data:
                    self.cached_data['release_date_string'] = release_date_string

            attribute_buffer = description.select_one('.SRP')

            if attribute_buffer is not None:
                price_string = attribute_buffer.extract()

                if 'price_string' not in self.cached_data:
                    self.cached_data['price_string'] = price_string.text

            parsed_description = []

            for line in description.strings:
                string = line.replace('\xa0', '').strip()

                if string:
                    parsed_description.append(string)

            parsed_description = '\n'.join(parsed_description).strip()

            if parsed_description:
                return parsed_description

        return None

    def get_category(self):
        if 'category' in self.cached_data:
            return self.cached_data['category']

        return None

    def get_publisher(self):
        if 'publisher' in self.cached_data:
            return self.cached_data['publisher']

        publisher_full_name = getattr(self.tree.select_one('.Publisher'), 'text', None)

        if publisher_full_name is not None:
            try:
                publisher = Publisher.objects.filter(publisherdata__full_name__iexact=publisher_full_name).first()
            except Publisher.DoesNotExist:
                publisher = Publisher.objects.filter(full_name__iexact=publisher_full_name).first()

            if publisher is not None:
                return publisher
            else:
                return Publisher.objects.create(full_name=publisher_full_name.title())

        return None


class PreviewsworldVariantExtractor(VariantExtractor):
    def get_title(self):
        if 'title' in self.cached_data:
            return self.cached_data['title']

        title = getattr(self.tree.select_one('.Title'), 'text', None)

        if title is not None:
            self.cached_data['title'] = title

        return title

    def get_origin_title(self):
        if 'title' in self.cached_data:
            return self.cached_data['title']

        title = getattr(self.tree.select_one('.Title'), 'text', None)

        if title is not None:
            self.cached_data['title'] = title

        return title

    def get_price_map(self):
        if 'price_map' in self.cached_data:
            return self.cached_data['price_map']

        price = getattr(self.tree.select_one('.SRP'), 'text', None)

        if price is not None and 'N/A' not in price and 'PI' not in price:
            price = float(price[price.find('$') + 1:])

            price_map = PriceMap.objects.filter(usd=price).first()

            if price_map is not None:
                self.cached_data['price_map'] = price_map

        if 'price_map' not in self.cached_data:
            self.cached_data['price_map'] = PriceMap.dummy()

        return self.cached_data['price_map']

    def get_bought(self):
        return self.get_price_map().bought

    def get_price(self):
        return self.get_price_map().default

    def get_weight(self):
        return self.get_price_map().weight

    def get_image(self):
        image_url = config.PREVIEWSWORLD_HOSTNAME + self.tree.select_one('#MainContentImage').get('src', '')

        return Cover.load(image_url)


class PreviewsworldPreviewExtractor(PreviewExtractor):
    def get_mode(self):
        return 'monthly'

    def get_origin_url(self):
        return self.tree.url

    def get_price_map(self):
        if 'price_map' in self.cached_data:
            return self.cached_data['price_map']

        price = getattr(self.tree.select_one('.SRP'), 'text', None)

        if price is not None and 'N/A' not in price and 'PI' not in price:
            price = float(price[price.find('$') + 1:])

            price_map = PriceMap.objects.filter(usd=price).first()

            if price_map is not None:
                self.cached_data['price_map'] = price_map

        if 'price_map' not in self.cached_data:
            self.cached_data['price_map'] = PriceMap.dummy()

        return self.cached_data['price_map']

    def get_release_date(self):
        if 'release_date_string' not in self.cached_data:
            self.cached_data['release_date_string'] = getattr(self.tree.select_one('.ReleaseDate'), 'text', None)

        if self.cached_data['release_date_string'] is not None and 'N/A' not in self.cached_data['release_date_string']:
            return datetime.strptime(self.cached_data['release_date_string'], 'In Shops: %b %d, %Y')

        return None
