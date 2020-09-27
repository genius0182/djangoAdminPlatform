"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "(odaf!f_qd2cspu4^_vut#29gc4s@qwm)c!m*kemop)9zvjs&&"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "rest_framework",
    "corsheaders",
    "apps.system",
    "apps.notice",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",
    "rest_framework_simplejwt.token_blacklist",
    "notifications",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "server.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
# mysql
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "djangodb",
#         "USER": "root",
#         "PASSWORD": "123456",
#         "HOST": "127.0.0.1",
#         "PORT": "3306",
#     }
# }

# postgresql12.3
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

# 缓存配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "PICKLE_VERSION": -1
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    # JWT
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "apps.system.rbac_perm.RbacPermission",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "utils.baseResponse.FitJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "utils.pagination.MyPagination",
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DATE_FORMAT": "%Y-%m-%d",
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

# drf-extensions的设置
REST_FRAMEWORK_EXTENSIONS = {
    #  'DEFAULT_OBJECT_CACHE_KEY_FUNC':
    #   'rest_framework_extensions.utils.default_object_cache_key_func',
    # 'DEFAULT_LIST_CACHE_KEY_FUNC':
    #   'rest_framework_extensions.utils.default_list_cache_key_func',
    # 过期时间  单位是秒
    "DEFAULT_CACHE_RESPONSE_TIMEOUT": 24 * 60 * 60,
    # 缓存存储
    "DEFAULT_USE_CACHE": "default",
}

# JWT配置 里面具体配置可以参考文档
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),  # 配置过期时间
    # 'REFRESH_TOKEN_LIFETIME': timedelta(days=),
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

# 跨域配置
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False

AUTH_USER_MODEL = "system.Users"
AUTHENTICATION_BACKENDS = ("apps.system.authentication.CustomBackend",)

# 日志配置
# 创建日志的路径
LOG_PATH = os.path.join(BASE_DIR, "log")
# 如果地址不存在，则自动创建log文件夹
if not os.path.join(LOG_PATH):
    os.mkdir(LOG_PATH)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # 日志格式
        "standard": {
            "format": "[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] "
                      "[%(levelname)s]- %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},  # 简单格式
    },
    # 过滤
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    # 定义具体处理日志的方式
    "handlers": {
        # 默认记录所有日志
        "default": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(
                LOG_PATH, "all-{}.log".format(datetime.now().strftime("%Y-%m-%d"))
            ),
            "maxBytes": 1024 * 1024 * 5,  # 文件大小
            "backupCount": 5,  # 备份数
            "formatter": "standard",  # 输出格式
            "encoding": "utf-8",  # 设置默认编码，否则打印出来汉字乱码
        },
        # 输出错误日志
        "error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(
                LOG_PATH, "error-{}.log".format(datetime.now().strftime("%Y-%m-%d"))
            ),
            "maxBytes": 1024 * 1024 * 5,  # 文件大小
            "backupCount": 5,  # 备份数
            "formatter": "standard",  # 输出格式
            "encoding": "utf-8",  # 设置默认编码
        },
        # 控制台输出
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        # 输出info日志
        "info": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(
                LOG_PATH, "info-{}.log".format(datetime.now().strftime("%Y-%m-%d"))
            ),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "standard",
            "encoding": "utf-8",  # 设置默认编码
        },
    },
    # 配置用哪几种 handlers 来处理日志
    "loggers": {
        # 类型 为 django 处理所有类型的日志， 默认调用
        "django": {
            "handlers": ["default", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        # log 调用时需要当作参数传入
        "log": {
            "handlers": ["error", "info", "console", "default"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
