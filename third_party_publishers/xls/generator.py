import locale
from datetime import datetime

from commerce.models import Publisher, Category
from parsers.models import ParseSession
from previews.models import Preview
from utils.google import get_service


def generate(session_id, publishers=None, categories=None, filename=None):
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

    columns = {
        'Наименование': 'preview.variant.title',
        'Наличие': '0',
        'Вход': 'preview.price_map.bought',
        'Цена': 'preview.price_map.discount',
        'Ссылка': 'preview.variant.cover.full',
        'Вес': 'preview.variant.weight',
        'Старая': 'preview.variant.price',
        'Дата выхода': 'preview.release_date.strftime("%-d %B %Y")',
        'Описание': 'preview.variant.item.description',
    }

    keys = list(columns.keys())

    session = ParseSession.objects.get(pk=session_id)
    publishers = publishers or Publisher.objects.all()
    categories = categories or Category.objects.all()

    session_date = datetime.fromisoformat(session.meta['date']).strftime('%B %Y')

    if filename is None:
        filename = f'Предзаказы {session_date}'

    service = get_service()

    workbook = service.spreadsheets().create(
        body={
            'properties': {
                'title': filename,
            },
        },
    ).execute()

    batches = [(pub, cat) for pub in publishers for cat in categories]

    for publisher, category in batches:
        previews = Preview.objects.filter(
            variant__item__publisher=publisher,
            variant__item__category=category,
        )

        if not previews.exists():
            continue

        sheet_name = f'{category.name} {publisher.short_name}'

        sheet = service.spreadsheets().batchUpdate(
            spreadsheetId=workbook['spreadsheetId'],
            body={
                'requests': [
                    {
                        'addSheet': {
                            'properties': {
                                'title': sheet_name,
                            },
                        },
                    },
                ],
            },
        ).execute()['replies'][0]['addSheet']

        values = [
            [sheet_name],
            [''] + keys,
        ]

        for preview in previews:
            row = ['']

            for key in keys:
                row.append(eval(columns[key]))

            values.append(row)

        range_name = f"'{sheet_name}'!A1:{chr(65 + len(keys))}{len(values)}"

        service.spreadsheets().values().update(
            spreadsheetId=workbook['spreadsheetId'],
            valueInputOption='RAW',
            range=range_name,
            body={
                'values': values,
            },
        ).execute()

        print(sheet)

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=workbook['spreadsheetId'],
            body={
                'requests': [
                    {
                        'autoResizeDimensions': {
                            'dimensions': {
                                'sheetId': sheet['properties']['sheetId'],
                                'dimension': 'COLUMNS',
                                'startIndex': 0,
                                'endIndex': len(keys),
                            },
                        },
                    },
                ],
            },
        ).execute()

    service.spreadsheets().batchUpdate(
        spreadsheetId=workbook['spreadsheetId'],
        body={
            'requests': [
                {
                    'deleteSheet': {
                        'sheetId': 0,
                    },
                },
            ],
        },
    ).execute()

    return workbook['spreadsheetUrl']
