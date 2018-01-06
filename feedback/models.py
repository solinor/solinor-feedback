from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser


class FeedbackUser(AbstractBaseUser):
    slack_id = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=255, unique=True)

    USERNAME_FIELD = 'email'


class SlackChat(models.Model):
    chat_id = models.CharField(max_length=50, primary_key=True, editable=False)
    members = models.ManyToManyField(FeedbackUser)

    def __str__(self):
        return self.chat_id


class Question(models.Model):
    question = models.CharField(max_length=200, primary_key=True)


class Answer(models.Model):
    response = models.TextField()
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    responses = models.ForeignKey("ResponseSet", models.CASCADE)


class ResponseSet(models.Model):
    respondent = models.EmailField()
    edit_response_url = models.URLField()
    answered_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, blank=True)
    anonymous = models.BooleanField(default=True, blank=True)

    fun_to_work_with = models.PositiveSmallIntegerField()
    gets_stuff_done = models.PositiveSmallIntegerField()
    work_with = models.CharField(max_length=200)
