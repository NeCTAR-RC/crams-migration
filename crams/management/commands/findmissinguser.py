from django.core.management.base import BaseCommand

from crams.find_missing_user_req import FindMissingKeystoneUsersRequest


class Command(BaseCommand):
    help = 'Find missing keystone users requests'

    def handle(self, *args, **options):
        req = FindMissingKeystoneUsersRequest()
        req.find()
