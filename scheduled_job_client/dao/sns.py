from django.urls import reverse
from scheduled_job_client import get_job_config
from scheduled_job_client.exceptions import InvalidSubcriptionTopicArn
import boto3
import re
import logging


logger = logging.getLogger(__name__)


def _get_client(config):
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

    return boto3.client('sns',
                        aws_access_key_id=config.get('KEY_ID'),
                        aws_secret_access_key=config.get('KEY'),
                        region_name=m.group('region'))


def subscribe_job_client_endpoint():
    """Subscribe to get Scheduled Job Manager control notifications
    """
    config = get_job_config()
    client = _get_client(config)
    endpoint = '{0}{1}'.format(
        config.get('NOTIFICATION').get('ENDPOINT_BASE'),
        reverse('notification'))

    logger.info('SNS: subscribe endpoint {0} to {1}'.format(
        endpoint, config.get('NOTIFICATION').get('TOPIC_ARN')))

    response = client.subscribe(
        TopicArn=config.get('NOTIFICATION').get('TOPIC_ARN'),
        Protocol=config.get('NOTIFICATION').get('PROTOCOL'),
        Endpoint=endpoint,
        ReturnSubscriptionArn=True)

    return response['SubscriptionArn']


def confirm_subscription(topic_arn, token):
    """Confirm subscription to get Scheduled Job Manager control notifications
    """
    config = get_job_config()
    if topic_arn != config.get('NOTIFICATION').get('TOPIC_ARN'):
        raise InvalidSubcriptionTopicArn(topic_arn)

    logger.info('SNS confirm subscription token {0}'.format(token))
    try:
        client = boto3.client('sns',
                              aws_access_key_id=config.get('KEY_ID'),
                              aws_secret_access_key=config.get('KEY'))
        response = client.confirm_subscription(
            TopicArn=topic_arn, Token=token,
            AuthenticateOnUnsubscribe='true'
        )
    except Exception as ex:
        if (type(ex).__name__ == 'AuthorizationErrorException' and
                'already confirmed' in '{0}'.format(ex)):
            logger.info('SNS subscription already confirmed')
        else:
            logger.exception('SNS confirm subscription: {0}'.format(ex))


def unsubscribe_job_client_endpoint():
    """Unsubscribe from Scheduled Job Manager control notifications
    """
    config = get_job_config()
    client = _get_client(config)

    SubscriptionArn = subscribe_job_client_endpoint()
    try:
        response = client.unsubscribe(
            SubscriptionArn=SubscriptionArn
        )
    except Exception as ex:
        if (type(ex).__name__ == 'InvalidParameterException' and
                'pending confirmation' in '{0}'.format(ex)):
            logger.info('SNS subscription already not subscribed')
        else:
            logger.exception('SNS unsubscribe: {0}'.format(ex))
