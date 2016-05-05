from django.core.management.base import BaseCommand

from crams.crams_migration.project import migrate


class Command(BaseCommand):
    help = 'Migrate data'

    def handle(self, *args, **options):
        migrate()
