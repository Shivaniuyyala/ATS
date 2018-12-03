from django.conf.urls import include, url
from classroom.views import *

urlpatterns = [

    url('students/', include(([
        url('profile/$', StudentProfile, name='student_profile'),
        url('view_attendance/(?P<course_id>\d+)/$', StudentAttendance, name='student_attendance'),
        url('add_course/$', AddCourseforStudent, name='add_course'),
        url('', StudentHome, name='student_home')
    ], 'classroom'), namespace='students')),

    url('instructor/', include(([
        url('profile/$', instructorProfile, name='instructor_profile'),
        url('add_course/$', AddCourseforInstuctor, name='add_course'),
        url('view_attendance/(?P<course_id>\d+)/$', allStudentAttendanceForCourse, name='instructor_attendance'),
        url('', InstructorHome, name='instructor_home')
    ], 'classroom'), namespace='instructor')),

    url('^', homepage, name='home'),
]
