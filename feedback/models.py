from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    unique_first_name = models.CharField(max_length=100, null=True)
    active = models.BooleanField(default=True, blank=True)

    @property
    def nick_name(self):
        if self.unique_first_name:
            return self.unique_first_name
        return self.first_name

    @property
    def full_name(self):
        if self.first_name:
            return "%s %s" % (self.first_name, self.last_name)
        else:
            return self.email

    def __str__(self):
        return self.email


class FeedbackRequest(models.Model):
    requester = models.ForeignKey("User", on_delete=models.CASCADE, related_name="requester")
    requestee = models.ForeignKey("User", on_delete=models.CASCADE, related_name="requestee")

    def active_form(self):
        forms = GoogleForm.objects.filter(receiver=self.requester).filter(active=True)
        if len(forms) > 0:
            return forms[0]
        return None

    def active_response(self):
        print(repr(self.requestee))
        response_set = ResponseSet.objects.filter(respondent=self.requestee).filter(active=True)
        if len(response_set) > 0:
            return response_set[0]
        return None


class GoogleForm(models.Model):
    TYPE = (
        ("F", "Full"),
        ("B", "Basic"),
    )
    form_id = models.CharField(max_length=500, primary_key=True)
    response_url = models.URLField(null=True)
    form_type = models.CharField(max_length=1, choices=TYPE)
    receiver = models.ForeignKey("User", on_delete=models.CASCADE)
    active = models.BooleanField(default=True, blank=True)


class Question(models.Model):
    question = models.CharField(max_length=200, primary_key=True)

    def __str__(self):
        return self.question


class Answer(models.Model):
    response = models.TextField()
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    responses = models.ForeignKey("ResponseSet", models.CASCADE)


class ResponseSet(models.Model):
    receiver = models.ForeignKey("User", on_delete=models.CASCADE, related_name="receiver", null=True)
    respondent = models.ForeignKey("User", on_delete=models.CASCADE, related_name="respondent", null=True)
    form = models.ForeignKey("GoogleForm", on_delete=models.CASCADE, null=True)
    edit_response_url = models.URLField()
    activated = models.BooleanField(default=False, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, blank=True)
    anonymous = models.BooleanField(default=True, blank=True)

    fun_to_work_with = models.PositiveSmallIntegerField()
    gets_stuff_done = models.PositiveSmallIntegerField()
    work_with = models.CharField(max_length=200)
