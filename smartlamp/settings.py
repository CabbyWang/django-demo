"""
Django settings for smartlamp project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import os
import sys
import datetime

from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
sys.path.insert(0, os.path.join(BASE_DIR, 'extra_apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0fpucpcxy=*zy&8&mmv$5l+i9t7z&df1afz(4dr)(m2ne^&xhw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'user.User'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'DjangoUeditor',
    'corsheaders',
    'base.apps.BaseConfig',
    'hub.apps.HubConfig',
    'lamp.apps.LampConfig',
    'asset.apps.AssetConfig',
    'notify.apps.NotifyConfig',
    'policy.apps.PolicyConfig',
    'projectinfo.apps.ProjectinfoConfig',
    'setting.apps.SettingConfig',
    'report.apps.ReportConfig',
    'user.apps.UserConfig',
    'workorder.apps.WorkorderConfig',
    'django_filters',
    'xadmin',
    'crispy_forms',
    'reversion',
    'rest_framework'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smartlamp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'smartlamp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "smartlamp",
        "USER": "root",
        "PASSWORD": "smartlamp",
        "HOST": "localhost",
        # "HOST": "127.0.0.1",
        "PORT": "3315",
        # 'ATOMIC_REQUESTS': True,  # wrap each request in a transaction
        'OPTIONS': {
            # 'init_command': 'SET storage_engine=INNODB;'
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh_hans'  # 中文支持，django1.8以后支持；1.8以前是zh-cn

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


AUTHENTICATION_BACKENDS = (
    'user.auth.CustomBackend',
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

# JWT
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': 'jwt',            # token放在cookie中
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'user.jwt.jwt_response_payload_handler'
}

# 手机号码正则表达式
REGEX_MOBILE = '^1[3|5|8|4|7][0-9]{9}$'

# 提示修改密码时间间隔
MODIFY_PSW_INTERVAL = datetime.timedelta(days=0.01)

# 默认密码
DEFAULT_PASSWORD = '12345678'

# 翻译路径
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

LANGUAGES = (
    ('en', _('English')),
    ('zh-Hans', _('中文简体')),
)

LOGGING = {}

# CORS
CORS_ORIGIN_ALLOW_ALL = True

CRONJOBS = [

    # ('*/5 * * * *', 'myapp.cron.my_scheduled_job'),
    #
    # # format 1
    # ('0   0 1 * *', 'myapp.cron.my_scheduled_job', '>> /tmp/scheduled_job.log'),
    #
    # # format 2
    # ('0   0 1 * *', 'myapp.cron.other_scheduled_job', ['myapp']),
    # ('0   0 * * 0', 'django.core.management.call_command', ['dumpdata', 'auth'], {'indent': 4}, '> /home/john/backups/last_sunday_auth_backup.json'),
]

ENABLE_ALERT_SMS = False
