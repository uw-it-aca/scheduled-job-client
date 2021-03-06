from scheduled_job_client import get_job_config
from scheduled_job_client.exceptions import (
    InvalidJobRequest, ScheduleJobClientNoOp, UnkownJobException)
from aws_message.message import Message
import logging


logger = logging.getLogger(__name__)


def get_control_message(mbody):
    if not (mbody and len(mbody) > 0):
        raise InvalidJobRequest('Missing or malformed Job Request')

    try:
        job_config = get_job_config()

        message = Message(mbody, job_config)
        message.validate()
        control_message = message.extract()
        logger.debug('SNS Job Message: {0}'.format(control_message))

        action = control_message['Action']
        data = control_message['Data']
        try:
            task = data['task']
            task_label = task['label']
            try:
                # verify notification is for us
                if (task['cluster'] == job_config['CLUSTER_NAME'] and
                        task['member'] == job_config['CLUSTER_MEMBER']):
                    try:
                        job_config['JOBS'][task_label]
                        return (action, data)
                    except KeyError:
                        raise UnkownJobException(task_label)
                else:
                    raise ScheduleJobClientNoOp()
            except KeyError:
                raise InvalidJobRequest('Missing Task Data')
        except KeyError:
            # broad cluster member control message
            return (action, data)
    except KeyError:
        raise InvalidJobRequest('Missing Action or Data')
