from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.db import Error, connection
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.urls import reverse
import random
import string
import re
import os
import time


from django.db.utils import IntegrityError

from .models import StudentSection
from .models import ApplicationStatus
from .models import EmployerSection
from .models import Department
from .models import CDCSection
from .models import attachments

import logging

from PyPDF2 import PdfFileMerger, PdfFileReader
from fpdf import FPDF
import pdfkit

# Create your views here.

def generateAppID():
    allowed_chars = ''.join((string.ascii_letters, string.digits))
    unique_id = ''.join(random.choice(allowed_chars) for _ in range(6))
    return unique_id


logger = logging.getLogger('django')

def studentForm(request):
    model = StudentSection
    context = {
            'student_app': model,
            'app_id': application_id,
            }
#    return HttpResponse("testing one two")
    return render(request, 'sef/studentForm.html', context)

#   we're going to create a second view function that will hopefully be the more enhanced version of our previous 'studentForm' view function
#   this one will take the 'application_id' parameter
def studentform(request, application_id, dept_code):
    app_id_from_url = application_id
    context = {
            'app_id': app_id_from_url,
            'dept_code': dept_code,
            }
    return render(request, 'sef/studentform.html', context)

def employerform(request, application_id, dept_code):
    context = {
            'app_id': application_id,
            'dept_code': dept_code,
            }
    return render(request, 'sef/employerform.html', context)
#    return HttpResponse("employers fill out section here")

def cdcform(request, app_id):
    context = {}
    context['app_id'] = app_id
    return render(request, 'sef/cdcform.html', context)

def submit_cdc_section(request):
    context = {}
    app_id = request.POST['app_id']
    try:
        cdcrecord = CDCSection.objects.get(application_fk = app_id)
    except ObjectDoesNotExist as no_cdc_record:
        error_msg = no_cdc_record.__str__() + ' Sorry, no record in CDC table was found with that application ID.'
        context['error_message'] = error_msg
        return render(request, 'sef/cdcform.html', context)

    verification = request.POST['verification']
    handshake = request.POST['job_id']
#    signature = request.POST['payroll_sign']
    signature = request.POST['urlInput']
    date_signed = request.POST['date_signed']
    date_linked = request.POST['date_linked']

    cdcrecord.verification = verification
    cdcrecord.handshake_id = handshake
    cdcrecord.payroll_sign = signature
    cdcrecord.date_signed = date_signed
    cdcrecord.date_linked = date_linked

    try:
        cdcrecord.save()
        context['success_message'] = "Successfully updated CDC record."
    except Error as a:
        error_msg = a.__str__() + ' Sorry, could not update CDC record for some reason. Please try again.'
        context['error_message'] = error_msg
        return render(request, 'sef/cdcform.html', context)

    return render(request, 'sef/cdcform.html', context)


def submit_employer_section(request):
    context = {}
    app_id = request.POST['app_id']
    try:
        existing_employer_record = EmployerSection.objects.get(application_id = app_id)
    except ObjectDoesNotExist as no_employer_record:
        context['error'] = no_employer_record.__str__()
        return render(request, 'sef/employerform_error.html', context)
    dept_code = request.POST['dept_code']
    try:
        agency = request.POST['agency_name']
    except KeyError as a:
        agency = None
    try:
        dept_name = request.POST['dept_name']
    except KeyError as b:
        dept_name = None
    try:
        dept_grant_no = request.POST['dept_grant_no']
    except KeyError as c:
        dept_grant_no = None
    
    position_sched = request.POST['position_sched']
    pos_title = request.POST['position_title']
    job_loc = request.POST['job_location']
    source_funds = request.POST['source']
    
    award = request.POST['award_amt']
    if (award):
        award = float(award)
    else:
        award = 0.00
    try:
        grant = request.POST['grant_no']
    except KeyError as e:
        grant = None
    try:
        acct_sign = request.POST['grant_signature']
    except KeyError as f:
        acct_sign = None

    hire_period = request.POST['hire_period']

    try:
        begin = request.POST['begin_date']
    except KeyError as g:
        begin = None

    pay_grade = request.POST['pay_grade']
    rate = request.POST['rate_of_pay']
    if (rate):
        rate = float(rate)
    else:
        rate = 0.00
    responsible = request.POST['resp']
    title = request.POST['title']
