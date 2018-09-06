# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class ScheduledJob(models.Model):
    """ Represents provisioning commands.
    """
    job_id = models.CharField(max_length=36, unique=True)
    job_label = models.CharField(max_length=128)
    pid = models.SmallIntegerField(default=-1)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)
    progress = models.SmallIntegerField(default=-1)
    exit_status = models.SmallIntegerField()
    exit_output = models.CharField(max_length=512, null=True)

    # should job table include logged data?  pointer/reference to log file?
