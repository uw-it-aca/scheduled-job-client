# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scheduled_job_client.notification import (
    notify_job_start, notify_job_finish)
from scheduled_job_client.job import start_background_job
from django.db import models
from django.utils.timezone import localtime
import threading

# Models support local scheduled job instance


class ScheduledJob(models.Model):
    """ Represents provisioning commands.
    """
    job_id = models.CharField(max_length=36, unique=True)
    job_label = models.CharField(max_length=128)
    pid = models.SmallIntegerField(null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)
    progress = models.SmallIntegerField(null=True)
    exit_status = models.SmallIntegerField(null=True)
    exit_output = models.CharField(max_length=512, null=True)

    # BUG should job table include logged data?  pointer/reference to log file?

    def launch(self):
        if self.pid is None:
            threading.Thread(
                target=start_background_job, args=(self,), daemon=True).start()
            self.report_start()
        # else already running
        # BUG verify?

    def reset(self):
        self.end_date = None
        self.progress = None
        self.exit_status = None
        self.exit_output = None
        self.save()

    def report_start(self):
        notify_job_start(self.json_data())

    def json_data(self):
        return {
            'JobId': self.job_id,
            'JobLabel': self.job_label,
            'StartDate': localtime(self.start_date).isoformat() if (
                self.start_date is not None) else None,
            'EndDate': localtime(self.end_date).isoformat() if (
                self.end_date is not None) else None,
            'Progress': self.progress,
            'ExitStatus': self.exit_status,
            'ExitOutput': self.exit_output
        }