#    signature = request.POST['signature']
    signature = request.POST['urlInput']
    name_depthead = request.POST['dept_head_name']
    date_signed = request.POST['date_signed']
    

    existing_employer_record.agency = agency
    existing_employer_record.dept_name = dept_name
    existing_employer_record.dept_grant_no = dept_grant_no
    existing_employer_record.pos_sched = position_sched
    existing_employer_record.pos_title = pos_title
    existing_employer_record.job_loc = job_loc
    existing_employer_record.source_funds = source_funds
    existing_employer_record.award_amt = award
    existing_employer_record.grant_no = grant
    existing_employer_record.acct_sign = acct_sign
    existing_employer_record.hire_period = hire_period
    existing_employer_record.begin_date = begin
    existing_employer_record.pay_grade = pay_grade
    existing_employer_record.rate_of_pay = rate
    existing_employer_record.responsible = responsible
    existing_employer_record.resp_title = title
    existing_employer_record.signature = signature
    existing_employer_record.name_dept_head = name_depthead
    existing_employer_record.date_signed = date_signed

    try:
#       employer_record = EmployerSection(**model_params)
#   actually, instead of creating a new record, we just have to update the existing record created by the 'notifyform' view.

        existing_employer_record.save()
        context['success'] = "Updated record in sef_employersection table. "
    except Error as a:
        error_msg = a.__str__()
        context['original_url'] = 'employerform/' + app_id + '/' + dept_code
        context['error'] = error_msg + " Sorry, couldn't update sef_employersection record for some reason"
        return (request, 'sef/employerform_result.html', context)

    app_status_to_update = ApplicationStatus.objects.get(application_fk = app_id)
    try:
        app_status_to_update.employer_completed = 1
        if (app_status_to_update.student_completed):
            app_status_to_update.app_status = "CDC reviewing"
        else:
            app_status_to_update.app_status = "In process"
        app_status_to_update.save()
        context['success'] += "Also updated record in sef_applicationstatus table. "
    except Error as b:
        error_msg = b.__str__()
        context['error'] = error_msg + " Sorry, couldn't update sef_applicationstatus table for some reason."
        context['original_url'] = 'employerform/' + app_id + '/' + dept_code
        return render(request, 'sef/employerform_result.html', context)

    return render(request, 'sef/employerform_result.html', context)

def submit_student_section(request):
    context = {
            }

    application_id = request.POST['app_id']
    student_to_update = StudentSection.objects.get(application = application_id)     
    app_status_to_update = ApplicationStatus.objects.get(application_fk = application_id)

    department_code = request.POST['dept_code']
    last_name = request.POST['l_name']
    
    stringResponse = "thanks %s." % last_name
    
    first_name = request.POST['f_name']
    try:
        middle_initial = request.POST['mi']
    except KeyError as a:
        # maybe i should initialize middle_initial = None but im unsure
        # if we could pass None to the database. will it just save as "Null"?
        # lol, someone on stack overflow said just return None so i'll initialize it to None.
        middle_initial = None
    ric_id = request.POST['ric_student_id']
    phone_number = request.POST['p_number']
    ric_email = request.POST['email']
    candidacy = request.POST['candidacy']
    no_credits = request.POST['number_credits']
    previous_employed = request.POST['previous_emp']
    current_employment = request.POST['current_emp']
    accepted = 1
#    signature = request.POST['signed']
    signature = request.POST['urlInput']
    date_signed = request.POST['date_student_signed']

