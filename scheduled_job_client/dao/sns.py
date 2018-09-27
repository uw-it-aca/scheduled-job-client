from django.urls import reverse
from scheduled_job_client import get_job_config
from scheduled_job_client.exceptions import InvalidSubcriptionTopicArn
import boto3
import logging


logger = logging.getLogger(__name__)


def register_job_client_endpoint():
    """Subscribe to get Scheduled Job Manager control notifications
    """
    config = get_job_config()
    endpoint = '{0}{1}'.format(
        config.get('NOTIFICATION').get('ENDPOINT_BASE'),
        reverse('notification'))

    logger.debug('SNS: subscribe endpoint {0} to {1}'.format(
        endpoint, config.get('NOTIFICATION').get('TOPIC_ARN')))
    client = boto3.client('sns',
                          aws_access_key_id=config.get('KEY_ID'),
                          aws_secret_access_key=config.get('KEY'))
    client.subscribe(
        TopicArn=config.get('NOTIFICATION').get('TOPIC_ARN'),
        Protocol=config.get('NOTIFICATION').get('PROTOCOL'),
        Endpoint=endpoint,
        ReturnSubscriptionArn=True)


def confirm_subscription(topic_arn, token):
    """Confirm subscription to get Scheduled Job Manager control notifications
    """
    config = get_job_config()
    if topic_arn != config.get('NOTIFICATION').get('TOPIC_ARN'):
        raise InvalidSubcriptionTopicArn(topic_arn)

    logger.debug('SNS confirm subscription token {0}'.format(token))
    try:
        client = boto3.client('sns',
                              aws_access_key_id=config.get('KEY_ID'),
                              aws_secret_access_key=config.get('KEY'))
        response = client.confirm_subscription(
            TopicArn=topic_arn, Token=token,
            AuthenticateOnUnsubscribe='true'
        )
    except Exception as ex:
        logger.exception('SNS confirm subscription: {0}'.format(ex))
