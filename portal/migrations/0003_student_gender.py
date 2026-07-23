from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0002_resultpublication"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Other", "Other"),
                    ("Prefer not to say", "Prefer not to say"),
                ],
                help_text="Example: Male, Female, or Other",
                max_length=30,
            ),
        ),
    ]
