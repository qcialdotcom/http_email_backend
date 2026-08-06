"""
http_email_backend._email
========================

HTTP Proxy Email Backend for Django.

By using this send the email request by http post request on http server
and server will send the email using smtp server

Note: This will increase one network call so used when you server not
able to connect to smtp server directly.

Reference Design: SMTP backend of Django
"""

from dataclasses import asdict, dataclass, field
from typing import Any

import requests
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from premailer import transform

API_URL = getattr(django_settings, "EMAIL_REQUEST_URL", "")
API_KEY = getattr(django_settings, "EMAIL_REQUEST_API_KEY", "")
TOKEN_TYPE = getattr(django_settings, "EMAIL_REQUEST_TOKEN_TYPE", "Bearer")
FAIL_SILENTLY = getattr(django_settings, "EMAIL_FAIL_SILENTLY", False)

if not API_URL or not API_KEY:
    raise ImproperlyConfigured(
        "HttpProxyEmailBackend requires both EMAIL_REQUEST_URL and EMAIL_REQUEST_API_KEY to be set."
    )


@dataclass(slots=True)
class EmailAddress:
    email: str
    name: str | None = None


@dataclass(slots=True)
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    sender: EmailAddress
    use_tls: bool
    use_ssl: bool
    timeout: float
    ssl_keyfile: str
    ssl_certfile: str


@dataclass(slots=True)
class Attachment:
    filename: str
    content: bytes
    mimetype: str


@dataclass(slots=True)
class EmailMessage:
    to: list[EmailAddress]
    subject: str | None = None
    text_body: str | None = None
    html_body: str | None = None
    cc: list[EmailAddress] = field(default_factory=list)
    bcc: list[EmailAddress] = field(default_factory=list)
    reply_to: EmailAddress | None = None
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    attachments: list[Attachment] = field(default_factory=list)


@dataclass(slots=True)
class EmailPayload:
    smtp_config: SMTPConfig
    sender: EmailAddress
    messages: list[EmailMessage]


class HttpProxyEmailBackend(BaseEmailBackend):
    """A Django email backend that sends email requests to an HTTP proxy server"""

    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        use_tls=None,
        fail_silently=None,
        use_ssl=None,
        timeout=None,
        api_url=None,
        api_key=None,
        token_type=None,
        ssl_keyfile=None,
        ssl_certfile=None,
        **kwargs,
    ):
        super().__init__(fail_silently=fail_silently)
        self.host = host or django_settings.EMAIL_HOST
        self.port = port or django_settings.EMAIL_PORT
        self.username = (
            django_settings.EMAIL_HOST_USER if username is None else username
        )
        self.password = (
            django_settings.EMAIL_HOST_PASSWORD if password is None else password
        )
        self.use_tls = django_settings.EMAIL_USE_TLS if use_tls is None else use_tls
        self.use_ssl = django_settings.EMAIL_USE_SSL if use_ssl is None else use_ssl
        self.timeout = django_settings.EMAIL_TIMEOUT if timeout is None else timeout
        self.ssl_keyfile = (
            django_settings.EMAIL_SSL_KEYFILE if ssl_keyfile is None else ssl_keyfile
        )
        self.ssl_certfile = (
            django_settings.EMAIL_SSL_CERTFILE if ssl_certfile is None else ssl_certfile
        )

        self.api_url = api_url or API_URL
        self.api_key = api_key or API_KEY
        self.token_type = token_type or TOKEN_TYPE
        self.fail_silently = fail_silently or FAIL_SILENTLY

        if not self.api_url or not self.api_key:
            raise ValueError(
                "HttpProxyEmailBackend requires both EMAIL_REQUEST_URL and EMAIL_REQUEST_API_KEY to be set."
            )

        if self.use_ssl and self.use_tls:
            raise ValueError(
                "EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive, so only set "
                "one of those settings to True."
            )

    def send_messages(self, email_messages):
        """Email messages sender function."""

        if not email_messages:
            return 0

        messages = self._prepare_messages(email_messages)
        if not messages:
            return 0

        payload = self._prepare_payload(messages)
        sent = self._post_payload(payload)

        return len(messages) if sent else 0

    def _prepare_smtp_config(self):
        """Build the SMTPConfig portion of the payload."""

        return SMTPConfig(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            sender=EmailAddress(email=self.username),
            use_tls=self.use_tls,
            use_ssl=self.use_ssl,
            timeout=self.timeout,
            ssl_keyfile=self.ssl_keyfile,
            ssl_certfile=self.ssl_certfile,
        )

    def _prepare_messages(self, email_messages):
        """Convert Django EmailMessage objects into our EmailMessage dataclasses."""

        messages = []
        for message in email_messages:
            if not message.recipients():
                continue
            messages.append(self._prepare_message(message))
        return messages

    def _prepare_message(self, message):
        """Build a single EmailMessage dataclass from a Django EmailMessage."""

        return EmailMessage(
            to=self._prepare_addresses(message.to),
            subject=message.subject,
            text_body=self._prepare_text_body(message),
            html_body=self._prepare_html_body(message),
            cc=self._prepare_addresses(message.cc),
            bcc=self._prepare_addresses(message.bcc),
            reply_to=self._prepare_reply_to(message),
            headers=dict(message.extra_headers),
            attachments=self._prepare_attachments(message),
        )

    def _prepare_addresses(self, addresses):
        """Convert a list of raw email address strings into EmailAddress objects."""

        return [EmailAddress(email=addr) for addr in addresses]

    def _prepare_reply_to(self, message):
        """Build the reply_to EmailAddress, if any, for the given message."""

        if not message.reply_to:
            return None
        return EmailAddress(email=message.reply_to[0])

    def _prepare_text_body(self, message):
        """Resolve the plain text body from the message body/alternatives."""

        text_body = message.body if message.content_subtype == "plain" else None
        for alt_body, alt_mimetype in getattr(message, "alternatives", []):
            if alt_mimetype == "text/plain":
                text_body = alt_body
        return text_body

    def _prepare_html_body(self, message):
        """Resolve the HTML body from the message body/alternatives."""

        html_body = message.body if message.content_subtype == "html" else None
        for alt_body, alt_mimetype in getattr(message, "alternatives", []):
            if alt_mimetype == "text/html":
                html_body = alt_body

        if html_body:
            html_body = transform(
                html_body,
                keep_style_tags=True,
                remove_classes=False,
                cssutils_logging_level="CRITICAL",
            )
        return html_body

    def _prepare_attachments(self, message):
        """Convert Django's raw attachment tuples into Attachment dataclasses."""

        return [
            Attachment(
                filename=attachment[0],
                content=attachment[1],
                mimetype=attachment[2],
            )
            for attachment in getattr(message, "attachments", [])
        ]

    def _prepare_payload(self, messages):
        """Assemble the full EmailPayload to be sent to the proxy server."""

        return EmailPayload(
            smtp_config=self._prepare_smtp_config(),
            sender=EmailAddress(email=self.username),
            messages=messages,
        )

    def _post_payload(self, payload):
        """POST the payload as JSON to the proxy server. Return True on success."""

        try:
            response = requests.post(
                self.api_url,
                json=asdict(payload),
                headers={"Authorization": f"{self.token_type} {self.api_key}"},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException:
            if not self.fail_silently:
                raise
            return False
        return True
