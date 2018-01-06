import os

from django.core.wsgi import get_wsgi_application  # pylint: disable=wrong-import-position
from whitenoise.django import DjangoWhiteNoise  # pylint: disable=wrong-import-position

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "improve_stuff.settings")

application = get_wsgi_application()  # pylint: disable=invalid-name
application = DjangoWhiteNoise(application)  # pylint: disable=invalid-name
