# //=======================================================================
# // Copyright Projectile, IIIT Delhi 2017.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================


# __author__ = 'naman'


import os
import zipfile
import StringIO

from dhcs import settings
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from projectile import forms
from projectile.helpers import *
from projectile.models import Project, Student, Professor, Application


@login_required()
def student_professor(request, profid):
    prof = Professor.objects.get(pk=profid)
    context = {'professor': prof}
    return render(request, "projectile/student_professor.html", context)


@login_required()
def admin_notifications(request):
    return render(request, "projectile/admin_notification.html")


def server_error(request):
    """Error page for 500."""
    response = render(request, "projectile/500.html")
    response.status_code = 500
    return response


def not_found(request):
    """Error page for 404."""
    response = render(request, "projectile/404.html")
    response.status_code = 404
    return response


def home(request):
    """Landing home page after login of student or admin."""
    if request.user.is_authenticated():
        all_projects = Project.objects.all().order_by('-deadline')
        my_projects = []
        working_projects = []

        try:
            applications = request.user.student.applications.filter(
                display=True)
            my_projects = [x.projects.first() for x in applications]
            working_projects = request.user.student.working_on.all()
            print working_projects
        except Exception:
            try:
                prof = Professor.objects.get(user=request.user)
                my_projects = prof.projects_mentored.all().order_by('-deadline')
            except Exception:
                pass

        context = {'user': request.user,
                   'all_projects': all_projects,
                   'my_projects': my_projects,
                   'working_projects': working_projects}

        if is_member(request.user, 'admin'):
            if not contains_group(request.user, 'admin'):
                return HttpResponseRedirect('/newadmin')
            else:
                return render(request, 'projectile/admin_home.html', context)
        else:
            studentgroup = Group.objects.get(name='student')
            if (not is_member(request.user, studentgroup)):
                return HttpResponseRedirect('/newuser')
            return render(request, 'projectile/student_home.html', context)
    return render(request, 'projectile/welcome.html')


@login_required()
def projectapply(request, projectid, appid):
    """Apply for a project, if deadline permits."""
    p = Project.objects.get(pk=projectid)
    if (timezone.now() < p.deadline):
        if (is_eligible(request.user.student, p)['value']):
            a = Application.objects.get(pk=appid)
            request.user.student.applications.add(a)
            a.projects.add(p)

            profs = Professor.objects.filter(projects_mentored=p)
            for prof in profs:
                send('Application received for ' + p.name,

                     'Hey! You have received an application for the project ' +
                     p.name + ' from ' + request.user.student.name +
                     '. You can check the application here - ' +
                     'jobport.iiitd.edu.in/project/' + projectid,

                     settings.EMAIL_HOST,
                     [prof.email],
                     )

            messages.success(request, 'Thanks for applying!')
            return HttpResponseRedirect('/')
        else:
            return render(request, 'projectile/badboy.html')
    else:
        return render(request, 'projectile/latedeadline.html')


@login_required()
def projectwithdraw(request, projectid):
    """Withdraw from the project, if deadline permits."""
    p = Project.objects.get(pk=projectid)
    if (timezone.now() < p.deadline):
        request.user.student.applications.projects.remove(p)
        request.user.student.applications.remove(p)
        messages.success(request, 'You have withdrawn!')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'projectile/latedeadline.html')


@login_required()
def projectpage(request, projectid):
    """Loads the page for a particular Project."""
    if is_admin(request.user):
        p = Project.objects.get(pk=projectid)
        count = 0
        for student in Student.objects.all():
            if is_eligible(student, p)['value']:
                count = count + 1

        applications = p.project_applications.filter(display=True)
        context = {'eligiblestudentcount': count,
                   'applications': applications,
                   'working_students': p.selectedcandidates.all(),
                   'project': p}
        return render(request, 'projectile/admin_project.html', context)
    else:
        p = Project.objects.get(pk=projectid)
        hasapplied = False
        applications = request.user.student.applications.filter(
            display=True)

        for x in applications:
            if x.projects.first().pk == projectid:
                hasapplied = True
                break
        display = True
        if p in request.user.student.working_on.all():
            display = False
        iseligible = is_eligible(request.user.student, p)
        deadlinepassed = checkdeadline(p)
        context = {'user': request.user, 'project': p, 'deadlinepassed': deadlinepassed,
                   'hasapplied': hasapplied, 'iseligible': iseligible['value'],
                   'iseligiblereasons': iseligible['reasons'], 'display': display,
                   'working_students': p.selectedcandidates.all()}
        return render(request, 'projectile/student_projectpage.html', context)


