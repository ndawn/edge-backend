import locale
import logging
import re
from datetime import datetime

from edge import config
from django.core.exceptions import ObjectDoesNotExist
from commerce.models import VariantIdentifier
from previews.models import PublisherData, CategoryData
from parsers.previews.performers import Performer as BasePerformer

import requests
from bs4 import BeautifulSoup
from celery import group, chord


logger = logging.getLogger()


class Performer(BasePerformer):
    class Meta:
        mode = 'monthly'
        host = 'previewsworld.com'

    def get_tasks(self):
        if self.urls is not None:
            return self.urls

        batch = ''

        if self.catalog_date is not None:
            target_month = self.catalog_date.month - 2 if self.catalog_date.month > 2 else self.catalog_date.month + 10
            batch = self.catalog_date.replace(month=target_month).strftime('%b%y')

        response = requests.get(
            'https://' + self.Meta.host + '/Catalog/',
            {'batch': batch},
        )

        if response.status_code == 404:
            self.session.delete()
            raise LookupError('Got to the 404 page')

        soup = BeautifulSoup(response.content, 'lxml')

        self.session.meta['date'] = datetime.strptime(
            soup.select('.catalogDisclaimer strong')[-1].text,
            '%B %Y',
        ).isoformat()

        self.session.save()

        logger.debug('PUBLISHERS: ' + str(self.publishers))
        logger.debug('CATEGORIES: ' + str(self.categories))

        tasks = []

        for publisher in self.publishers:
            try:
                if not publisher.publisherdata.short_name:
                    continue
            except ObjectDoesNotExist:
                continue

            for category in self.categories:
                search_params = {'class': 'nrGalleryItem'}

                try:
                    search_params['dmd-pub'] = publisher.publisherdata.full_name
                except ObjectDoesNotExist:
                    break

                try:
                    search_params['dmd-cat'] = category.categorydata.identifier
                except ObjectDoesNotExist:
                    continue

                items = soup('div', search_params)

                for url in list(map(
                    lambda x: 'https://' + self.Meta.host + x.select_one('a').get('href'),
                    items,
                )):
                    tasks.append({
                        'url': url,
                        'publisher': publisher,
                        'category': category,
                    })

        return tasks

    @staticmethod
    def get_default_publishers():
        return list(map(
            lambda x: x.publisher,
            PublisherData.objects.filter(
                site__address=Performer.Meta.host,
                default=True,
            ),
        ))

    @staticmethod
    def get_default_categories():
        return list(map(
            lambda x: x.category,
            CategoryData.objects.filter(
                site__address=Performer.Meta.host,
                default=True,
            ),
        ))

    @staticmethod
    def get_last_available_date():
        lc = locale.getlocale(locale.LC_TIME)

        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

        response = requests.get('https://' + Performer.Meta.host + '/Catalog/')

        date = datetime.strptime(
            BeautifulSoup(response.content, 'lxml').select_one('#CatalogListingPageTitle').next.strip(),
            'PREVIEWS %B %Y',
        )

        target_month = date.month + 2 if date.month < 10 else date.month - 10
        date = date.replace(month=target_month)

        locale.setlocale(locale.LC_TIME, lc)

        return date

    @staticmethod
    def get_identifiers_and_response(response):
        ids = {response.url.split('/')[-1]}

        resolved_response = response

        soup = BeautifulSoup(response.content, 'lxml')

        title = soup.select_one('.Title')

        if title is None:
            return ids, None

        re_match = re.match(r'^\(USE ([A-Z]{3}[0-9]{6})', title.text)

        if re_match is not None:
            follow_url = response.url[:response.url.rfind('/') + 1] + re_match.groups()[0]

            follow_response = requests.get(follow_url)

            add_ids, resolved_response = Performer.get_identifiers_and_response(follow_response)

            ids.update(add_ids)

        for res in response.history:
            ids.add(res.url.split('/')[-1])

        return ids, resolved_response

    @staticmethod
    def get_common_item(soup, ids):
        series_btn = soup.select_one('.ViewSeriesItemsLink')

        if series_btn is not None:
            logger.debug('Found series link')

            response = requests.get('https://' + Performer.Meta.host + series_btn['href'])

            series_page = BeautifulSoup(response.content, 'lxml').select_one('.CatalogFullDetail')

            for var_id in ids:
                if series_page is None:
                    continue

                dmd_no_element = series_page(
                    'div',
                    {'class': 'nrGalleryItemDmdNo'},
                    text=re.compile(var_id, re.I),
                )

                if dmd_no_element is None:
                    continue

                try:
                    dmd_no_element = dmd_no_element[0]
                except IndexError:
                    continue

                issue_number_element = dmd_no_element.parent.select_one('.nrGalleryItemIssue')

                if issue_number_element is not None:
                    issue_number = issue_number_element.text.strip().strip(' VAR')

                    break
            else:
                issue_number = None

            if issue_number is not None:
                siblings = series_page('div', {'class': 'nrGalleryItemIssue'}, text=re.compile(issue_number, re.I))
            else:
                siblings = []

            identifiers = []

            for sibling in siblings:
                identifier = sibling.parent.select_one('.nrGalleryItemDmdNo')

                if identifier is not None:
                    identifiers.append(identifier.text)

            for identifier in identifiers:
                if identifier in ids:
                    continue

                found_var_id = VariantIdentifier.objects.filter(identifier=identifier).first()

                if found_var_id is not None:
                    logger.debug(
                        f'Found common item with variant {found_var_id.variant.id}: {found_var_id.variant.item.id}'
                    )

                    return found_var_id.variant.item

            return None

    @staticmethod
    def run(**kwargs):
        from parsers.tasks import (
            parse_previewsworld_item as parse_item,
            finish_previewsworld_parse as finish,
        )

        performer = Performer(**kwargs)

        urls = performer.get_tasks()

        if not urls:
            performer.session.delete()
            raise AttributeError('No url list found')

        tasks = []

        if urls[:1] and isinstance(urls[0], dict):
            for url in urls:
                tasks.append(parse_item.s(
                    url=url['url'],
                    session_id=performer.session.id,
                    publisher_id=url['publisher'].id,
                    category_id=url['category'].id,
                ))
        else:
            for url in urls:
                tasks.append(parse_item.s(url, performer.session.id))

        performer.session.item_count = len(tasks)
        performer.session.save()

        chord(group(tasks))(
            finish.s(session_id=performer.session.id).set(link_error=[finish.si(session_id=performer.session.id)])
        )

        return {'session_id': performer.session.id}
