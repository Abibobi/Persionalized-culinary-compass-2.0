# Generated by Django 5.1.2 on 2024-10-23 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="ingredients",
            field=models.CharField(max_length=500),
        ),
    ]
