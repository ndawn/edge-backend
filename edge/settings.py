import os
from datetime import timedelta
from multiprocessing import cpu_count
from edge import config

from kombu import Queue, Exchange


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config.SECRET_KEY

DEBUG = config.DEBUG

ALLOWED_HOSTS = config.ALLOWED_HOSTS

AUTH_USER_MODEL = 'accounts.User'

AUTO_LOGOUT = 52560000


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'django_filters',
    'django_celery_results',
    'accounts.apps.AccountsConfig',
    'commerce.apps.CommerceConfig',
    'previews.apps.PreviewsConfig',
    'parsers.apps.ParsersConfig',
    'third_party_publishers.apps.ThirdPartyPublishersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'edge.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'edge.wsgi.application'


DATABASES = {
    'default': config.DB
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000


SESSION_COOKIE_AGE = 52560000


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

APPEND_SLASH = True


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}


CELERY_TASK_RESULT_EXPIRES = 86400
CELERY_TASK_DEFAULT_RATE_LIMIT = f'{300 // cpu_count()}/m'
CELERY_BROKER_URL = config.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)
CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
