import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from syllabus.models import Syllabus


class Command(BaseCommand):
    help = "Import JHTET syllabus data from syllabus_data.json"

    def handle(self, *args, **options):
        data_file = Path(__file__).resolve().parents[2] / "syllabus_data.json"

        if not data_file.exists():
            raise CommandError(
                f"Syllabus data file not found: {data_file}"
            )

        try:
            with data_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise CommandError(
                f"Invalid JSON in {data_file}: {exc}"
            ) from exc

        if not isinstance(data, list):
            raise CommandError(
                "syllabus_data.json must contain a JSON list."
            )

        required_fields = {
            "exam",
            "paper",
            "subject",
            "topic",
            "subtopic",
        }

        created = 0
        updated = 0

        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                raise CommandError(
                    f"Entry {index} must be a JSON object."
                )

            missing = required_fields - item.keys()

            if missing:
                raise CommandError(
                    f"Entry {index} is missing fields: "
                    f"{', '.join(sorted(missing))}"
                )

            _, was_created = Syllabus.objects.update_or_create(
                exam=item["exam"],
                paper=item["paper"],
                subject=item["subject"],
                topic=item["topic"],
                subtopic=item["subtopic"],
                defaults=item,
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {created} created, "
                f"{updated} already existed/updated."
            )
        )