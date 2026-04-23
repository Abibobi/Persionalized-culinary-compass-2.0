import csv
import json
from django.core.management.base import BaseCommand
from recipes.models import Recipe

class Command(BaseCommand):
    help = 'Import recipes from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The CSV file to import')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        imported_count = 0
        skipped_count = 0

        with open(csv_file, 'r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            for row_number, row in enumerate(reader, start=2):
                try:
                    recipe = Recipe.objects.create(
                        name=self._required(row, "name"),
                        description=self._required(row, "description"),
                        ingredients=self._required(row, "ingredients"),
                        category=self._required(row, "category"),
                        protein=float(self._required(row, "protein")),
                        carbs=float(self._required(row, "carbs")),
                        fat=float(self._required(row, "fat")),
                        fiber=float(self._required(row, "fiber")),
                        vitamins=self._parse_vitamins(row.get("vitamins")),
                        calories=int(self._required(row, "calories")),
                        cooking_time=int(self._required(row, "cooking_time")),
                        spicy_level=int(self._required(row, "spicy_level")),
                        instructions=(row.get("instructions") or "").strip(),
                        is_vegetarian=self._parse_bool(row.get("is_vegetarian")),
                    )
                    imported_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully imported recipe: {recipe.name}'))
                except (ValueError, TypeError, json.JSONDecodeError) as exc:
                    skipped_count += 1
                    self.stderr.write(
                        self.style.WARNING(f"Skipping row {row_number}: {exc}")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Imported: {imported_count}, Skipped: {skipped_count}"
            )
        )

    @staticmethod
    def _required(row, key):
        value = (row.get(key) or "").strip()
        if not value:
            raise ValueError(f"Missing required field '{key}'")
        return value

    @staticmethod
    def _parse_bool(value):
        if value is None:
            return False
        return str(value).strip().lower() in {"true", "1", "yes", "y"}

    @staticmethod
    def _parse_vitamins(raw_value):
        if raw_value is None:
            return {}
        value = str(raw_value).strip()
        if not value:
            return {}

        parsed = json.loads(value)
        if not isinstance(parsed, dict):
            raise ValueError("Field 'vitamins' must be a JSON object.")
        return parsed
