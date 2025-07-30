import os
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')
DEBUG = config('DEBUG', default=True, cast=bool)

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = os.environ.get('CELERY_ACCEPT_CONTENT', "['json']").strip("[]").replace("'", "").replace('"', '').split(',')
CELERY_ACCEPT_CONTENT = [item.strip() for item in CELERY_ACCEPT_CONTENT if item.strip()] # Clean up list
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = config('CELERY_TIMEZONE', default='Africa/Lagos')  # Nigeria timezone
CELERY_ENABLE_UTC = config('CELERY_ENABLE_UTC', default=False, cast=bool)

# Celery Beat Schedule for periodic tasks
CELERY_BEAT_SCHEDULE = {
    'process-scheduled-messages': {
        'task': 'whatsapp_automation.tasks.process_scheduled_messages',
        'schedule': config('PROCESS_SCHEDULED_MESSAGES_INTERVAL', default=300.0, cast=float),  # Run every 5 minutes by default
    },
    'cleanup-old-logs': {
        'task': 'whatsapp_automation.tasks.cleanup_old_logs',
        'schedule': config('CLEANUP_OLD_LOGS_INTERVAL', default=86400.0, cast=float),  # Run daily by default
    },
}


ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_apscheduler',
    'whatsapp_automation',  # Our main app
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

ROOT_URLCONF = 'watrhc_automation.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

DATABASE_URL_PARSER = config('DATABASE_URL')
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL_PARSER)
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Time zone
TIME_ZONE = 'Africa/Lagos'  # For Port Harcourt, Nigeria
USE_TZ = True

# APScheduler settings
SCHEDULER_CONFIG = {
    "apscheduler.jobstores.default": {
        "class": "django_apscheduler.jobstores:DjangoJobStore"
    },
    'apscheduler.executors.processpool': {
        'type': 'threadpool'
    },
}
SCHEDULER_AUTOSTART = True