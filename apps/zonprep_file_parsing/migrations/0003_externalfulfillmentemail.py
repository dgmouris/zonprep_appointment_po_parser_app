# Generated by Django 5.0.8 on 2024-08-12 21:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zonprep_file_parsing", "0002_zonprepappointment_created_at_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExternalFulfillmentEmail",
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
                ("site_name", models.CharField(max_length=100)),
                ("name", models.CharField(max_length=100)),
                ("contact_email", models.EmailField(max_length=254)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
