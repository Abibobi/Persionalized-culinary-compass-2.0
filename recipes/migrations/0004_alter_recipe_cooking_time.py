# Generated by Django 5.1.2 on 2024-10-23 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0003_alter_recipe_nutritional_info"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="cooking_time",
            field=models.CharField(max_length=200),
        ),
    ]
