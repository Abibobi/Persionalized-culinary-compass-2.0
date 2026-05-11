from django.contrib import admin

from .models import MealPlan, MealPlanItem


class MealPlanItemInline(admin.TabularInline):
	model = MealPlanItem
	extra = 0


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
	list_display = ("user", "date", "day_type", "num_meals", "total_calories")
	list_filter = ("day_type", "date")
	inlines = [MealPlanItemInline]
