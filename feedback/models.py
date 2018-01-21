from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    unique_first_name = models.CharField(max_length=100, null=True)
    active = models.BooleanField(default=True, blank=True)

    active_full_form = models.URLField(null=True, blank=True)
    active_basic_form = models.URLField(null=True, blank=True)
    active_client_form = models.URLField(null=True, blank=True)

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
    receiver = models.ForeignKey("User", on_delete=models.CASCADE, related_name="feedback_receiver")
    giver = models.ForeignKey("User", on_delete=models.CASCADE, related_name="feedback_giver")
    requested_by = models.ForeignKey("User", on_delete=models.CASCADE, related_name="requested_by")
    active_response = models.ForeignKey("ResponseSet", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ("receiver",)
        unique_together = (("receiver", "giver", "requested_by"))

    def __str__(self):
        answered = self.active_response is not None
        return "Request by %s for %s; answered: %s" % (self.receiver, self.giver, answered)


class GoogleForm(models.Model):
    TYPE = (
        ("F", "Full"),
        ("B", "Basic"),
        ("C", "Client"),
    )
    form_id = models.CharField(max_length=500, primary_key=True)
    response_url = models.URLField(null=True)
    form_type = models.CharField(max_length=1, choices=TYPE)
    receiver = models.ForeignKey("User", on_delete=models.CASCADE)
    active = models.BooleanField(default=True, blank=True)
    script_id = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ("receiver",)


class Question(models.Model):
    question = models.CharField(max_length=200, primary_key=True)

    def __str__(self):
        return self.question


class Answer(models.Model):
    response = models.TextField()
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    responses = models.ForeignKey("ResponseSet", models.CASCADE)


class ResponseSet(models.Model):
    receiver = models.ForeignKey("User", on_delete=models.CASCADE, related_name="receiver")
    giver = models.ForeignKey("User", on_delete=models.CASCADE, related_name="giver")
    form = models.ForeignKey("GoogleForm", on_delete=models.CASCADE)
    edit_response_url = models.URLField()
    activated = models.BooleanField(default=False, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, blank=True)
    anonymous = models.BooleanField(default=True, blank=True)

    fun_to_work_with = models.PositiveSmallIntegerField()
    gets_stuff_done = models.PositiveSmallIntegerField()
    work_with = models.CharField(max_length=200)

    def __str__(self):
        return "Response from %s to %s (active: %s)" % (self.giver, self.receiver, self.active)
