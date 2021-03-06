# scheduled job management service status responsders
from scheduled_job_client import get_job_config
from scheduled_job_client.dao.sqs import job_client_update


def register_job_client():
    """READY: app cluster, member, and services
    """
    config = get_job_config()
    job_client_update('register', {
        'job_list': list(config['JOBS'])
    })


def deregister_job_client():
    """REMOVE: app cluster, member, and services
    """
    job_client_update('register', {
        'job_list': []
    })


def notify_job_start(json_data):
    job_client_update('launch', json_data)


def notify_job_finish(json_data):
    job_client_update('exit', json_data)


def notify_job_status(json_data):
    """Report current state of all known jobs
    """
    job_client_update('status', json_data)


def invalid_job_error(cause, label):
    job_client_update('error', {
        'cause': cause,
        'data': label
    })
