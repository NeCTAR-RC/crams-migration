from django.core.management.base import BaseCommand

from crams.migration_validation import MigrationValidation


class Command(BaseCommand):
    help = 'Validate Migrate data'

    def handle(self, *args, **options):
        mv = MigrationValidation()
        mv.validate()