#    try:
#        candidacy = request.POST['ugrad_box']
#    except KeyError as b:
#        try:
#            candidacy = request.POST['grad_box']
#        except KeyError as c:
#            error_message = "sorry, you have to select an option for candidacy."
#            context['error_message'] = error_message
#            return render(request, 'sef/studentForm.html', context)
#           lol, using 'redirect' below vs 'render' in above line because it was sending using to incorrect view 'sef/studentForm.html', 
#           instead we want to redirect student back to form but also with prepopulated app_id and dept_code so url 'studentform/app_id/dept_code'.
#           lol but we won't anticipate this sort of error checking and redirecting because we're going to change this input element from a checkbox
#           to a more appropriate input element of radio because it forces selection of only 1 selection i think. same with the other checkbox input elements.
#           but other reason why i wanted to use 'redirect' was to test using the method as i don't think i've used it before.
#            return redirect('studentform/' + application_id + '/' + department_code, error_message)
#        pass


    try:
        d_employed = request.POST['date_employed']
    except KeyError as f:
        d_employed = None


    #   i want to possibly set up a dictionary containing all the fields-value pairs
    #   so i can either log this dictionary or serialize it for logging/debugging purposes.
    #   we can also possible pass this dictionary to StudentSection as an argument to save lines
    #   and or make code more readable.

#    form_dict = {
#            'application': application_id,
#            'dept_code': department_code,
#            'ric_student': ric_id,
#            'last_name': last_name,
#            'first_name': first_name,
#            'm_initial': middle_initial,
#            'phone_number': phone_number,
#            'ric_email': ric_email,
#            'candidate_degree': candidacy,
#            'number_credits': no_credits,
#            'previous_employed': previous_employed,
#            'date_employed': d_employed,
#            'current_employed': current_employment,
#            'acceptance': accepted,
#            'signature_captured': signature,
#            'date_signed': date_signed
#            }
#    stringified_form_dict = '('
#    for k, v in form_dict.items():
#        stringified_form_dict += k + ": " + str(v) + ", "
#    stringified_form_dict += ')'
#    logger.warning(f'values before trying to save() to StudentSection table {stringified_form_dict}')
    
#    new_student_application = StudentSection(**form_dict)
#   since we're going to now attempt to update an existing record in the database, we now have to use the instance.attribute notation rather than call "StudentSection()" method.
    try:
        student_to_update.last_name = last_name
        student_to_update.first_name = first_name
        student_to_update.m_initial = middle_initial
        student_to_update.phone_number = phone_number
        student_to_update.ric_email = ric_email
        student_to_update.candidate_degree = candidacy
        student_to_update.number_credits = no_credits
        student_to_update.previous_employed = previous_employed
        student_to_update.date_employed = d_employed
        student_to_update.current_employed = current_employment
        student_to_update.acceptance = accepted
        student_to_update.signature_url = signature
        student_to_update.date_signed = date_signed
#        new_student_application.save()
        student_to_update.save()
#        logger.debug('successfully saved a new record to StudentSection db')
        logger.debug('successfully updated existing record in StudentSection db')
    except IntegrityError as j:
        logger.critical('failed to update record in StudentSection db: {0}'.format(j))
        error_as_string = j.__str__()
        if ('unique' in error_as_string):
            context['error_message'] = "sorry, couldn't save record to database possibly because student has already completed/submitted an application for same department/employer. Double check the student ID and department code. If updating/submitting another application for same department, please contact responsible person in department"
            context['original_url'] = 'studentform/' + application_id + '/' + department_code
        return render(request, 'sef/error_on_save.html', context)

    try:
        app_status_to_update.student_completed = 1
        if (app_status_to_update.employer_completed == 1):
            app_status_to_update.app_status = "CDC reviewing"
        else:
            app_status_to_update.app_status = "In process"
        app_status_to_update.save()
    except Error as k:
        context['error_message'] += k.__str__()
        return render(request, 'sef/error_on_save.html', context)


    return HttpResponse("Success, double check database for new application.")



def cdcView(request):
#    applications_list = StudentSection.objects.all()
#   lol, i actually used the wrong model, it should be "ApplicationStatus"
#   not StudentSection. don't forget to import the appropriate model as well
    applications_list = ApplicationStatus.objects.all()
#    application_status = ApplicationStatus.objects.all()
#   we got a "NameError" when navigating to this view
#   stating "name 'ApplicationStatus' is not defined, 
#   showing line 105 in the "Traceback" which made me realize
#   we never import the model "ApplicationStatus" but we
#   actually don't need this model as django is able to 
#   do "joins" or queries that span multiple/related tables.
#   so we really just need "StudentSection" model.

