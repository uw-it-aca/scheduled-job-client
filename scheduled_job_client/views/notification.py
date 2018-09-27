from django.views import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from logging import getLogger
from scheduled_job_client.models import ScheduledJob
from scheduled_job_client.message import get_job_message
from scheduled_job_client.dao.sns import confirm_subscription
from scheduled_job_client.status import report_job_start, update_job_progress
from scheduled_job_client.exceptions import (
    InvalidJobRequest, InvalidJobConfig, ScheduleJobClientNoOp)
from aws_message.message import validate_message_body
import json


logger = getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class JobClient(View):
    """ Respond to scheduled job management notifications
    """
    def post(self, request, *args, **kwargs):
        try:
            mbody = json.loads(request.read())
            logger.debug('SNS body: {0}'.format(mbody))

            validate_message_body(mbody)

            if mbody['Type'] == 'SubscriptionConfirmation':
                confirm_subscription(mbody['TopicArn'], mbody['Token'])
            else:
                job_message = get_job_message(mbody)
                logger.debug('job message: {0}'.format(mbody))
                _dispatch_on_job_type(job_message)

        except InvalidJobConfig as ex:
            logger.info('Invalid Job Config: {0}'.format(ex))
        except InvalidJobRequest as ex:
            logger.info('Invalid Job Request: {0}'.format(ex))
        except ScheduleJobClientNoOp as ex:
            pass
        except Exception as ex:
            logger.exception('JobClient.post: {0}'.format(ex))

        return HttpResponse('OK')


def _dispatch_on_job_type(job_message):
    """Dispatch on the type of job control notification
    """
    job = None
    try:
        job = ScheduledJob.objects.get(job_id=job_message.job_id)
    except ScheduledJob.DoesNotExist as ex:
        pass

    if job_message.type == 'launch':
        if not job:
            job = ScheduledJob.ojects.create(
                job_id=job_message.job_id,
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
    elif job_message.type == 'status':
        if job:
            update_job_progress(job)
