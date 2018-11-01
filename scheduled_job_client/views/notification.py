from django.views import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from logging import getLogger
from scheduled_job_client.models import ScheduledJob
from scheduled_job_client.message import get_control_message
from scheduled_job_client.dao.sns import confirm_subscription
from scheduled_job_client.notification import (
    invalid_job_error, register_job_client, notify_job_status)
from scheduled_job_client.exceptions import (
    InvalidJobRequest, InvalidJobConfig,
    ScheduleJobClientNoOp, UnkownJobException)
from aws_message.aws import SNS
import json
import os


logger = getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class JobClient(View):
    """ Respond to scheduled job management notifications
    """
    def post(self, request, *args, **kwargs):
        try:
            mbody = json.loads(request.read())
            logger.debug('SNS body: {0}'.format(mbody))
            sns = SNS(mbody)
            sns.validate()

            if mbody['Type'] == 'SubscriptionConfirmation':
                confirm_subscription(mbody['TopicArn'], mbody['Token'])
            else:
                action, data = get_control_message(mbody)

                logger.info('job request: action: {}, data: {}'.format(
                    action, data))

                _dispatch_on_control_message(action, data)
        except InvalidJobConfig as ex:
            logger.error('Invalid Job Config: {0}'.format(ex))
            invalid_job_error('invalid_job_configuration', '{}'.format(ex))
        except InvalidJobRequest as ex:
            logger.error('Invalid Job Request: {0}'.format(ex))
            invalid_job_error('invalid_job_request', '{}'.format(ex))
        except ScheduleJobClientNoOp as ex:
            pass
        except UnkownJobException as ex:
            logger.error('Invalid Job Label: {0}'.format(ex))
            invalid_job_error('invalid_job_label', '{}'.format(ex))
        except Exception as ex:
            logger.exception('JobClient.post: {0}'.format(ex))

        return HttpResponse('OK')


def _dispatch_on_control_message(action, data):
    """Dispatch on control message type
    """
    if action == 'status':
        json_data = {}
        logger.debug('status check: checking jobs')
        for job in ScheduledJob.objects.all():
            logger.debug('status check: adding job {}'.format(job.job_id))
            json_data[job.job_id] = job.json_data()

        logger.info('status reponse: {}'.format(json_data))
        notify_job_status({'jobs': json_data})
        register_job_client()
    else:
        try:
            job_id = data['job_id']
            job_label = data['task']['label']
            logger.debug('dispatch: job id: {}, job_label: {}'.format(
                job_id, job_label))
            if action == 'launch':
                job, created = ScheduledJob.objects.get_or_create(
                    job_id=job_id, job_label=job_label)

                logger.info('launch - job id: {}, created: {}'.format(
                    job.job_id, created))

                # if new job or restarting previous job
                if created:
                    # fresh job
                    job.launch()
                elif job.exit_status is not None:
                    # finished job
                    job.launch()
                elif job.pid is not None:
                    # verify that it's running
                    try:
                        os.kill(job.pid, 0)
                        return
                    except OSError:
                        job.pid = None

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
