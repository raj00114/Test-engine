from django.test import TestCase
from django.urls import reverse

from syllabus.models import Syllabus


class SyllabusViewTest(TestCase):
    def test_syllabus_list_view_empty(self):
        response = self.client.get(reverse("syllabus_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "syllabus/list.html")
        self.assertContains(response, "No syllabus records found")

    def test_syllabus_list_view_with_records(self):
        Syllabus.objects.create(
            exam="JHTET 2026",
            paper="Primary level (Classes 1–5)",
            subject="Mathematics",
            topic="Geometry",
            subtopic="Triangles and Quadrilaterals",
        )
        Syllabus.objects.create(
            exam="JHTET 2026",
            paper="Upper-primary level (Classes 6–8)",
            subject="Mathematics",
            topic="Algebra",
            subtopic="Linear Equations",
        )

        response = self.client.get(reverse("syllabus_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "syllabus/list.html")
        self.assertContains(response, "Primary level (Classes 1–5)")
        self.assertContains(response, "Upper-primary level (Classes 6–8)")
        self.assertContains(response, "Geometry")
        self.assertContains(response, "Algebra")
        self.assertContains(response, "Triangles and Quadrilaterals")
