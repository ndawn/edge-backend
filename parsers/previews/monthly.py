import os.path
import datetime
import re

from previews.models import Preview
from parsers.previews import Parser, SingleItemParser as _SingleItemParser
from edge.settings import MEDIA_ROOT
from commerce.models import Publisher, PriceMap

from bs4 import BeautifulSoup
import titlecase
import requests


class MonthlyParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._make_soup()

    parse_url = 'https://previewsworld.com/catalog'
    publishers = filter(lambda x: getattr(x, 'load_monthly'), Publisher.objects.all())
    release_date_batch = ''
    page = None
    soup = None
    cover_url = 'https://previewsworld.com/siteimage/catalogimage/%s?type=1'

    def _process_title(self, title):
        def abbrs(word, *args, **kwargs):
            if word in ('TP', 'HC'):
                return word

        string = titlecase.titlecase(title, callback=abbrs) \
            .replace('Var Ed', 'Variant') \
            .replace('Var ', 'Variant ') \
            .replace('Leg', '')

        return ' '.join(re.sub('\(.*\)', '', string).split())

    def _set_date(self):
        if self.release_date is not None:
            self.release_date = datetime.datetime.strptime(self.release_date, '%Y-%m-%d')
            self.release_date_batch = self.release_date.strftime('%b%y')

    def _delete_old(self):
        Preview.objects.filter(mode='monthly', release_date__month=self.release_date.month).delete()
        # TODO: rewrite

    def _make_soup(self):
        self.page = requests.get(self.parse_url, {'batch': self.release_date_batch})
        self.soup = BeautifulSoup(self.page.text, self.parse_engine)

    def _date_from_soup(self):
        if self.soup is not None:
            date_container = self.soup.find('div', {'class': 'catalogDisclaimer'})
            date_string = date_container.find_all('strong')[-1].text

            self.release_date = datetime.datetime.strptime(date_string, '%B %Y')
            self.release_date_batch = self.release_date.strftime('%b%y')
        else:
            raise ValueError('The soup is not yet cooked')

    def _parse_by_publisher(self, publisher):
        entries = self.soup.find('div', {'id': 'NewReleases_' + publisher.abbreviature}) \
                           .find_all('div', {'class': 'nrGalleryItem'})

        for entry in entries:
            title = entry.find('div', {'class': 'nrGalleryItemTitle'}).text.replace('\xa0', ' ')

            params = {
                'mode': 'monthly',
                'title_origin': title,
                'title': self._process_title(title),
                'publisher': publisher,
                'quantity': None,
                'diamond_id': entry.find('div', {'class': 'nrGalleryItemDmdNo'}).text,
                'session': self.session,
            }

            usd = entry.find('div', {'class': 'nrGalleryItemSRP'}).text.lstrip('$')

            try:
                usd = float(usd)
            except ValueError:
                usd = 0.0

            try:
                price_map = PriceMap.objects.get(mode='monthly', usd=usd)
            except (PriceMap.DoesNotExist, PriceMap.MultipleObjectsReturned):
                price_map = PriceMap.dummy()

            params['price_map'] = price_map
            params['price'] = price_map.default
            params['weight'] = price_map.weight

            cover_element = entry.find('div', {'class': 'nrGalleryItemImage'}).a.img
            cover_name = os.path.basename(cover_element.get('data-src', cover_element.get('src')))

            instance = Preview.objects.create(**params)
            instance.cover_origin = self.cover_url % cover_name
            instance.save()

            self.producer.send({'preview_id': instance.id})

            self.count += 1


class SingleItemParser(_SingleItemParser):
    description_url = 'https://previewsworld.com/catalog/%s'
    dummy_vendor = 'prwld'

    def postparse(self):
        description_page = requests.get(self.description_url % self.instance.diamond_id)
        description_soup = BeautifulSoup(description_page.text, self.parse_engine)

        text_container = description_soup.find('div', {'class': 'Text'})

        if text_container is not None:
            try:
                text_container.find('div', {'class': 'ItemCode'}).decompose()
            except AttributeError:
                pass

            try:
                text_container.find('div', {'class': 'Creators'}).decompose()
            except AttributeError:
                pass

            try:
                text_container.find('div', {'class': 'SRP'}).decompose()
            except AttributeError:
                pass

            try:
                release_date = text_container.find('div', {'class': 'ReleaseDate'}).extract().text.strip()
            except AttributeError:
                release_date = None

            try:
                self.instance.release_date = datetime.datetime.strptime(release_date, 'In Shops: %b %d, %Y')
            except (ValueError, AttributeError):
                self.instance.release_date = None

            self.instance.description = text_container.text.strip()

            self.instance.save()

        return self.instance.description
