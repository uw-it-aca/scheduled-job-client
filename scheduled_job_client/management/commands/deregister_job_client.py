from django.core.management.base import BaseCommand
from scheduled_job_client.utils import deinit_job_client


class Command(BaseCommand):
    help = "Remove availability of scheduled job client"

    def handle(self, *args, **options):
        deinit_job_client()
