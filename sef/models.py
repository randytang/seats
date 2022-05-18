from django.db import models
import random
import string

from django.db.models.signals import post_save
#from .signals import update_app_status


def update_app_status(sender, **kwargs):
    #   remember, this receiver function/trigger is called only when a new record is saved on the "student section" table, not from "employer section" table.
    #   so we'll have to remember to create a separate/similar update receiver function/trigger for the "employer" table
    new_student_record = kwargs['instance']
    app_id = new_student_record.application
    student_done = True
    #   ok, i think i figured it out, when a student submits an app, this receiver function will find an existing app id regardless because it's the 
    #   employer that initiates and generates the app_id and when they do, it should also trigger a new record in the 'applicationStatus' table, even 
    #   if the employer doesn't finish their section. So when the student completes theirs first, it'll check if an existing app id exists which
    #   it should find, and when, not if, it will make "student_done" = True, everytime. We don't have to have this "if" block below us as it doesn't
    #   matter, we just have to modify/adjust our ORM's call instead of creating a new record, it will alter/update the existing record to indicate
    #   the student has completed their section. So instead of checking for an existing app-id, it looks/queries for the app-id, and updates/alters it
    #   to reflect which sections have been completed.
    if (ApplicationStatus.objects.filter(application_fk=app_id)):
        employer_done = True
    else:
        employer_done = False
    status = "In process"
    new_tracking = ApplicationStatus(application_fk = new_student_record, student_completed = student_done, employer_completed = employer_done, app_status = status)
    new_tracking.save()
#    print(app_id, new_student_record.last_name, new_student_record.first_name)
    


# Create your models here.

class StudentSection(models.Model):

#    candidate_options = [
#            ('UNDERGRADUATE', 'undergraduate degree'),
#            ('GRADUATE', 'graduate degree'),
#            ]

    application = models.CharField(max_length = 6, primary_key = True)
#    ric_student = models.CharField(unique = True, max_length = 7, blank = True)
#   we actually, don't need to make ric_student a 'unique' field because a student can actually have multiple applications so long as each is for a different department
#   so we only need to create a multicolumn index/primary key for both ric_student and dept_code but since django doesn't support multi-column index/primary key insofar as i know
#   we'll have to use what django does support which is "UniqueConstraint" and see if that works. So we unset 'unique = True' for ric_student field.
    ric_student = models.CharField(max_length = 7, blank = True)
    last_name = models.CharField(max_length = 20, blank = True)
    first_name = models.CharField(max_length = 20, blank = True)
    m_initial = models.CharField(max_length = 1, blank = True)
#    phone_number = models.CharField(max_length = 10, unique = True, blank = True)
#   lol, same with 'phone_number' and 'email' field. we don't have to make it unique like ric_student because same student can have multiple applications so long as each is for different dept.
    phone_number = models.CharField(max_length = 10, blank = True)
#    ric_email = models.EmailField(unique = True, max_length = 45, blank = True)
    ric_email = models.EmailField(max_length = 45, blank = True)


#    candidate_degree = models.CharField(choices = candidate_options)
#   i think instead of setting the choices on the model's field above, we
#   can instead set choices on the widget which will pass the appropriate value
#   when we're handling the data/request from the forms view.
    candidate_degree = models.CharField(max_length = 13, blank = True)
    number_credits = models.SmallIntegerField(null = True, blank = True)
    previous_employed = models.BooleanField(blank = True, null = True)
    date_employed = models.CharField(max_length=9, blank = True)
    current_employed = models.BooleanField(blank = True, null = True)
    acceptance = models.BooleanField(blank = True, null = True)
#   i think for now, because we dont know yet how to implement this
#   we'll set null and blank to true.
#    signature_captured = models.BinaryField(null = True, blank = True)
#    signature_captured = models.CharField(max_length = 20, blank = True)
    signature_url = models.TextField(null = True, blank = True)
    date_signed = models.DateField(blank = True, null = True)
    dept_code = models.SmallIntegerField(blank = True, null = True)
#    dept_code = models.ForeignKey("Department", null = True, on_delete = models.SET_NULL) 

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
#    award_amt = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
    award_amt = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
    grant_no = models.CharField(max_length = 10, null = True,  blank = True)
    acct_sign = models.CharField(max_length = 20, null = True,  blank = True)
    hire_period = models.CharField(max_length = 15, null = True,  blank = True)
    begin_date = models.DateField(null = True,  blank = True)
    pay_grade = models.CharField(max_length = 10, null = True,  blank = True)
    rate_of_pay = models.DecimalField(max_digits = 5, decimal_places = 2, null = True, blank = True)
    responsible = models.CharField(max_length = 20, null = True,  blank = True)
    resp_title = models.CharField(max_length = 30, null = True,  blank = True)
#    signature = models.CharField(max_length = 20, null = True,  blank = True)
    signature = models.TextField(null = True,  blank = True)
    name_dept_head = models.CharField(max_length = 20, null = True,  blank = True)
    date_signed = models.DateField(blank = True, null = True)

#   im going to add a new field/attribute to this model 'dept_code' because im not yet sure if 'dept_code' is the same thing as 'dept_grant_no' ill have to ask demetria
    dept_code = models.SmallIntegerField(blank = True, null = True)



class ApplicationStatus(models.Model):
#   i'm thinking of making 'application_fk' no longer a foreign key 
#   the primary reason for this is because the 'application id' can 
#   be generated either from the student completing and submitting their 
#   section or from the employer notifying the student. So maybe
#   we should decouple this field from the parent table "StudentSection"?
#   as this field is going to depend on both the "app id" in "StudentSection"
#   and/or "EmployerSection".
#   just remember, if we do decouple this, remember to update/modify the
#   receiver function "update_app_status" to make sure we're creating a new 
#   record for this database appropriately as "application_fk" will no longer
#   be taking an object/instance, but rather a string of the app id.
    application_fk = models.ForeignKey(
            'StudentSection',
            on_delete=models.CASCADE,
            )
    student_completed = models.BooleanField(null = True, blank = True)
    employer_completed= models.BooleanField(null = True, blank = True)
    app_status = models.CharField(max_length = 15, null = True, blank = True)
    dept_code = models.ForeignKey('Department', on_delete = models.SET_NULL, null = True, blank = True)
    email_used = models.EmailField(max_length = 45, blank = True)



#post_save.connect(receiver=update_app_status, sender=StudentSection)


class Department(models.Model):
    code = models.SmallIntegerField(primary_key = True)
    name = models.CharField(max_length = 50, unique = True, null = False)
#   i think we're going to set a "UniqueConstraint" for these 2 fields above because django only allows one primary key for each model and/or doesn't support multi column primary keys/indexes. 
#   actually, on second thought, i don't think we need a uniqueConstraint. what we actually need is to just to make sure there are no duplicate entries of the department name. if someone is trying to add the same department name, they may be trying to map a new department code. so we are correct in setting the the 'code' field to primary key to make sure its unique, and its also correct to set 'name' field as 'unique' so there's no duplicates. 
#    class Meta:
#        constraints = [
#            models.UniqueConstraint(fields=['code', 'name'], name='unique_dept')
#        ]

class CDCSection(models.Model):    
    application_fk = models.ForeignKey(
            'EmployerSection',
            on_delete=models.CASCADE,
            )
    verification = models.CharField(max_length = 4, blank = True)
    handshake_id = models.CharField(max_length = 20, blank = True)
#    payroll_sign = models.CharField(max_length = 20, blank = True)
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
#            'EmployerSection',
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

