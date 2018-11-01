from scheduled_job_client import get_job_config
import json
from boto.sqs import connect_to_region
from boto.sqs.queue import Queue
from aws_message.aws import SNSException
from scheduled_job_client.dao import https_connection_factory
import logging
import re


logger = logging.getLogger(__name__)


def job_client_update(message_action, json_data):
    """Send messages to the Scheduled Job Manager response queue
    """
    config = get_job_config()

    # dig region, account and queue_name out of ARN
    #     arn:aws:sqs:<region>:<account-id>:<queuename>
    # defined at:
    #     https://docs.aws.amazon.com/general/latest/
    #         gr/aws-arns-and-namespaces.html
    queue_arn = config.get('STATUS').get('QUEUE_ARN')
    m = re.match(r'^arn:aws:sqs:'
                 r'(?P<region>([a-z]{2}-[a-z]+-\d+|mock)):'
                 r'(?P<account_id>\d+):'
                 r'(?P<queue_name>[a-z\d\-\_\.]*)$',
                 queue_arn, re.I)
    if not m:
        raise Exception('Invalid SQS ARN: {}'.format(queue_arn))

    connection = _sqs_connection()

    message = {
        'Message': {
            'Type': 'ScheduledJobMessage',
            'Cluster': {
                'ClusterName': config.get('CLUSTER_NAME'),
                'ClusterMemberName': config.get('CLUSTER_MEMBER'),
            },
            'Action': message_action,
            'Data': json_data
        }
    }

    logger.debug('SQS send: {0}'.format(message))

    queue = Queue(connection=connection,
                  url=config.get('STATUS').get('QUEUE_URL'))

    response = connection.send_message(queue, json.dumps(message))

    logger.debug('SQS response: {0}'.format(response))

    if hasattr(response, 'id'):
        return response.id

    logger.error('SQS Failed: {0}'.format(response.SendMessageResponse))
    return None



def _sqs_connection():
    config = get_job_config()

    # dig region, account and queue_name out of ARN
    #     arn:aws:sqs:<region>:<account-id>:<queuename>
    # defined at:
    #     https://docs.aws.amazon.com/general/latest/
    #         gr/aws-arns-and-namespaces.html
    queue_arn = config.get('STATUS').get('QUEUE_ARN')
    m = re.match(r'^arn:aws:sqs:'
                 r'(?P<region>([a-z]{2}-[a-z]+-\d+|mock)):'
                 r'(?P<account_id>\d+):'
                 r'(?P<topic_name>[a-z\d\-\_\.]*)$',
                 queue_arn, re.I)
    if not m:
        raise Exception('Invalid SQS ARN: {}'.format(queue_arn))

    connection_kwargs = {
        'aws_access_key_id': config.get('KEY_ID'),
        'aws_secret_access_key': config.get('KEY')
    }

    if config.get('LOCAL_CLIENT_VALIDATION', False):
        connection_kwargs['https_connection_factory'] = (
            https_connection_factory, ())

    connection = connect_to_region(m.group('region'), **connection_kwargs)

    if connection is None:
        raise SNSException('no connection')

    return connection
