import pprint
import logging
import urllib.request
import urllib.request
import urllib.error
import json
import mimetypes
import uuid

from django.utils.module_loading import import_string

from .utils import Backend
from .app_settings import app_settings

logger = logging.getLogger(__name__)



class UrllibBackend(Backend):
    def send(self, url, message_data, **kwargs):
        # Extract 'files' from message_data, if any
        files = message_data.pop('files', None)

        if files:
            # Handle multipart/form-data request
            body, content_type = self.encode_multipart_formdata(message_data, files)
            headers = {'Content-Type': content_type}
            req = urllib.request.Request(url, data=body, headers=headers)
        else:
            # Handle JSON data
            data = json.dumps(message_data).encode('utf-8')
            headers = {'Content-Type': 'application/json'}
            req = urllib.request.Request(url, data=data, headers=headers)

        try:
            r = urllib.request.urlopen(req)
            result = r.read().decode('utf-8')
            content_type = r.headers.get('Content-Type') or r.headers.get('content-type')
            return self.validate(content_type, result, message_data)
        except urllib.error.HTTPError as e:
            # Handle HTTP errors
            result = e.read().decode('utf-8')
            content_type = e.headers.get('Content-Type') or e.headers.get('content-type')
            return self.validate(content_type, result, message_data)
        except Exception as e:
            # Handle other exceptions
            raise e

    def encode_multipart_formdata(self, fields, files, boundary=None):
        """
        Encode fields and files for multipart/form-data.

        :param fields: Dictionary of form fields.
        :param files: Dictionary of files. Format: {fieldname: (filename, file_object)}
        :param boundary: Boundary string for separating parts.
        :return: (body, content_type)
        """
        boundary = boundary or uuid.uuid4().hex
        boundary_bytes = boundary.encode('utf-8')
        crlf = b'\r\n'
        body = []

        # Fields
        for key, value in fields.items():
            body.append(b'--' + boundary_bytes)
            body.append(('Content-Disposition: form-data; name="{}"'.format(key)).encode('utf-8'))
            body.append(b'')
            body.append(str(value).encode('utf-8'))

        # Files
        for key, file_tuple in files.items():
            filename, file_object = file_tuple
            if hasattr(file_object, 'seek'):
                file_object.seek(0)
            file_content = file_object.read()
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            body.append(b'--' + boundary_bytes)
            body.append(('Content-Disposition: form-data; name="{}"; filename="{}"'.format(key, filename)).encode('utf-8'))
            body.append(('Content-Type: {}'.format(content_type)).encode('utf-8'))
            body.append(b'')
            if isinstance(file_content, str):
                body.append(file_content.encode('utf-8'))
            else:
                body.append(file_content)

        body.append(b'--' + boundary_bytes + b'--')
        body.append(b'')
        body_bytes = crlf.join(body)
        content_type = 'multipart/form-data; boundary={}'.format(boundary)
        return body_bytes, content_type



class RequestsBackend(Backend):
    def __init__(self):
        # Lazily import to avoid dependency
        import requests

        self.session = requests.Session()

    def send(self, url, message_data, **kwargs):
        if kwargs.get('files'):
            r = self.session.post(url, json=message_data, files=kwargs['files'])
        else:
            r = self.session.post(url, json=message_data)

        return self.validate(r.headers['Content-Type'], r.text, message_data)


class ConsoleBackend(Backend):
    def send(self, url, message_data, **kwargs):
        print("I: Discord message:")
        pprint.pprint(message_data, indent=4)
        print("-" * 79)


class LoggerBackend(Backend):
    def send(self, url, message_data, **kwargs):
        logger.info(pprint.pformat(message_data, indent=4))


class DisabledBackend(Backend):
    def send(self, url, message_data, **kwargs):
        pass


class CeleryBackend(Backend):
    def __init__(self):
        # Lazily import to avoid dependency
        from .tasks import send

        self._send = send

        # Check we can import our specified backend up-front
        import_string(app_settings.BACKEND_FOR_QUEUE)()

    def send(self, *args, **kwargs):
        # Send asynchronously via Celery
        self._send.delay(*args, **kwargs)


class TestBackend(Backend):
    """
    This backend is for testing.

    Before a test, call `reset_messages`, and after a test, call
    `retrieve_messages` for a list of all messages that have been sent during
    the test.
    """

    def __init__(self, *args, **kwargs):
        super(TestBackend, self).__init__(*args, **kwargs)
        self.reset_messages()

    def send(self, url, message_data, **kwargs):
        self.messages.append(message_data)

    def reset_messages(self):
        self.messages = []

    def retrieve_messages(self):
        messages = self.messages
        self.reset_messages()
        return messages


# For backwards-compatibility
Urllib2Backend = UrllibBackend
