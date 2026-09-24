from django.shortcuts import get_object_or_404, render

from .models import Test


def home(request):
    tests = (
        Test.objects
        .filter(is_published=True)
        .order_by("-created_at")[:6]
    )

    return render(
        request,
        "home.html",
        {"tests": tests},
    )


def test_list(request):
    tests = (
        Test.objects
        .filter(is_published=True)
        .order_by("-created_at")
    )

    return render(
        request,
        "tests/list.html",
        {"tests": tests},
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
        percentage = (
            round((score / total) * 100, 1)
            if total > 0
            else 0
        )

        result = {
                "score": score,
                "total": total,
                "percentage": percentage,
                "answered": answered,
                "unanswered": total - answered,
                "review": review,
        }

    return render(
        request,
        "tests/take.html",
        {
            "test": test,
            "questions": questions,
            "result": result,
        },
    )