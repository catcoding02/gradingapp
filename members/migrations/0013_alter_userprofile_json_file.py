# Generated by Django 5.0 on 2024-01-16 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0012_rename_sheet_name_userprofile_google_sheet_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="json_file",
            field=models.FileField(
                blank=True, null=True, upload_to="documents/%Y/%m/%d"
            ),
        ),
    ]
