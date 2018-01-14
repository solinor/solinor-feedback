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
            "responseUrl": schema.And(str, len),
        }
    ],
})


@login_required
def frontpage(request):
    user, _ = User.objects.get_or_create(email=request.user.email)
    all_forms = GoogleForm.objects.all().filter(active=True).exclude(receiver=user).filter(form_type="B").select_related("receiver")
    requests = FeedbackRequest.objects.filter(requestee=user).select_related("requestee", "requester", "requested_by")
    feedback_given = ResponseSet.objects.filter(respondent=user)
    return render(request, "frontpage.html", {"all_forms": all_forms, "requests": requests, "given": feedback_given})


@login_required
def ask_for_feedback(request):
    user, _ = User.objects.get_or_create(email=request.user.email)
    if request.method == "POST":
        requestee_email = request.POST.get("email")
        requestee = User.objects.get(email=requestee_email)
        fbr = FeedbackRequest(requestee=requestee, requester=user, requested_by=user)
        fbr.save()
        return HttpResponse(json.dumps({"success": True}), content_type="application/json")
    users = User.objects.filter(active=True).exclude(email=request.user.email)
    return render(request, "ask_for_feedback.html", {"users": users})


def get_missing_forms(request):
    if request.GET.get("sharedSecret") != settings.RESPONSE_SHARED_SECRET:
        return HttpResponseForbidden()

    users = User.objects.filter(active=True)
    google_forms_list = GoogleForm.objects.filter(active=True).values_list("receiver__email", flat=True)
    google_forms = {k for k in google_forms_list}
    i = 0
    items = []
    for user in users:
        if user.email not in google_forms:
            items.append([user.email, user.nick_name, user.full_name])
            i += 1
        if i > 10:
            break
    return HttpResponse(json.dumps(items), content_type="application/json")


def get_forms_for_script(request):
    if request.GET.get("sharedSecret") != settings.RESPONSE_SHARED_SECRET:
        return HttpResponseForbidden("Invalid shared secret")
    script_id = request.GET.get("scriptId")
    if not script_id:
        return HttpResponseBadRequest("Missing scriptId")

    google_forms_list = list(GoogleForm.objects.filter(active=True).filter(script_id=script_id).values_list("form_id", flat=True))
    with transaction.atomic():
        unassigned_forms = GoogleForm.objects.filter(active=True).filter(script_id=None)
        for a in range(0, min(len(unassigned_forms), 19 - len(google_forms_list))):
            unassigned_forms[a].script_id = script_id
            unassigned_forms[a].save()
            google_forms_list.append(unassigned_forms[a].form_id)
    return HttpResponse(json.dumps(google_forms_list), content_type="application/json")


@csrf_exempt
def store_forms(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    data = json.loads(request.body.decode())
    validated_data = forms_schema.validate(data)
    if validated_data["sharedSecret"] != settings.RESPONSE_SHARED_SECRET:
        return HttpResponseForbidden()

    with transaction.atomic():
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

            GoogleForm.objects.filter(receiver=receiver, form_type=form_type).update(active=False)
            GoogleForm(form_id=form["id"], form_type=form_type, receiver=receiver, response_url=form["responseUrl"]).save()
            if form_type == "F":
                receiver.active_full_form = form["responseUrl"]
            if form_type == "B":
                receiver.active_basic_form = form["responseUrl"]
            receiver.save()

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

    form_id = validated_data["editUrl"].replace("https://docs.google.com/forms/d/e/", "").split("/")[0]
    receiver = GoogleForm.objects.get(form_id=form_id).receiver

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
