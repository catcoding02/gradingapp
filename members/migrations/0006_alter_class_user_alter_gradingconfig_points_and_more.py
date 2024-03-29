# Generated by Django 5.0 on 2024-01-15 21:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0005_gradingconfig_points_gradingconfig_row_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="class",
            name="user",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="gradingconfig",
            name="points",
            field=models.CharField(default="Points", max_length=200),
        ),
        migrations.AlterField(
            model_name="gradingconfig",
            name="row",
            field=models.CharField(default="Row", max_length=200),
        ),
        migrations.AlterField(
            model_name="gradingconfig",
            name="standard",
            field=models.CharField(default="Standard", max_length=200),
        ),
        migrations.AlterField(
            model_name="student",
            name="user_1",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_1",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
