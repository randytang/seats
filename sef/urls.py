from django.urls import path
from . import views


urlpatterns = [
        path('studentPortion', views.studentForm, name='studentSection'),
        path('completeStudent', views.submit_student_section, name='complete_student'),
        path('employerform/<str:application_id>/<int:dept_code>', views.employerform, name='employerSection'),
        path('completeemployer', views.submit_employer_section, name = 'complete_employer'),
        path('cdcqueue', views.cdcView, name='cdcadmin'),
#        path('viewApplication/<int:app_id>', views.app_details, name = 'app_view'),
        path('viewApplication/<str:app_id>', views.app_details, name = 'app_view'),
        path('studentform/<str:application_id>/<int:dept_code>', views.studentform, name='studentsection'),
        path('notifyform', views.autonotify, name='notificationform'),
        path('sendnotification', views.sendnotice, name='notify'),
        path('employerqueue/<int:dept_code>', views.employerview, name = 'employerportal'),
        path('cdcform/<str:app_id>', views.cdcform, name = 'cdcsection'),
        path('submitcdc', views.submit_cdc_section, name = 'complete_cdc'),
        path('attachments/<str:app_id>', views.viewattachment, name='attachment_view'),
        path('studentprofile/upload/<str:app_id>', views.uploadattachment, name='upload_attachments'),
        path('studentprofile/uploadsubmit/<str:app_id>', views.submitattachments, name='submit_attachments'),
        path('deleteapps', views.delete, name='delete_apps'),
        path('searchqueue', views.searchApps, name='searchapps'),
        path('printapps', views.print_apps_selected, name='print_apps'),
]
