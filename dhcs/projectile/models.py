# //=======================================================================
# // Copyright Projectile, IIIT Delhi 2017.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================


# __author__ = 'naman'

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from storage import OverwriteStorage


class Project(models.Model):

    def checkdeadline(self):
        if (timezone.now() > self.deadline):
            return True
        else:
            return False

    project_name = models.CharField("Project Title", max_length=200)

    PROJECTSTREAMS = (
        ('CSE', 'CSE'),
        ('ECE', 'ECE'),
        ('CSAM', 'CSAM'),
        ('CB', 'CB'),
        ('DES', 'Design'),
        ('ITS', 'IT and Society'),
        ('B', 'Both'),
    )
    project_stream = models.CharField(
        "Project Stream", max_length=3, choices=PROJECTSTREAMS, default='CSE')

    cgpa_min = models.FloatField(
        "Minimum CGPA", max_length=2, default=0, blank=True)

    OPENED_CLOSED = (
        ('O', 'Open'),
        ('A', 'Applications Closed'),
        ('C', 'Closed')
    )
    status = models.CharField("Status", max_length=1,
                              choices=OPENED_CLOSED, default='O')

    projectfile = models.FileField("File ", upload_to='projectfiles',
                                   default='', storage=OverwriteStorage(),
                                   blank=True, null=True)

    createdon = models.DateTimeField(
        "Application Creation Date", default=datetime.now)
    deadline = models.DateTimeField(
        "Application Deadline", default=datetime.now)
    deadlineexpired = property(checkdeadline)

    def __str__(self):  # __unicode__ on Python 2
        return self.project_name


class Student(models.Model):
    user = models.OneToOneField(User)
    rollno = models.CharField("Roll No", max_length=10, primary_key=True)
    name = models.CharField("Full Name", max_length=100)
    batch_year = models.CharField("Batch Year", max_length=100)
    course_enrolled = models.CharField("Course Enrolled in", max_length=100)
    course_stream = models.CharField("Course Stream", max_length=100)

    email = models.EmailField(max_length=70)
    cgpa = models.FloatField(
        "Postgraduate CGPA", max_length=4, default=0, blank=True)

    backs = (
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4+'),
    )
    backlogs = models.IntegerField(
        "Number of Backlogs", max_length=2, default=0, choices=backs)

    interest_areas = models.CharField(
        "Interest Areas (comma separated)", default="None", max_length=10000, blank=True)
    expertise_areas = models.CharField(
        "Expertise Areas (comma separated)", default="None", max_length=10000, blank=True)
    programming_languages = models.CharField(
        "Programming Languages (comma separated)", default="None", max_length=10000, blank=True)
    tools_and_technologies = models.CharField(
        "Tools and technologies (comma separated)", default="None", max_length=10000, blank=True)
    work_experience = models.CharField(
        "Work Experience (comma separated)", default="None", max_length=10000, blank=True)

    resume = models.FileField(
        "resume", upload_to='resume', default='', storage=OverwriteStorage())
    transcript = models.FileField(
        "transcript", upload_to='transcript', default='', storage=OverwriteStorage())

    projectapplications = models.ManyToManyField(
        Project, related_name='applicants', null=True, blank=True)

    createdon = models.DateTimeField(
        "Student Creation Date", default=datetime.now)

    def __str__(self):  # __unicode__ on Python 2
        return self.pk + ' ' + self.name


class Feedback(models.Model):
    TYPES = (
        ('B', 'Bug Report'),
        ('F', 'Feature Request'),
        ('C', 'Comment'),
    )
    type = models.CharField("Feedback Type", max_length=1,
                            choices=TYPES, default='C')
    title = models.CharField("Title", max_length=100)
    body = models.TextField("Feedback Details")
    createdon = models.DateTimeField(auto_now_add=True)
