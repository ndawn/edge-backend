import locale
import logging
import re
from datetime import datetime

from edge import config
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from commerce.models import Category, Publisher, VariantIdentifier
from previews.models import PublisherData, CategoryData
from parsers.previews.performers import ItemParsePerformer
from parsers.previews.extractors.previewsworld import (
    PreviewsworldItemExtractor,
    PreviewsworldVariantExtractor,
    PreviewsworldPreviewExtractor,
)
from parsers.models import ParseSession
from edge.celery import app

import requests
from bs4 import BeautifulSoup
from celery import group, chord
from yadisk.exceptions import TooManyRequestsError


logger = logging.getLogger()


class PreviewsworldItemParsePerformer(ItemParsePerformer):
    _session_meta = {
        'mode': 'monthly',
        'host': config.PREVIEWSWORLD_HOSTNAME,
    }

    def get_tasks(self):
        if self.urls is not None:
            return self.urls

        response = requests.get(
            config.PREVIEWSWORLD_CATALOG_URL,
            {'batch': self.catalog_date.strftime('%b%y') if self.catalog_date is not None else ''},
        )

        soup = BeautifulSoup(response.content, 'lxml')

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
                    lambda x: config.PREVIEWSWORLD_HOSTNAME + x.select_one('a').get('href'),
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
                site__address=config.PREVIEWSWORLD_HOSTNAME.replace('https://', '', 1),
                default=True,
            ),
        ))

    @staticmethod
    def get_default_categories():
        return list(map(
            lambda x: x.category,
            CategoryData.objects.filter(
                site__address=config.PREVIEWSWORLD_HOSTNAME.replace('https://', '', 1),
                default=True,
            ),
        ))

    @staticmethod
    def get_last_available_date():
        lc = locale.getlocale(locale.LC_TIME)

        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

        response = requests.get(config.PREVIEWSWORLD_CATALOG_URL)

        date = datetime.strptime(
            BeautifulSoup(response.content, 'lxml').select_one('#CatalogListingPageTitle').next.strip(),
            'PREVIEWS %B %Y',
        )

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

            add_ids, resolved_response = PreviewsworldItemParsePerformer.get_identifiers_and_response(follow_response)

            ids.update(add_ids)

        for res in response.history:
            ids.add(res.url.split('/')[-1])

        return ids, resolved_response

    @staticmethod
    def get_common_item(soup, ids):
        series_btn = soup.select_one('.ViewSeriesItemsLink')

        if series_btn is not None:
            logger.debug('Found series link')

            response = requests.get(config.PREVIEWSWORLD_HOSTNAME + series_btn['href'])

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


def run(**kwargs):
    performer = PreviewsworldItemParsePerformer(**kwargs)

    urls = performer.get_tasks()

    if not urls:
        performer.session.delete()
        raise AttributeError('No url list found')

    tasks = []

    if isinstance(urls[0], dict):
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

    chord(group(tasks))(finish.s(session_id=performer.session.id))

    return {'session_id': performer.session.id}


@app.task(
    name='parsers.prwld.parse',
    throws=(ObjectDoesNotExist, ),
    autoretry_for=(TooManyRequestsError, ),
    max_retries=5,
    default_retry_delay=5,
)
def parse_item(url, session_id, publisher_id=None, category_id=None):
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'lxml')

    identifiers, response = PreviewsworldItemParsePerformer.get_identifiers_and_response(response)

    if response is None:
        raise ObjectDoesNotExist

    logger.debug('Variant Identifiers found: ' + ', '.join(identifiers))

    cache = {}

    if publisher_id is not None:
        cache['publisher'] = Publisher.objects.get(pk=publisher_id)

    if category_id is not None:
        cache['category'] = Category.objects.get(pk=category_id)

    item_extractor = PreviewsworldItemExtractor(soup, cache=cache)
    variant_extractor = PreviewsworldVariantExtractor(soup, cache=cache)
    preview_extractor = PreviewsworldPreviewExtractor(soup, cache=cache)

    item_instance = item_extractor.model_instance
    variant_instance = variant_extractor.model_instance
    preview_instance = preview_extractor.model_instance

    for var_id in identifiers:
        found_var_id = VariantIdentifier.objects.filter(identifier=var_id).first()

        if found_var_id is not None:
            logger.debug(f'Found variant by id {var_id}: {found_var_id.variant.id}')

            found_variant = found_var_id.variant

            for field in variant_extractor.non_null_fields:
                setattr(found_variant, field, getattr(variant_instance, field, None))

            variant = found_variant
            item = variant.item

            break
    else:
        logger.debug('Didn\'t find any variants by any of the extracted ids')

        item = PreviewsworldItemParsePerformer.get_common_item(soup, identifiers)

        if item is None:
            item = item_instance

            logger.debug('Publisher id: ' + str(publisher_id))
            logger.debug('Category id: ' + str(category_id))

            try:
                item.publisher = item.publisher or Publisher.objects.get(id=publisher_id)
            except Publisher.DoesNotExist:
                item.publisher = None

            try:
                item.category = item.category or Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                item.category = None

            item.save()

        variant = variant_instance
        variant.item = item

    variant.save()

    preview_instance.variant = variant
    preview_instance.session_id = session_id
    preview_instance.save()

    for identifier in identifiers:
        try:
            VariantIdentifier.objects.create(identifier=identifier, variant=variant)
        except IntegrityError:
            continue

    logger.info('Parsed preview: %d' % preview_instance.id)

    return {
        'item_id': item.id,
        'variant_id': variant.id,
        'preview_id': preview_instance.id,
    }


@app.task(name='parsers.prwld.finish', ignore_result=True)
def finish(results, session_id):
    try:
        session = ParseSession.objects.get(pk=session_id)
        session.status = 'finished'
        session.finished = datetime.now()
        session.save()
    except ParseSession.DoesNotExist:
        pass
