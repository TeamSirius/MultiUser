from django.core.management.base import BaseCommand, CommandError
from marauder.models import AccessPoint, Location, Floor
import pytz
import sqlite3


class Command(BaseCommand):
    args = 'old_database_password'
    help = 'Used to migrate from Flask-era database to Django-era database'

    def get_cursor(self, database_path):
        """Get the sqlite database cursor for the old database"""

        try:
            conn = sqlite3.connect(database_path)
            return conn.cursor()

        except psycopg2.OperationalError, e:
            raise CommandError("Something went wrong connecting to the database", e)

        return None

    def migrate_floors(self, cursor):
        """Migrate the floor data from the old database"""
        cursor.execute('SELECT * FROM marauder_floor')
        floor_data = cursor.fetchall()

        for floor in floor_data:
            Floor.objects.create(building_name=floor[3],
                                 floor_number=floor[2],
                                 temp_id=floor[0])

    def migrate_locations(self, cursor):
        """Migrate the location data from the old database"""
        cursor.execute('SELECT * FROM marauder_location')
        location_data = cursor.fetchall()

        for location in location_data:
            floor_id = location[6]
            floor = Floor.objects.get(temp_id=floor_id)
            Location.objects.create(short_name=location[1],
                                    verbose_name=location[2],
                                    x_coordinate=location[3],
                                    y_coordinate=location[4],
                                    direction=location[5],
                                    floor=floor,
                                    temp_id=location[0])

    def migrate_accesspoints(self, cursor):
        """Migrate the access point data from the old database"""
        cursor.execute('SELECT * FROM marauder_accesspoint')
        accesspoint_data = cursor.fetchall()
        timezone = pytz.timezone('America/New_York')

        for accesspoint in accesspoint_data:
            location_id = accesspoint[4]
            location = Location.objects.get(temp_id=location_id)
            recorded = timezone.localize(accesspoint[5])
            AccessPoint.objects.create(mac_address=accesspoint[1],
                                       signal_strength=accesspoint[2],
                                       standard_deviation=accesspoint[3],
                                       recorded=recorded,
                                       location=location,
                                       temp_id=accesspoint[0])

    def migrate_database(self, cursor):
        """Perform the database migration operations"""
        self.stderr.write('About to clear tables....')
        AccessPoint.objects.all().delete()
        Floor.objects.all().delete()
        Location.objects.all().delete()

        self.stderr.write('About to migrate floors....')
        self.migrate_floors(cursor)
        self.stderr.write('About to migrate locations....')
        self.migrate_locations(cursor)
        self.stderr.write('About to migrate access points....')
        self.migrate_accesspoints(cursor)

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Database path not supplied")

        db_path = args[0]

        cursor = self.get_cursor(db_path)

        self.migrate_database(cursor)
