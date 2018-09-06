from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^logging/', include('django_client_logger.urls')),
    url(r'^', include('scheduled_job_client.urls')),
]
