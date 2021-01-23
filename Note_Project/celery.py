from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Note_Project.settings')
app = Celery('Note_Project')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'every-five-seconds': {
        'task': 'Note_App.tasks.set_reminder',
        'schedule': 5,
    }
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
