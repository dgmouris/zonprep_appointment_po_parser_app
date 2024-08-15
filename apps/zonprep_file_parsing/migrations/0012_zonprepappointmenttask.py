# Generated by Django 5.0.8 on 2024-08-15 20:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zonprep_file_parsing", "0011_alter_zonpreppurchaseorder_p_arn"),
    ]

    operations = [
        migrations.CreateModel(
            name="ZonprepAppointmentTask",
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
                ("task_name", models.CharField(max_length=255)),
                ("state", models.CharField(max_length=255)),
                (
                    "successful",
                    models.BooleanField(blank=True, default=False, null=True),
                ),
                ("error_details", models.TextField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
