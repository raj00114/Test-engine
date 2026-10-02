from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Test


def home(request):
    tests = (
        Test.objects
        .filter(is_published=True)
        .order_by("-created_at")[:6]
    )
    recent_results = request.session.get("recent_test_results", [])

    return render(
        request,
        "home.html",
        {
            "tests": tests,
            "recent_results": recent_results,
        },
    )


def test_list(request):
    tests = (
        Test.objects
        .filter(is_published=True)
        .order_by("-created_at")
    )
    recent_results = request.session.get("recent_test_results", [])

    return render(
        request,
        "tests/list.html",
        {
            "tests": tests,
            "recent_results": recent_results,
        },
    )


def take_test(request, pk):
    test = get_object_or_404(
        Test.objects.prefetch_related("questions"),
        pk=pk,
        is_published=True,
    )

    questions = list(test.questions.all())
    result = None

    if request.method == "POST":
        score = 0
        answered = 0
        review = []

        for question in questions:
            answer = request.POST.get(f"question_{question.pk}")

            is_correct = (
                answer is not None
                and answer.upper() == question.correct_answer.upper()
            )

            if answer:
                answered += 1

            if is_correct:
                score += 1

            review.append(
                {
                    "question": question,
                    "selected_answer": answer,
                    "is_correct": is_correct,
                }
            )

        total = len(questions)
        attempted = answered
        unanswered = total - attempted
        correct = score
        wrong = attempted - correct
        percentage = (
            round((score / total) * 100, 1)
            if total > 0
            else 0
        )

        result = {
            "total": total,
            "attempted": attempted,
            "unanswered": unanswered,
            "correct": correct,
            "wrong": wrong,
            "score": score,
            "percentage": percentage,
            "review": review,
        }

        # Store in rolling session history (strictly last 5 results)
        recent = request.session.get("recent_test_results", [])
        new_entry = {
            "test_id": test.pk,
            "test_title": test.title,
            "submitted_at": timezone.now().strftime("%Y-%m-%d %H:%M"),
            "total": total,
            "attempted": attempted,
            "unanswered": unanswered,
            "correct": correct,
            "wrong": wrong,
            "score": score,
            "percentage": percentage,
        }
        request.session["recent_test_results"] = [new_entry] + recent[:4]
        request.session.modified = True

    recent_results = request.session.get("recent_test_results", [])

    return render(
        request,
        "tests/take.html",
        {
            "test": test,
            "questions": questions,
            "result": result,
            "recent_results": recent_results,
        },
    )