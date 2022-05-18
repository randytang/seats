# Generated by Django 3.2.7 on 2021-10-24 01:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sef', '0015_applicationstatus_email_used'),
    ]

    operations = [
        migrations.CreateModel(
            name='CDCSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verification', models.CharField(blank=True, max_length=4)),
                ('handshake_id', models.CharField(blank=True, max_length=20)),
                ('payroll_sign', models.CharField(blank=True, max_length=20)),
                ('date_linked', models.DateField(blank=True)),
                ('application_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sef.employersection')),
            ],
        ),
    ]