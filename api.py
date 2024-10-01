import io
import json

from .app_settings import app_settings
from .utils import get_backend


def discord_message(
        webhook_url,
        payload=None,
        level_name=None,
        fail_silently=None,
        **kwargs,
):
    COLORS = {
        "CRITICAL": 14362664,  # Red
        "ERROR": 14362664,
        "WARNING": 16497928,  # Yellow
        "INFO": 2196944,  # Blue
        "DEBUG": 6559689,  # Gray
    }
    backend = get_backend(name=kwargs.pop('backend', None))

    if fail_silently is None:
        fail_silently = app_settings.FAIL_SILENTLY

    text = payload.get('text', '')
    subject = payload.get('title', '')
    level_color = COLORS.get(level_name, 2040357)

    # Prepare the embed
    embed = {
        "title": subject,
        "description": f"```{text[:4000]}```",  # Embed description limit is 4096
        "color": level_color,
    }

    # Check if the text exceeds Discord's embed description limit
    if len(text) > 4000:
        # Truncate the description and indicate that it's truncated
        embed["description"] = f"```{text[:3900]}... (truncated)```"

        # Attach the full error details as a file
        file = io.BytesIO(text.encode())
        files = {
            'file': ('error_details.txt', file)
        }
        # When sending files, use 'payload_json' and 'files'
        data = {
            "payload_json": json.dumps({
                "username": app_settings.BOT_USERNAME,
                "embeds": [embed],
            })
        }
        # Send the message
        try:
            return backend.send(webhook_url, data, files=files, **kwargs)
        except Exception:
            if not fail_silently:
                raise
    else:
        # No need to attach a file
        data = {
            "username": app_settings.BOT_USERNAME,
            "embeds": [embed],
        }
        # Send the message
        try:
            return backend.send(webhook_url, data, **kwargs)
        except Exception:
            if not fail_silently:
                raise
