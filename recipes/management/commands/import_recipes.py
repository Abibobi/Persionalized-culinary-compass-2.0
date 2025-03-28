import csv
from django.core.management.base import BaseCommand
from recipes.models import Recipe  # replace 'your_app' with the actual app name

class Command(BaseCommand):
    help = 'Import recipes from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The CSV file to import')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Recipe.objects.create(
                    name=row['name'],
                    description=row['description'],
                    ingredients=row['ingredients'],
                    category=row['category'],
                    protein=float(row['protein']),
                    carbs=float(row['carbs']),
                    fat=float(row['fat']),
                    fiber=float(row['fiber']),
                    vitamins=row['vitamins'],
                    calories=int(row['calories']),
                    cooking_time=int(row['cooking_time']),
                    spicy_level=int(row['spicy_level']),
                    instructions=row['instructions'],
                    is_vegetarian=row['is_vegetarian'] == 'TRUE'  # Convert to boolean
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully imported recipe: {row["name"]}'))
