"""ATS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import include, url
from django.contrib import admin
from adminplus.sites import AdminSitePlus

admin.site = AdminSitePlus()
admin.autodiscover()


from classroom.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/get_students_for_course/', get_students_for_course),
    url('^accounts/signup/student/', StudentSignUpView.as_view(), name='student_signup'),
    url('^accounts/signup/teacher/', InstructorSignUpView.as_view(), name='instructor_signup'),
    url('^accounts/signup/staff/', InstructorSignUpView.as_view(), name='staff_signup'),
    url('^accounts/signup/', SignUpView.as_view(), name='signup'),

    url('^accounts/', include('django.contrib.auth.urls')),
    url('', include('classroom.urls'))
]
