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
    job_client_update('launch', {
        'JobLabel': job.job_label,
        'JobId': job.job_id,
        'StartDate': job.start_date
    })


def report_job_finish(job):
    job_client_update('exit', {
        'JobLabel': job.job_label,
        'JobId': job.job_id,
        'EndDate': job.end_date,
        'ExitStatus': job.exit_status,
        'ExitOutput': job.exit_output
    })


def update_job_progress(job):
    job_client_update('progress', {
        'JobLabel': job.job_label,
        'JobId': job.job_id,
        'Progress': job.progress
    })


def update_job_ping(job):
    job_client_update('ping', {})
