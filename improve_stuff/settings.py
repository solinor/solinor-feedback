import os

import dj_database_url

RESPONSE_SHARED_SECRET = os.environ.get("RESPONSE_SHARED_SECRET")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sr_hxcfy32#fmut4x#x#8&(dc1ipqqq-gl-kww7lrmckztw8nc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", True) in (True, "True", "true")
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
ALLOWED_HOSTS = ["*"]
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", 0))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'googleauth',
    'feedback',
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

# client ID from the Google Developer Console
GOOGLEAUTH_CLIENT_ID = os.environ["GOOGLEAUTH_CLIENT_ID"]

# client secret from the Google Developer Console
GOOGLEAUTH_CLIENT_SECRET = os.environ["GOOGLEAUTH_CLIENT_SECRET"]

# your app's domain, used to construct callback URLs
GOOGLEAUTH_CALLBACK_DOMAIN = os.environ["GOOGLEAUTH_CALLBACK_DOMAIN"]

# callback URL uses HTTPS (your side, not Google), default True
GOOGLEAUTH_USE_HTTPS = os.environ.get("GOOGLEAUTH_USE_HTTPS", True) in (True, "True", "true")

# restrict to the given Google Apps domain, default None
GOOGLEAUTH_APPS_DOMAIN = os.environ["GOOGLEAUTH_APPS_DOMAIN"]

# get user's name, default True (extra HTTP request)
GOOGLEAUTH_GET_PROFILE = True

# sets value of user.is_staff for new users, default False
GOOGLEAUTH_IS_STAFF = False

# list of default group names to assign to new users
GOOGLEAUTH_GROUPS = []

AUTHENTICATION_BACKENDS = (
    'googleauth.backends.GoogleAuthBackend',
)

ROOT_URLCONF = 'improve_stuff.urls'

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

WSGI_APPLICATION = 'improve_stuff.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DB_FROM_ENV = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(DB_FROM_ENV)

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
]
