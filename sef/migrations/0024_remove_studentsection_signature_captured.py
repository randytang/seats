# Generated by Django 3.2.7 on 2021-11-11 04:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sef', '0023_studentsection_signature_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentsection',
            name='signature_captured',
        ),
    ]
