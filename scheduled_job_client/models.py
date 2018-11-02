# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scheduled_job_client.notification import (
    notify_job_start, notify_job_status)
from scheduled_job_client.job import start_background_job
from django.db import models
from django.utils.timezone import localtime, now
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
            thread = threading.Thread(
                target=start_background_job, args=(self,))
            thread.daemon = True
            thread.start()
            self.start_date = now()
            self.sav()

    def save(self, *args, **kwargs):
        notify_job_status({'jobs': {self.job_id: self.json_data()}})
        super(ScheduledJob, self).save(*args, **kwargs)

    def json_data(self):
        return {
            'job_id': self.job_id,
            'job_label': self.job_label,
            'start_date': localtime(self.start_date).isoformat() if (
                self.start_date is not None) else None,
            'end_date': localtime(self.end_date).isoformat() if (
                self.end_date is not None) else None,
            'progress': self.progress,
            'exit_status': self.exit_status,
            'exit_output': self.exit_output
        }
