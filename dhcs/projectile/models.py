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

    name = models.CharField("Title", max_length=200)
    description = models.CharField("Description", max_length=10000)
    incentive = models.CharField("Incentive", max_length=10000)
    progress_till_date = models.CharField(
        "Progress till date", max_length=10000, blank=True)

    eligibility_criteria = models.CharField(
        "Eligibility Criteria", max_length=10000, blank=True)

    PROJECT_TYPES = (
        ('R', 'Research'),
        ('IP', 'Independent Project'),
        ('IS', 'Independent Study'),
        ('BTP', 'B. Tech Project'),
        ('MTP', 'M. Tech Project (Thesis)'),
        ('IN', 'Internship'),
        ('ENT', 'Enterpreneurship'),
        ('DEV', 'Development'),
        ('GEN', 'General'),
    )
    project_type = models.CharField(
        "Project Type", max_length=3, choices=PROJECT_TYPES, default='R')

    interest_areas = models.CharField(
        "Interest Areas (comma separated)", default="None",
        max_length=10000, blank=True)
    image_file = models.ImageField("Picture", upload_to='image_file',
                                   default='image_file/project.jpeg',
                                   storage=OverwriteStorage(),
                                   blank=True, null=True)

    PROJECTSTREAMS = (
        ('CS', 'Computer Science'),
        ('EC', 'Eelectronics and Communications'),
        ('CSAM', 'Computer Science in Applied Mathematics'),
        ('CB', 'Computational Biology'),
        ('DES', 'Design'),
        ('ITS', 'IT and Society'),
    )
    streams = models.CharField(
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
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User)
    rollno = models.CharField("Roll No", max_length=10, primary_key=True)
    name = models.CharField("Full Name", max_length=100)
    batch_year = models.CharField("Batch Year", max_length=100)
    course_enrolled = models.CharField("Course Enrolled in", max_length=100)
    course_stream = models.CharField("Course Stream", max_length=100)
    display_picture = models.ImageField("Picture", upload_to='display_picture',
                                        default='display_picture/user.jpg',
                                        storage=OverwriteStorage(),
                                        blank=True, null=True)
    email = models.EmailField(max_length=70)
    cgpa = models.FloatField(
        "CGPA", max_length=4, default=0, blank=True)

    backlogs = models.IntegerField(
        "Number of Backlogs", max_length=2, default=0)

    interest_areas = models.CharField(
        "Interest Areas (comma separated)", default="None",
        max_length=10000, blank=True)
    expertise_areas = models.CharField(
        "Expertise Areas (comma separated)", default="None",
        max_length=10000, blank=True)
    programming_languages = models.CharField(
        "Programming Languages (comma separated)", default="None",
        max_length=10000, blank=True)
    tools_and_technologies = models.CharField(
        "Tools and technologies (comma separated)", default="None",
        max_length=10000, blank=True)
    work_experience = models.CharField(
        "Work Experience (comma separated)", default="None",
        max_length=10000, blank=True)

    resume = models.FileField(
        "resume", upload_to='resume', default='',
        storage=OverwriteStorage())
    transcript = models.FileField(
        "transcript", upload_to='transcript', default='',
        storage=OverwriteStorage())

    projectapplications = models.ManyToManyField(
        Project, related_name='applicants', null=True, blank=True)

    working_on = models.ManyToManyField(
        Project, related_name='selectedcandidates', null=True, blank=True)

    createdon = models.DateTimeField(
        "Student Creation Date", default=datetime.now)

    def __str__(self):  # __unicode__ on Python 2
        return self.pk + ' ' + self.name


class Professor(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField("Full Name", max_length=100)
    email = models.EmailField(max_length=70)
    display_picture = models.ImageField("Picture", upload_to='display_picture',
                                        default='display_picture/professor.png',
                                        storage=OverwriteStorage(),
                                        blank=True, null=True)

    interest_areas = models.CharField(
        "Interest Areas (comma separated)", default="None",
        max_length=10000, blank=True)
    website = models.CharField(
        "Website Link: ", max_length=100, blank=True, null=True)
    projects_mentored = models.ManyToManyField(
        Project, related_name='mentors', null=True, blank=True)


class Feedback(models.Model):
    TYPES = (
        ('B', 'Bug Report'),
        ('F', 'Feature Request'),
        ('C', 'Comment'),
    )
    feedback_type = models.CharField("Feedback Type", max_length=1,
                                     choices=TYPES, default='C')
    title = models.CharField("Title", max_length=100)
    body = models.TextField("Feedback Details")
    createdon = models.DateTimeField(auto_now_add=True)
