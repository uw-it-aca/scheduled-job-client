from django.views import View
from django.http import HttpResponse
from logging import getLogger
from scheduled_job_client.models import Job
from scheduled_job_client.message import get_job_message
from scheduled_job_client.dao.sns import confirm_subscription
from scheduled_job_client.status import report_job_start, update_job_progress
from scheduled_job_client.exceptions import (
    InvalidJobRequest, InvalidJobConfig, NoOpJobRequest)


logger = getLogger(__name__)


class JobClient(View):
    """ Respond to scheduled job management notifications
    """
    def post(self, request, *args, **kwargs):
        try:
            mbody = request.read()
            import pdb; pdb.set_trace()
            job_message = get_job_message(mbody)

            if job_message['ConfirmSubscription']:
                token = job_message['token']
                confirm_subscription(token)
            else:
                _dispatch_on_job_type(job_message)
        except InvalidJobConfig as ex:
            logger.info('Invalid Job Config' % ex)
        except InvalidJobRequest as ex:
            logger.info('Invalid Job Request' % ex)
        except NoOpJobRequest as ex:
            pass

        return HttpResponse('OK')


def _dispatch_on_job_type(job_message):
    """Dispatch on the type of job control notification
    """
    job = None
    try:
        job = Job.objects.get(job_id=job_message.job_id)
    except Job.DoesNotExist as ex:
        pass

    if job_message.type == 'RUN':
        if not job:
            job = Job.ojects.create(job_id=job_message.job_id,
                                    job_label=job_message.job_label)

            # # # # # # # # # # # # # # # # # # # # # # #
            #
            # do stuff to launch task
            #
            # # # # # # # # # # # # # # # # # # # # # # #



            # report status
            report_job_start(job)
            # else:
            #     redundant message, fall through silently
    elif job_message.type == 'PROGRESS':
        if job:
            update_job_progress(job)
