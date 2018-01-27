import json
import random
from collections import defaultdict

import schema
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

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
    all_requests = {req.receiver.email: req for req in FeedbackRequest.objects.filter(giver=user).filter(active_response=None).select_related("giver", "receiver", "requested_by")}
    receiver_requests = FeedbackRequest.objects.filter(receiver__in=[req.receiver for req in all_requests.values()]).values("receiver__email").order_by("receiver__email").annotate(requests=Count('receiver')).order_by("requests")

    requests = []
    for item in receiver_requests:
        requests.append(all_requests[item["receiver__email"]])

    feedback_given = ResponseSet.objects.filter(giver=user).filter(active=True).select_related("giver", "receiver")
    existing_users = {k.receiver.email for k in requests}
    existing_users.update({k.receiver.email for k in feedback_given})
    all_forms = list(GoogleForm.objects.filter(active=True).exclude(receiver=user).filter(form_type="B").select_related("receiver"))
    unanswered_forms = []
    for form in all_forms:
        if form.receiver.email not in existing_users:
            unanswered_forms.append(form)
    random.shuffle(unanswered_forms)
    return render(request, "frontpage.html", {"all_forms": unanswered_forms, "requests": requests, "given": feedback_given})


@login_required
def ask_for_feedback(request):
    user, _ = User.objects.get_or_create(email=request.user.email)
    if request.method == "POST":
        giver = User.objects.get(email=request.POST.get("email"))
        fbr = FeedbackRequest(giver=giver, receiver=user, requested_by=user)
        fbr.save()
        return HttpResponse(json.dumps({"success": True}), content_type="application/json")
    users = list(User.objects.filter(active=True).exclude(email=request.user.email))
    requests = {k.giver.email: k for k in FeedbackRequest.objects.filter(receiver=user)}
    for user in users:
        user.fb_request = requests.get(user.email)
    random.shuffle(users)
    return render(request, "ask_for_feedback.html", {"users": users})


def get_missing_forms(request):
    if request.GET.get("sharedSecret") != settings.RESPONSE_SHARED_SECRET:
        return HttpResponseForbidden()

    users = User.objects.filter(active=True)
    google_forms_list = GoogleForm.objects.filter(active=True).values_list("receiver__email", "form_type")
    google_forms = defaultdict(set)
    for item in google_forms_list:
        google_forms[item[0]].add(item[1])
    i = 0
    items = []
    for user in users:
        for db_name, item_type in [("C", "client"), ("F", "full"), ("B", "basic")]:
            if db_name not in google_forms[user.email]:
                items.append([[user.email, user.nick_name, user.full_name], item_type])
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

    google_forms_list = list(GoogleForm.objects.filter(active=True).filter(script_id=script_id).exclude(form_type="C").values_list("form_id", flat=True))
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
            elif form["type"] == "client":
                form_type = "C"
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
            if form_type == "C":
                receiver.active_client_form = form["responseUrl"]
            receiver.save()

    return HttpResponse()


def get_answers(active_responses, admin_view=False):
    questions = defaultdict(list)
    stats = {
        "fun_to_work_with": [0, 0, 0, 0],
        "gets_stuff_done": [0, 0, 0, 0],
        "work_with": [0, 0, 0, 0],
    }
    work_with_mapping = {k: i for i, k in enumerate(("I would prefer not to work with them", "I don't know", "Yes, but I would not pick them as my first choice", "Yes, absolutely!"))}
    for response in active_responses:
        stats["fun_to_work_with"][response.fun_to_work_with - 1] += 1
        stats["gets_stuff_done"][response.gets_stuff_done - 1] += 1
        stats["work_with"][work_with_mapping[response.work_with]] += 1
        for answer in response.answer_set.all():
            if response.activated:
                answer.released = True
            if response.anonymous:
                if admin_view:
                    answer.anonymous_giver_name = response.giver.nick_name
            else:
                answer.public_giver_name = response.giver.nick_name

            questions[answer.question.question].append(answer)
    questions = list(dict(questions).items())
    questions.reverse()
    return questions, stats


