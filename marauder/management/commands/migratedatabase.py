from django.core.management.base import BaseCommand, CommandError
from marauder.models import AccessPoint, Location, Floor

class Command(BaseCommand):
    args = 'old_database_password'
    help = 'Used to migrate from Flask-era database to Django-era database'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Database password not supplied")

        db_password = args[0]

        # TODO:
        #   First, migrate the Floors
        #   Then, the Locations
        #   Then, the AccessPoints
