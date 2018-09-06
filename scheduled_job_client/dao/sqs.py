from scheduled_job_client import get_job_config
import boto3


def job_client_update(message_type, message_body):
    """Send messages to the Scheduled Job Manager response queue
    """
    config = get_job_config()
    sqs = boto3.client('sqs',
                       aws_access_key_id=config['KEY_ID'],
                       aws_secret_access_key=config['KEY'])

    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=config['STATUS.QUEUE_URL'],
        DelaySeconds=10,
        MessageAttributes={
            'Cluster': {
                'Name': config['CLUSTER_NAME'],
                'Member': config['CLUSTER_MEMBER'],
            },
            'MessageType': message_type
        },
        MessageBody=message_body
    )

    return response['MessageId']
