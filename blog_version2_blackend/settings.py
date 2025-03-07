"""
Django settings for blog_version2_blackend project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
import environ
from pathlib import Path

# Definir la ruta base
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializar environ y leer el archivo .env
env = environ.Env(
    # Puedes definir valores por defecto y castear los valores
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Asignar las variables a las configuraciones
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = ["10.0.0.6", "localhost", "192.168.47.225", "192.168.0.105", "51.222.159.144",
                 "tucodigocotidiano.yarumaltech.com", "www.tucodigocotidiano.yarumaltech.com"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'paypal.standard.ipn',
    'payment',
    'core',
    'inicio',
    'tutoriales',
    'guias',
    'podcast',
    'suscripcion',
    'contacto',
    'login',
    'registrarse',
    'olvidar_contraseña',
    # Aplicaciones de allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.linkedin_oauth2',
    'allauth.socialaccount.providers.github',
    'perfil',
    'crear_tutoriales',
    'leer_tutoriales',
    'escuchar_podcast',
    'crear_podcast',
    'politica_privacidad',
    'terminos',

]

SITE_ID = 3

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'blog_version2_blackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'blog_version2_blackend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Configuración de la base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Configuración de redirección y allauth
LOGOUT_REDIRECT_URL = 'inicio_home'
LOGIN_REDIRECT_URL = 'http://localhost:8000'
SOCIALACCOUNT_LOGIN_REDIRECT_URL = 'http://localhost:8000'
SOCIALACCOUNT_LOGIN_ON_GET = True

# Configuración específica para los proveedores de redes sociales
SOCIALACCOUNT_PROVIDERS = {
    'linkedin_oauth2': {
        'SCOPE': ['openid', 'profile', 'email'],
        'PROFILE_FIELDS': [
            'id',
            'firstName',
            'lastName',
            'profilePicture(displayImage~:playableStreams)',
            'emailAddress',
        ],
    },
    # Aquí puedes agregar o modificar la configuración para otros proveedores si es necesario.
}
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

AUTH_USER_MODEL = 'core.Lector'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # Si usas Pathlib; alternativamente: os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CSRF_TRUSTED_ORIGINS = [
    "https://tucodigocotidiano.yarumaltech.com",
    "http://tucodigocotidiano.yarumaltech.com",
    "https://www.tucodigocotidiano.yarumaltech.com",
    "http://www.tucodigocotidiano.yarumaltech.com",
    "https://51.222.159.144",
    "http://51.222.159.144",
]

# Si usas environ:
PAYPAL_RECEIVER_EMAIL = env('PAYPAL_RECEIVER_EMAIL')
