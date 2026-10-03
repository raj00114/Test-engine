import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from engine.models import Question


class QuestionImporterContractTests(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_file(self, filename: str, content: str, encoding: str = "utf-8") -> Path:
        file_path = self.temp_path / filename
        file_path.write_text(content, encoding=encoding)
        return file_path

    def test_valid_csv_import(self):
        csv_content = (
            "exam_code,paper_code,subject_code,topic_code,subtopic_code,"
            "question_text,question_text_hindi,option_a,option_b,option_c,option_d,"
            "correct_answer,explanation,explanation_hindi,language,difficulty,source\n"
            "JHTET,Paper 1,Mathematics,Arithmetic,Addition,"
            "What is 2 + 2?,2 + 2 क्या है?,1,2,3,4,"
            "D,Two plus two is four,दो और दो चार होते हैं,BILINGUAL,Easy,JHTET 2024 P1\n"
        )
        file_path = self.create_file("valid.csv", csv_content, encoding="utf-8-sig")

        out = StringIO()
        call_command("import_questions", str(file_path), stdout=out)

        self.assertEqual(Question.objects.count(), 1)
        q = Question.objects.first()
        self.assertEqual(q.exam, "JHTET")
        self.assertEqual(q.paper, "Paper 1")
        self.assertEqual(q.subject, "Mathematics")
        self.assertEqual(q.topic, "Arithmetic")
        self.assertEqual(q.subtopic, "Addition")
        self.assertEqual(q.question_text, "What is 2 + 2?")
        self.assertEqual(q.question_text_hindi, "2 + 2 क्या है?")
        self.assertEqual(q.option_a, "1")
        self.assertEqual(q.option_b, "2")
        self.assertEqual(q.option_c, "3")
        self.assertEqual(q.option_d, "4")
        self.assertEqual(q.correct_answer, "D")
        self.assertEqual(q.explanation, "Two plus two is four")
        self.assertEqual(q.explanation_hindi, "दो और दो चार होते हैं")
        self.assertEqual(q.language, "BILINGUAL")
        self.assertEqual(q.difficulty, "Easy")
        self.assertEqual(q.source, "JHTET 2024 P1")
        self.assertIn("Import complete: 1 question(s) imported successfully.", out.getvalue())

    def test_valid_json_import(self):
        json_data = {
            "questions": [
                {
                    "exam_code": "CTET",
                    "paper_code": "Paper 2",
                    "subject_code": "Science",
                    "topic_code": "Physics",
                    "subtopic_code": "Mechanics",
                    "question_text": "What is the SI unit of force?",
                    "question_text_hindi": "बल का SI मात्रक क्या है?",
                    "option_a": "Joule",
                    "option_b": "Newton",
                    "option_c": "Watt",
                    "option_d": "Pascal",
                    "correct_answer": "B",
                    "explanation": "Force is measured in Newtons.",
                    "explanation_hindi": "बल न्यूटन में मापा जाता है।",
                    "language": "BILINGUAL",
                    "difficulty": "Medium",
                    "source": "CTET 2023",
                }
            ]
        }
        file_path = self.create_file("valid.json", json.dumps(json_data))

        out = StringIO()
        call_command("import_questions", str(file_path), stdout=out)

        self.assertEqual(Question.objects.count(), 1)
        q = Question.objects.first()
        self.assertEqual(q.exam, "CTET")
        self.assertEqual(q.paper, "Paper 2")
        self.assertEqual(q.subject, "Science")
        self.assertEqual(q.topic, "Physics")
        self.assertEqual(q.subtopic, "Mechanics")
        self.assertEqual(q.question_text, "What is the SI unit of force?")
        self.assertEqual(q.correct_answer, "B")
        self.assertEqual(q.difficulty, "Medium")
        self.assertIn("Import complete: 1 question(s) imported successfully.", out.getvalue())

    def test_json_missing_root_questions_key(self):
        json_data = [{"exam_code": "JHTET"}]
        file_path = self.create_file("missing_root.json", json.dumps(json_data))

        with self.assertRaises(CommandError) as ctx:
            call_command("import_questions", str(file_path))

        self.assertIn("JSON file must be an object with a 'questions' key.", str(ctx.exception))

    def test_missing_required_fields(self):
        # Missing 'correct_answer' and 'option_d'
        csv_content = (
            "exam_code,paper_code,subject_code,topic_code,"
            "question_text,option_a,option_b,option_c\n"
            "JHTET,Paper 1,Mathematics,Arithmetic,What is 1 + 1?,1,2,3\n"
        )
        file_path = self.create_file("missing_fields.csv", csv_content)

        with self.assertRaises(CommandError) as ctx:
            call_command("import_questions", str(file_path))

        err_msg = str(ctx.exception)
        self.assertIn("row_number: 1", err_msg)
        self.assertIn("field: option_d", err_msg)
        self.assertIn("field: correct_answer", err_msg)
        self.assertIn("error: Missing required field", err_msg)
        self.assertEqual(Question.objects.count(), 0)

    def test_empty_required_fields(self):
        # 'question_text' and 'option_a' are empty
        csv_content = (
            "exam_code,paper_code,subject_code,topic_code,"
            "question_text,option_a,option_b,option_c,option_d,correct_answer\n"
            "JHTET,Paper 1,Mathematics,Arithmetic,   ,,2,3,4,A\n"
        )
        file_path = self.create_file("empty_fields.csv", csv_content)

        with self.assertRaises(CommandError) as ctx:
            call_command("import_questions", str(file_path))

        err_msg = str(ctx.exception)
        self.assertIn("row_number: 1", err_msg)
        self.assertIn("field: question_text", err_msg)
        self.assertIn("field: option_a", err_msg)
        self.assertIn("cannot be empty", err_msg)
        self.assertEqual(Question.objects.count(), 0)

    def test_invalid_values(self):
        # Invalid exam_code, correct_answer, language, and difficulty
        csv_content = (
            "exam_code,paper_code,subject_code,topic_code,"
            "question_text,option_a,option_b,option_c,option_d,"
            "correct_answer,language,difficulty\n"
            "UNKNOWN_EXAM,Paper 1,Math,Algebra,Solve x,1,2,3,4,E,FRENCH,SuperHard\n"
        )
        file_path = self.create_file("invalid_values.csv", csv_content)

        with self.assertRaises(CommandError) as ctx:
            call_command("import_questions", str(file_path))

        err_msg = str(ctx.exception)
        self.assertIn("row_number: 1", err_msg)
        self.assertIn("field: exam_code", err_msg)
        self.assertIn("value: 'UNKNOWN_EXAM'", err_msg)
        self.assertIn("field: correct_answer", err_msg)
        self.assertIn("value: 'E'", err_msg)
        self.assertIn("field: language", err_msg)
        self.assertIn("value: 'FRENCH'", err_msg)
        self.assertIn("field: difficulty", err_msg)
        self.assertIn("value: 'SuperHard'", err_msg)
        self.assertEqual(Question.objects.count(), 0)

    def test_duplicate_questions_within_import(self):
        csv_content = (
            "exam_code,paper_code,subject_code,topic_code,"
            "question_text,option_a,option_b,option_c,option_d,correct_answer\n"
            "JHTET,Paper 1,Math,Arithmetic,What is 2+2?,1,2,3,4,D\n"
            "JHTET,Paper 1,Math,Arithmetic,What is 2+2?,1,2,3,4,D\n"
        )
        file_path = self.create_file("duplicate_file.csv", csv_content)

        with self.assertRaises(CommandError) as ctx:
            call_command("import_questions", str(file_path))

        err_msg = str(ctx.exception)
        self.assertIn("row_number: 2", err_msg)
        self.assertIn("field: question_text", err_msg)
        self.assertIn("Duplicate question found within import (matches row 1)", err_msg)
        self.assertEqual(Question.objects.count(), 0)

    def test_duplicate_question_against_existing_database(self):
        Question.objects.create(
            exam="JHTET",
            paper="Paper 1",
            subject="Math",
            topic="Arithmetic",
            question_text="What is 2+2?",
            option_a="1",
            option_b="2",
            option_c="3",
            option_d="4",
            correct_answer="D",
        )

        csv_content = (
            "exam_code,paper_code,subject_code,topic_code,"
            "question_text,option_a,option_b,option_c,option_d,correct_answer\n"
            "JHTET,Paper 1,Math,Arithmetic,What is 2+2?,1,2,3,4,D\n"
        )
        file_path = self.create_file("duplicate_db.csv", csv_content)

        with self.assertRaises(CommandError) as ctx:
            call_command("import_questions", str(file_path))

        err_msg = str(ctx.exception)
        self.assertIn("row_number: 1", err_msg)
        self.assertIn("field: question_text", err_msg)
        self.assertIn("Question already exists in database", err_msg)
        self.assertEqual(Question.objects.count(), 1)

    def test_dry_run_success(self):
        csv_content = (
            "exam_code,paper_code,subject_code,topic_code,"
            "question_text,option_a,option_b,option_c,option_d,correct_answer\n"
            "JHTET,Paper 1,Math,Arithmetic,What is 5*5?,20,25,30,35,B\n"
        )
        file_path = self.create_file("dry_run_valid.csv", csv_content)

        out = StringIO()
        call_command("import_questions", str(file_path), dry_run=True, stdout=out)

        self.assertEqual(Question.objects.count(), 0)
        self.assertIn("Validation successful (dry-run)", out.getvalue())

    def test_dry_run_with_errors(self):
        csv_content = (
            "exam_code,paper_code,subject_code,topic_code,"
            "question_text,option_a,option_b,option_c,option_d,correct_answer\n"
            "INVALID,Paper 1,Math,Arithmetic,,20,25,30,35,B\n"
        )
        file_path = self.create_file("dry_run_invalid.csv", csv_content)

        with self.assertRaises(CommandError) as ctx:
            call_command("import_questions", str(file_path), dry_run=True)

        err_msg = str(ctx.exception)
        self.assertIn("row_number: 1", err_msg)
        self.assertIn("field: exam_code", err_msg)
        self.assertIn("field: question_text", err_msg)
        self.assertEqual(Question.objects.count(), 0)

    def test_unknown_fields_reported(self):
        csv_content = (
            "exam_code,paper_code,subject_code,topic_code,unknown_column,"
            "question_text,option_a,option_b,option_c,option_d,correct_answer\n"
            "JHTET,Paper 1,Math,Arithmetic,EXTRA,What is 1+2?,1,2,3,4,C\n"
        )
        file_path = self.create_file("unknown_field.csv", csv_content)

        with self.assertRaises(CommandError) as ctx:
            call_command("import_questions", str(file_path))

        err_msg = str(ctx.exception)
        self.assertIn("row_number: 1", err_msg)
        self.assertIn("field: unknown_column", err_msg)
        self.assertIn("Unknown field 'unknown_column'", err_msg)
        self.assertEqual(Question.objects.count(), 0)

    def test_unsupported_file_extension(self):
        file_path = self.create_file("questions.txt", "some content")
        with self.assertRaises(CommandError) as ctx:
            call_command("import_questions", str(file_path))

        self.assertIn("Unsupported file format '.txt'", str(ctx.exception))
