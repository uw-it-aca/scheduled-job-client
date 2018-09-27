from django.urls import reverse
from scheduled_job_client import get_job_config
import boto3


def register_job_client_endpoint():
    """Subscribe to get Scheduled Job Manager control notifications
    """
    config = get_job_config()
    client = boto3.client('sns',
                          aws_access_key_id=config.get('KEY_ID'),
                          aws_secret_access_key=config.get('KEY'))

    endpoint = '/'.join(
        [config.get('NOTIFICATION').get('ENDPOINT_BASE'),
         reverse('notification')])

    client.subscribe(
        TopicArn=config.get('NOTIFICATION').get('TOPIC_ARN'),
        Protocol=config.get('NOTIFICATION').get('PROTOCOL'),
        Endpoint=endpoint,
        ReturnSubscriptionArn=True)


def confirm_subscription(token):
    """Confirm subscription to get Scheduled Job Manager control notifications
    """
    config = get_job_config()
    client = boto3.client('sns',
                          aws_access_key_id=config.get('KEY_ID'),
                          aws_secret_access_key=config.get('KEY'))
    response = client.confirm_subscription(
        TopicArn=config.get('NOTIFICATION').get('TOPIC_ARN'),
        Token='string',
        AuthenticateOnUnsubscribe='string'
    )
