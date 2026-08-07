# http_email_backend

`http_email_backend` is a Django email backend for projects that cannot (or should not) send SMTP traffic directly from the application server.

Instead of opening an SMTP connection itself, it sends a single HTTP `POST` request to an email proxy service you control. The proxy service is then responsible for relaying the message via SMTP (or any delivery method it implements).

This is useful when:

- the application runs in a restricted network or container that cannot reach an SMTP server directly
- outbound SMTP ports are blocked by your hosting provider or cloud firewall
- you want to centralize email delivery behind a proxy, queue, or gateway service
- you need a single HTTP hop from Django to a service that already knows how to talk to SMTP

## Installation

```bash
pip install http_email_backend
```

## Django settings

Set the backend and its connection settings in `settings.py`:

```python
EMAIL_BACKEND = "http_email_backend.HttpProxyEmailBackend"

# Forwarded to the proxy as the SMTP config it should use for delivery
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
EMAIL_TIMEOUT = (
    int(os.getenv("EMAIL_TIMEOUT")) if os.getenv("EMAIL_TIMEOUT") else None
)
EMAIL_SSL_KEYFILE = os.getenv("EMAIL_SSL_KEYFILE", None)
EMAIL_SSL_CERTFILE = os.getenv("EMAIL_SSL_CERTFILE", None)

# Proxy-specific settings, required by this backend
EMAIL_REQUEST_URL = os.getenv("EMAIL_REQUEST_URL")
EMAIL_REQUEST_API_KEY = os.getenv("EMAIL_REQUEST_API_KEY")
EMAIL_REQUEST_TOKEN_TYPE = os.getenv("EMAIL_REQUEST_TOKEN_TYPE", "Bearer")
EMAIL_FAIL_SILENTLY = os.getenv("EMAIL_FAIL_SILENTLY", "False").lower() == "true"
```

### Required settings

| Setting                 | Description                                  |
| ----------------------- | -------------------------------------------- |
| `EMAIL_REQUEST_URL`     | HTTP endpoint that accepts the email payload |
| `EMAIL_REQUEST_API_KEY` | API key sent in the `Authorization` header   |

The backend raises `ImproperlyConfigured` on import, and `ValueError` on instantiation, if either of these is missing.

### Optional settings

| Setting                    | Default    | Description                                                        |
| -------------------------- | ---------- | ------------------------------------------------------------------ |
| `EMAIL_REQUEST_TOKEN_TYPE` | `"Bearer"` | Prefix used in the `Authorization` header, e.g. `Bearer <api_key>` |
| `EMAIL_FAIL_SILENTLY`      | `False`    | If `True`, request failures are swallowed instead of raised        |

### SMTP-style settings

These are not used to open an SMTP connection locally — they are forwarded to your proxy as part of the JSON payload, so the proxy knows how to deliver the message:

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `EMAIL_TIMEOUT`
- `EMAIL_SSL_KEYFILE`
- `EMAIL_SSL_CERTFILE`

`EMAIL_USE_TLS` and `EMAIL_USE_SSL` are mutually exclusive; setting both raises a `ValueError`.

The sender address included in the payload is taken from `EMAIL_HOST_USER`.

## How it works

When Django sends an email, this backend:

1. Collects the message(s) — recipients, subject, plain-text/HTML body, headers, and attachments.
2. Skips any message with no recipients.
3. Builds a JSON payload containing the SMTP-style config and the message data.
4. Sends the payload with an HTTP `POST` request to `EMAIL_REQUEST_URL`, authenticated with `Authorization: <EMAIL_REQUEST_TOKEN_TYPE> <EMAIL_REQUEST_API_KEY>`.
5. Returns the number of messages sent on success, or `0` if there was nothing to send.

If the HTML body is present, it is automatically inlined with [`premailer`](https://pypi.org/project/premailer/) before being sent, so CSS `<style>` blocks work reliably in email clients.

If the proxy request fails and `EMAIL_FAIL_SILENTLY` is `False`, the backend raises the underlying `requests` exception. If `EMAIL_FAIL_SILENTLY` is `True`, the failure is ignored and `0` messages are reported as sent.

## Usage

Once configured, use Django's mail API as usual — no code changes needed:

```python
from django.core.mail import send_mail

send_mail(
    subject="Hello",
    message="This message is sent through the HTTP proxy backend.",
    from_email="webmaster@localhost",
    recipient_list=["user@example.com"],
)
```

## Notes

- This package is only the Django-side backend. You still need a separate HTTP proxy service that receives the request and performs the actual delivery.
- It does not send mail over SMTP directly — SMTP settings are only forwarded to the proxy for it to use.
- Best suited for deployments where direct SMTP access from the app server is not possible or not desired.

## HTTP proxy service Setup

- [HttpSmtpProxy](https://github.com/PackageSphere/HttpSmtpProxy)
- [HttpSmtpProxy README](https://github.com/PackageSphere/HttpSmtpProxy/blob/master/README.md)
