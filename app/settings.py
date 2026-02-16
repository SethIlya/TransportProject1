from pathlib import Path
import platform
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-d7rlo8mw56gl(^g@bm-5uou(o9jzk*gt97re13bd*og@!z8%)_'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    # Сторонние приложения
    'rest_framework',
    'corsheaders',
    'django_q', 

    'project.apps.ProjectConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'app.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'test',
        'USER': 'sys_admin',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'

# Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# GeoDjango settings for Windows
if platform.system() == 'Windows':
    CONDA_BIN_PATH = 'C:/Users/iimin/miniconda3/Library/bin'
    if os.path.exists(CONDA_BIN_PATH):
        os.environ['PATH'] = CONDA_BIN_PATH + os.pathsep + os.environ.get('PATH', '')
        GDAL_LIBRARY_PATH = os.path.join(CONDA_BIN_PATH, 'gdal.dll') 

# Django Q settings
Q_CLUSTER = {
    'name': 'DjangORM',
    'workers': 4,  
    'timeout': 900, 
    'retry': 1200,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
}