# Generated by Django 2.0 on 2018-01-06 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('question', models.CharField(max_length=200, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='ResponseSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('respondent', models.EmailField(max_length=254)),
                ('edit_response_url', models.URLField()),
                ('answered_at', models.DateTimeField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('anonymous', models.BooleanField(default=True)),
                ('fun_to_work_with', models.PositiveSmallIntegerField()),
                ('gets_stuff_done', models.PositiveSmallIntegerField()),
                ('work_with', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feedback.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='responses',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feedback.ResponseSet'),
        ),
    ]
