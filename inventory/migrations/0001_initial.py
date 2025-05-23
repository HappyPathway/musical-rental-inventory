# Generated by Django 4.2.11 on 2025-03-29 17:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name_plural": "Categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Equipment",
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
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("brand", models.CharField(max_length=100)),
                ("model_number", models.CharField(blank=True, max_length=100)),
                (
                    "serial_number",
                    models.CharField(blank=True, max_length=100, unique=True),
                ),
                ("purchase_date", models.DateField(blank=True, null=True)),
                (
                    "purchase_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "rental_price_daily",
                    models.DecimalField(decimal_places=2, max_digits=8),
                ),
                (
                    "rental_price_weekly",
                    models.DecimalField(decimal_places=2, max_digits=8),
                ),
                (
                    "rental_price_monthly",
                    models.DecimalField(decimal_places=2, max_digits=8),
                ),
                ("deposit_amount", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("available", "Available"),
                            ("rented", "Rented"),
                            ("maintenance", "Under Maintenance"),
                            ("damaged", "Damaged"),
                            ("retired", "Retired"),
                        ],
                        default="available",
                        max_length=20,
                    ),
                ),
                ("condition", models.TextField(blank=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "qr_code",
                    models.ImageField(blank=True, null=True, upload_to="qr_codes/"),
                ),
                (
                    "qr_uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "main_image",
                    models.ImageField(
                        blank=True, null=True, upload_to="equipment_images/"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="equipment",
                        to="inventory.category",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="MaintenanceRecord",
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
                ("date", models.DateField()),
                ("description", models.TextField()),
                (
                    "cost",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("performed_by", models.CharField(blank=True, max_length=100)),
                (
                    "equipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="maintenance_records",
                        to="inventory.equipment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalEquipment",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("brand", models.CharField(max_length=100)),
                ("model_number", models.CharField(blank=True, max_length=100)),
                (
                    "serial_number",
                    models.CharField(blank=True, db_index=True, max_length=100),
                ),
                ("purchase_date", models.DateField(blank=True, null=True)),
                (
                    "purchase_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "rental_price_daily",
                    models.DecimalField(decimal_places=2, max_digits=8),
                ),
                (
                    "rental_price_weekly",
                    models.DecimalField(decimal_places=2, max_digits=8),
                ),
                (
                    "rental_price_monthly",
                    models.DecimalField(decimal_places=2, max_digits=8),
                ),
                ("deposit_amount", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("available", "Available"),
                            ("rented", "Rented"),
                            ("maintenance", "Under Maintenance"),
                            ("damaged", "Damaged"),
                            ("retired", "Retired"),
                        ],
                        default="available",
                        max_length=20,
                    ),
                ),
                ("condition", models.TextField(blank=True)),
                ("notes", models.TextField(blank=True)),
                ("qr_code", models.TextField(blank=True, max_length=100, null=True)),
                (
                    "qr_uuid",
                    models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
                ),
                ("main_image", models.TextField(blank=True, max_length=100, null=True)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="inventory.category",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical equipment",
                "verbose_name_plural": "historical equipments",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="EquipmentAttachment",
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
                ("file", models.FileField(upload_to="equipment_attachments/")),
                ("description", models.CharField(blank=True, max_length=255)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "equipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="inventory.equipment",
                    ),
                ),
            ],
        ),
    ]
