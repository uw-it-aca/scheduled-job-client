# scheduled job management job manager
from scheduled_job_client import get_job_config
from datetime import datetime
from subprocess import Popen, PIPE
import logging
import traceback
import re


logger = logging.getLogger(__name__)


def start_background_job(job):
    logger.debug('starting background job')
    try:
        job_config = get_job_config()['JOBS'][job.job_label]
        job_type = job_config['type']
        job_action = job_config['action']

        logger.debug(
            'background job: type: {}, action: {}, conf: {}'.format(
                job_type, job_action, job_config))

        if job_type == 'method':
            command = 'python manage.py run_method {}'.format(job_action)
        elif job_type == 'management_command':
            command = 'python manage.py {}'.format(job_action)
        elif job_type == 'shell':
            command = job_action
        else:
            _job_error(job, 'Unknown job type for {}'.format(job.job_label))
            return

        try:
            output = ''
            proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
            job.pid = proc.pid
            job.save()

            logger.info(
                'background job - pid: {}, type: {}, command: {}'.format(
                    proc.pid, job_type, command))

            while True:
                line = proc.stdout.readline().decode('utf-8').strip()
                logger.debug('background job read: {}'.format(line))
                if line == '':
                    if proc.poll() is not None:
                        break
                else:
                    if re.match(r'^\d+$', line):
                        job.progress = int(line)
                        job.save()
                    else:
                        output += '{}'.format(line)

            logger.info(
                'background job finish - pid: {}, returncode: {}'.format(
                    proc.pid, proc.returncode))
        except Exception as ex:
            job.pid = None
            job.exit_status = -1
            job.exit_output = traceback.format_exc()
            job.save()
            logger.exception('background job: {}'.format(ex))
            return

        job.pid = None
        job.end_date = datetime.now()
        job.exit_status = proc.returncode
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
