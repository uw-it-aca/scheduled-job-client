from django.views import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from logging import getLogger
from scheduled_job_client.models import ScheduledJob
from scheduled_job_client.message import get_control_message
from scheduled_job_client.dao.sns import confirm_subscription
from scheduled_job_client.notification import (
    invalid_job_error, register_job_client, report_job_status)
from scheduled_job_client.exceptions import (
    InvalidJobRequest, InvalidJobConfig,
    ScheduleJobClientNoOp, UnkownJobException)
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
                action, data = get_control_message(mbody)
                _dispatch_on_control_message(action, data)
        except InvalidJobConfig as ex:
            logger.info('Invalid Job Config: {0}'.format(ex))
            invalid_job_error('invalid_job_configuration', '{}'.format(ex))
        except InvalidJobRequest as ex:
            logger.info('Invalid Job Request: {0}'.format(ex))
            invalid_job_error('invalid_job_request', '{}'.format(ex))
        except ScheduleJobClientNoOp as ex:
            pass
        except UnkownJobException as ex:
            logger.info('Invalid Job Label: {0}'.format(ex))
            invalid_job_error('invalid_job_label', '{}'.format(ex))
        except Exception as ex:
            logger.exception('JobClient.post: {0}'.format(ex))

        return HttpResponse('OK')


def _dispatch_on_control_message(action, data):
    """Dispatch on control message type
    """
    if action == 'status':
        json_data = {}
        for job in ScheduledJob.objects.all():
            json_data[job.job_id] = job.json_data()

        report_job_status({'Jobs': json_data})
        register_job_client()
    else:
        try:
            job_id = data['job_id']
            job_label = data['task']['label']
            if action == 'launch':
                job, created = ScheduledJob.objects.get_or_create(
                    job_id=job_id, job_label=job_label)

                if created:
                    job.launch()

                job.report_start()
            elif action == 'terminate':
                try:
                    ScheduledJob.objects.get(
                        job_id=job_id).report_progress()

                    # do something to terminate job

                except ScheduledJob.DoesNotExist:
                    raise InvalidJobRequest(
                        'Kill unknown job - {}'.format(job_id))
        except KeyError:
            raise InvalidJobRequest('Missing Data Fields')
