import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from feedback.models import FeedbackRequest, User
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When, Exists, OuterRef, Subquery


class Command(BaseCommand):
    help = 'Get list of users with no feedback requests'

    def add_arguments(self, parser):
        parser.add_argument(
            "--ignore",
            action="append",
            dest="ignore",
            help="Ignored emails",
        )

    def handle(self, *args, **options):
        for user in User.objects.all().prefetch_related("feedback_receiver", "feedback_receiver__giver"):
            request_count = 0
            for request in user.feedback_receiver.all():
                if request.giver.email not in options.get("ignore", []):
                    request_count += 1
#            if request_count == 0:
            print(user, request_count)
