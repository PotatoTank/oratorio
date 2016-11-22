"""
Django settings for oratorio project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Try to get variables from secret_settings.py. If that fails, check if they
# exist as enviromental variables.
try:
    from coach.secret_settings import *
except ImportError:
    try:
        SECRET_KEY = os.environ["SECRET_KEY"]
        ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split()
        WATSON_USER_NAME = os.environ["WATSON_USER_NAME"]
        WATSON_PASSWORD = os.environ["WATSON_PASSWORD"]
        SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ["SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"]
    except KeyError:
        print("Please create a secret_settings.py file following instructions from secret_settings.py.template")

# Key for Google authentication
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '829611170519-u2fu8nis9unm4nvlmfdcuhiqod9rsbuh.apps.googleusercontent.com'

AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ROOT_URLCONF = 'coach.urls'

INSTALLED_APPS = [
    'coach.apps.CoachConfig',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django_nose',
    #'social.apps.django_app.default',
    #'django.contrib.contenttypes.models.ContentType',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
    },
]

WSGI_APPLICATION = 'coach.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

COACH_ROOT = os.path.join(BASE_DIR, 'coach')

DATA_UPLOAD_MAX_MEMORY_SIZE = None

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=coach',
]
