# Generated by Django 5.0.8 on 2024-08-15 17:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("zonprep_file_parsing", "0009_zonpreppurchaseorder"),
    ]

    operations = [
        migrations.RenameField(
            model_name="zonpreppurchaseorder",
            old_name="P_pallets",
            new_name="p_pallets",
        ),
    ]