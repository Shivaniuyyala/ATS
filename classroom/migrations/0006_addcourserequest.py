# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-03 07:45
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0005_auto_20181202_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddCourseRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'requested'), (2, 'accepted'), (3, 'rejected')], default=1)),
                ('reason', models.TextField(blank=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.Course')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addcourserequest_created_by', to=settings.AUTH_USER_MODEL)),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.Instructor')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.Student')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addcourserequest_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]