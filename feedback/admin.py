from django.contrib import admin

from feedback.models import FeedbackRequest, User


class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    search_fields = ("first_name",)


admin.site.register(User, UserAdmin)


class FeedbackRequestAdmin(admin.ModelAdmin):
    list_display = ("receiver", "giver")


admin.site.register(FeedbackRequest, FeedbackRequestAdmin)
