import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "http_email_backend_project.settings")

application = get_asgi_application()
