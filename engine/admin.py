from django.contrib import admin
from .models import Question, Test


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "exam",
        "paper",
        "subject",
        "topic",
        "subtopic",
        "difficulty",
        "correct_answer",
    )

    list_filter = (
        "exam",
        "paper",
        "subject",
        "difficulty",
        "language",
    )

    search_fields = (
        "question_text",
        "question_text_hindi",
        "topic",
        "subtopic",
        "source",
    )

    fieldsets = (
        (
            "Question Information",
            {
                "fields": (
                    "exam",
                    "paper",
                    "subject",
                    "topic",
                    "subtopic",
                    "difficulty",
                    "language",
                    "source",
                )
            },
        ),
        (
            "Question",
            {
                "fields": (
                    "question_text",
                    "question_text_hindi",
                )
            },
        ),
        (
            "Options & Answer",
            {
                "fields": (
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_answer",
                )
            },
        ),
        (
            "Explanation",
            {
                "fields": (
                    "explanation",
                    "explanation_hindi",
                )
            },
        ),
    )


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "exam",
        "paper",
        "duration_minutes",
        "total_questions",
        "is_published",
        "created_at",
    )

    list_filter = (
        "exam",
        "paper",
        "is_published",
    )

    search_fields = (
        "title",
        "description",
    )

    filter_horizontal = ("questions",)