from scheduled_job_client import get_job_config
from random import randint
import boto3
import json
import logging


logger = logging.getLogger(__name__)


def job_client_update(message_type, json_data):
    """Send messages to the Scheduled Job Manager response queue
    """
    config = get_job_config()
    sqs = boto3.client('sqs',
                       aws_access_key_id=config.get('KEY_ID'),
                       aws_secret_access_key=config.get('KEY'))

    json_data['ClusterMember'] = {
        'ClusterName': config.get('CLUSTER_NAME'),
        'ClusterMemberName': config.get('CLUSTER_MEMBER'),
    }

    logger.debug('SQS send: {0}'.format(json_data))

    response = sqs.send_message(
        QueueUrl=config.get('STATUS').get('QUEUE_URL'),
        MessageAttributes={
            'JobMessageType': {
                'StringValue': message_type,
                'DataType': 'String'
            }
        },
        MessageDeduplicationId='ScheduledJobManager{0}'.format(
            randint(1000000000, 9999999999)),
        MessageGroupId='ScheduledJobManager',
        MessageBody=json.dumps(json_data)
    )

    logger.debug('SQS response: {0}'.format(response))

    if response.get('Failed'):
        logger.error('SQS Failed: {0}'.format(response.get('Failed')))
        return None

    return response['MessageId']
