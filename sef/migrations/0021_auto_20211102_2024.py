# Generated by Django 3.2.7 on 2021-11-02 20:24

from django.db import migrations, models
import django.db.models.deletion
import sef.models


class Migration(migrations.Migration):

    dependencies = [
        ('sef', '0020_auto_20211029_0518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachments',
            name='application_fk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sef.studentsection'),
        ),
        migrations.AlterField(
            model_name='attachments',
            name='claims',
            field=models.FileField(blank=True, upload_to=sef.models.studentmedia),
        ),
        migrations.AlterField(
            model_name='attachments',
            name='drug',
            field=models.FileField(blank=True, upload_to=sef.models.studentmedia),
        ),
        migrations.AlterField(
            model_name='attachments',
            name='i9',
            field=models.FileField(blank=True, upload_to=sef.models.studentmedia),
        ),
        migrations.AlterField(
            model_name='attachments',
            name='identification',
            field=models.FileField(blank=True, upload_to=sef.models.studentmedia),
        ),
        migrations.AlterField(
            model_name='attachments',
            name='schedule',
            field=models.FileField(blank=True, upload_to=sef.models.studentmedia),
        ),
        migrations.AlterField(
            model_name='attachments',
            name='w4',
            field=models.FileField(blank=True, upload_to=sef.models.studentmedia),
        ),
        migrations.AlterField(
            model_name='attachments',
            name='work_study',
            field=models.FileField(blank=True, upload_to=sef.models.studentmedia),
        ),
    ]
