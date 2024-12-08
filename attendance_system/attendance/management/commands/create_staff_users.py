from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from pymongo import MongoClient

class Command(BaseCommand):
    help = 'Create Django users for all staff in the database and add them to the Staff group'

    def handle(self, *args, **kwargs):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['attendance_system']

        staff_group, created = Group.objects.get_or_create(name='Staff')

        staff_members = db.staff.find()
        for staff in staff_members:
            staff_id = str(staff['staff_id'])  
            first_name = staff['name'].split()[0]
            last_name = ' '.join(staff['name'].split()[1:])

            if not User.objects.filter(username=staff_id).exists():
                user = User.objects.create_user(username=staff_id, password=staff_id)
                user.first_name = first_name
                user.last_name = last_name
                user.is_staff = True 
                user.save()
                user.groups.add(staff_group) 
                self.stdout.write(self.style.SUCCESS(f'Created user for staff ID: {staff_id} and added to Staff group'))
            else:
                self.stdout.write(self.style.WARNING(f'User already exists for staff ID: {staff_id}'))
