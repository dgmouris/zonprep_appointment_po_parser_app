# Generated by Django 5.0.8 on 2024-08-15 18:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "zonprep_file_parsing",
            "0010_rename_p_pallets_zonpreppurchaseorder_p_pallets",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="zonpreppurchaseorder",
            name="p_arn",
            field=models.TextField(blank=True, null=True),
        ),
    ]
