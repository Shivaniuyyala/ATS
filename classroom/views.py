# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.http import HttpResponse, Http404
from django.views.generic import *
from classroom.models import *
from classroom.forms import *
from classroom.decorators import *
import json
import csv, StringIO
from django.template import loader
from django.contrib import messages
from decimal import Decimal


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


def homepage(request):
    if request.user.is_authenticated:
        if request.user.user_type == User.INSTRUCTOR:
            return redirect('instructor:instructor_home')
        else:
            return redirect('students:student_home')
    return render(request, 'home.html')


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super(StudentSignUpView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('students:student_home')


class InstructorSignUpView(CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super(InstructorSignUpView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        # user.is_instructor = True
        # user.save()
        login(self.request, user)
        return redirect('instructor:instructor_home')


@student_required
def StudentHome(request):
    if request.method == "GET":
        username, profile_pic = User.objects.filter(id=request.user.id).values_list('username', 'profile_pic')[0]
        courses = Course.objects.filter(student__user_id=request.user.id)
        return render(request, 'student/student_home.html', {"courses": courses, "username": username, 'profile_pic':
            profile_pic, "MEDIA_ROOT": str(settings.MEDIA_ROOT+"/"+str(profile_pic))})


@student_required
def StudentAttendance(request, course_id=None):
    if request.method == "GET":
        attendances = Attendance.objects.filter(student__user_id=request.user.id, course_id=course_id)
        return render(request, 'student/view_student_attendance.html', {"attendances": attendances})


@student_required
def AddCourseforStudent(request):
    if request.method == "GET":
        form = AddCourseforStudentForm()
        choices = Course.objects.exclude(student=request.user.id).values_list('id', 'name')
        form.fields['course'] = forms.MultipleChoiceField(choices=choices)
        if not choices:
            messages.info(request, "There is no courses to add")
        return render(request, 'student/add_course_for_student.html', {"form": form})
    else:
        form = AddCourseforStudentForm(request.POST)
        courses = request.POST.getlist('course')
        courses = [int(each) for each in courses]
        for course in courses:
            AddCourseRequest.objects.create(course_id=course, student_id=request.user.id)
        messages.success(request, "Successfully Requested for adding new course")
        return render(request, 'student/add_course_for_student.html', {"form": form})

@student_required
def StudentProfile(request):
    if request.method == "GET":
        student = User.objects.get(id=request.user.id)
        form = StudentProfileForm(instance=student)
        return render(request, 'student/profile.html', {"form": form})
    else:
        student = User.objects.get(id=request.user.id)
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
        messages.success(request, "Profile updated Successfully")
    return redirect('students:student_home')


# @instructor_required
def InstructorHome(request):
    template_name = 'instructor/instructor_home.html'
    if request.method == "GET":
        username, profile_pic = User.objects.filter(id=request.user.id).values_list('username', 'profile_pic')[0]
        courses = Course.objects.filter(instructor__user_id=request.user.id)
        return render(request, template_name, {"courses": courses, "username": username, 'profile_pic':
            profile_pic, "MEDIA_ROOT": str(settings.MEDIA_ROOT+"/"+str(profile_pic))})


@instructor_required
def instructorProfile(request):
    if request.method == "GET":
        instructor = User.objects.get(id=request.user.id)
        form = InstructorProfileForm(instance=instructor)
        return render(request, 'instructor/profile.html', {"form": form})
    else:
        instructor = User.objects.get(id=request.user.id)
        form = InstructorProfileForm(request.POST, instance=instructor)
        if form.is_valid():
            form.save()
        messages.success(request, "Profile updated Successfully")
    return redirect('instructor:instructor_home')


@instructor_required
def AddCourseforInstuctor(request):
    if request.method == "GET":
        form = AddCourseforStudentForm()
        choices = Course.objects.exclude(instructor_id=request.user.id).values_list('id', 'name')
        form.fields['course'] = forms.MultipleChoiceField(choices=choices)
        if not choices:
            messages.info(request, "There is no courses to add")
        return render(request, 'instructor/add_course_for_instructor.html', {"form": form})
    else:
        form = AddCourseforStudentForm(request.POST)
        courses = request.POST.getlist('course')
        courses = [int(each) for each in courses]
        for course in courses:
            AddCourseRequest.objects.create(course_id=course, instructor_id=request.user.id)
        messages.success(request, "Successfully Requested for adding new course")
        return render(request, 'instructor/add_course_for_instructor.html', {"form": form})

@instructor_required
def allStudentAttendanceForCourse(request, course_id=None):
    course = Course.objects.get(id=course_id)
    if request.method == "GET":
        form = StudentAttendanceforCourseForm()
        return render(request, 'instructor/view_all_students_attendance.html', {"form": form, "course": course.name})
    else:
        form = StudentAttendanceforCourseForm(request.POST)
        from_date = request.POST.get('from_date', None)
        to_date = request.POST.get('to_date', None)
        students = request.POST.getlist('student', None)
        students = [int(each) for each in students]
        if not from_date or not to_date:
            messages.error(request, "Provide valid Date Range")
            return render(request, 'instructor/view_all_students_attendance.html',
                          {"form": form, "course": course.name})
        from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()

        attendances = Attendance.objects.filter(course_id=course_id, student__user_id__in=students,
                                                day__lte=to_date, day__gte=from_date)
        return render(request, 'instructor/view_all_students_attendance.html', {"form": form, "course": course.name,
                                                                                'attendances': attendances})

@admin_login_required
def get_students_for_course(request):
    if not request.user.is_staff:
        raise Http404
    if request.is_ajax():
        course = request.POST.get('course', None)
        students_html = ""
        if course:
            students = list(Course.objects.filter(id=int(course)).values_list('student', 'student__user__username'))

            for each in students:
                students_html += '<option value="' + str(each[0]) + '">' + str(each[1]) + '</option>'

        success = True

        d = {
            'success': success,
            'students': loader.get_template('show_students.html').render(
                {'students': students_html})
        }
        return HttpResponse(json.dumps(d))
    raise Http404


def downloadAttendance(course, students, from_date, to_date):
    course = Course.objects.get(id=int(course))
    response = HttpResponse(content_type='text/csv')
    report_name = "Attendace" + "_" + str(course) + ".xlsx"
    response['Content-Disposition'] = 'attachment; filename=%s' % report_name
    writer = csv.writer(response)
    headers = ["Course", "Student", "Date", "is_present"]
    writer.writerow(headers)

    data = list(Attendance.objects.filter(course=course, student__user_id__in=students, day__lte=to_date,
                                          day__gte=from_date).values_list('course__name', 'student__user__name',
                                                                          'day', 'is_present'))

    for each_row in data:
        writer.writerow(each_row)

    return response


def emailAttendance(course, students, from_date, to_date):
    course = Course.objects.get(id=int(course))
    student_dict = dict(Student.objects.filter(user_id__in=students).values_list('user_id', 'user__username'))
    student_email = dict(Student.objects.filter(user_id__in=students).values_list('user_id', 'user__email'))
    for student in students:
        file_name = "Attendace_for_" + str(course) +"_"+str(from_date)+"_"+str(to_date)+ ".xlsx"
        attachment = StringIO.StringIO()
        writer = csv.writer(attachment)
        headers = ["Course", "Student", "from_date", "to_date", "Attendance Percent"]
        writer.writerow(headers)
        total = Attendance.objects.filter(course=course, student__user_id=student, day__lte=to_date,
                                              day__gte=from_date).count()
        num_present = Attendance.objects.filter(course=course, student__user_id=student, day__lte=to_date,
                                              day__gte=from_date, is_present=True).count()

        percent = (Decimal(num_present)/total)*100 if total else 0
        writer.writerow([course, student_dict[student], from_date, to_date, percent])

        from django.core.mail import EmailMessage
        subject = "Percentage of Attendance for Date Range %s to %s" % (str(from_date), str(to_date))
        body = """Hi %s,
        PFA for Attendance Percentage""" % student_dict[student]
        email = EmailMessage(subject, body, 'uyyala.shivani@gmail.com', [student_email[student]])
        email.attach(file_name, attachment.getvalue(), 'text/csv')
        email.send(fail_silently=False)

