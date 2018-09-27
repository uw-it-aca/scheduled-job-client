from scheduled_job_client import get_job_config
from scheduled_job_client.exceptions import (
    InvalidJobRequest, ScheduleJobClientNoOp)
from aws_message.message import SNSException
from aws_message.message import extract_inner_message


def get_job_message(mbody):
    if not (mbody and len(mbody) > 0):
        raise InvalidJobRequest('Missing or malformed Job Request')

    try:
        job_config = get_job_config()
        job_message = extract_inner_message(mbody)
    except SNSException as ex:
        raise InvalidJobRequest('Invalid SNS Message: {0}'.format(ex))

    # verify notification is for us
    if not (job_message.cluster_name == job_config['CLUSTER_NAME'] and
            job_message.cluster_member == job_config['CLUSTER_MEMBER'] and
            job_message.task_label in job_config['JOBS']):
        raise ScheduleJobClientNoOp()

    return job_message
