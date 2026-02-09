import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'menu',
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

ROOT_URLCONF = 'config.urls'

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
                'menu.context_processors.cart_context',
                'menu.context_processors.restaurant_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# معلومات المطعم
RESTAURANT_NAME = os.getenv('RESTAURANT_NAME', 'So Bnin')
RESTAURANT_PHONE = os.getenv('RESTAURANT_PHONE', '+212600000000')
RESTAURANT_WHATSAPP = os.getenv('RESTAURANT_WHATSAPP', '+212600000000')
RESTAURANT_ADDRESS = os.getenv('RESTAURANT_ADDRESS', 'مراكش، المغرب')
RESTAURANT_MAPS = os.getenv('RESTAURANT_MAPS', 'https://maps.google.com')

# إعدادات Jazzmin للوحة التحكم
JAZZMIN_SETTINGS = {
    "site_title": "So Bnin Admin",
    "site_header": "So Bnin",
    "site_brand": "So Bnin",
    "welcome_sign": "مرحباً بك في لوحة تحكم So Bnin",
    "copyright": "So Bnin Restaurant",
    "search_model": ["menu.MenuItem"],
    "topmenu_links": [
        {"name": "الموقع", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "menu.Category": "fas fa-layer-group",
        "menu.MenuItem": "fas fa-utensils",
        "menu.Order": "fas fa-shopping-bag",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": None,
    "navbar": "navbar-dark",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "accent": "accent-warning",
    "brand_colour": "navbar-warning",
}
