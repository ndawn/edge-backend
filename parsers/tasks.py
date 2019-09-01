import logging
from datetime import datetime

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from commerce.models import Category, Publisher, VariantIdentifier
from parsers.previews.performers.previewsworld import Performer
from parsers.previews.extractors.previewsworld import (
    PreviewsworldItemExtractor,
    PreviewsworldVariantExtractor,
    PreviewsworldPreviewExtractor,
)
from parsers.models import ParseSession
from edge.celery import app

import requests
from bs4 import BeautifulSoup
from yadisk.exceptions import TooManyRequestsError


logger = logging.getLogger()


@app.task(
    name='parsers.prwld.parse',
    autoretry_for=(TooManyRequestsError, ),
    max_retries=5,
    default_retry_delay=1,
)
def parse_previewsworld_item(url, session_id, publisher_id=None, category_id=None):
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'lxml')

    identifiers, response = Performer.get_identifiers_and_response(response)

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

        item = Performer.get_common_item(soup, identifiers)

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


@app.task(name='parsers.prwld.finish')
def finish_previewsworld_parse(session_id):
    try:
        session = ParseSession.objects.get(pk=session_id)
        session.status = 'finished'
        session.finished = datetime.now().astimezone()
        session.save()
    except ParseSession.DoesNotExist:
        pass
