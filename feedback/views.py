from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.conf import settings
import json
from feedback.models import *
import schema


response_schema = schema.Schema({
    "sharedSecret": schema.And(str, len),
    "respondent": schema.And(str, len, lambda s: "@" in s),
    "editUrl": schema.And(str, len),
    "responses": [
        {
            "question": schema.And(str, len),
            "answer": schema.And(str, len),
        }
    ]
})


def frontpage(request):
    pass


def record_response(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    data = simplejson.loads(request.POST['data'])
    validated_data = response_schema.validate(data)
    if validated_data["sharedSecret"] != settings.RESPONSE_SHARED_SECRET:
        return HttpResponseForbidden()

    anonymous = not validated_data["responses"][0].startswith("Yes")
    fun_to_work_with = int(validated_data["responses"][1])
    gets_stuff_done = int(validated_data["responses"][2])
    work_with = validated_data["responses"][3]

    response_set = ResponseSet(respondent=validated_data["respondent"],
                               anonymous=anonymous,
                               fun_to_work_with=fun_to_work_with,
                               gets_stuff_done=gets_stuff_done,
                               work_with=work_with,
                               edit_response_url=validated_data["editUrl"])
    response_set.save()
    for item in validated_data["responses"][4:]:
        question, created = Question.objects.get_or_create(question=item["question"])
        if created:
            question.save()
        answer = Answer(question=question, responses=response_set, response=item["answer"])
        answer.save()
    return HttpResponse()
