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
from projectile.helpers import is_admin, is_member, is_eligible, checkdeadline, contains_group
from projectile.models import Project, Student


def student_professor(request):
    return render(request, "projectile/student_professor.html")


def professor_addproject(request):
    return render(request, "projectile/professor_addproject.html")


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
        context = {'user': request.user,
                   'projects': Project.objects.all().order_by('-deadline')}

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
def projectapply(request, projectid):
    """Apply for a project, if deadline permits."""
    if (timezone.now() < Project.objects.get(pk=projectid).deadline):
        if (is_eligible(request.user.student, Project.objects.get(pk=projectid))['value']):
            request.user.student.projectapplications.add(
                Project.objects.get(pk=projectid))
            messages.success(request, 'Thanks for applying!')
            return HttpResponseRedirect('/')
        else:
            return render(request, 'projectile/badboy.html')
    else:
        return render(request, 'projectile/latedeadline.html')


@login_required()
def projectwithdraw(request, projectid):
    """Withdraw from the project, if deadline permits."""
    if (timezone.now() < Project.objects.get(pk=projectid).deadline):
        request.user.student.projectapplications.remove(
            Project.objects.get(pk=projectid))
        messages.success(request, 'You have withdrawn!')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'projectile/latedeadline.html')


@login_required()
def myapplications(request):
    """Enumerate student's applications for a project."""
    studentgroup = Group.objects.get(name='student')
    if (not is_member(request.user, studentgroup)):
        return HttpResponseRedirect('/newuser')
    context = {'user': request.user,
               'projects': request.user.student.projectapplications.all()}
    return render(request, 'projectile/applications_student.html', context)


@login_required()
def projectpage(request, projectid):
    """Loads the page for a particular Project."""
    if is_admin(request.user):
        context = {'user': request.user,
                   'project': Project.objects.get(pk=projectid)}
        return render(request, 'projectile/admin_project.html', context)
    else:
        hasapplied = request.user.student.projectapplications.filter(
            pk__contains=projectid).count()
        iseligible = is_eligible(request.user.student,
                                 Project.objects.get(pk=projectid))
        deadlinepassed = checkdeadline(Project.objects.get(pk=projectid))
        context = {'user': request.user, 'project': Project.objects.get(pk=projectid), 'deadlinepassed': deadlinepassed,
                   'hasapplied': hasapplied, 'iseligible': iseligible['value'],
                   'iseligiblereasons': iseligible['reasons']}
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
            form = forms.NewProfessorForm(request.POST)
            if form.is_valid():
                usr = form.save(commit=False)
                usr.user = request.user
                usr.email = request.user.username
                usr.name = request.user.first_name + " " + request.user.last_name
                admingroup.user_set.add(request.user)

                # prof = Professor()
                # prof.website = request.POST.get("website", "")
                # prof.email = usr.email
                # prof.name = usr.name
                # prof.interest_areas = request.POST.get("interest_areas", "")
                # prof.save()

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
            form = forms.ProjectForm(request.POST)
            if form.is_valid():
                tosaveproject = form.save(commit=False)
                tosaveproject.createdon = timezone.now()
                tosaveproject.save()
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
        if (request.GET.get('req') == 'selected'):
            checklist = Project.objects.get(
                pk=projectid).selectedcandidates.all()
            zip_subdir = Project.objects.get(
                pk=projectid).name + "_Selected_Resumes"
        else:
            checklist = Project.objects.get(
                pk=projectid).applicants.all()  # AllApplicants
            zip_subdir = Project.objects.get(
                pk=projectid).name + "_Applicant_Resumes"
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


@login_required()
def projectapplicants(request, projectid):
    """See the applicants for a particular Project."""
    if is_admin(request.user):
        count = 0
        for student in Student.objects.all():
            if is_eligible(student, Project.objects.get(pk=projectid))['value']:
                count = count + 1
        context = {'eligiblestudentcount': count, 'applicants': Project.objects.get(pk=projectid).applicants.all(),
                   'project': Project.objects.get(pk=projectid)}
        return render(request, 'projectile/admin_projectapplicants.html', context)


@login_required()
def adminprojectselected(request, projectid):
    """Select the final students fot the Project :D"""
    if is_admin(request.user):
        if request.method == 'POST':
            form = forms.AdminSelectedApplicantsForm(
                request.POST, instance=Project.objects.get(pk=projectid))
            if form.is_valid():
                tosaveproject = form.save(commit=False)
                tosaveproject.save()
                form.save()
                form.save_m2m()
                for candidate in Project.objects.get(pk=projectid).selectedcandidates.all():
                    candidate.status = 'P'
                    candidate.save()
                return HttpResponseRedirect('/')
            else:
                context = {'form': form}
                return render(request, 'projectile/admin_projectselections.html', context)
        else:
            form = forms.AdminSelectedApplicantsForm(
                instance=Project.objects.get(pk=projectid))
            context = {'selected': Project.objects.get(pk=projectid).selectedcandidates.all(), 'form': form,
                       'project': Project.objects.get(pk=projectid)}
            return render(request, 'projectile/admin_projectselections.html', context)


def feedback(request):
    """FeedbackForm"""
    if (request.method == 'POST'):
        form = forms.FeedbackForm(request.POST)
        # pdb.set_trace()
        if form.is_valid():
            form.save()
            type = form.cleaned_data['type']
            type = dict(form.fields['type'].choices)[type]
            settings.EMAIL_HOST_USER += 'Tester@projectile.iiitd.edu.in'
            # send_mail(
            #     '[' + type + '] ' + form.cleaned_data['title'],
            #     'A new feedback was posted on Projectile' + '\n\n' +
            #     form.cleaned_data['body'], ['projectileiiitd@gmail.com']
            # )
            settings.EMAIL_HOST_USER += ''
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


def apply(request):
    return render(request, 'projectile/student_project_apply.html')


# @login_required()
# def fileview(request, filename):
#     """Protect the resume location, by adding headers, using nginx."""
#     response = HttpResponse()
#     response['Content-Type'] = 'application/png'
#     response['X-Accel-Redirect'] = "/protected/%s" % filename
#     return response


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
def student_professors(request):
    context = Professor.objects.all()
    return render(request, 'projectile/student_professors.html', context)
