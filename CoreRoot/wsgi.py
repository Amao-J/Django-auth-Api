import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoreRoot.settings')

application = get_wsgi_application()

app = application
