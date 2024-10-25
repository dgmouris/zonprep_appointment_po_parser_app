# Generated by Django 5.0.8 on 2024-10-25 15:52

import apps.utils.storage
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zonprep_file_parsing", "0019_zonprepappointment_p_actual_arrival_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="zonpreppurchaseorder",
            name="raw_parsed_attachment_json_field",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="ZonprepPOImageAttachments",
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
                (
                    "image_attachment",
                    models.FileField(
                        blank=True,
                        null=True,
                        storage=apps.utils.storage.CustomGoogleCloudStorage(),
                        upload_to="zonprep_po_image_attachments/",
                    ),
                ),
                (
                    "raw_parsed_attachment_json_field",
                    models.JSONField(blank=True, null=True),
                ),
                (
                    "purchase_order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="image_attachments",
                        to="zonprep_file_parsing.zonpreppurchaseorder",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ZonprepPurchaseOrderSKU",
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
                ("p_fnsku", models.CharField(blank=True, max_length=255, null=True)),
                ("p_iaid", models.CharField(blank=True, max_length=255, null=True)),
                ("p_msku", models.CharField(blank=True, max_length=255, null=True)),
                ("p_weight", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "p_shipped_quantity",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "p_recieved_quantity",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "p_update_date",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "p_create_date",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "p_prep_details_item_labelling",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "p_prep_details_item_labelling_owner",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "p_prep_details_item_labelling_cost_owner",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "p_prep_details_polybagging",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "p_prep_details_polybagging_owner",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "p_prep_details_polybagging_cost_owner",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "purchase_order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skus",
                        to="zonprep_file_parsing.zonpreppurchaseorder",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
