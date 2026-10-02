from django.test import TestCase
from django.urls import reverse

from engine.models import Question, Test


class ViewTests(TestCase):
    def setUp(self):
        self.q1 = Question.objects.create(
            exam="JHTET",
            paper="Primary level (Classes 1–5)",
            subject="Mathematics",
            topic="Arithmetic",
            question_text="What is 5 + 3?",
            question_text_hindi="5 + 3 का मान क्या है?",
            option_a="7",
            option_b="8",
            option_c="9",
            option_d="10",
            correct_answer="B",
        )
        self.q2 = Question.objects.create(
            exam="JHTET",
            paper="Primary level (Classes 1–5)",
            subject="Mathematics",
            topic="Arithmetic",
            question_text="What is 10 - 4?",
            question_text_hindi="10 - 4 का मान क्या है?",
            option_a="5",
            option_b="6",
            option_c="7",
            option_d="8",
            correct_answer="B",
        )
        self.q3 = Question.objects.create(
            exam="JHTET",
            paper="Primary level (Classes 1–5)",
            subject="Mathematics",
            topic="Geometry",
            question_text="How many sides does a triangle have?",
            question_text_hindi="त्रिभुज की कितनी भुजाएं होती हैं?",
            option_a="3",
            option_b="4",
            option_c="5",
            option_d="6",
            correct_answer="A",
        )

        self.published_test = Test.objects.create(
            title="JHTET Math Mock 1",
            exam="JHTET",
            paper="Primary level (Classes 1–5)",
            duration_minutes=30,
            is_published=True,
        )
        self.published_test.questions.add(self.q1, self.q2, self.q3)

        self.unpublished_test = Test.objects.create(
            title="Unpublished Draft Test",
            exam="JHTET",
            is_published=False,
        )

    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, self.published_test.title)
        self.assertNotContains(response, self.unpublished_test.title)

    def test_test_list_view(self):
        response = self.client.get(reverse("test_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tests/list.html")
        self.assertContains(response, self.published_test.title)
        self.assertNotContains(response, self.unpublished_test.title)

    def test_take_test_get(self):
        response = self.client.get(reverse("take_test", args=[self.published_test.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tests/take.html")
        self.assertEqual(len(response.context["questions"]), 3)
        self.assertIsNone(response.context["result"])

    def test_take_test_get_unpublished_returns_404(self):
        response = self.client.get(reverse("take_test", args=[self.unpublished_test.pk]))
        self.assertEqual(response.status_code, 404)

    def test_take_test_post_scoring_accuracy(self):
        # q1: correct (B), q2: wrong (A, correct is B), q3: unanswered (None)
        post_data = {
            f"question_{self.q1.pk}": "B",
            f"question_{self.q2.pk}": "A",
        }
        response = self.client.post(
            reverse("take_test", args=[self.published_test.pk]),
            data=post_data,
        )
        self.assertEqual(response.status_code, 200)
        result = response.context["result"]

        self.assertEqual(result["total"], 3)
        self.assertEqual(result["attempted"], 2)
        self.assertEqual(result["unanswered"], 1)
        self.assertEqual(result["correct"], 1)
        self.assertEqual(result["wrong"], 1)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["percentage"], 33.3)

    def test_session_rolling_five_results(self):
        # Create 6 published tests and submit each one
        tests = []
        for i in range(1, 7):
            t = Test.objects.create(
                title=f"Practice Test {i}",
                exam="JHTET",
                is_published=True,
            )
            t.questions.add(self.q1)
            tests.append(t)

        for t in tests:
            self.client.post(
                reverse("take_test", args=[t.pk]),
                data={f"question_{self.q1.pk}": "B"},
            )

        session_history = self.client.session.get("recent_test_results", [])
        # Must cap strictly at 5
        self.assertEqual(len(session_history), 5)
        # Most recent test (Practice Test 6) must be first
        self.assertEqual(session_history[0]["test_title"], "Practice Test 6")
        self.assertEqual(session_history[-1]["test_title"], "Practice Test 2")
