from django.test import TestCase

from engine.models import Question, Test


class QuestionModelTest(TestCase):
    def test_question_can_be_created(self):
        question = Question.objects.create(
            exam="JHTET",
            paper="Primary level (Classes 1–5)",
            subject="गणित",
            topic="सामान्य गणित",
            subtopic="संख्याएँ एवं गणितीय संक्रियाएँ",
            question_text="2 + 2 = ?",
            question_text_hindi="2 + 2 = ?",
            option_a="3",
            option_b="4",
            option_c="5",
            option_d="6",
            correct_answer="B",
            explanation="2 + 2 equals 4.",
            explanation_hindi="2 + 2 का मान 4 है।",
            language="BILINGUAL",
            difficulty="Easy",
        )

        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(question.correct_answer, "B")
        self.assertEqual(question.subtopic, "संख्याएँ एवं गणितीय संक्रियाएँ")


class TestModelTest(TestCase):
    def test_test_can_be_created(self):
        test = Test.objects.create(
            title="JHTET Mathematics Test",
            exam="JHTET",
            paper="Primary level (Classes 1–5)",
            duration_minutes=30,
            total_questions=30,
        )

        self.assertEqual(Test.objects.count(), 1)
        self.assertEqual(test.exam, "JHTET")