@login_required()
def admineditstudent(request, studentid):
    """Allows admin to change the student details."""
    if is_admin(request.user):
        if request.method == 'POST':
            form = forms.AdminStudentForm(
                request.POST, request.FILES, instance=Student.objects.get(pk=studentid))
            if form.is_valid():
                usr = form.save(commit=False)
                if (request.FILES.__len__() == 0):
                    usr.resume = Student.objects.get(pk=studentid).resume
                else:
                    my_student = Student.objects.get(pk=studentid)
                    usr.resume.name = my_student.course_enrolled + '_' + \
                        my_student.user.username.split('@')[0] + ".pdf"
                    usr.transcript.name = my_student.course_enrolled + '_' + \
                        my_student.user.username.split('@')[0] + ".pdf"
                usr.save()
                form.save_m2m()
                messages.success(request, 'Your form was saved')
                return HttpResponseRedirect('/')
            else:
                messages.error(request, 'Error in form!')
                context = {'form': form}
                return render(request, 'projectile/admin_editstudent.html', context)
        elif request.method == 'GET':
            studentform = forms.AdminStudentForm(
                instance=Student.objects.get(pk=studentid))
            context = {'user': request.user,
                       'form': studentform, 'layout': 'horizontal'}
            return render(request, 'projectile/admin_editstudent.html', context)
        return HttpResponseRedirect('/')
    else:
        return render(request, 'projectile/badboy.html')


@login_required()
def professor_profile(request):
    """Allows editing student profile by themselves."""
    if request.method == 'POST':
        form = forms.ProfessorForm(
            request.POST, request.FILES, instance=request.user.professor)
        if form.is_valid():
            usr = form.save(commit=False)
            usr.user = request.user
            usr.save()
            messages.success(request, 'Your details were saved.')
            return HttpResponseRedirect('/')
        else:
            context = {'form': form}
            return render(request, 'projectile/admin_profile.html', context)
    elif request.method == 'GET':
        studentform = forms.ProfessorForm(instance=request.user.professor)
        context = {'user': request.user,
                   'form': studentform, 'layout': 'horizontal'}
        return render(request, 'projectile/admin_profile.html', context)


@login_required()
def profile(request):
    """Allows editing student profile by themselves."""
    studentgroup = Group.objects.get(name='student')
    if (not is_member(request.user, studentgroup)):
        return HttpResponseRedirect('/newuser')
    if request.method == 'POST':
        form = forms.StudentForm(
            request.POST, request.FILES, instance=request.user.student)
        if form.is_valid():
            usr = form.save(commit=False)
            usr.user = request.user
            if (request.FILES.__len__() == 0):
                usr.resume = request.user.student.resume
            else:
                usr.resume.name = usr.course_enrolled + '_' + \
                    request.user.username.split('@')[0] + ".pdf"
            usr.save()
            messages.success(request, 'Your details were saved.')
            return HttpResponseRedirect('/')
        else:
            context = {'form': form, 'student': request.user.student}
            return render(request, 'projectile/student_profile.html', context)
    elif request.method == 'GET':
        studentform = forms.StudentForm(instance=request.user.student)
        context = {'user': request.user, 'form': studentform, 'layout': 'horizontal',
                   'student': request.user.student}
        return render(request, 'projectile/student_profile.html', context)


def newadmin(request):
    """New User Sign Up form."""
    admingroup, created = Group.objects.get_or_create(
        name='admin')  # Creating user group
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = forms.NewProfessorForm(request.POST, request.FILES)
            if form.is_valid():
                usr = form.save(commit=False)
                usr.user = request.user
                usr.email = request.user.username
                usr.name = request.user.first_name + " " + request.user.last_name
                usr.save()
                admingroup.user_set.add(request.user)
                messages.success(
                    request, 'Your details were saved. Welcome to Projectile.')
                return HttpResponseRedirect('/')
            else:
                context = {'form': form}
                return render(request, 'projectile/newadmin.html', context)
        elif request.method == 'GET':
            prof_form = forms.NewProfessorForm()
            context = {'user': request.user,
                       'form': prof_form, 'layout': 'horizontal'}
            return render(request, 'projectile/newadmin.html', context)
    return HttpResponseRedirect('/')


