from django.conf import settings
from django.urls import reverse
from scheduled_job_client import get_job_config
from scheduled_job_client.exceptions import InvalidSubcriptionTopicArn
from boto.sns.connection import SNSConnection
from boto.sns import connect_to_region
from aws_message.aws import SNSException
from scheduled_job_client.dao import https_connection_factory
import re
import logging


logger = logging.getLogger(__name__)


def register_job_client_endpoint():
    """Subscribe to get Scheduled Job Manager control notifications
    """
    config = get_job_config()

    endpoint = '{0}{1}'.format(
        config.get('NOTIFICATION').get('ENDPOINT_BASE'),
        reverse('notification'))

    logger.info('SNS: subscribe endpoint {0} to {1}'.format(
        endpoint, config.get('NOTIFICATION').get('TOPIC_ARN')))

    connection = _sns_connection()

    connection.subscribe(
        config.get('NOTIFICATION').get('TOPIC_ARN'),
        config.get('NOTIFICATION').get('PROTOCOL'),
        endpoint)


def confirm_subscription(topic_arn, token):
    """Confirm subscription to get Scheduled Job Manager control notifications
    """
    config = get_job_config()
    if topic_arn != config.get('NOTIFICATION').get('TOPIC_ARN'):
        raise InvalidSubcriptionTopicArn(topic_arn)

    logger.info('SNS confirm subscription token {0}'.format(token))
    try:
        connection = _sns_connection()
        connection.confirm_subscription(
            topic_arn, token, authenticate_on_unsubscribe=True)
    except Exception as ex:
        if (type(ex).__name__ == 'AuthorizationErrorException' and
                'already confirmed' in '{0}'.format(ex)):
            logger.info('SNS subscription already confirmed')
        else:
            logger.exception('SNS confirm subscription: {0}'.format(ex))


def _sns_connection():
    config = get_job_config()

    # dig region, account and queue_name out of ARN
    #     arn:aws:sqs:<region>:<account-id>:<queuename>
    # defined at:
    #     https://docs.aws.amazon.com/general/latest/
    #         gr/aws-arns-and-namespaces.html
    topic_arn = config.get('NOTIFICATION').get('TOPIC_ARN')
    m = re.match(r'^arn:aws:sns:'
                 r'(?P<region>([a-z]{2}-[a-z]+-\d+|mock)):'
                 r'(?P<account_id>\d+):'
                 r'(?P<topic_name>[a-z\d\-\_\.]*)$',
                 topic_arn, re.I)
    if not m:
        raise Exception('Invalid SNS ARN: {}'.format(topic_arn))

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
