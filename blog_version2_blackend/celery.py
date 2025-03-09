# blog_version2_blackend/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_version2_blackend.settings")

app = Celery("blog_version2_blackend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

