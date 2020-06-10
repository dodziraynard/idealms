from django.contrib.staticfiles.handlers import StaticFilesHandler
import sys
import os

from django.core.wsgi import get_wsgi_application

path = '/home/lms/lms'
if path not in sys.path:
	sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')

application = StaticFilesHandler(get_wsgi_application())

# import os
# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')

# application = get_wsgi_application()
