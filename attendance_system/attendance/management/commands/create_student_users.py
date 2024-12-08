from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from pymongo import MongoClient

class Command(BaseCommand):
    help = 'Create Django users for all students in the database and add them to the Students group'

    def handle(self, *args, **kwargs):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['attendance_system']

        students_group, created = Group.objects.get_or_create(name='Students')

        students = db.students.find()
        for student in students:
            roll_number = str(student['roll_number'])  
            first_name = student['name'].split()[0] 
            last_name = ' '.join(student['name'].split()[1:]) 

            if not User.objects.filter(username=roll_number).exists():
                user = User.objects.create_user(username=roll_number, password=roll_number)
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                user.groups.add(students_group)  
                self.stdout.write(self.style.SUCCESS(f'Created user for roll number: {roll_number} and added to Students group'))
            else:
                self.stdout.write(self.style.WARNING(f'User already exists for roll number: {roll_number}'))
