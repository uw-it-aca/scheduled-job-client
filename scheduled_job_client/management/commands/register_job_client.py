from django.core.management.base import BaseCommand
from scheduled_job_client.utils import init_job_client


class Command(BaseCommand):
    help = "Initialize Scheduled Job Client"

    def handle(self, *args, **options):
        init_job_client()
