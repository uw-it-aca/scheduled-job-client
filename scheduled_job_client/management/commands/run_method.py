from django.core.management.base import BaseCommand
import importlib
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run given python method"

    def add_arguments(self, parser):
        parser.add_argument(
            'module_and_method',
            help='module.method to execute')

    def handle(self, *args, **options):
        try:
            module_name, method_name = options[
                'module_and_method'].rsplit('.', 1)
            module = importlib.import_module(module_name)
            job_method = getattr(module, method_name)
            job_method()
        except Exception as ex:
            logger.exception('run_method: {0}'.format(ex))
