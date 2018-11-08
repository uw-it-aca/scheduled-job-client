# scheduled job management job manager
from scheduled_job_client import get_job_config
from django.utils.timezone import now
from subprocess import Popen, PIPE
import select
import logging
import traceback
import os
import sys
import re


logger = logging.getLogger(__name__)


def start_background_job(job):
    logger.debug('starting background job')
    try:
        job_config = get_job_config()['JOBS'][job.job_label]
        job_type = job_config['type']
        job_action = job_config['action']
        job_args = ' '.join(map(lambda i: '{}'.format(i),
                                job_config.get('arguments', [])))
        job_cwd = job_config.get('cwd')

        if job_type == 'method':
            command = 'python manage.py run_method {} {}'.format(
                job_action, job_args)
        elif job_type == 'management_command':
            command = 'python manage.py {} {}'.format(
                job_action, job_args)
        elif job_type == 'shell':
            command = '{} {}'.format(job_action, job_args)
        else:
            _job_error(job, 'Unknown job type for {} {}'.format(
                job.job_label, job_args))
            return

        logger.info(
            'background job: type: {}, command: {}, conf: {}'.format(
                job_type, command, job_config))

        try:
            proc_env = os.environ.copy()
            popen_args = {
                'shell': True,
                'env': proc_env,
                'stdout': PIPE,
                'stderr': PIPE
            }

            if job_cwd:
                popen_args['cwd'] = job_cwd
                proc_env['PYTHONPATH'] = os.path.join(
                    job_cwd, 'lib/python{}.{}/site-packages'.format(
                        sys.version_info.major, sys.version_info.minor))
                proc_env['PATH'] = os.path.join(job_cwd, 'bin')

            proc = Popen(command, **popen_args)
            job.pid = proc.pid
            job.start_date = now()
            job.progress = 0
            job.end_date = None
            job.exit_status = None
            job.exit_output = None
            job.save()
        except Exception as ex:
            logger.exception('background job - Popen fail: {}'.format(ex))
            return

        logger.info(
            'background job - pid: {}, type: {}, command: {}'.format(
                proc.pid, job_type, command))

        output = ''
        stdout = proc.stdout.fileno()
        stderr = proc.stderr.fileno()
        while True:
            r, w, e = select.select([stdout, stderr], [], [])
            line = ''
            for descriptor in r:
                if descriptor == stdout:
                    line = proc.stdout.readline().decode('utf-8').strip()
                    if re.match(r'^\d+$', line):
                        job.progress = int(line)
                        job.save()
                    else:
                        output += '{}\n'.format(line)

                if descriptor == stderr:
                    line = proc.stderr.readline().decode('utf-8').strip()
                    output += '{}\n'.format(line)

            if line == '' and proc.poll() is not None:
                break

        logger.info(
            'background job finish - pid: {}, returncode: {}'.format(
                proc.pid, proc.returncode))

        job.pid = None
        job.end_date = now()
        job.progress = 100
        job.exit_status = proc.returncode
        job.exit_output = output
        job.save()
    except KeyError:
        _job_error(job, 'Broken job config for {}'.format(job.job_label))
    except Exception as ex:
        job.pid = None
        job.exit_status = -1
        job.exit_output = traceback.format_exc()
        job.save()
        logger.exception('background job: {}'.format(ex))


def _job_error(job, reason):
    logger.error(reason)
    job.end_date = now()
    job.progress = 0
    job.exit_status = -1
    job.exit_output = reason
    job.save()
