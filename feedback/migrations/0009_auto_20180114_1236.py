# Generated by Django 2.0 on 2018-01-14 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0008_auto_20180114_1234'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='feedbackrequest',
            unique_together={('requester', 'requestee')},
        ),
    ]
