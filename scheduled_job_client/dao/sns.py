from scheduled_job_client import get_job_config
import boto3


def register_job_client_endpoint(endpoint):
    """Subscribe to get Scheduled Job Manager control notifications
    """
    config = get_job_config()
    client = boto3.client('sns',
                          aws_access_key_id=config.KEY_ID,
                          aws_secret_access_key=config.KEY)
    client.subscribe(
        TopicArn=config['NOTIFICATION']['TOPIC_ARN'],
        Protocol=config['NOTIFICATION']['PROTOCOL'],
        Endpoint=endpoint,
        ReturnSubscriptionArn=True)


def confirm_subscription(token):
    """Confirm subscription to get Scheduled Job Manager control notifications
    """
    config = get_job_config()
    client = boto3.client('sns',
                          aws_access_key_id=config.KEY_ID,
                          aws_secret_access_key=config.KEY)

    response = client.confirm_subscription(
        TopicArn=config['NOTIFICATION']['TOPIC_ARN'],
        Token='string',
        AuthenticateOnUnsubscribe='string'
    )
