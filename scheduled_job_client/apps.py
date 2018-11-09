# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig
from scheduled_job_client.utils import init_job_client
from time import time
import os
import errno


class ScheduledJobClientConfig(AppConfig):
    name = 'scheduled_job_client'
    init_file = '/tmp/scheduled_job_init_date'
    init_refresh = 90  # minutes

    def ready(self):
        try:
            mode = os.stat(self.init_file)
            if (time() - mode.st_mtime) > (self.init_refresh * 60):
                self._init_job_client()
        except OSError as ex:
            if ex.errno == errno.ENOENT:
                self._init_job_client()
            else:
                raise

    def _init_job_client(self):
        init_job_client()
        with open(self.init_file, 'w') as f:
            f.write('')
