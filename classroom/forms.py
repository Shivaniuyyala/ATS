from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from classroom.models import *


class InstructorSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    def save(self, commit=True):
        user = super(InstructorSignUpForm, self).save(commit=False)
        user.user_type = User.INSTRUCTOR
        user.save()
        instructor = Instructor.objects.create(user=user)
        return user


class StudentSignUpForm(UserCreationForm):
    # interests = forms.ModelMultipleChoiceField(
    #     queryset=Subject.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=True
    # )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    @transaction.atomic
    def save(self):
        user = super(StudentSignUpForm, self).save(commit=False)
        user.user_type = User.STUDENT
        user.save()
        student = Student.objects.create(user=user)
        # student.interests.add(*self.cleaned_data.get('interests'))
        return user


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", 'email', 'profile_pic']

    def __init__(self, *args, **kwargs):
        super(StudentProfileForm, self).__init__(*args, **kwargs)


class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", 'email', 'profile_pic']

    def __init__(self, *args, **kwargs):
        super(InstructorProfileForm, self).__init__(*args, **kwargs)


class StudentAttendanceforCourseForm(forms.Form):
    student = forms.MultipleChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        super(StudentAttendanceforCourseForm, self).__init__(*args, **kwargs)
        self.fields['student'] = forms.MultipleChoiceField(choices=Student.objects.all().values_list('user_id',
                                                                                                     'user__username'))


class StudentAttendanceForm(forms.Form):
    course = forms.ChoiceField(required=True)
    student = forms.MultipleChoiceField(required=True)
    from_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class': 'from_date'}))
    to_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class': 'from_date'}))

    def __init__(self, *args, **kwargs):
        super(StudentAttendanceForm, self).__init__(*args, **kwargs)
        self.fields['student'] = forms.MultipleChoiceField(choices=Student.objects.all().values_list('user_id',
                                                                                                     'user__username'))
        self.fields['course'] = forms.ChoiceField(choices=Course.objects.all().values_list('id', 'name'))


class AddCourseforStudentForm(forms.Form):
    course = forms.MultipleChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        super(AddCourseforStudentForm, self).__init__(*args, **kwargs)
        self.fields['course'] = forms.MultipleChoiceField(choices=Course.objects.all().values_list('id', 'name'))





