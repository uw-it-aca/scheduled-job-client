# scheduled job management job manager
from scheduled_job_client import get_job_config
from datetime import datetime
from subprocess import Popen, PIPE
import logging
import re


logger = logging.getLogger(__name__)


def start_background_job(job):
    try:
        job_config = get_job_config()['JOBS'][job.job_label]
        job_type = job_config['type']
        job_action = job_config['action']

        if job_type == 'method':
            command = 'python manage.py run_method {}'.format(job_action)
        elif job_type == 'management_command':
            command = 'python manage.py {}'.format(job_action)
        elif job_type == 'shell':
            command = job_action
        else:
            _job_error(job, 'Unknown job type for {}'.format(job.job_label))
            return

        output = ''
        proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        while True:
            line = proc.stdout.readline()
            if line == '':
                if proc.poll() is not None:
                    break
            else:
                n = line.strip()
                if re.match(r'^\d+$', n):
                    job.progress = int(n)
                    job.save()
                else:
                    output += '{}'.format(line)

        job.end_date = datetime.now()
        job.exit_status = proc.poll()
        if job.exit_status != 0:
            job.exit_output = output
        job.save()
    except KeyError:
        _job_error(job, 'Broken job config for {}'.format(job.job_label))


def _job_error(job, reason):
    logger.error(reason)
    job.end_date = datetime.now()
    job.progress = 0
    job.exit_status = -1
    job.exit_output = reason
    job.save()
    job.notify_job_finish()
