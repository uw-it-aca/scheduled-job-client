from scheduled_job_client.dao.sns import (
    subscribe_job_client_endpoint, unsubscribe_job_client_endpoint)
from scheduled_job_client.notification import (
    register_job_client, deregister_job_client)
from scheduled_job_client.exceptions import InvalidJobConfig
from logging import getLogger


logger = getLogger(__name__)


def init_job_client():
    try:
        # subscribe to job manager queue
        logger.debug('subscribe client endpoint')
        subscribe_job_client_endpoint()

        # notify scheduled job manager we exist
        logger.debug('register job client')
        register_job_client()
    except InvalidJobConfig as ex:
        logger.error("Cannot initialize: {0}".format(ex))


def deinit_job_client():
    try:
        logger.debug('Unsubscribe client endpoint')
        unsubscribe_job_client_endpoint()

        logger.debug('deregister job client')
        deregister_job_client()
    except InvalidJobConfig as ex:
        logger.error("Cannot deinitialize: {0}".format(ex))
