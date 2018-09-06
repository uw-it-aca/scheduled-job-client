from django.urls import reverse
from scheduled_job_client.dao.sns import register_job_client_endpoint
from scheduled_job_client.status import register_job_client
from scheduled_job_client.exceptions import InvalidJobConfig
from logging import getLogger


logger = getLogger(__name__)


def init_job_client():
    try:
        # subscribe to job manager queue
        register_job_client_endpoint(reverse('notification'))

        # notify scheduled job manager we exist
        register_job_client()
    except InvalidJobConfig as ex:
        logger.error("Cannot initialize: %s" % ex)