@login_required
def user_view_feedback(request):
    user, _ = User.objects.get_or_create(email=request.user.email)
    active_responses = ResponseSet.objects.filter(receiver=user).filter(active=True).filter(activated=True)
    questions, stats = get_answers(active_responses)
    unreleased_feedback = ResponseSet.objects.filter(receiver=user).filter(active=True).filter(activated=False).count()
    return render(request, "user_view_feedback.html", {"questions": questions, "stats": stats, "unreleased_feedback": unreleased_feedback})


@login_required
@permission_required("feedback.can_share_feedback")
def admin_view_feedback(request, user_email):
    user = User.objects.get(email=user_email)
    admin_user = User.objects.get(email=request.user.email)
    if user.feedback_admin != admin_user:
        return HttpResponseForbidden("%s is not assigned for you." % user_email)

    if request.method == "POST":
        if request.POST.get("release-feedback"):
            ResponseSet.objects.filter(receiver_user).filter(active=True).update(activated=True)
            messages.add_message(request, messages.INFO, "Feedback released")
        active_responses = ResponseSet.objects.filter(receiver=user).filter(active=True).select_related("giver").prefetch_related("answer_set")
        admin_view = request.POST.get("admin_view")
        questions, stats = get_answers(active_responses, admin_view)
        return render(request, "admin_view_feedback.html", {"questions": questions, "admin_view": admin_view, "user": user, "stats": stats})

    return render(request, "admin_view_feedback_decide.html", {"user": user})


@login_required
@permission_required("feedback.can_share_feedback")
def admin_book_feedback(request):
    admin_user, _ = User.objects.get_or_create(email=request.user.email)
    if request.method == "POST":
        email = request.POST.get("email")
        if email == request.user.email:
            return HttpResponseForbidden("You can't see your own feedback")
        user = User.objects.get(email=email)
        if user.feedback_admin == None:
            user.feedback_admin = admin_user
            user.save()
            messages.add_message(request, messages.INFO, "You booked %s" % email)
        else:
            messages.add_message(request, messages.WARNING, "%s has already been booked by %s" % (email, user.feedback_admin))
        return HttpResponseRedirect(reverse("admin_book_feedback"))

    you_give_feedback_to = User.objects.filter(feedback_admin=admin_user).filter(active=True).values("receiver__activated").annotate(c=Count("receiver__activated")).values_list("email", "receiver__activated",  "c")
    non_assigned_users = User.objects.filter(feedback_admin=None).filter(active=True).exclude(email=request.user.email)
    return render(request, "admin_book_feedback.html", {"you_give_feedback_to": you_give_feedback_to, "non_assigned_users": non_assigned_users})


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

    giver, created = User.objects.get_or_create(email=validated_data["respondent"])
    if created:
        respondent.save()

    form_id = validated_data["editUrl"].replace("https://docs.google.com/forms/d/e/", "").split("/")[0]
    form = GoogleForm.objects.filter(response_url__contains=form_id)[0]
    receiver = form.receiver
    fb_request = FeedbackRequest.objects.filter(receiver=receiver, giver=giver)

    with transaction.atomic():
        ResponseSet.objects.filter(giver=giver).filter(receiver=receiver).update(active=False)
        response_set = ResponseSet(form=form,
                                   giver=giver,
                                   receiver=receiver,
                                   anonymous=anonymous,
                                   fun_to_work_with=fun_to_work_with,
                                   gets_stuff_done=gets_stuff_done,
                                   work_with=work_with,
                                   edit_response_url=validated_data["editUrl"])
        response_set.save()
        fb_request.update(active_response=response_set)

        for item in validated_data["responses"][4:]:
            if item["answer"] == "":
                continue
            question, created = Question.objects.get_or_create(question=item["question"])
            if created:
                question.save()
            answer = Answer(question=question, responses=response_set, response=item["answer"])
            answer.save()
    return HttpResponse()
