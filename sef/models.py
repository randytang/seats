from django.db import models
import random
import string

from django.db.models.signals import post_save



def update_app_status(sender, **kwargs):
    #   remember, this receiver function/trigger is called only when a new record is saved on the "student section" table, not from "employer section" table.
    #   so we'll have to remember to create a separate/similar update receiver function/trigger for the "employer" table
    new_student_record = kwargs['instance']
    app_id = new_student_record.application
    student_done = True

    if (ApplicationStatus.objects.filter(application_fk=app_id)):
        employer_done = True
    else:
        employer_done = False
    status = "In process"
    new_tracking = ApplicationStatus(application_fk = new_student_record, student_completed = student_done, employer_completed = employer_done, app_status = status)
    new_tracking.save()


class StudentSection(models.Model):

    application = models.CharField(max_length = 6, primary_key = True)
    ric_student = models.CharField(max_length = 7, blank = True)
    last_name = models.CharField(max_length = 20, blank = True)
    first_name = models.CharField(max_length = 20, blank = True)
    m_initial = models.CharField(max_length = 1, blank = True)
    phone_number = models.CharField(max_length = 10, blank = True)
    ric_email = models.EmailField(max_length = 45, blank = True)
    candidate_degree = models.CharField(max_length = 13, blank = True)
    number_credits = models.SmallIntegerField(null = True, blank = True)
    previous_employed = models.BooleanField(blank = True, null = True)
    date_employed = models.CharField(max_length=9, blank = True)
    current_employed = models.BooleanField(blank = True, null = True)
    acceptance = models.BooleanField(blank = True, null = True)
    signature_url = models.TextField(null = True, blank = True)
    date_signed = models.DateField(blank = True, null = True)
    dept_code = models.SmallIntegerField(blank = True, null = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ric_student', 'dept_code'], name='unique_application')
        ]

        indexes = [
                models.Index(fields=['application', 'ric_student', 'last_name', 'first_name']),
            ]

    def __str__(self):
        return self.application + " " + self.last_name + ", " + self.first_name

class EmployerSection(models.Model):
    application_id = models.CharField(max_length = 6, primary_key = True, blank = False)
    agency = models.CharField(max_length = 30, null = True,  blank = True)
    dept_name = models.CharField(max_length = 30, null = True,  blank = True)
    dept_grant_no = models.CharField(max_length = 5, null = True,  blank = False)
    pos_sched = models.CharField(max_length = 10, null = True,  blank = True)
    pos_title = models.CharField(max_length = 30, null = True,  blank = True)
    job_loc = models.CharField(max_length = 30, null = True,  blank = True)
    source_funds = models.CharField(max_length = 20, null = True,  blank = True)
    award_amt = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
    grant_no = models.CharField(max_length = 10, null = True,  blank = True)
    acct_sign = models.CharField(max_length = 20, null = True,  blank = True)
    hire_period = models.CharField(max_length = 15, null = True,  blank = True)
    begin_date = models.DateField(null = True,  blank = True)
    pay_grade = models.CharField(max_length = 10, null = True,  blank = True)
    rate_of_pay = models.DecimalField(max_digits = 5, decimal_places = 2, null = True, blank = True)
    responsible = models.CharField(max_length = 20, null = True,  blank = True)
    resp_title = models.CharField(max_length = 30, null = True,  blank = True)
    signature = models.TextField(null = True,  blank = True)
    name_dept_head = models.CharField(max_length = 20, null = True,  blank = True)
    date_signed = models.DateField(blank = True, null = True)
    dept_code = models.SmallIntegerField(blank = True, null = True)



class ApplicationStatus(models.Model):

    application_fk = models.ForeignKey(
            'StudentSection',
            on_delete=models.CASCADE,
            )
    student_completed = models.BooleanField(null = True, blank = True)
    employer_completed= models.BooleanField(null = True, blank = True)
    app_status = models.CharField(max_length = 15, null = True, blank = True)
    dept_code = models.ForeignKey('Department', on_delete = models.SET_NULL, null = True, blank = True)
    email_used = models.EmailField(max_length = 45, blank = True)


class Department(models.Model):
    code = models.SmallIntegerField(primary_key = True)
    name = models.CharField(max_length = 50, unique = True, null = False)

class CDCSection(models.Model):    
    application_fk = models.ForeignKey(
            'EmployerSection',
            on_delete=models.CASCADE,
            )
    verification = models.CharField(max_length = 4, blank = True)
    handshake_id = models.CharField(max_length = 20, blank = True)
    payroll_sign = models.TextField(null = True, blank = True)
    date_signed = models.DateField(null = True, blank = True)
    date_linked = models.DateField(null = True, blank = True)
    


def studentmedia(instance, filename):
    studentdir = instance.application_fk.first_name[0] + instance.application_fk.last_name + instance.application_fk.ric_student[3:]
    if 'pdf' in filename or 'docx' in filename:
        return '{0}/docs/{1}'.format(studentdir, filename)
    elif 'png' in filename or 'jpg' in filename or 'jpeg' in filename:
        return '{0}/images/{1}'.format(studentdir, filename)

class attachments(models.Model):
    application_fk = models.ForeignKey(
            'StudentSection',
            on_delete=models.CASCADE,
            )
    i9 = models.FileField(upload_to = studentmedia, blank = True)
    identification =models.ImageField(upload_to = studentmedia, blank = True) 
    w4 = models.FileField(upload_to = studentmedia, blank = True) 
    claims = models.FileField(upload_to = studentmedia, blank = True) 
    drug = models.FileField(upload_to = studentmedia, blank = True) 
    schedule = models.ImageField(upload_to = studentmedia, blank = True) 
    work_study = models.ImageField(upload_to = studentmedia, blank = True) 

