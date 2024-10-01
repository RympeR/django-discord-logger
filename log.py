import copy
import logging

from django.conf import settings
from django.views.debug import get_exception_reporter_class

from .api import discord_message


class DiscordExceptionHandler(logging.Handler):
    """
    An exception log handler that sends log entries to a Slack channel.
    """

    def __init__(self, **kwargs):
        # Pop any kwargs that shouldn't be passed into the Slack message
        # attachment here.
        self.webhook_url = settings.DISCORD_WEBHOOK_URL
        self.kwargs = kwargs
        logging.Handler.__init__(self)

    def emit(self, record):
        try:
            # Try to get the request from the record
            request = getattr(record, 'request', None)

            # Determine if the IP is internal or external
            if request:
                internal = (
                    'internal'
                    if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                    else 'EXTERNAL'
                )
                # url = request.build_absolute_uri()
            else:
                internal = 'EXTERNAL'
#                 url = ''

            # Build the subject/title
            subject = f'{record.levelname} ({internal} IP): {record.getMessage()}'

            # Copy the record to avoid modifying the original
            no_exc_record = copy.copy(record)
            no_exc_record.exc_info = None
            no_exc_record.exc_text = None

            # Get the traceback text
            if record.exc_info:
                exc_info = record.exc_info
            else:
                exc_info = (None, record.getMessage(), None)

            reporter = get_exception_reporter_class(request)(request, is_email=True, *exc_info)

            try:
                tb = reporter.get_traceback_text()
            except Exception:
                tb = "(An exception occurred when getting the traceback text)"
                if reporter.exc_type:
                    tb = (
                        f"{reporter.exc_type.__name__} (An exception occurred when rendering the "
                        "traceback)"
                    )

            # Prepare the message (you can customize this as needed)
            message = f"{self.format(no_exc_record)}\n\n{tb}"

            # Send the message to Discord
            self.send_message(
                self.webhook_url,
                payload={'title': subject, 'text': message},
                level_name=record.levelname
            )

        except Exception:
            self.handleError(record)

    def send_message(self, webhook_url, payload=None, level_name=None, **kwargs):
        """
        Send a message to the Discord webhook.
        """
        return discord_message(
            webhook_url=webhook_url,
            payload=payload,
            level_name=level_name,
            **kwargs
        )

    def handleError(self, record):
        """
        Handle errors which occur during an emit() call.
        """
        logging.getLogger('django').error('Failed to send log to Discord', exc_info=True)