#    output = '\n'.join([app.application + " " + app.last_name + " " + app.first_name for app in applications_list])  
#    template = loader.get_template('sef/cdc_queue.html')
    context = {
            'apps_list': applications_list,
#            'app_status': application_status,
            }
#    return HttpResponse("career development admin view\n" + output)
#    return HttpResponse(template.render(context, request))
    return render(request, 'sef/cdc_queue.html', context)

def employerview(request, dept_code):
    return HttpResponse('employer portal')


def app_details(request, app_id):
    context = {}
    try:
        student_section = StudentSection.objects.get(application = app_id)
        context['student_record'] = student_section
    except ObjectDoesNotExist as no_student_found:
        context['error_msg'] = no_student_found.__str__() + " Sorry, couldn't find a student record with that application ID"
        context['apps_list'] = ApplicationStatus.objects.all()
        return render(request, 'sef/cdc_queue.html', context)
    try:
        employer_section = EmployerSection.objects.get(application_id = app_id)
        context['employer_record'] = employer_section
    except ObjectDoesNotExist as no_employer_found:
        context['error_msg'] += no_employer_found.__str__() + " Sorry, couldn't find an employer record with that application ID"
        context['apps_list'] = ApplicationStatus.objects.all()
        return render(request, 'sef/cdc_queue.html', context)
    try:
        cdc_section = CDCSection.objects.get(application_fk = app_id)
        context['cdc_record'] = cdc_section
    except ObjectDoesNotExist as no_cdc_record:
        context['error_msg'] += no_cdc_record.__str__() + " Sorry, couldn't find a cdc record with that application ID"
        context['apps_list'] = ApplicationStatus.objects.all()
        return render(request, 'sef/cdc_queue.html', context)
    
    return render(request, 'sef/application_details.html', context)

def autonotify(request):
    return render(request, 'sef/notification.html')

def sendnotice(request):
    app_id = generateAppID()
    student_id = request.POST['student_id']
    student_email = request.POST['student_email']
    dept_code = int(request.POST['dept_code'])

    context = {}

#   in this below try/except block, we are essentially trying to make sure the department exists first in our department model/table. and we want to check this before actually saving a student record as we don't want a student record created before we find out we dont have the right department as the student record also depends on the department which we also pass in when we are creating a student record.
    try:
        dept_match = Department.objects.get(code = dept_code)
    except ObjectDoesNotExist as no_dept_found:
        context['error_message'] = no_dept_found.__str__() + ' Sorry, that department code was not found in our database.'
        return render(request, 'sef/notifyform_error.html', context)

    try:
        student_record = StudentSection(application=app_id, ric_student = student_id, ric_email = student_email, dept_code = dept_code)
        student_record.save()
        success_msg = "created record in student_section table. notified student. "
        context['success_message'] = success_msg
    except IntegrityError as a:
        error_msg = a.__str__()
        if ('unique' in error_msg):
            context['error_message'] = "sorry, couldn't save record to database possibly because student has already completed/submitted an application for same department/employer. Double check the student ID and department code. If updating/submitting another application for same department, please contact responsible person in department"
            return render(request, 'sef/notifyform_error.html', context)
#   is there any point in putting a "return" statement in this "if" clause if we're returning the same thing at the end of the function?
#   i'm thinking we probably should return from the above "except" clause because we allow the code to run through completion, it may attempt to create an "ApplicationStatus" record.
        else:
            pass
#   and if we're just "passing" in the "else" clause, do we even need an "else" clause?

    try:
        application_status_record = ApplicationStatus(application_fk = student_record, app_status = "Notified", dept_code = dept_match, email_used = student_email)
        application_status_record.save()
        success_msg = "created record in application_status table. "
        context['success_message'] += success_msg
    except IntegrityError as b:
        error_msg = b.__str__()
        context['error_message'] = error_msg
        return render(request, 'sef/notifyform_error.html', context)


