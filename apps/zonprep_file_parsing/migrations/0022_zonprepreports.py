# Generated by Django 5.0.8 on 2024-11-21 23:22

import apps.utils.storage
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zonprep_file_parsing", "0021_zonpreppurchaseordersku_p_all_prep_details"),
    ]

    operations = [
        migrations.CreateModel(
            name="ZonprepReports",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("report_type", models.CharField(max_length=255)),
                (
                    "report_document",
                    models.FileField(
                        blank=True,
                        null=True,
                        storage=apps.utils.storage.CustomGoogleCloudStorage(),
                        upload_to="zonprep_reports/",
                    ),
                ),
                ("report_start_date", models.DateField(blank=True, null=True)),
                ("report_end_date", models.DateField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
