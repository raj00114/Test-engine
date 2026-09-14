from django.contrib import admin

from .models import Syllabus


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = (
        "exam",
        "paper",
        "subject",
        "topic",
        "subtopic",
    )

    list_filter = (
        "exam",
        "paper",
        "subject",
    )

    search_fields = (
        "subject",
        "topic",
        "subtopic",
    )

    ordering = (
        "exam",
        "paper",
        "subject",
        "topic",
        "subtopic",
    )
    