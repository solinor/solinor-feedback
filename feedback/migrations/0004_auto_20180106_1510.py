# Generated by Django 2.0 on 2018-01-06 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_auto_20180106_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleForm',
            fields=[
                ('form_id', models.CharField(max_length=500, primary_key=True, serialize=False)),
                ('form_type', models.CharField(choices=[('F', 'Full'), ('B', 'Basic')], max_length=1)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='googleform',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feedback.User'),
        ),
        migrations.AddField(
            model_name='responseset',
            name='form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='feedback.GoogleForm'),
        ),
    ]
