# scheduled job management service status responsders
from scheduled_job_client import get_job_config
from scheduled_job_client.dao.sqs import job_client_update


def register_job_client():
    """READY: app cluster, member, and services
    """
    config = get_job_config()
    job_client_update('register', {
        'job_list': config['JOBS'].keys()
    })


def report_job_start(job):
    job_client_update('start', {
        'job_label': job.job_label,
        'job_id': job.job_id,
        'start_date': job.start_date
    })


def report_job_finish(job):
    job_client_update('finish', {
        'job_label': job.job_label,
        'job_id': job.job_id,
        'end_date': job.end_date,
        'exit_status': job.exit_status,
        'exit_output': job.exit_output
    })


def update_job_progress(job):
    job_client_update('progress', {
        'job_label': job.job_label,
        'job_id': job.job_id,
        'progress': job.progress
    })
