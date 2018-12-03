# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.forms import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class User(AbstractUser):
    STUDENT = 1
    INSTRUCTOR = 2
    USER_TYPE_CHOICES = (
        (STUDENT, 'student'),
        (INSTRUCTOR, 'instructor'),
    )
    profile_pic = models.ImageField(upload_to='profilepics', blank=True, null=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, blank=True, default=0)
    email = models.EmailField(_('email address'), unique=True)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.username


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.username


class BaseClass(models.Model):
    created_on = models.DateTimeField(editable=False, default=datetime.datetime.now)
    updated_on = models.DateTimeField(editable=False,  auto_now=True)
    created_by = models.ForeignKey(User, editable=False, blank=True, null=True,
                                   related_name="%(class)s_created_by")
    updated_by = models.ForeignKey(User, editable=False, blank=True, null=True,
                                   related_name="%(class)s_updated_by")

    class Meta:
        abstract = True

    @classmethod
    def table_name(cls):
        return cls._meta.db_table


class Course(BaseClass):
    name = models.CharField(max_length=30, unique=True)
    seats = models.IntegerField()
    active_from = models.DateTimeField()
    active_to = models.DateTimeField()
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    student = models.ManyToManyField(Student)

    def __str__(self):
        return self.name


class Attendance(BaseClass):
    course = models.ForeignKey(Course)
    student = models.ForeignKey(Student)
    is_present = models.BooleanField(default=False)
    day = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s - %s - %s" % (self.course, self.student, "Present" if self.is_present else "Absent")


class AddCourseRequest(BaseClass):
    REQUESTED = 1
    ACCEPTED = 2
    REJECTED = 3
    REQUEST_TYPES = (
        (REQUESTED, 'requested'),
        (ACCEPTED, 'accepted'),
        (REJECTED, 'rejected')
    )
    course = models.ForeignKey(Course)
    student = models.ForeignKey(Student, blank=True, null=True)
    instructor = models.ForeignKey(Instructor, blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=REQUEST_TYPES, default=1)
    reason = models.TextField(blank=True)

    def __str__(self):
        return "%s - %s - %s" % (self.course, self.student, self.status)

    def clean(self):
        if self.status == AddCourseRequest.REJECTED and not self.reason:
            raise ValidationError('Provide valid Reason')

    def save(self, *args, **kwargs):
        if self.status == AddCourseRequest.ACCEPTED:
            if self.student:
                Course.objects.get(id=self.course_id).student.add(self.student)
            if self.instructor:
                Course.objects.filter(id=self.course_id).update(instructor_id=self.instructor)
        super(AddCourseRequest, self).save(*args, **kwargs)




