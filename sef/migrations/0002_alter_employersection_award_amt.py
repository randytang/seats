# Generated by Django 3.2.7 on 2021-10-15 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sef', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employersection',
            name='award_amt',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]