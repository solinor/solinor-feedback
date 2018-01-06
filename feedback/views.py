import json

import schema
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction

from feedback.models import *

response_schema = schema.Schema({
    "sharedSecret": schema.And(str, len),
    "respondent": schema.And(str, len, lambda s: "@" in s),
    "editUrl": schema.And(str, len),
    "responses": [
        {
            "question": schema.And(str, len),
            "answer": str,
        }
    ]
})

forms_schema = schema.Schema({
    "sharedSecret": schema.And(str, len),
    "items": [
        {
            "id": schema.And(str, len),
            "email": schema.And(str, len, lambda s: "@" in s),
            "type": schema.And(str, len),
        }
    ],
})


@login_required
def frontpage(request):
    pass


@csrf_exempt
def store_forms(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    data = json.loads(request.body.decode())
    validated_data = forms_schema.validate(data)
    if validated_data["sharedSecret"] != settings.RESPONSE_SHARED_SECRET:
        return HttpResponseForbidden()

    with transaction.atomic():
        GoogleForm.objects.all().update(active=False)
        for form in validated_data["items"]:
            if form["type"] == "full":
                form_type = "F"
            elif form["type"] == "basic":
                form_type = "B"
            else:
                return HttpResponseBadRequest("Invalid form type: %s" % form["type"])
            receiver, created = User.objects.get_or_create(email=form["email"])
            if created:
                receiver.save()
            GoogleForm(form_id=form["id"], form_type=form_type, receiver=receiver).save()
    return HttpResponse()


@csrf_exempt
def record_response(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    data = json.loads(request.body.decode())
    validated_data = response_schema.validate(data)
    print(validated_data)
    if validated_data["sharedSecret"] != settings.RESPONSE_SHARED_SECRET:
        return HttpResponseForbidden()

    anonymous = not validated_data["responses"][0]["answer"].startswith("Yes")
    fun_to_work_with = int(validated_data["responses"][1]["answer"])
    gets_stuff_done = int(validated_data["responses"][2]["answer"])
    work_with = validated_data["responses"][3]["answer"]

    respondent, created = User.objects.get_or_create(email=validated_data["respondent"])
    if created:
        respondent.save()


    ResponseSet.objects.filter(respondent=respondent).filter(receiver=receiver).update(active=False)
    response_set = ResponseSet(respondent=respondent,
                               receiver=receiver,
                               anonymous=anonymous,
                               fun_to_work_with=fun_to_work_with,
                               gets_stuff_done=gets_stuff_done,
                               work_with=work_with,
                               edit_response_url=validated_data["editUrl"])
    response_set.save()
    for item in validated_data["responses"][4:]:
        if item["answer"] == "":
            continue
        question, created = Question.objects.get_or_create(question=item["question"])
        if created:
            question.save()
        answer = Answer(question=question, responses=response_set, response=item["answer"])
        answer.save()
    return HttpResponse()
