# Generated by Django 2.0 on 2018-02-01 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0005_user_admin_feedback_form'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='responseset',
            options={'permissions': (('can_share_feedback', 'Can admin feedback responses'), ('can_see_all_feedback', 'Can see all feedback'))},
        ),
    ]