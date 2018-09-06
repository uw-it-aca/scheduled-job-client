from scheduled_job_client.utils import get_job_config
from scheduled_job_client.exceptions import InvalidJobRequest, NoOpJobRequest
from aws_message.message import validate_message_body, extract_inner_message
from aws_message.exceptions import SNSException


def get_job_message(mbody):
    if not (mbody and len(mbody) > 0):
        raise InvalidJobRequest('Missing or malformed Job Request')

    try:
        job_config = get_job_config()
        validate_message_body(mbody)
        job_message = extract_inner_message(mbody)
    except SNSException as ex:
        raise InvalidJobRequest('Invalid SNS Message: %s' % ex)

    # verify notification is for us
    if not (job_message.cluster_name == job_config['CLUSTER_NAME'] and
            job_message.cluster_member == job_config['CLUSTER_MEMBER'] and
            job_message.task_label in job_config['JOBS']):
        raise NoOpJobRequest()

    return job_message
