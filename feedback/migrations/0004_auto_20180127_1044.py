# Generated by Django 2.0 on 2018-01-27 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_auto_20180121_1832'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='responseset',
            options={'permissions': (('can_share_feedback', 'Can admin feedback responses'),)},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('email',)},
        ),
        migrations.AddField(
            model_name='user',
            name='feedback_admin',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='feedback.User'),
        ),
    ]
