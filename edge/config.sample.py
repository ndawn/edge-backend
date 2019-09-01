import sentry_sdk
import yadisk
from sentry_sdk.integrations.django import DjangoIntegration
import cloudinary
import boto3


SENTRY_TOKEN = ''
SENTRY = sentry_sdk.init(
    dsn='',
    integrations=[DjangoIntegration()]
)

DB = {
    'ENGINE': '',
    'NAME': '',
    'HOST': '',
    'PORT': '',
    'USER': '',
    'PASSWORD': '',
}

SECRET_KEY = ''

SITE_ADDRESS = ''

ALLOWED_HOSTS = []

DEBUG = False

SESSION_COOKIE_SECURE = True

VK_ACCESS_TOKEN = ''
VK_API_VERSION = '5.74'

CLOUDINARY_CLOUD_NAME = ''
CLOUDINARY_API_KEY = ''
CLOUDINARY_API_SECRET = ''
CLOUDINARY_COVER_FOLDER = 'cover'
CLOUDINARY_CONFIG = cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)

SIZES = {
    'xxs': 'thumb-xxs',
    'xs': 'thumb-xs',
    'sm': 'thumb-sm',
    'md': 'thumb-md',
    'lg': 'thumb-lg',
}

DUMMY = {
    'edge': {
        'id': 'dummy/dummy',
        'phash': '4897196d6cd8d32d',
    },
    'prwld': {
        'id': 'dummy/prwld_dummy',
        'phash': 'cef1fc934c80f229',
    },
    'mdtwn': {
        'id': 'dummy/mdtwn_dummy',
        'phash': '903d0cbc3170efcb',
    },
}

PHASH_IDENTITY_THRESHOLD = 0.75

YADISK_CLIENT_ID = ''
YADISK_CLIENT_SECRET = ''
YADISK_REFRESH_TOKEN = ''
YADISK_ROOT_PATH = 'disk:/'
YADISK_COVER_PATH = 'cover'

YADISK = yadisk.YaDisk(id=YADISK_CLIENT_ID, secret=YADISK_CLIENT_SECRET)
YADISK.token = YADISK.refresh_token(YADISK_REFRESH_TOKEN).access_token

YC_ENDPOINT_URL = 'https://storage.yandexcloud.net'
YC_BUCKET_NAME = 'cover'
YC_SESSION = boto3.session.Session().client(
    service_name='s3',
    endpoint_url=YC_ENDPOINT_URL,
)

CELERY_BROKER_URL = ''

GOOGLE_API_CREDENTIALS = {}
