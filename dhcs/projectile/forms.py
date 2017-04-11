# //=======================================================================
# // Copyright Projectile, IIIT Delhi 2017.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================


# __author__ = 'naman'

import haystack.forms
from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.db.models.fields.files import FieldFile
from django.forms import RadioSelect
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from projectile.models import Project, Student, Feedback, Professor

EXTENSIONS = ['pdf']
MAX_UPLOAD_SIZE = "5242880"


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        exclude = ['createdon']
        widgets = {'deadline': DateTimePicker(
            options={"format": "YYYY-MM-DD HH:mm", "pickTime": True})}

    def clean_jobfile(self):
        jobfile = self.cleaned_data['jobfile']
        if type(jobfile) == FieldFile:
            return jobfile
        return jobfile

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if (deadline < timezone.now()):
            raise forms.ValidationError("Deadline cannot be in the Past.")
        return deadline


class AdminSelectedApplicantsForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['selected']

    # widgets = {'CB':forms.CheckBoxSelectMultiple}

    # Representing the many to many related field in Project
    selected = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, queryset=Student.objects.all(),
        required=False)

    # Overriding __init__ here allows us to provide initial
    # data for 'selected' field
    def __init__(self, *args, **kwargs):
        # Only in case we build the form from an instance
        # (otherwise, 'selected' list should be empty)
        forms.ModelForm.__init__(self, *args, **kwargs)
        if 'instance' in kwargs:
            self.fields['selected'].queryset = kwargs[
                'instance'].applicants.all()
            # We get the 'initial' keyword argument or initialize it
            # as a dict if it didn't exist.
            initial = kwargs.setdefault('initial', {})
            # The widget for a ModelMultipleChoiceField expects
            # a list of primary key for the selected data.
            # for t in kwargs['instance'].selectedcandidates.all():
            # print t
            initial['selected'] = [t.pk for t in kwargs[
                'instance'].selectedcandidates.all()]  # applicants.all()]

    # Overriding save allows us to process the value of 'selected' field
    def save(self, commit=True):
        # Get the unsaved Project instance
        instance = forms.ModelForm.save(self, False)

        # Prepare a 'save_m2m' method for the form,
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            # This is where we actually link the selected with job
            instance.selectedcandidates.clear()
            for student in self.cleaned_data['selected']:
                instance.selectedcandidates.add(student)

        self.save_m2m = save_m2m

        # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()

        return instance


class ProfessorForm(forms.ModelForm):

    class Meta:
        model = Professor
        exclude = ['user', 'projects_mentored', 'createdon']


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['cgpa', 'resume', 'transcript',
                  'backlogs', 'display_picture']

    def clean_resume(self):
        cgpa = self.cleaned_data['cgpa']
        if cgpa < 0 or cgpa > 10:
            raise forms.ValidationError(
                'CGPA cannot be negative or greater than 10. Please provide a value between 0 and 10')
        return cgpa

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        resumeext = resume.name.split('.')[-1]
        if type(resume) == FieldFile:
            return resume
        if resumeext in EXTENSIONS:
            if resume._size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Please keep filesize under %s. Current filesize %s') % (
                    filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(resume._size))
        else:
            raise forms.ValidationError('File type is not supported')
        return resume

    def clean_transcript(self):
        transcript = self.cleaned_data['transcript']
        transcriptext = transcript.name.split('.')[-1]
        if type(transcript) == FieldFile:
            return transcript
        if transcriptext in EXTENSIONS:
            if transcript._size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Please keep filesize under %s. Current filesize %s') % (
                    filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(transcript._size))
        else:
            raise forms.ValidationError('File type is not supported')
        return transcript


class NewStudentForm(forms.ModelForm):

    class Meta:
        model = Student
        exclude = ['user', 'email', 'projectapplications', 'status', 'name',
                   'createdon', 'working_on']

    def clean_rollno(self):
        rollno = self.cleaned_data['rollno']
        rollno = rollno.upper()
        if (not rollno.isalnum()):
            raise forms.ValidationError(
                "Roll number should not contain any special characters.")
        return rollno

    def clean_resume(self):
        cgpa = self.cleaned_data['cgpa']
        if cgpa < 0 or cgpa > 10:
            raise forms.ValidationError(
                'CGPA cannot be negative or greater than 10. Please provide a value between 0 and 10')
        return cgpa

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        resumeext = resume.name.split('.')[-1]
        if type(resume) == FieldFile:
            return resume
        if resumeext in EXTENSIONS:
            if resume._size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Please keep filesize under %s. Current filesize %s') % (
                    filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(resume._size))
        else:
            raise forms.ValidationError('File type is not supported')
        return resume

    def clean_transcript(self):
        transcript = self.cleaned_data['transcript']
        transcriptext = transcript.name.split('.')[-1]
        if type(transcript) == FieldFile:
            return transcript
        if transcriptext in EXTENSIONS:
            if transcript._size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Please keep filesize under %s. Current filesize %s') % (
                    filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(transcript._size))
        else:
            raise forms.ValidationError('File type is not supported')
        return transcript


class NewProfessorForm(forms.ModelForm):
    """for NewProfessorForm"""
    class Meta:
        model = Professor
        fields = ['interest_areas', 'website', 'display_picture']


class AdminStudentForm(forms.ModelForm):

    class Meta:
        model = Student
        exclude = ['user']
        widgets = {'gender': RadioSelect(),
                   'projectapplications': forms.CheckboxSelectMultiple}

    def clean_resume(self):
        cgpa = self.cleaned_data['cgpa']
        if cgpa < 0 or cgpa > 10:
            raise forms.ValidationError(
                'CGPA cannot be negative or greater than 10. Please provide a value between 0 and 10')
        return cgpa

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        resumeext = resume.name.split('.')[-1]
        if type(resume) == FieldFile:
            return resume
        if resumeext in EXTENSIONS:
            if resume._size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Please keep filesize under %s. Current filesize %s') % (
                    filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(resume._size))
        else:
            raise forms.ValidationError('File type is not supported')
        return resume

    def clean_transcript(self):
        transcript = self.cleaned_data['transcript']
        transcriptext = transcript.name.split('.')[-1]
        if type(transcript) == FieldFile:
            return transcript
        if transcriptext in EXTENSIONS:
            if transcript._size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Please keep filesize under %s. Current filesize %s') % (
                    filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(transcript._size))
        else:
            raise forms.ValidationError('File type is not supported')
        return transcript


class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Feedback
        widgets = {'type': RadioSelect()}


class RootSearchForm(haystack.forms.SearchForm):

    def no_query_found(self):
        return self.searchqueryset.all()

    def search(self):
        # First, store the SearchQuerySet received from other processing. (the
        # main work is run internally by Haystack here).
        sqs = super(RootSearchForm, self).search()
        # if something goes wrong
        if not self.is_valid():
            return self.no_query_found()
        # you can then adjust the search results and ask for instance to order the results by title
        # sqs = sqs.order_by(title)
        return sqs
