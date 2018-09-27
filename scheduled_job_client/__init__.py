from django.conf import settings
from scheduled_job_client.exceptions import InvalidJobConfig


def get_job_config():
    try:
        return settings.SCHEDULED_JOB_CLIENT
    except AttributeError as ex:
        raise InvalidJobConfig('Missing Scheduled Job Client Configuration')
