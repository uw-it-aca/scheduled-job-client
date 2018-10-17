from django.core.management.base import BaseCommand
from scheduled_job_client.testme import test_me
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Prod cluster members to report status"

    def handle(self, *args, **options):
        try:
            test_me()
        except Exception as ex:
            logger.exception('testme: {0}'.format(ex))
