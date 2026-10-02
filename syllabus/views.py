from django.shortcuts import render

from .models import Syllabus


def syllabus_list(request):
    records = Syllabus.objects.all().order_by("paper", "subject", "topic", "subtopic")

    return render(
        request,
        "syllabus/list.html",
        {"syllabus_records": records},
    )
