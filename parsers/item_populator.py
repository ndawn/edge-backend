import datetime

from django.db import IntegrityError
from django.db.models import Q
from commerce.models import PriceMap, Publisher, Item, Variant, VariantIdentifier
from edge import config

import requests
from bs4 import BeautifulSoup, SoupStrainer
import cloudinary
import cloudinary.uploader


def populate(start_from=0):
    glob_item = None
    glob_variant = None

    current_i = -1

    sitemap = BeautifulSoup(requests.get('https://previewsworld.com/sitemap.xml').content, 'xml')

    catalog_links = reversed([x.text for x in sitemap.find_all('loc') if 'Catalog' in x.text])

    loc_strainer = SoupStrainer('loc')

    for catalog_link in catalog_links:
        print(f'[CATALOG: {catalog_link}]')

        catalog = requests.get(catalog_link)

        link_elements = BeautifulSoup(catalog.content, 'xml', parse_only=loc_strainer).children

        for link_element in link_elements:
            current_i += 1

            if current_i < start_from:
                continue

            link = link_element.text

            response = requests.get(link)

            page = BeautifulSoup(response.content, 'lxml').select_one('#PageContent')

            if page.select_one('.CatalogFullDetail') is None:
                print(f'[-] {link}')
                continue

            print(f'[+] {link}')

            extracted = {
                'identifiers': [
                    response.url[response.url.rindex('/') + 1:],
                    *[x.url[x.url.rindex('/') + 1:] for x in response.history],
                ],
            }

            print(f'Ids found: {", ".join(extracted["identifiers"])}')

            # TITLE
            attribute_buffer = page.select_one('.Title')
            extracted['title'] = attribute_buffer.text if attribute_buffer is not None else ''

            # PUBLISHER
            attribute_buffer = page.select_one('.Publisher')
            extracted['publisher'] = attribute_buffer.text if attribute_buffer is not None else None

            # COVER
            attribute_buffer = page.select_one('#MainContentImage').get('src')
            extracted['cover_origin'] = f'https://previewsworld.com{attribute_buffer}' if attribute_buffer is not None else None

            # RELEASE DATE
            try:
                attribute_buffer = page.select_one('.ReleaseDate')
                extracted['release_date'] = datetime.datetime.strptime(attribute_buffer.text, 'In Shops: %b %d, %Y') if attribute_buffer is not None else None
            except ValueError:
                extracted['release_date'] = None

            # PRICE
            attribute_buffer = page.select_one('.SRP')
            attribute_buffer = attribute_buffer.text if attribute_buffer is not None else ''
            extracted['price_origin'] = float(attribute_buffer[attribute_buffer.index('$') + 1:]) if '$' in attribute_buffer else 0.0

            # DESCRIPTION
            description = page.select_one('.Text')

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
                attribute_buffer.extract()

            attribute_buffer = description.select_one('.SRP')
            if attribute_buffer is not None:
                attribute_buffer.extract()

            extracted['description'] = []

            for line in description.strings:
                string = line.replace('\xa0', '').strip()

                if string:
                    extracted['description'].append(string)

            extracted['description'] = '\n'.join(extracted['description'])

            # =======================================================================

            for extracted_var_id in extracted['identifiers']:
                var_query = VariantIdentifier.objects.filter(name=extracted_var_id)

                if var_query.exists():
                    print(f'Found variant by id {extracted_var_id}: {var_query[0].variant.id}')

                    variant = var_query[0].variant

                    price_map_query = PriceMap.objects.filter(usd=extracted['price_origin'], mode='monthly')

                    if price_map_query.exists():
                        price_map = price_map_query[0]
                    else:
                        price_map = PriceMap.dummy()

                    # TITLE
                    variant.title = extracted['title']
                    variant.origin_title = extracted['title']

                    # PRICE & WEIGHT
                    variant.bought = price_map.bought
                    variant.price = price_map.default
                    variant.weight = price_map.weight
                    variant.stock_quantity = 0

                    # PUBLISHER
                    if variant.item.publisher is None and extracted['publisher'] is not None:
                        publisher = Publisher.objects.filter(Q(full_name__iexact=extracted['publisher']) | Q(short_name__iexact=extracted['publisher']) | Q(abbreviature__iexact=extracted['publisher']))
                        if publisher.exists():
                            variant.item.publisher = publisher[0]
                        else:
                            variant.item.publisher = Publisher.objects.create(full_name=extracted['publisher'].title())

                    # COVER
                    try:
                        image_data = cloudinary.uploader.upload(
                            extracted['cover_origin'],
                            folder='cover',
                            phash=True,
                            config=config.CLOUDINARY_CONFIG,
                        )

                        phash_distance = int(image_data['phash'], base=16) ^ int(config.DUMMY['prwld']['phash'], base=16)
                        phash_identity = 1 - bin(phash_distance).count('1') / 64

                        if phash_identity > 0.9:
                            cloudinary.uploader.destroy(image_data['public_id'], config=config.CLOUDINARY_CONFIG)
                            variant.cover = None
                        else:
                            variant.cover = image_data['public_id']
                    except cloudinary.api.Error:
                        variant.cover = None

                    variant.item.save()
                    variant.save()

                    glob_variant = variant
                    glob_item = variant.item

                    break
            else:
                print('Didn\'t find any variants by any of the extracted ids')

                series_btn = page.select_one('.ViewSeriesItemsLink')

                if series_btn is not None:
                    print('Found series link')

                    response = requests.get(f'https://previewsworld.com{series_btn.get("href")}')
                    series_page = BeautifulSoup(response.content, 'lxml').select_one('.CatalogFullDetail')

                    for extracted_var_id in extracted['identifiers']:
                        if series_page is None:
                            continue

                        issue_number_element = series_page(text=extracted_var_id)

                        if issue_number_element is not None and len(issue_number_element) > 0:
                            issue_number = issue_number_element[0].parent.parent.previous.previous.strip(' VAR')

                            break
                    else:
                        issue_number = None

                    if issue_number is not None:
                        variants = series_page(text=issue_number) + series_page(text=issue_number + ' VAR')
                    else:
                        variants = []

                    params = {}

                    for variant in variants:
                        identifier = variant.next.next.text

                        if identifier in extracted['identifiers']:
                            continue

                        var_query = VariantIdentifier.objects.filter(name=identifier)

                        if var_query.exists():
                            print(f'Found common item with variant {var_query[0].variant.id}: {var_query[0].variant.item.id}')

                            glob_variant = var_query[0].variant
                            glob_item = glob_variant.item

                            break
                    else:
                        print('Didn\'t find any variants with common item')

                        glob_item = Item.objects.create(
                            title=extracted['title'],
                            origin_title=extracted['title'],
                            description=extracted['description'],
                        )

                        price_map_query = PriceMap.objects.filter(usd=extracted['price_origin'], mode='monthly')

                        if price_map_query.exists():
                            price_map = price_map_query[0]
                        else:
                            price_map = PriceMap.dummy()

                        # TITLE
                        params['title'] = params['origin_title'] = extracted['title']

                        # PRICE & WEIGHT
                        params['bought'] = price_map.bought
                        params['price'] = price_map.default
                        params['weight'] = price_map.weight
                        params['stock_quantity'] = 0

                        # COVER
                        try:
                            image_data = cloudinary.uploader.upload(
                                extracted['cover_origin'],
                                folder='cover',
                                phash=True,
                                config=config.CLOUDINARY_CONFIG,
                            )

                            phash_distance = int(image_data['phash'], base=16) ^ int(config.DUMMY['prwld']['phash'], base=16)
                            phash_identity = 1 - bin(phash_distance).count('1') / 64

                            if phash_identity > 0.9:
                                cloudinary.uploader.destroy(image_data['public_id'], config=config.CLOUDINARY_CONFIG)
                                params['cover'] = None
                            else:
                                params['cover'] = image_data['public_id']
                        except cloudinary.api.Error:
                            params['cover'] = None

                        # PUBLISHER
                        if glob_item.publisher is None and extracted['publisher'] is not None:
                            publisher = Publisher.objects.filter(Q(full_name__iexact=extracted['publisher']) | Q(short_name__iexact=extracted['publisher']) | Q(abbreviature__iexact=extracted['publisher']))
                            if publisher.exists():
                                glob_item.publisher = publisher[0]
                            else:
                                glob_item.publisher = Publisher.objects.create(full_name=extracted['publisher'].title())

                        glob_variant = Variant.objects.create(item=glob_item, **params)
                else:
                    glob_item = Item.objects.create(
                        title=extracted['title'],
                        origin_title=extracted['title'],
                        description=extracted['description'],
                    )

                    # PUBLISHER
                    if glob_item.publisher is None and extracted['publisher'] is not None:
                        publisher = Publisher.objects.filter(Q(full_name__iexact=extracted['publisher']) | Q(
                            short_name__iexact=extracted['publisher']) | Q(
                            abbreviature__iexact=extracted['publisher']))
                        if publisher.exists():
                            glob_item.publisher = publisher[0]
                        else:
                            glob_item.publisher = Publisher.objects.create(full_name=extracted['publisher'].title())

                    price_map_query = PriceMap.objects.filter(usd=extracted['price_origin'], mode='monthly')

                    if price_map_query.exists():
                        price_map = price_map_query[0]
                    else:
                        price_map = PriceMap.dummy()

                    params = {}

                    # TITLE
                    params['title'] = params['origin_title'] = extracted['title']

                    # PRICE & WEIGHT
                    params['bought'] = price_map.bought
                    params['price'] = price_map.default
                    params['weight'] = price_map.weight
                    params['stock_quantity'] = 0

                    # COVER
                    try:
                        image_data = cloudinary.uploader.upload(
                            extracted['cover_origin'],
                            folder='cover',
                            phash=True,
                            config=config.CLOUDINARY_CONFIG,
                        )

                        phash_distance = int(image_data['phash'], base=16) ^ int(config.DUMMY['prwld']['phash'],
                                                                                 base=16)
                        phash_identity = 1 - bin(phash_distance).count('1') / 64

                        if phash_identity > 0.9:
                            cloudinary.uploader.destroy(image_data['public_id'], config=config.CLOUDINARY_CONFIG)
                            params['cover'] = None
                        else:
                            params['cover'] = image_data['public_id']
                    except cloudinary.api.Error:
                        params['cover'] = None

                    # PUBLISHER
                    if glob_item.publisher is None and extracted['publisher'] is not None:
                        publisher = Publisher.objects.filter(Q(full_name__iexact=extracted['publisher']) | Q(
                            short_name__iexact=extracted['publisher']) | Q(
                            abbreviature__iexact=extracted['publisher']))
                        if publisher.exists():
                            glob_item.publisher = publisher[0]
                        else:
                            glob_item.publisher = Publisher.objects.create(full_name=extracted['publisher'].title())

                    glob_variant = Variant.objects.create(item=glob_item, **params)

                for identifier in extracted['identifiers']:
                    try:
                        VariantIdentifier.objects.create(name=identifier, variant=glob_variant)
                    except IntegrityError:
                        continue
