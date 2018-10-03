# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig
from scheduled_job_client.utils import init_job_client


class ScheduledJobClientConfig(AppConfig):
    name = 'scheduled_job_client'

    def ready(self):
        init_job_client()
