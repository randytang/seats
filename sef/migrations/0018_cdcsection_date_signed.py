# Generated by Django 3.2.7 on 2021-10-24 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sef', '0017_alter_cdcsection_date_linked'),
    ]

    operations = [
        migrations.AddField(
            model_name='cdcsection',
            name='date_signed',
            field=models.DateField(blank=True, null=True),
        ),
    ]
