# Generated by Django 3.2.7 on 2021-10-15 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sef', '0005_auto_20211015_1910'),
    ]

    operations = [
        migrations.AddField(
            model_name='employersection',
            name='dept_code',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]
