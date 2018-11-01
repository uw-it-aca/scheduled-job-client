from scheduled_job_client import get_job_config
import boto3
import json
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

    sqs = boto3.client('sqs',
                       aws_access_key_id=config.get('KEY_ID'),
                       aws_secret_access_key=config.get('KEY'),
                       region_name=m.group('region'))
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

    response = sqs.send_message(
        QueueUrl=config.get('STATUS').get('QUEUE_URL'),
        MessageBody=json.dumps(message)
    )

    logger.debug('SQS response: {0}'.format(response))

    if response.get('Failed'):
        logger.error('SQS Failed: {0}'.format(response.get('Failed')))
        return None

    return response['MessageId']
