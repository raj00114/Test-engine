# Generated manually to align the applied legacy syllabus schema with
# syllabus.models.Syllabus.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("syllabus", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="syllabus",
            old_name="title",
            new_name="topic",
        ),
        migrations.AlterField(
            model_name="syllabus",
            name="exam",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="syllabus",
            name="paper",
            field=models.CharField(max_length=100),
        ),
        migrations.AddField(
            model_name="syllabus",
            name="subject",
            field=models.CharField(default="", max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="syllabus",
            name="subtopic",
            field=models.CharField(blank=True, default="", max_length=250),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name="syllabus",
            name="description",
        ),
        migrations.RemoveField(
            model_name="syllabus",
            name="source",
        ),
        migrations.RemoveField(
            model_name="syllabus",
            name="created_at",
        ),
        migrations.DeleteModel(
            name="SyllabusTopic",
        ),
        migrations.AlterModelOptions(
            name="syllabus",
            options={
                "ordering": ["exam", "paper", "subject", "topic", "subtopic"],
            },
        ),
    ]
