# Generated by Django 5.0.8 on 2024-08-12 21:12

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("zonprep_file_parsing", "0003_externalfulfillmentemail"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="externalfulfillmentemail",
            name="site_name",
        ),
    ]
