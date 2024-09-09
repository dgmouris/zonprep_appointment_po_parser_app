# Generated by Django 5.0.8 on 2024-09-08 22:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "zonprep_file_parsing",
            "0014_rename_appointment_id_zonprepappointment_request_id",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="zonprepappointment",
            name="raw_attachment_download",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="zonprep_appointment_attachments/",
                verbose_name="storage",
            ),
        ),
    ]