from django.db import models


class Question(models.Model):
    EXAM_CHOICES = [
        ("JHTET", "JHTET"),
        ("CTET", "CTET"),
        ("JSSC", "JSSC"),
        ("IGNOU", "IGNOU"),
        ("OTHER", "Other"),
    ]

    LANGUAGE_CHOICES = [
        ("EN", "English"),
        ("HI", "Hindi"),
        ("BILINGUAL", "Bilingual"),
    ]

    exam = models.CharField(max_length=20, choices=EXAM_CHOICES)
    paper = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=100)
    topic = models.CharField(max_length=150, blank=True)

    question_text = models.TextField()
    question_text_hindi = models.TextField(blank=True)

    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()

    correct_answer = models.CharField(max_length=1)

    explanation = models.TextField(blank=True)
    explanation_hindi = models.TextField(blank=True)

    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="BILINGUAL",
    )

    difficulty = models.CharField(
        max_length=20,
        default="Medium",
    )

    source = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam} - {self.subject} - {self.question_text[:60]}"


class Test(models.Model):
    title = models.CharField(max_length=200)

    exam = models.CharField(
        max_length=20,
        choices=Question.EXAM_CHOICES,
    )

    paper = models.CharField(max_length=50, blank=True)

    description = models.TextField(blank=True)

    duration_minutes = models.PositiveIntegerField(default=30)

    total_questions = models.PositiveIntegerField(default=30)

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    questions = models.ManyToManyField(
        Question,
        related_name="tests",
        blank=True,
    )

    def __str__(self):
        return self.title