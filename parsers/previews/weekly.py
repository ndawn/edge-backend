import os.path
import datetime
import time
import json
import re

from previews.models import Preview
from parsers.previews import Parser, SingleItemParser as _SingleItemParser
from edge import config
from commerce.models import Publisher, PriceMap

from bs4 import BeautifulSoup
import requests
import demjson


class WeeklyParser(Parser):
    parse_url = 'http://midtowncomics.com/store/ajax_wr_online.asp'
    publishers = filter(lambda x: getattr(x, 'load_weekly'), Publisher.objects.all())
    release_date_wdate = ''
    session = int(time.time())
    page = None
    soup = None
    cover_url = 'http://midtowncomics.com/images/product/xl/%s_xl.jpg'

    def _process_title(self, title):
        title = re.sub('\(.*\)| \(Marvel Legacy Tie-In\)', '', title)
        title = re.sub('Vol [0-9]+', '', title)

        title = title.rstrip()

        re_cover_a = re.compile('Cover A')
        re_cover_b = re.compile('Cover [B-Z]')

        if re_cover_b.search(title):
            title = re_cover_b.sub('', title)

            if title.endswith('Cover'):
                title = title[:-5]
        elif re_cover_a.search(title):
            title = re_cover_a.split(title)[0]

        title = re.sub('Ptg', 'Printing', title)

        return ' '.join(title.split())

    def _set_date(self):
        if self.release_date is not None:
            self.release_date_wdate = self.release_date.strftime('%-m/%-d/%Y')
        else:
            self._date_from_soup()

    def _request_entries(self, publisher):
        raw = requests.get(self.parse_url, {'cat': publisher.midtown_code, 'wdate': self.release_date_wdate}).text
        return demjson.decode(raw)

    def _date_from_soup(self):
        date_page = requests.get('http://midtowncomics.com/store/weeklyreleasebuy.asp')
        date_soup = BeautifulSoup(date_page.text, self.parse_engine)
        date_string = date_soup.find('option', {'selected': ''})['value']

        self.release_date = datetime.datetime.strptime(date_string, '%m/%d/%Y')
        self.release_date_wdate = date_string

    def _parse_by_publisher(self, publisher):
        entries = self._request_entries(publisher)

        for entry in entries:
            params = {
                'mode': 'weekly',
                'title': self._process_title(entry['pr_ttle']),
                'publisher': publisher,
                'quantity': None,
                'diamond_id': None,
                'midtown_id': entry['pr_id'],
                'release_date': self.release_date,
                'session': self.session,
            }

            usd = entry['pr_lprice']

            try:
                usd = float(usd)
            except ValueError:
                usd = 0.0

            try:
                price_map = PriceMap.objects.get(mode='weekly', usd=usd)
            except (PriceMap.DoesNotExist, PriceMap.MultipleObjectsReturned):
                price_map = PriceMap.dummy()

            params['price_map'] = price_map
            params['price'] = price_map.default
            params['weight'] = price_map.weight

            instance = Preview.objects.create(**params)
            instance.cover_origin = self.cover_url % params['midtown_id']
            instance.save()

            self.producer.send({'preview_id': instance.id})

            self.count += 1


class SingleItemParser(_SingleItemParser):
    description_url = 'http://midtowncomics.com/store/dp.asp'
    dummy_vendor = 'mdtwn'

    def postparse(self):
        description_page = requests.get(self.description_url, {'PRID': self.instance.midtown_id})
        description_soup = BeautifulSoup(description_page.text, self.parse_engine)

        description_element = description_soup.find('p', {'class': 'shorten'})

        if description_element is not None:
            self.instance.description = description_element.text

        diamond_container = description_soup.find('span', {'id': 'diamond_container'})

        if diamond_container is not None:
            self.instance.diamond_id = diamond_container.text[:9]

        self.instance.save()