#   this section below is to add a new record to sef_employersection table so that in our employer_submit_section view
#   we are updating an existing record that we have created/added from code below
    employer_section_record = EmployerSection(application_id = app_id, dept_code = dept_code)
    try:
        employer_section_record.save()
        context['success_message'] += "Created a new record in sef_employersection table. "
    except Error as c:
        error_msg = c.__str__()
        context['error_message'] = error_msg + " Sorry, couldn't create a new record in sef_employersection table for some reason"
        return render(request, 'sef/notifyform_error.html', context)

    cdc_record = CDCSection(application_fk = employer_section_record)
    try:
        cdc_record.save()
        context['success_message'] += "Created a new record in sef_cdcsection table. "
    except Error as d:
        error_msg = d.__str__()
        context['error_message'] = error_msg + " Sorry, couldn't create a new record in sef_cdcsection table for some reason"
        return render(request, 'sef/notifyform_error.html', context)

    generated_url = 'studentform/' + app_id + '/' + str(dept_code)
    context['url_for_student'] = generated_url

#   i have to remember to also generate url for employer to navigate them to fill out their section just as we did above for student url. but right now i 
#   have to make certain our employer section is submitted with no issues and that the application_status table gets updated accordingly.
    employer_url = 'employerform/' + app_id + '/' + str(dept_code)
    context['employer_url'] = employer_url

    cdc_url = 'cdcform/' + app_id
    context['cdc_url'] = cdc_url

#   studentfolder = attachments(application_fk = app_id)
#   we kept getting an error saying we have to pass in a 'StudentSection' instance. this is where i have to debate how decoupled i want this web app to make it easier or minimize complexity.
    studentfolder = attachments(application_fk = student_record)

    try:
        studentfolder.save()
        context['success_message'] += "Created a new record in sef_attachments table. "
    except Error as e:
        error_msg = e.__str__()
        context['error_message'] = error_msg + " Sorry, couldn't create a new record in sef_attachments table for some reason"
        return render(request, 'sef/notifyform_error.html', context)

    return render(request, 'sef/notifyform_success.html', context)


def viewattachment(request, app_id):
    context= {}
    try:
        attachment = attachments.objects.get(application_fk = app_id)
        context['attachment'] = attachment
    except ObjectDoesNotExist as a:
        context['apps_list'] = ApplicationStatus.objects.all()
        context['error_msg'] = " Sorry, no record in attachments table found for that application ID."
        return render(request, 'sef/cdc_queue.html', context)
    return render(request, 'sef/attachments.html', context)

def uploadattachment(request, app_id):
    context = {}
    context['app_id'] = app_id
    return render(request, 'sef/uploadattachments.html', context)

def submitattachments(request, app_id):
    context = {}
    context['app_id'] = app_id
    try:
        studentprofile = attachments.objects.get(application_fk = app_id)
    except ObjectDoesNotExist as a:
        context['error_message'] = 'sorry, that student profile doesn"t exist. Please try again with a correct application ID.'
        return render(request, 'sef/uploadattachments.html', context)


    try:
        studentprofile.i9 = request.FILES['i9']
    except KeyError as b:
#   the reason why we're passing in the except clauses is because we're calling ".save()" on an EXISTING record, not a new instance/object of the table so we don't need to actually call the table/model's constructor and pass in keyword arguments. so we don't have to worry about passing in "None" values because we're not passing any arguments. We're just assigning and then calling '.save()'.
        pass

    try:
        studentprofile.identification = request.FILES['identification']
    except KeyError as c:
        pass

    try:
        studentprofile.w4 = request.FILES['w4']
    except KeyError as d:
        pass

    try:
        studentprofile.claims = request.FILES['barclaims']
    except KeyError as e:
        pass

    try:
        studentprofile.drug = request.FILES['drug_free']
    except KeyError as f:
        pass

    try:
        studentprofile.schedule = request.FILES['class_sched']
    except KeyError as g:
        pass

    try:
        studentprofile.work_study = request.FILES['work_study']
    except KeyError as h:
        pass

    try:
        studentprofile.save()
    except IndexError as i:
        context['error_message'] = "sorry, you might be trying to upload attachments before completing the student section of the SEF form. Please complete student section before uploading any attachments. Thank you"
#        return redirect(reverse('upload_attachments', kwargs={'app_id': app_id}))
        return render(request, 'sef/uploadattachments.html', context)
    except Error as j:
        context['error_message'] = 'sorry, couldn"t update student attachments for some reason'
        return render(request, 'sef/uploadattachments.html', context)

    return redirect(reverse('attachment_view', kwargs={'app_id': app_id}))

    

