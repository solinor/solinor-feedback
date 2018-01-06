from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.conf import settings
import json
from feedback.models import *
import schema
from django.views.decorators.csrf import csrf_exempt


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


def frontpage(request):
    pass


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

    response_set = ResponseSet(respondent=validated_data["respondent"],
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
