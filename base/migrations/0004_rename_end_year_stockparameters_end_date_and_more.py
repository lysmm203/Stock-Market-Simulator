# Generated by Django 4.1.3 on 2023-01-29 02:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0003_alter_stockparameters_end_year_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="stockparameters",
            old_name="end_year",
            new_name="end_date",
        ),
        migrations.RenameField(
            model_name="stockparameters",
            old_name="start_year",
            new_name="start_date",
        ),
    ]