def delete(request):
    selected = request.POST.getlist('selectedApplication')
    for checked in selected:
        with connection.cursor() as cursor:
                cursor.execute("DELETE from sef_applicationstatus WHERE application_fk_id = %s", [checked])
                cursor.execute("DELETE from sef_cdcsection WHERE application_fk_id = %s", [checked])
                cursor.execute("DELETE from sef_employersection WHERE application_id = %s", [checked])
                cursor.execute("DELETE from sef_attachments WHERE application_fk_id = %s", [checked])
                cursor.execute("DELETE from sef_studentsection WHERE application = %s", [checked])

    applications_list = ApplicationStatus.objects.all()
    context = {
            'apps_list': applications_list,
            }
    return render(request, 'sef/cdc_queue.html', context)


def searchApps(request):
    context = {}
    uInput = request.GET['qinput']
    app_id_pattern = re.compile(r"\w{1,6}", re.ASCII)
    ric_id_pattern = re.compile(r"\d{1,7}", re.ASCII)
    name_pattern = re.compile(r"[a-zA-Z]+")
    app_id_match = app_id_pattern.fullmatch(uInput)
    ric_id_match = ric_id_pattern.fullmatch(uInput)
    name_match = name_pattern.fullmatch(uInput)
    if app_id_match or ric_id_match or name_match:
        records = ApplicationStatus.objects.filter(Q(application_fk__first_name__icontains=uInput) | Q(application_fk__last_name__icontains=uInput) | Q(application_fk__application__icontains=uInput) | Q(application_fk__ric_student__icontains=uInput) | Q(application_fk__application__icontains=uInput))
        context['apps_list'] = records
    else:
        context['apps_list'] = ApplicationStatus.objects.all()
        context['error_msg'] = "No records found with that student ID, application ID, student's last/first name."

    return render(request, 'sef/cdc_queue.html', context)


def convert_sef_to_pdf(app_id):
    #   when we deploy to production, we'll have to change the url we're passing to call to pdfkit.from_url
    #   right now, we're just using local urls.
    #   but i wonder if django has a shortcut to generate the url from our urls.py instead of hardcoding the url
    #   just like how we call 'url' in django templates, can we do that in views?
    #   design decision, where should we store the converted/merged pdf files? maybe in a directory django already has access to which is the directory we use to serve/store uploaded attachments.
    #app_record = ApplicationStatus.objects.get(application_fk_id = app_id)
    dir_to_save = settings.MEDIA_ROOT + 'converted_pdfs'
    try:
        os.mkdir(dir_to_save)
    except FileExistsError:
        pass
    except PermissionError:
        logger.critical("Incorrect permissions to create directory to save converted pdf. Don't forget to give 'django' group 'write' permissions on the dir_to_save directory.")
        return
    filename = dir_to_save + '/' + app_id + '_sef.pdf'
    root_domain = 'http://127.0.0.1:8000'
    try:
        pdfkit.from_url(root_domain + reverse('app_view', kwargs={'app_id': app_id}), filename)
    except OSError:
        logger.critical("Probably forgot to install 'wkhtmltopdf'. If on debian/ubuntu, run 'sudo apt-get install wkhtmltopdf'. ")
    return filename

def print_apps_selected(request):
    selected = request.POST.getlist('selectedApplication')
    list_selected = []
    for app in selected:
        list_selected.append(convert_sef_to_pdf(app))
    merged_pdfs = PdfFileMerger()
    for filename in list_selected:
        merged_pdfs.append(PdfFileReader(filename, 'rb'))
    dir_to_save = settings.MEDIA_ROOT + 'merged_pdfs'
    try:
        os.mkdir(dir_to_save)
    except FileExistsError:
        pass
    pdf_name = str(time.time()) + '_.pdf'
    path_final_pdf = dir_to_save + '/out_' + pdf_name
    merged_pdfs.write(path_final_pdf)
    return FileResponse(open(path_final_pdf, 'rb'), as_attachment=True, filename=pdf_name)

