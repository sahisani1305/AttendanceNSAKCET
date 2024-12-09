from collections import OrderedDict, defaultdict
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from pymongo import MongoClient
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .forms import StudentRegistrationForm
from .forms import StaffRegistrationForm
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['attendance_system']

def create_student_user(roll_number):
    roll_number_str = str(roll_number)  # Convert roll number to string
    user = User.objects.create_user(username=roll_number_str, password=roll_number_str)
    user.save()

def base_page(request):
    return render(request, 'base_page.html')

def student_login(request):
    if request.method == 'POST':
        roll_number = request.POST['roll_number']
        password = request.POST['password']        
        user = authenticate(request, username=roll_number, password=password)
        if user is not None and user.groups.filter(name='Students').exists():
            login(request, user)
            return redirect('student_home')
        else:
            messages.error(request, 'Invalid roll number or password, or not a student.')
    return render(request, 'student_login.html')

def admin_login(request):
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        password = request.POST.get('password')
        
        # Your authentication logic here
        user = authenticate(request, username=admin_id, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('admin_home')
        else:
            messages.error(request, 'Invalid admin ID or password. Please try again.')
            return redirect('admin_login')
    
    return render(request, 'admin_login.html')

def staff_login(request):
    if request.method == 'POST':
        staff_id = request.POST['staff_id']
        password = request.POST['password']
        user = authenticate(request, username=staff_id, password=password)
        if user is not None and user.groups.filter(name='Staff').exists():
            login(request, user)
            return redirect('attendance_home')
        else:
            messages.error(request, 'Invalid staff ID or password, or not a staff member.')
    return render(request, 'staff_login.html')

@login_required
def admin_home(request):
    return render(request, 'admin_home.html')

@login_required
def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            roll_number = form.cleaned_data['roll_number']
            name = form.cleaned_data['name']
            semester = form.cleaned_data['semester']
            year = form.cleaned_data['year']
            class_name = form.cleaned_data['class_name']
            section = form.cleaned_data.get('section', 'Nil')

            try:
                # Check if student already exists in MongoDB
                existing_student = db.students.find_one({
                    'roll_number': roll_number
                })
                
                if existing_student:
                    messages.warning(request, f'Student with Roll Number {roll_number} already exists.')
                    return render(request, 'register_student.html', {'form': form})

                # Check if user already exists
                existing_user = User.objects.filter(username=roll_number).first()
                if existing_user:
                    messages.warning(request, f'User with Roll Number {roll_number} already exists.')
                    return render(request, 'register_student.html', {'form': form})

                # Add student to MongoDB
                db.students.insert_one({
                    'roll_number': roll_number,
                    'name': name,
                    'class': class_name,
                    'year': year,
                    'semester': semester,
                    'section': section,
                    'registration_date': datetime.now()
                })

                # Create Django user
                user = User.objects.create_user(
                    username=roll_number, 
                    password=roll_number  # Using roll number as default password
                )
                user.first_name = name.split()[0]
                user.last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                user.save()

                # Add user to Students group
                students_group, created = Group.objects.get_or_create(name='Students')
                user.groups.add(students_group)

                # Success message
                messages.success(
                    request, 
                    f'Student {name} registered successfully! '
                    f'Roll Number: {roll_number}'
                )

                return redirect('register_student')

            except Exception as e:
                # Catch any unexpected errors
                messages.error(
                    request, 
                    f'An unexpected error occurred: {str(e)}. '
                    'Please contact the system administrator.'
                )
                return render(request, 'register_student.html', {'form': form})

    else:
        form = StudentRegistrationForm()

    return render(request, 'register_student.html', {'form': form})

@login_required
def register_staff(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            staff_id = form.cleaned_data['staff_id']
            name = form.cleaned_data['name']

            try:
                # Check if staff member already exists in MongoDB
                existing_staff = db.staff.find_one({'staff_id': staff_id})
                
                if existing_staff:
                    messages.warning(request, f'Staff member with ID {staff_id} already exists.')
                    return render(request, 'register_staff.html', {'form': form})

                # Check if user already exists
                existing_user = User.objects.filter(username=staff_id).first()
                if existing_user:
                    messages.warning(request, f'User with staff ID {staff_id} already exists.')
                    return render(request, 'register_staff.html', {'form': form})

                # Add staff member to MongoDB
                db.staff.insert_one({
                    'staff_id': staff_id,
                    'name': name,
                    'registration_date': datetime.now()
                })

                # Create Django user
                user = User.objects.create_user(
                    username=staff_id, 
                    password=staff_id  # Using staff_id as default password
                )
                user.first_name = name.split()[0]
                user.last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                user.is_staff = True
                user.save()

                # Add user to Staff group
                staff_group, created = Group.objects.get_or_create(name='Staff')
                user.groups.add(staff_group)

                # Success message
                messages.success(
                    request, 
                    f'Staff member {name} registered successfully! '
                    f'Staff ID: {staff_id}'
                )

                return redirect('register_staff')

            except Exception as e:
                # Catch any unexpected errors
                messages.error(
                    request, 
                    f'An unexpected error occurred: {str(e)}. '
                    'Please contact the system administrator.'
                )
                return render(request, 'register_staff.html', {'form': form})

    else:
        form = StaffRegistrationForm()

    return render(request, 'register_staff.html', {'form': form})

def get_sections(request, class_name):
    sections = db.students.distinct('section', {'class': class_name})
    if not sections:
        sections = ['Nil']
    return JsonResponse({'sections': sections})

def home(request):
    return render(request, 'home.html')

def index(request):
    classes = db.students.distinct('class')
    periods = db.periods.find()
    return render(request, 'index.html', {'classes': classes, 'periods': periods})

def attendance(request):
    if request.method == 'POST':
        class_name = request.POST['class']
        section = request.POST['section']
        periods = request.POST.getlist('periods')  # Fetch multiple periods
        date = request.POST['date']
        semester = int(request.POST['semester'])
        year = int(request.POST['year'])
        subject = request.POST['subject']
        staff_name = request.user.get_full_name()  # Get the full name of the staff member

        # Fetch all students in the class and section
        all_students = list(db.students.find({'class': class_name, 'section': section, 'semester': semester, 'year': year}))

        # Fetch existing attendance records for the given criteria
        existing_attendance = list(db.attendance.find({
            'class': class_name,
            'section': section,
            'period': {'$in': periods},
            'date': date,
            'semester': semester,
            'year': year,
            'subject': subject
        }))

        # Create a set of roll numbers for students whose attendance is already marked
        marked_roll_numbers = set()
        for record in existing_attendance:
            marked_roll_numbers.update(record['present_students'])

        # Filter out students whose attendance is already marked
        students_to_mark = [student for student in all_students if student['roll_number'] not in marked_roll_numbers]

        return render(request, 'attendance.html', {
            'students': students_to_mark,
            'class_name': class_name,
            'section': section,
            'periods': periods,
            'date': date,
            'semester': semester,
            'year': year,
            'subject': subject,
            'staff_name': staff_name  # Pass the staff name to the template
        })
    return redirect('index')

@login_required
def mark_attendance(request):
    if request.method == 'POST':
        class_name = request.POST['class']
        section = request.POST['section']
        periods = request.POST.getlist('periods')  # Fetch multiple periods
        date = request.POST['date']
        semester = int(request.POST['semester'])
        year = int(request.POST['year'])
        subject = request.POST['subject']
        present_students = request.POST.getlist('present')  # List of roll numbers for present students
        absent_students = request.POST.get('absent_students', '').split(',')  # Roll numbers for absent students

        staff_name = request.user.get_full_name()  # Get the full name of the staff member

        # Loop through each period and mark attendance
        for period in periods:
            # Find the existing attendance record for the given class, section, period, and date
            existing_record = db.attendance.find_one({
                'class': class_name,
                'section': section,
                'period': period,
                'date': date,
                'semester': semester,
                'year': year,
                'subject': subject
            })

            if existing_record:
                # Update the existing attendance record with present and absent students
                # Ensure that if a student is present in any period, they are marked as present
                updated_present_students = set(existing_record['present_students']).union(set(present_students))
                updated_absent_students = set(existing_record.get('absent_students', [])).union(set(absent_students))

                # We ensure that a student can't be both present and absent at the same time
                final_absent_students = updated_absent_students - updated_present_students

                db.attendance.update_one(
                    {'_id': existing_record['_id']},
                    {'$set': {
                        'present_students': list(updated_present_students),
                        'absent_students': list(final_absent_students),
                        'staff_name': staff_name
                    }}
                )
            else:
                # If no existing record, create a new one
                db.attendance.insert_one({
                    'class': class_name,
                    'section': section,
                    'period': period,
                    'date': date,
                    'semester': semester,
                    'year': year,
                    'subject': subject,
                    'present_students': present_students,
                    'absent_students': absent_students,
                    'staff_name': staff_name  # Save the staff name
                })

        # Show success message
        messages.success(request, 'Attendance has been marked/updated successfully!')
        return redirect('view_attendance', year=year, semester=semester, class_name=class_name, section=section)
    return redirect('index')

@login_required
def student_home(request):
    roll_number = request.user.username.strip()  # Ensure roll number is stripped of whitespace
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Debugging: Print the roll number
    print(f"Roll Number: {roll_number}")

    # Fetch the student's information from the database
    student_info = db.students.find_one({'roll_number': int(roll_number)})
    
    if student_info:
        # Extract relevant student information
        student_name = student_info.get('name')
        student_class = student_info.get('class')
        student_year = student_info.get('year')
        student_section = student_info.get('section')
        student_semester = student_info.get('semester')
        
        # Debugging: Print student information
        print(f"Student Info: {student_name}, {student_class}, {student_section}, {student_year}, {student_semester}")

        # Fetch subjects based on the student's class, section, year, and semester
        subjects = list(db.subjects.find({
            'class': student_class,
            'year': student_year,
            'semester': student_semester
        }))

        # Debugging: Print the subjects found
        print(f"Subjects for {student_name} ({student_class}, {student_section}, {student_year}, {student_semester}): {subjects}")

    else:
        print(f"No student found with Roll Number: {roll_number}")
        messages.error(request, 'Student not found.')
        return render(request, 'student_home.html', {})

    # Build the query based on the date range
    query = {}
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query['date'] = {'$gte': start_date.strftime('%Y-%m-%d'), '$lte': end_date.strftime('%Y-%m-%d')}

    # Fetch all attendance records for the given date range
    all_records = list(db.attendance.find(query).sort([('date', 1)]))

    # First pass: Calculate total sessions per subject and date
    subject_total_sessions = defaultdict(lambda: defaultdict(int))
    subject_attended_sessions = defaultdict(lambda: defaultdict(int))
    attendance_summary = {}

    # Iterate through all records to count total sessions
    for record in all_records:
        date = record['date']
        subject = record['subject']
        
        # Count total sessions for each subject and date
        subject_total_sessions[subject][date] += 1

    # Now fetch student's specific attendance records
    student_query = dict(query, present_students=roll_number)
    student_records = list(db.attendance.find(student_query).sort([('date', 1)]))

    # Process student's attendance
    for record in student_records:
        date = record['date']
        subject = record['subject']
        
        # Initialize subject entry if not present
        if subject not in attendance_summary:
            attendance_summary[subject] = {}

        # Initialize date entry if not present
        if date not in attendance_summary[subject]:
            attendance_summary[subject][date] = {
                'classes_attended': 0,
                'total_classes': subject_total_sessions[subject][date]
            }
        
        # Increment the count of classes attended
        attendance_summary[subject][date]['classes_attended'] += 1
        subject_attended_sessions[subject][date] += 1
    # Calculate attendance percentages
    attendance_percentages = {}
    overall_total_sessions = 0
    overall_attended_sessions = 0

    # Create a set of subject names for quick lookup
    subject_names = set()
    for subject in subjects:
        # Assuming 'subjects' is a list of subject names
        for name in subject['subjects']:  # Adjust this if the field name is different
            subject_names.add(name)

    # Filter subjects to calculate overall attendance percentage
    for subject_name in subject_names:
        if subject_name in subject_total_sessions:
            total_sessions = sum(subject_total_sessions[subject_name].values())
            attended_sessions = sum(subject_attended_sessions[subject_name].values())
            
            # Calculate individual subject attendance percentage
            attendance_percentages[subject_name] = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            # Debugging: Print individual subject attendance details
            print(f"Subject: {subject_name}")
            print(f"  Total Sessions: {total_sessions}")
            print(f"  Attended Sessions: {attended_sessions}")
            print(f"  Attendance Percentage: {attendance_percentages[subject_name]:.2f}%")

            # Update overall totals
            overall_total_sessions += total_sessions
            overall_attended_sessions += attended_sessions

    # Calculate overall attendance percentage
    overall_attendance_percentage = (overall_attended_sessions / overall_total_sessions * 100) if overall_total_sessions > 0 else 0

    # Debugging: Print overall attendance details
    print(f"Overall Total Sessions: {overall_total_sessions}")
    print(f"Overall Attended Sessions: {overall_attended_sessions}")
    print(f"Overall Attendance Percentage: {overall_attendance_percentage:.2f}%")
    return render(request, 'student_home.html', {
        'attendance_summary': attendance_summary,
        'start_date': start_date,
        'end_date': end_date,
        'total_sessions': {subject: sum(dates.values()) for subject, dates in subject_total_sessions.items()},
        'total_sessions_attended': {subject: sum(dates.values()) for subject, dates in subject_attended_sessions.items()},
        'attendance_percentages': attendance_percentages,
        'overall_attendance_percentage': overall_attendance_percentage,
    })

@login_required
def view_attendance(request, year, semester, class_name, section):
    classes = db.students.distinct('class')
    attendance_records = []

    # Fetch all students in the class and section, sorted by roll number
    all_students = list(db.students.find({
        'class': class_name, 
        'section': section
    }, {'roll_number': 1, '_id': 0}).sort('roll_number', 1))

    # Modify roll number sorting to ensure consistent type
    def roll_number_key(student):
        return str(student['roll_number'])

    all_students.sort(key=roll_number_key)
    all_roll_numbers = {str(student['roll_number']) for student in all_students}

    # Fetch attendance records based on class, semester, year, and section
    if class_name and semester and year and section:
        attendance_records = list(db.attendance.find({
            'class': class_name,
            'semester': semester,
            'year': year,
            'section': section
        }))

    if not attendance_records:
        messages.info(request, 'No attendance records found for the selected class, semester, and year.')

    # Group attendance records by roll number and date
    students_attendance = defaultdict(list)
    present_students = set()
    subject_total_periods = defaultdict(int)

    # First pass: Calculate total periods per subject
    for record in attendance_records:
        subject = record['subject']
        subject_total_periods[subject] += 1

    # Processing attendance records
    for record in attendance_records:
        staff_name = record.get('staff_name', 'Nil')
        date = record['date']
        subject = record['subject']
        period = record['period']

        # Track students marked present
        record_present_students = set(str(roll) for roll in record.get('present_students', []))
        present_students.update(record_present_students)

        # Process present students
        for roll_number in record_present_students:
            existing_record = next((r for r in students_attendance[roll_number] 
                                    if r['date'] == date and 
                                    r['subject'] == subject), None)

            if existing_record:
                # Update existing record
                existing_record['periods_attended'] += 1
                existing_record['periods'].append(period)
            else:
                # Create new record for present student
                new_record = {
                    'roll_number': roll_number,
                    'date': date,
                    'periods_attended': 1,
                    'overall_periods': subject_total_periods[subject],
                    'semester': record['semester'],
                    'year': record['year'],
                    'subject': subject,
                    'staff_name': staff_name,
                    'periods': [period],
                    'status': 'Present'
                }
                students_attendance[roll_number].append(new_record)

    # Add absent records for students not marked present
    for roll_number in all_roll_numbers:
        date_subjects = set((record['date'], record['subject']) for record in attendance_records)

        for date, subject in date_subjects:
            if not any(r['date'] == date and r['subject'] == subject for r in students_attendance[roll_number]):
                absent_record = {
                    'roll_number': roll_number,
                    'date': date,
                    'periods_attended': 0,
                    'overall_periods': subject_total_periods[subject],
                    'semester': semester,
                    'year': year,
                    'subject': subject,
                    'staff_name': 'Nil',
                    'periods': [],
                    'status': 'Absent'
                }
                students_attendance[roll_number].append(absent_record)

    # Calculate total attended periods and attendance percentage
    # Initialize a dictionary to keep track of total attended periods irrespective of date range
    total_attended_periods = defaultdict(lambda: defaultdict(int))

    # Calculate total attended periods irrespective of date range
    for record in attendance_records:
        staff_name = record.get('staff_name', 'Nil')
        date = record['date']
        subject = record['subject']
        record_present_students = set(str(roll) for roll in record.get('present_students', []))

        for roll_number in record_present_students:
            total_attended_periods[roll_number][subject] += 1  # Increment total attended periods

    # Now process attendance records for the date range
    subject_total_attended_periods = {}
    for roll_number, records in students_attendance.items():
        if roll_number not in subject_total_attended_periods:
            subject_total_attended_periods[roll_number] = {}

        for record in records:
            subject = record['subject']
            if subject not in subject_total_attended_periods[roll_number]:
                subject_total_attended_periods[roll_number][subject] = 0
            
            periods_attended = record.get('periods_attended', 0)
            subject_total_attended_periods[roll_number][subject] += periods_attended
            
            record['total_attended_subject_periods'] = total_attended_periods[roll_number][subject]  # Use the global count
            total_subject_periods = subject_total_periods[subject]
            record['attendance_percentage'] = (record['total_attended_subject_periods'] / total_subject_periods * 100) if total_subject_periods > 0 else 0
    # Ensure no duplicate attendance status for a student on the same day and subject
    for roll_number, records in students_attendance.items():
        dates_subjects = set((r['date'], r['subject']) for r in records)
        for date, subject in dates_subjects:
            present_record = next((r for r in records if r['date'] == date and r['subject'] == subject and r['status'] == 'Present'), None)
            if present_record:
                records[:] = [r for r in records if not (r['date'] == date and r['subject'] == subject and r['status'] == 'Absent')]

    # Sort records by date within each roll number group
    for records in students_attendance.values():
        records.sort(key=lambda x: x['date'])

    # Get date ranges from request parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter attendance records by date range if specified
    filtered_attendance = defaultdict(list)
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        for roll_number, records in students_attendance.items():
            for record in records:
                record_date = datetime.strptime(record['date'], '%Y-%m-%d')
                if start_date <= record_date <= end_date:
                    filtered_attendance[roll_number].append(record)
    else:
        filtered_attendance = students_attendance

    # Group attendance records by subject
    subject_attendance = defaultdict(list)
    for roll_number, records in filtered_attendance.items():
        for record in records:
            subject_attendance[record['subject']].append(record)

    # Sort students attendance by roll number
    sorted_students_attendance = OrderedDict(sorted(filtered_attendance.items(), key=lambda x: str(x[0])))

    # Fetch periods from the database
    periods = list(db.periods.find({}, {'_id': 0}))

    return render(request, 'view_attendance.html', {
        'filtered_attendance': dict(subject_attendance),
        'class_name': class_name,
        'semester': semester,
        'year': year,
        'section': section,
        'classes': classes,
        'all_students': [str(student['roll_number']) for student in all_students],
        'present_students': list(present_students),
        'periods': periods,
        'start_date': start_date,
        'end_date': end_date
    })

@login_required
def admin_view_attendance(request, year, semester, class_name, section):
    classes = db.students.distinct('class')
    attendance_records = []

    # Fetch all students in the class and section, sorted by roll number
    all_students = list(db.students.find({
        'class': class_name, 
        'section': section
    }, {'roll_number': 1, '_id': 0}).sort('roll_number', 1))

    # Modify roll number sorting to ensure consistent type
    def roll_number_key(student):
        return str(student['roll_number'])

    all_students.sort(key=roll_number_key)
    all_roll_numbers = {str(student['roll_number']) for student in all_students}

    # Fetch attendance records based on class, semester, year, and section
    if class_name and semester and year and section:
        attendance_records = list(db.attendance.find({
            'class': class_name,
            'semester': semester,
            'year': year,
            'section': section
        }))

    if not attendance_records:
        messages.info(request, 'No attendance records found for the selected class, semester, and year.')

    # Group attendance records by roll number and date
    students_attendance = defaultdict(list)
    present_students = set()
    subject_total_periods = defaultdict(int)

    # First pass: Calculate total periods per subject
    for record in attendance_records:
        subject = record['subject']
        subject_total_periods[subject] += 1

    # Processing attendance records
    for record in attendance_records:
        staff_name = record.get('staff_name', 'Nil')
        date = record['date']
        subject = record['subject']
        period = record['period']

        # Track students marked present
        record_present_students = set(str(roll) for roll in record.get('present_students', []))
        present_students.update(record_present_students)

        # Process present students
        for roll_number in record_present_students:
            existing_record = next((r for r in students_attendance[roll_number] 
                                    if r['date'] == date and 
                                    r['subject'] == subject), None)

            if existing_record:
                # Update existing record
                existing_record['periods_attended'] += 1
                existing_record['periods'].append(period)
            else:
                # Create new record for present student
                new_record = {
                    'roll_number': roll_number,
                    'date': date,
                    'periods_attended': 1,
                    'overall_periods': subject_total_periods[subject],
                    'semester': record['semester'],
                    'year': record['year'],
                    'subject': subject,
                    'staff_name': staff_name,
                    'periods': [period],
                    'status': 'Present'
                }
                students_attendance[roll_number].append(new_record)

    # Add absent records for students not marked present
    for roll_number in all_roll_numbers:
        date_subjects = set((record['date'], record['subject']) for record in attendance_records)

        for date, subject in date_subjects:
            if not any(r['date'] == date and r['subject'] == subject for r in students_attendance[roll_number]):
                absent_record = {
                    'roll_number': roll_number,
                    'date': date,
                    'periods_attended': 0,
                    'overall_periods': subject_total_periods[subject],
                    'semester': semester,
                    'year': year,
                    'subject': subject,
                    'staff_name': 'Nil',
                    'periods': [],
                    'status': 'Absent'
                }
                students_attendance[roll_number].append(absent_record)

    # Calculate total attended periods and attendance percentage
    subject_total_attended_periods = {}
    for roll_number, records in students_attendance.items():
        if roll_number not in subject_total_attended_periods:
            subject_total_attended_periods[roll_number] = {}

        for record in records:
            subject = record['subject']
            if subject not in subject_total_attended_periods[roll_number]:
                subject_total_attended_periods[roll_number][subject] = 0
            
            periods_attended = record.get('periods_attended', 0)
            subject_total_attended_periods[roll_number][subject] += periods_attended
            
            record['total_attended_subject_periods'] = subject_total_attended_periods[roll_number][subject]
            total_subject_periods = subject_total_periods[subject]
            record['attendance_percentage'] = (record['total_attended_subject_periods'] / total_subject_periods * 100) if total_subject_periods > 0 else 0

    # Ensure no duplicate attendance status for a student on the same day and subject
    for roll_number, records in students_attendance.items():
        dates_subjects = set((r['date'], r['subject']) for r in records)
        for date, subject in dates_subjects:
            present_record = next((r for r in records if r['date'] == date and r['subject'] == subject and r['status'] == 'Present'), None)
            if present_record:
                records[:] = [r for r in records if not (r['date'] == date and r['subject'] == subject and r['status'] == 'Absent')]

    # Sort records by date within each roll number group
    for records in students_attendance.values():
        records.sort(key=lambda x: x['date'])

    # Get date ranges from request parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter attendance records by date range if specified
    filtered_attendance = defaultdict(list)
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        for roll_number, records in students_attendance.items():
            for record in records:
                record_date = datetime.strptime(record['date'], '%Y-%m-%d')
                if start_date <= record_date <= end_date:
                    filtered_attendance[roll_number].append(record)
    else:
        filtered_attendance = students_attendance

    # Group attendance records by subject
    subject_attendance = defaultdict(list)
    for roll_number, records in filtered_attendance.items():
        for record in records:
            subject_attendance[record['subject']].append(record)

    # Sort students attendance by roll number
    sorted_students_attendance = OrderedDict(sorted(filtered_attendance.items(), key=lambda x: str(x[0])))

    # Fetch periods from the database
    periods = list(db.periods.find({}, {'_id': 0}))

    return render(request, 'admin_view_attendance.html', {
        'filtered_attendance': dict(subject_attendance),
        'class_name': class_name,
        'semester': semester,
        'year': year,
        'section': section,
        'classes': classes,
        'all_students': [str(student['roll_number']) for student in all_students],
        'present_students': list(present_students),
        'periods': periods,
        'start_date': start_date,
        'end_date': end_date
    })

def get_subjects(request, class_name, year, semester):
    try:
        subjects_data = db.subjects.find_one({
            'class': class_name,
            'year': year,
            'semester': semester
        })

        if subjects_data:
            subjects = subjects_data.get('subjects', [])
            return JsonResponse({'subjects': subjects})
        else:
            return JsonResponse({'error': 'No subjects found for the specified class, year, and semester.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def attendance_home(request):
    return render(request, 'home.html')

def view_summary(request, year, semester, class_name, section):
    classes = db.students.distinct('class')
    attendance_records = []

    # Fetch all students in the class and section, sorted by roll number
    all_students = list(db.students.find({
        'class': class_name, 
        'section': section
    }, {'roll_number': 1, '_id': 0}).sort('roll_number', 1))

    # Modify roll number sorting to ensure consistent type
    def roll_number_key(student):
        return str(student['roll_number'])

    all_students.sort(key=roll_number_key)
    all_roll_numbers = {str(student['roll_number']) for student in all_students}

    # Fetch attendance records based on class, semester, year, and section
    if class_name and semester and year and section:
        attendance_records = list(db.attendance.find({
            'class': class_name,
            'semester': semester,
            'year': year,
            'section': section
        }))

    if not attendance_records:
        messages.info(request, 'No attendance records found for the selected class, semester, and year.')

    # Group attendance records by roll number and calculate attendance percentage
    subject_total_periods = defaultdict(int)
    total_attended_periods = defaultdict(lambda: defaultdict(int))

    # First pass: Calculate total periods per subject
    for record in attendance_records:
        subject = record['subject']
        subject_total_periods[subject] += 1

        # Track attendance for present students
        record_present_students = set(str(roll) for roll in record.get('present_students', []))
        for roll_number in record_present_students:
            total_attended_periods[roll_number][subject] += 1  # Increment total attended periods

    # Prepare summary data
    attendance_summary = {}
    unique_subjects = list(subject_total_periods.keys())  # Get all unique subjects

    for roll_number in all_roll_numbers:
        attendance_summary[roll_number] = {
            'total_attended': 0,
            'attendance_percentage': 0.0,
        }
        for subject in unique_subjects:
            attended_count = total_attended_periods[roll_number].get(subject, 0)
            attendance_summary[roll_number][subject] = attended_count  # Store sessions attended for each subject
            attendance_summary[roll_number]['total_attended'] += attended_count

        # Calculate total classes conducted
        total_classes_conducted = sum(subject_total_periods.values())

        # Calculate attendance percentage
        if total_classes_conducted > 0:
            attendance_summary[roll_number]['attendance_percentage'] = (
                (attendance_summary[roll_number]['total_attended'] / total_classes_conducted) * 100
            )

    # Sort the summary by roll number
    sorted_attendance_summary = dict(sorted(attendance_summary.items()))

    return render(request, 'view_summary.html', {
        'attendance_summary': sorted_attendance_summary,
        'class_name': class_name,
        'semester': semester,
        'year': year,
        'section': section,
        'classes': classes,
        'all_students': [str(student['roll_number']) for student in all_students],
        'unique_subjects': unique_subjects,  # Pass unique subjects to the template
        'total_classes_conducted': total_classes_conducted,  # Pass total classes conducted to the template
    })

def admin_view_summary(request, year, semester, class_name, section):
    classes = db.students.distinct('class')
    attendance_records = []

    # Fetch all students in the class and section, sorted by roll number
    all_students = list(db.students.find({
        'class': class_name, 
        'section': section
    }, {'roll_number': 1, '_id': 0}).sort('roll_number', 1))

    # Modify roll number sorting to ensure consistent type
    def roll_number_key(student):
        return str(student['roll_number'])

    all_students.sort(key=roll_number_key)
    all_roll_numbers = {str(student['roll_number']) for student in all_students}

    # Fetch attendance records based on class, semester, year, and section
    if class_name and semester and year and section:
        attendance_records = list(db.attendance.find({
            'class': class_name,
            'semester': semester,
            'year': year,
            'section': section
        }))

    if not attendance_records:
        messages.info(request, 'No attendance records found for the selected class, semester, and year.')

    # Group attendance records by roll number and calculate attendance percentage
    subject_total_periods = defaultdict(int)
    total_attended_periods = defaultdict(lambda: defaultdict(int))

    # First pass: Calculate total periods per subject
    for record in attendance_records:
        subject = record['subject']
        subject_total_periods[subject] += 1

        # Track attendance for present students
        record_present_students = set(str(roll) for roll in record.get('present_students', []))
        for roll_number in record_present_students:
            total_attended_periods[roll_number][subject] += 1  # Increment total attended periods

    # Prepare summary data
    attendance_summary = {}
    unique_subjects = list(subject_total_periods.keys())  # Get all unique subjects

    for roll_number in all_roll_numbers:
        attendance_summary[roll_number] = {
            'total_attended': 0,
            'attendance_percentage': 0.0,
        }
        for subject in unique_subjects:
            attended_count = total_attended_periods[roll_number].get(subject, 0)
            attendance_summary[roll_number][subject] = attended_count  # Store sessions attended for each subject
            attendance_summary[roll_number]['total_attended'] += attended_count

        # Calculate total classes conducted
        total_classes_conducted = sum(subject_total_periods.values())

        # Calculate attendance percentage
        if total_classes_conducted > 0:
            attendance_summary[roll_number]['attendance_percentage'] = (
                (attendance_summary[roll_number]['total_attended'] / total_classes_conducted) * 100
            )

    # Sort the summary by roll number
    sorted_attendance_summary = dict(sorted(attendance_summary.items()))

    return render(request, 'admin_view_summary.html', {
        'attendance_summary': sorted_attendance_summary,
        'class_name': class_name,
        'semester': semester,
        'year': year,
        'section': section,
        'classes': classes,
        'all_students': [str(student['roll_number']) for student in all_students],
        'unique_subjects': unique_subjects,  # Pass unique subjects to the template
        'total_classes_conducted': total_classes_conducted,  # Pass total classes conducted to the template
    })