def newuser(request):
    """New User Sign Up form."""
    studentgroup, created = Group.objects.get_or_create(
        name='student')  # Creating user group
    if request.user.is_authenticated():
        if is_member(request.user, studentgroup):
            HttpResponseRedirect('/')
        if request.method == 'POST':
            form = forms.NewStudentForm(request.POST, request.FILES)
            # print form.cleaned_data
            if form.is_valid():
                usr = form.save(commit=False)
                usr.user = request.user
                usr.email = request.user.username
                usr.name = request.user.first_name + " " + request.user.last_name
                usr.resume.name = request.user.username.split('@')[0] + ".pdf"
                usr.transcript.name = request.user.username.split('@')[
                    0] + ".pdf"
                usr.save()
                studentgroup.user_set.add(request.user)

                messages.success(
                    request, 'Your details were saved. Welcome to Projectile.')
                return HttpResponseRedirect('/')
            else:
                context = {'form': form, 'resume_url': settings.RESUME_URL}
                return render(request, 'projectile/newstudent.html', context)
        elif request.method == 'GET':
            studentform = forms.NewStudentForm()
            context = {'user': request.user, 'form': studentform, 'layout': 'horizontal',
                       'resume_url': settings.RESUME_URL}
            return render(request, 'projectile/newstudent.html', context)
    return HttpResponseRedirect('/')


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')


def needlogin(request):
    """need login"""
    return render(request, 'projectile/needlogin.html')


@login_required()
def openproject(request):
    """Open a new Project from admin side."""
    if is_admin(request.user):
        if request.method == 'POST':
            form = forms.ProjectForm(request.POST, request.FILES)
            if form.is_valid():
                project = form.save(commit=False)
                project.createdon = timezone.now()
                project.save()

                prof = Professor.objects.get(user=request.user)
                prof.projects_mentored.add(project)
                return HttpResponseRedirect('/')
            else:
                context = {'form': form}
                return render(request, 'projectile/openproject.html', context)
        else:
            form = forms.ProjectForm()
            context = {'form': form}
            return render(request, 'projectile/openproject.html', context)
    else:
        return render(request, 'projectile/notallowed.html')


