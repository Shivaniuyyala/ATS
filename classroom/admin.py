# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from classroom.models import *
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.contrib import messages
import threading
import datetime


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('id', 'email', 'user_type', 'is_active', 'is_staff', 'is_superuser', 'date_joined')


class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ('name', 'seats', 'active_from', 'active_to', 'instructor')
    filter_horizontal = ('student',)


class AddCourseRequestAdmin(admin.ModelAdmin):
    model = AddCourseRequest
    list_display = ('course','student', 'instructor', 'status', 'reason')


class AttendanceAdmin(admin.ModelAdmin):
    model = Attendance
    list_display = ('course', 'student', 'is_present', 'day', 'created_on', 'updated_on', 'created_by', 'updated_by')

    class Media:
        js = ("get_students_for_course.js",)


class StudentAttendanceView(TemplateView):
    template_name = 'student_attendance.html'
    permission_name = 'bb.access_crate_segregation_master'
    from classroom.forms import StudentAttendanceForm
    form = StudentAttendanceForm

    def dispatch(self, request, *args, **kwargs):
        return super(StudentAttendanceView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_response({'title': 'Download/Email Student Attendance', 'form': self.form})

    def post(self, request):
        from_date = request.POST.get('from_date', None)
        to_date = request.POST.get('to_date', None)
        students = request.POST.getlist('student')
        course = request.POST.get('course', None)
        type = request.POST.get('button', None)
        students = [int(each) for each in students]
        from_date = datetime.datetime.strptime(from_date, '%m/%d/%Y').date()
        to_date = datetime.datetime.strptime(to_date, '%m/%d/%Y').date()
        if from_date > to_date:
            messages.error(request, "Provide valid date range: from_date should be less than to_date")
            return HttpResponseRedirect('/admin/get_student_attendance/')
        if type == "Download":
            from classroom.views import downloadAttendance
            threading.Thread(group=None,
                             target=downloadAttendance,
                             name='downloadAttendance',
                             args=(course, students, from_date, to_date)).start()

            messages.success(request, "Request accepted Successfully")
            return HttpResponseRedirect('/admin/get_student_attendance/')
        else:
            from classroom.views import emailAttendance
            threading.Thread(group=None,
                             target=emailAttendance,
                             name='emailAttendance',
                             args=(course, students, from_date, to_date)).start()

            messages.success(request, "Email will be sent Successfully")
            return HttpResponseRedirect('/admin/get_student_attendance/')

admin.site.register(User, UserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(AddCourseRequest, AddCourseRequestAdmin)
admin.site.register_view('get_student_attendance/', view=StudentAttendanceView.as_view())

