from django.conf.urls import url
from scheduled_job_client.views.notification import JobClient


urlpatterns = [
    url(r'notification$', JobClient.as_view(), name='notification'),
]
