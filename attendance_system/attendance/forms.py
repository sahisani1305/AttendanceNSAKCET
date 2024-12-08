from django import forms

class StudentRegistrationForm(forms.Form):
    roll_number = forms.CharField(max_length=20)
    name = forms.CharField(max_length=100)
    semester = forms.IntegerField()
    year = forms.IntegerField()
    class_name = forms.CharField(max_length=50)
    section = forms.CharField(max_length=10, required=False)

class StaffRegistrationForm(forms.Form):
    staff_id = forms.CharField(max_length=20, label='Staff ID')
    name = forms.CharField(max_length=100, label='Name')
