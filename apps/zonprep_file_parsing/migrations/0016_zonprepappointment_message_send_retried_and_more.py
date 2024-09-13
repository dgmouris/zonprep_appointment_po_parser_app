# Generated by Django 5.0.8 on 2024-09-13 22:00

import apps.utils.storage
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "zonprep_file_parsing",
            "0015_alter_zonprepappointment_raw_attachment_download",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="zonprepappointment",
            name="message_send_retried",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="zonprepappointment",
            name="raw_attachment_download",
            field=models.FileField(
                blank=True,
                null=True,
                storage=apps.utils.storage.CustomGoogleCloudStorage(),
                upload_to="zonprep_appointment_attachments/",
            ),
        ),
    ]