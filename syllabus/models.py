from django.db import models


class Syllabus(models.Model):
    exam = models.CharField(max_length=50)
    paper = models.CharField(max_length=100)
    subject = models.CharField(max_length=150)
    topic = models.CharField(max_length=200)
    subtopic = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["exam", "paper", "subject", "topic", "subtopic"]

    def __str__(self):
        parts = [self.exam, self.paper, self.subject, self.topic]

        if self.subtopic:
            parts.append(self.subtopic)

        return " → ".join(parts)