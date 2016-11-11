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


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# Try to get the SECRET_KEY from secret_settings.py. If that fails, check if it
# exists as an enviromental variable.
try:
    from coach import secret_settings
    SECRET_KEY = secret_settings.SECRET_KEY
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = secret_settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
    ALLOWED_HOSTS = secret_settings.ALLOWED_HOSTS
except ImportError:
    try:
        temp = os.environ["SECRET_KEY"]
    except KeyError:
        print("Please specify SECRET_KEY either as an enviroment variable or in secret_settings.py")
    SECRET_KEY = temp

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
