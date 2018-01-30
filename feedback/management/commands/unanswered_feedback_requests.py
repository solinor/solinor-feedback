import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Avg, Case, Count, Exists, F, Max, Min, OuterRef, Prefetch, Q, Subquery, Sum, When
from django.utils import timezone

from feedback.models import FeedbackRequest, User


class Command(BaseCommand):
    help = 'Get users along with unanswered feedback requests'
    def add_arguments(self, parser):
        parser.add_argument(
            "--filter",
            action="append",
            dest="filter",
            help="Filter by emails",
        )


    def handle(self, *args, **options):
        for user in User.objects.filter(active=True).prefetch_related("feedback_receiver", "feedback_receiver__giver"):
            print(user)
            for req in user.feedback_giver.filter(active_response=None):
                if options["filter"]:
                    if req.receiver.email in options["filter"]:
                        print(" - " + req.receiver.nick_name + " - " + req.receiver.active_full_form)
                else:
                    print(" - " + req.receiver.nick_name + " - " + req.receiver.active_full_form)
