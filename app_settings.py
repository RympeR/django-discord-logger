from django.conf import settings



def setting(suffix, default):
    @property
    def fn(self):
        return getattr(settings, 'DISCORD_{}'.format(suffix), default)

    return fn


class AppSettings(object):
    DEFAULT_BACKEND = (
        'django_discord_logger.backends.DisabledBackend'
        if settings.DEBUG
        else 'django_discord_logger.backends.UrllibBackend'
    )

    BOT_USERNAME = setting('BOT_USERNAME', None)
    ICON_EMOJI = setting('ICON_EMOJI', None)

    ENDPOINT_URL = setting('WEBHOOK_URL', settings.DISCORD_WEBHOOK_URL)

    BACKEND = setting('BACKEND', DEFAULT_BACKEND)
    BACKEND_FOR_QUEUE = setting('BACKEND_FOR_QUEUE', DEFAULT_BACKEND)

    FAIL_SILENTLY = setting('FAIL_SILENTLY', False)


app_settings = AppSettings()
