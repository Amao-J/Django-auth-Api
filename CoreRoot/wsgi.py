
import os



from django.core.wsgi import get_wsgi_application

project_home = 'Django-auth-Api/CoreRoot'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoreRoot.settings')
application = get_wsgi_application()
