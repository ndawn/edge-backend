import sentry_sdk
import yadisk
from sentry_sdk.integrations.django import DjangoIntegration
import cloudinary
import boto3


SENTRY_TOKEN = '5207adab9158436aa1094dd5379754c86d6b8d73038b4b019ba477397b62eda8'
SENTRY = sentry_sdk.init(
    dsn='https://9775ff8505674df69cb1c647078c7a26@sentry.io/1364522',
    integrations=[DjangoIntegration()]
)

DB = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'edgecomics',
    'HOST': '127.0.0.1',
    'PORT': '5432',
    'USER': 'www',
    'PASSWORD': 'www',
}

SECRET_KEY = 'rjxa=x3dp_ci4e3-w$f@suqw**2$0xyb!etc2c$d@chg3)g8bd'

SITE_ADDRESS = 'http://edgecomics.loc'

ALLOWED_HOSTS = ['*']

DEBUG = True

SESSION_COOKIE_SECURE = False

VK_ACCESS_TOKEN = '0cf62b46642e7e8eb52a33979ad74f57728469ac6211071c10236b25f4780e3a7e66c35afe3ec455969c5'
VK_API_VERSION = '5.74'

CLOUDINARY_CLOUD_NAME = 'edgecomics'
CLOUDINARY_API_KEY = '761131635936262'
CLOUDINARY_API_SECRET = '4onGOzNsO_dFQmQayA-EDIoWoPw'
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

PREVIEWSWORLD_HOSTNAME = 'https://previewsworld.com'
PREVIEWSWORLD_CATALOG_URL = PREVIEWSWORLD_HOSTNAME + '/Catalog/'

MIDTOWNCOMICS_HOSTNAME = 'https://midtowncomics.com'

YADISK_CLIENT_ID = '4e67ab47e0584cc4a7c4f9e87e5cf7d2'
YADISK_CLIENT_SECRET = '467251eaa7164cfca56fd1a9e9f726de'
YADISK_REFRESH_TOKEN = '1:yv0S82tFv9kqmwL3:mZGMei5pCAUETxJldRduHrLz7InUJ5nJcYUO_iapvsWBYpeLl7En:bbnrpn9qE_5HooYsDbcgOQ'
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
