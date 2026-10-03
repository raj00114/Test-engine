import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from engine.models import Question


@dataclass
class ImportErrorItem:
    row_number: int
    field: str
    value: Any
    error: str

    def __str__(self) -> str:
        val_repr = repr(self.value) if self.value is not None else "None"
        return f"row_number: {self.row_number}, field: {self.field}, value: {val_repr}, error: {self.error}"


class Command(BaseCommand):
    help = "Import questions from CSV or JSON adhering to question_bank_importer_contract v1.0."

    REQUIRED_FIELDS = [
        "exam_code",
        "paper_code",
        "subject_code",
        "topic_code",
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
    ]

    OPTIONAL_FIELDS = [
        "subtopic_code",
        "question_text_hindi",
        "explanation",
        "explanation_hindi",
        "language",
        "difficulty",
        "source",
    ]

    CANONICAL_FIELDS = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)

    ALLOWED_EXAMS = {choice[0] for choice in Question.EXAM_CHOICES}
    ALLOWED_LANGUAGES = {choice[0] for choice in Question.LANGUAGE_CHOICES}
    ALLOWED_DIFFICULTIES = {
        choice[0]
        for choice in getattr(
            Question,
            "DIFFICULTY_CHOICES",
            [("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")],
        )
    }
    ALLOWED_ANSWERS = {"A", "B", "C", "D"}

    def add_arguments(self, parser):
        parser.add_argument(
            "file",
            help="Path to the CSV or JSON file to import.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate input file without writing to the database.",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])

        if not file_path.exists():
            raise CommandError(f"Question file not found: {file_path}")

        ext = file_path.suffix.lower()
        if ext == ".csv":
            data = self.load_csv(file_path)
        elif ext == ".json":
            data = self.load_json(file_path)
        else:
            raise CommandError(
                f"Unsupported file format '{ext}'. Expected .csv or .json."
            )

        if not isinstance(data, list):
            raise CommandError("Question data must be a list of records.")

        if not data:
            raise CommandError("Question file contains no records to import.")

        errors = self.validate_questions(data)
        if errors:
            self.report_errors(errors)
            error_details = "\n".join(str(err) for err in errors)
            raise CommandError(
                f"Validation failed with {len(errors)} error(s):\n{error_details}"
            )

        if options.get("dry_run"):
            self.stdout.write(
                self.style.SUCCESS(
                    f"Validation successful (dry-run). {len(data)} question(s) are valid and ready to import."
                )
            )
            return

        created_count = 0
        with transaction.atomic():
            for item in data:
                mapped_fields = self.map_to_question_model(item)
                Question.objects.create(**mapped_fields)
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {created_count} question(s) imported successfully."
            )
        )

    def load_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        try:
            with file_path.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    raise CommandError("CSV file is empty.")
                records = []
                for row in reader:
                    cleaned_row = {}
                    for k, v in row.items():
                        if k is not None:
                            cleaned_row[k.strip()] = v
                    records.append(cleaned_row)
                return records
        except csv.Error as exc:
            raise CommandError(f"Invalid CSV file: {exc}") from exc

    def load_json(self, file_path: Path) -> List[Dict[str, Any]]:
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON file: {exc}") from exc

        if not isinstance(data, dict):
            raise CommandError(
                "JSON file must be an object with a 'questions' key."
            )

        if "questions" not in data:
            raise CommandError("JSON file missing root key 'questions'.")

        questions = data["questions"]
        if not isinstance(questions, list):
            raise CommandError(
                "The 'questions' key in JSON file must contain a list."
            )

        return questions

    def validate_questions(self, data: List[Dict[str, Any]]) -> List[ImportErrorItem]:
        errors: List[ImportErrorItem] = []
        seen_in_file: Dict[tuple, int] = {}

        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                errors.append(
                    ImportErrorItem(
                        row_number=index,
                        field="record",
                        value=item,
                        error="Record must be an object/dict.",
                    )
                )
                continue

            # 1. Structural check: unknown fields
            unknown_fields = set(item.keys()) - self.CANONICAL_FIELDS
            for uf in sorted(unknown_fields):
                errors.append(
                    ImportErrorItem(
                        row_number=index,
                        field=uf,
                        value=item.get(uf),
                        error=f"Unknown field '{uf}'. Not allowed in contract v1.0.",
                    )
                )

            # 2. Required fields check (presence and non-empty)
            for rf in self.REQUIRED_FIELDS:
                if rf not in item:
                    errors.append(
                        ImportErrorItem(
                            row_number=index,
                            field=rf,
                            value=None,
                            error=f"Missing required field '{rf}'.",
                        )
                    )
                else:
                    raw_val = item[rf]
                    if raw_val is None or (isinstance(raw_val, str) and not raw_val.strip()):
                        errors.append(
                            ImportErrorItem(
                                row_number=index,
                                field=rf,
                                value=raw_val,
                                error=f"Field '{rf}' cannot be empty.",
                            )
                        )

            # 3. Content and choice validation
            # exam_code
            if "exam_code" in item and item["exam_code"] is not None and str(item["exam_code"]).strip():
                val = str(item["exam_code"]).strip()
                if val not in self.ALLOWED_EXAMS:
                    errors.append(
                        ImportErrorItem(
                            row_number=index,
                            field="exam_code",
                            value=item["exam_code"],
                            error=f"Invalid exam_code '{val}'. Allowed choices: {', '.join(sorted(self.ALLOWED_EXAMS))}.",
                        )
                    )

            # correct_answer
            if "correct_answer" in item and item["correct_answer"] is not None and str(item["correct_answer"]).strip():
                val = str(item["correct_answer"]).strip()
                if val not in self.ALLOWED_ANSWERS:
                    errors.append(
                        ImportErrorItem(
                            row_number=index,
                            field="correct_answer",
                            value=item["correct_answer"],
                            error=f"Invalid correct_answer '{val}'. Must be one of: {', '.join(sorted(self.ALLOWED_ANSWERS))}.",
                        )
                    )

            # language (optional, but if present must be valid)
            if "language" in item and item["language"] is not None and str(item["language"]).strip():
                val = str(item["language"]).strip()
                if val not in self.ALLOWED_LANGUAGES:
                    errors.append(
                        ImportErrorItem(
                            row_number=index,
                            field="language",
                            value=item["language"],
                            error=f"Invalid language '{val}'. Allowed choices: {', '.join(sorted(self.ALLOWED_LANGUAGES))}.",
                        )
                    )

            # difficulty (optional, but if present must be valid)
            if "difficulty" in item and item["difficulty"] is not None and str(item["difficulty"]).strip():
                val = str(item["difficulty"]).strip()
                if val not in self.ALLOWED_DIFFICULTIES:
                    errors.append(
                        ImportErrorItem(
                            row_number=index,
                            field="difficulty",
                            value=item["difficulty"],
                            error=f"Invalid difficulty '{val}'. Allowed choices: {', '.join(sorted(self.ALLOWED_DIFFICULTIES))}.",
                        )
                    )

            # 4. Duplicate detection
            # Check duplicate within import and against existing questions in database
            can_check_duplicate = all(
                rf in item and item[rf] is not None and str(item[rf]).strip()
                for rf in ["exam_code", "paper_code", "subject_code", "question_text"]
            )
            if can_check_duplicate:
                dup_key = (
                    str(item["exam_code"]).strip().lower(),
                    str(item["paper_code"]).strip().lower(),
                    str(item["subject_code"]).strip().lower(),
                    str(item["question_text"]).strip().lower(),
                )

                if dup_key in seen_in_file:
                    first_row = seen_in_file[dup_key]
                    errors.append(
                        ImportErrorItem(
                            row_number=index,
                            field="question_text",
                            value=item["question_text"],
                            error=f"Duplicate question found within import (matches row {first_row}).",
                        )
                    )
                else:
                    seen_in_file[dup_key] = index

                    # Check against existing DB questions
                    if Question.objects.filter(
                        exam__iexact=str(item["exam_code"]).strip(),
                        paper__iexact=str(item["paper_code"]).strip(),
                        subject__iexact=str(item["subject_code"]).strip(),
                        question_text__iexact=str(item["question_text"]).strip(),
                    ).exists():
                        errors.append(
                            ImportErrorItem(
                                row_number=index,
                                field="question_text",
                                value=item["question_text"],
                                error="Question already exists in database.",
                            )
                        )

        return errors

    def map_to_question_model(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps canonical contract fields strictly to existing Question model fields.
        """
        return {
            "exam": str(item["exam_code"]).strip(),
            "paper": str(item["paper_code"]).strip(),
            "subject": str(item["subject_code"]).strip(),
            "topic": str(item["topic_code"]).strip(),
            "subtopic": str(item.get("subtopic_code") or "").strip(),
            "question_text": str(item["question_text"]).strip(),
            "question_text_hindi": str(item.get("question_text_hindi") or "").strip(),
            "option_a": str(item["option_a"]).strip(),
            "option_b": str(item["option_b"]).strip(),
            "option_c": str(item["option_c"]).strip(),
            "option_d": str(item["option_d"]).strip(),
            "correct_answer": str(item["correct_answer"]).strip(),
            "explanation": str(item.get("explanation") or "").strip(),
            "explanation_hindi": str(item.get("explanation_hindi") or "").strip(),
            "language": str(item.get("language") or "BILINGUAL").strip(),
            "difficulty": str(item.get("difficulty") or "Medium").strip(),
            "source": str(item.get("source") or "").strip(),
        }

    def report_errors(self, errors: List[ImportErrorItem]):
        self.stderr.write(
            self.style.ERROR(f"Validation failed with {len(errors)} error(s):")
        )
        for err in errors:
            self.stderr.write(f"  {err}")
