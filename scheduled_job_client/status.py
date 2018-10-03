# scheduled job management service status responsders
from scheduled_job_client import get_job_config
from scheduled_job_client.dao.sqs import job_client_update


def register_job_client():
    """READY: app cluster, member, and services
    """
    config = get_job_config()
    job_client_update('register', {
        'JobList': config['JOBS'].keys()
    })


def report_job_start(job):
    job_client_update('launch', job.json_data())


def report_job_finish(job):
    job_client_update('exit', job.json_data())


def update_job_progress(job):
    job_client_update('progress', job.json_data())


def invalid_job_error(cause, label):
    job_client_update('error', {
        'Cause': cause,
        'Data': label
    })


def update_job_ping():
    job_client_update('ping', {})