@login_required()
def getresumes(request, projectid):
    """Return resumes for students according to the incoming request."""
    if is_admin(request.user):
        filenames = []
        p = Project.objects.get(pk=projectid)
        if (request.GET.get('req') == 'selected'):
            checklist = p.selectedcandidates.all()
            zip_subdir = p.name + "_Selected_Resumes"
        else:
            checklist = p.project_applications.applicants.all()  # AllApplicants
            zip_subdir = p.name + "_Applicant_Resumes"
        for student in checklist:
            filenames.append(student.resume.path)
        zip_filename = "%s.zip" % zip_subdir
        s = StringIO.StringIO()
        zf = zipfile.ZipFile(s, "w")

        for fpath in filenames:
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            zf.write(fpath, zip_path)
        zf.close()
        resp = HttpResponse(
            s.getvalue(), mimetype="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp
    else:
        return render(request, 'projectport/badboy.html')


@login_required()
def projectapprove(request, projectid, applicantid):
    """Delete a Project from admin side."""
    if is_admin(request.user):
        p = Project.objects.get(pk=projectid)
        a = Application.objects.get(pk=applicantid)
        s = a.applicants.first()
        s.working_on.add(p)
        p.selectedcandidates.add(s)
        a.display = False
        a.save()

        prof = Professor.objects.get(user=request.user)
        send(
            'Congratulations! :D',
            'Your request for the project ' + p.name +
            ' has been approved! You have been shortlisted! ',
            prof.email,
            [s.email, settings.EMAIL_HOST_USER, prof.email]
        )
        messages.success(
            request, 'Project approved!')

    return HttpResponseRedirect('/project/' + projectid)


@login_required()
def projectreject(request, projectid, applicantid):
    """Delete a Project from admin side."""
    if is_admin(request.user):
        p = Project.objects.get(pk=projectid)
        a = Application.objects.get(pk=applicantid)
        s = a.applicants.first()
        s.working_on.add(p)

        a.display = False

        a.save()
        prof = Professor.objects.get(user=request.user)
        send(
            'Sad news! :(',
            'Your request for the project ' + p.name +
            ' has NOT been approved! You have not been shortlisted!' +
            ' Please try again next time :)',
            prof.email,
            [s.email, settings.EMAIL_HOST_USER, prof.email]
        )
        messages.success(
            request, 'Project rejected! Notification sent!')
        return HttpResponseRedirect('/project/' + projectid)


@login_required()
def projectdelete(request, projectid):
    """Delete a Project from admin side."""
    if is_admin(request.user):
        Project.objects.get(pk=projectid).delete()
        return HttpResponseRedirect('/')


@login_required()
def projectedit(request, projectid):
    """Edit Project details from admin side."""
    if is_admin(request.user):
        if request.method == 'POST':
            form = forms.ProjectForm(request.POST, request.FILES,
                                     instance=Project.objects.get(pk=projectid))
            if form.is_valid():
                form.save()  # This does the trick!
                messages.success(request, 'Project was saved')
                return HttpResponseRedirect('/project/' + str(projectid) + '/')
            else:
                context = {'form': form}
                return render(request, 'projectile/admin_editproject.html', context)
        else:
            form = forms.ProjectForm(
                instance=Project.objects.get(pk=projectid))
            c = {'form': form}
            return render(request, 'projectile/admin_editproject.html', c)


def feedback(request):
    """FeedbackForm"""
    if (request.method == 'POST'):
        form = forms.FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            type_ = form.cleaned_data['type']
            type_ = dict(form.fields['type'].choices)[type]
            # settings.EMAIL_HOST_USER += 'Tester@projectile.com'
            send(
                '[' + type_ + '] ' + form.cleaned_data['title'],
                'A new feedback was posted on Projectile' + '\n\n' +
                form.cleaned_data['body'], 'tester@projectile.com', [
                    'projectile.iiitd@gmail.com']
            )
            messages.success(
                request, 'Thanks for filling your precious feedback! :) ')
            return HttpResponseRedirect('/')
        else:
            context = {'form': form}
            return render(request, 'projectile/feedback.html', context)
    else:
        form = forms.FeedbackForm()
        context = {'form': form}
        return render(request, 'projectile/feedback.html', context)


def filter(request):
    return render(request, 'projectile/student_filter_modal.html')


def apply_modal(request, projectid):
    p = Project.objects.get(pk=projectid)

    if (request.method == 'POST'):
        form = forms.ApplicationForm(request.POST)
        if form.is_valid():
            a = form.save()
            return HttpResponseRedirect('/project/' + projectid + '/apply/' + str(a.pk))
        else:
            context = {'form': form, 'project': p}
            return render(request, 'projectile/student_project_apply.html', context)
    else:
        form = forms.ApplicationForm()
        context = {'form': form, 'project': p}
        return render(request, 'projectile/student_project_apply.html', context)


@login_required()
def fileview(request, filename):
    """Protect the resume location, by adding headers, using nginx."""
    response = HttpResponse()
    response['Content-Type'] = 'application/pdf'
    response['X-Accel-Redirect'] = "/protected/%s" % filename
    return response


@login_required()
def docfileview(request, filename):
    """Protect the project file location, by adding headers, using nginx."""
    response = HttpResponse()
    response['Content-Type'] = 'application/pdf'
    response['X-Accel-Redirect'] = "/projectfiles/%s" % filename
    return response


@login_required()
def display_picture(request, filename):
    """Protect the project file location, by adding headers, using nginx."""
    response = HttpResponse()
    # response['Content-Type'] = 'application/pdf'
    response['X-Accel-Redirect'] = "/display_picture/%s" % filename
    return response


@login_required()
def search(request):
    """Search, something. anything."""
    if is_admin(request.user):
        form = forms.RootSearchForm(request.GET)
        query = request.GET.get('q')
        if query == '':
            messages.error(request, 'Please enter a Query!')
            return render(request, 'projectile/notallowed.html')
        else:
            return render(request, 'projectile/result.html',
                          {'search_query': query, 'results': form.search()})
    else:
        return render(request, 'projectile/notallowed.html')  # 403 Error


@login_required()
def profile_modal(request, studid):
    context = {'student': Student.objects.get(pk=studid)}
    return render(request, 'projectile/student_profile_modal.html', context)


@login_required()
def student_professors(request):
    if not is_admin(request.user):
        a = Professor.objects.all()
        ps = request.user.student.working_on.all()
        my = [p.mentors.first for p in ps]
        context = {"all_professors": a, "my_professors": my}
        return render(request, 'projectile/student_professors.html', context)
