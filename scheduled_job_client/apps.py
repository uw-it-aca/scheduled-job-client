# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from django.apps import AppConfig
from scheduled_job_client.utils import init_job_client


logger = logging.getLogger(__name__)


class ScheduledJobClientConfig(AppConfig):
    name = 'scheduled_job_client'

    def ready(self):
        logger.debug('init_job_client')
        init_job_client()
