from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['attendance_system']

subjects_data = [
    {
        'class': 'CSE(IOT)',
        'year': 2,
        'semester': 3,
        'subjects': ['Data Structures Using Python', 'OOPs through Java', 'Computer Networks', 'Environmental Science', 'Probability and Statistics', 'Basic Electronics', 'Finance and Accounting', 'Data Structures Using Python Lab', 'OOPs through Java Lab', 'Basic Electronics Lab', 'English lab', 'C Programming Lab']
    },
    {
        'class': 'CSE(IOT)',
        'year': 2,
        'semester': 4,
        'subjects': ['Operating Systems', 'Computer Organization', 'Database Management Systems', 'Automata Theory and Compiler Design', 'Indian Constitution', 'Effective Technical Communication in English', 'Software Engineering', 'Operating Systems Lab', 'Computer Organization Lab', 'Database Management Systems Lab']
    },
    {
        'class': 'CSE(DS)',
        'year': 2,
        'semester': 3,
        'subjects': ['Data Structures', 'Python Programming', 'Database Management Systems', 'Discrete Mathematics', 'Environmental Science', 'Basic Electronics', 'Operations Research', 'Data Structures and Algorithms using C Lab', 'Python Programming Lab', 'Database Management Systems Lab', 'Basic Electronics Lab', 'English lab', 'C Programming Lab']
    },
    {
        'class': 'CSE(DS)',
        'year': 2,
        'semester': 4,
        'subjects': ['Operating Systems', 'OOPs through Java', 'Principles of Data Science and Machine Learning', 'Indian Constitution', 'Computer Oriented Statistical Methods', 'Effective Technical Communication in English', 'Finance and Accounting', 'Operating Systems Lab', 'OOPs through Java Lab']
    },
    {
        'class': 'CSE',
        'year': 2,
        'semester': 3,
        'subjects': ['Data Structures Using Python', 'Discrete Mathematics', 'Database Management Systems', 'Environmental Science', 'Effective Technical Communication in English', 'Basic Electronics', 'Operations Research', 'Data Structures Using Python Lab', 'Database Management Systems Lab', 'Basic Electronics Lab', 'Advanced Computer Skills Lab', 'English lab', 'C Programming Lab']
    },
    {
        'class': 'CSE',
        'year': 2,
        'semester': 4,
        'subjects': ['Operating Systems', 'OOPs through Java', 'Artificial Intelligence', 'Indian Constitution', 'Probability and Statistics', 'Switching Theory and Logic Design', 'Finance and Accounting', 'Operating Systems Lab', 'OOPs through Java Lab', 'Artificial Intelligence Lab']
    },
    {
        'class': 'CSE(AI&ML)',
        'year': 4,
        'semester': 7,
        'subjects': ['Information Security', 'Data Visualization', 'Principles of Green Building', 'Big Data Analytics', 'Predictive Analysis', 'Information Security Lab', 'Big Data Analytics Lab', 'Major Project 1']
    }
]

for subject in subjects_data:
    existing_subject = db.subjects.find_one(
        {
            'class': subject['class'],
            'year': subject['year'],
            'semester': subject['semester']
        }
    )
    
    if existing_subject:
        print(f"Subjects for {subject['class']} year {subject['year']} semester {subject['semester']} already exist.")
    else:
        db.subjects.update_one(
            {
                'class': subject['class'],
                'year': subject['year'],
                'semester': subject['semester']
            },
            {
                '$set': {
                    'subjects': subject['subjects']
                }
            },
            upsert=True
        )
        print(f"Subjects for {subject['class']} year {subject['year']} semester {subject['semester']} have been added to the database.")
