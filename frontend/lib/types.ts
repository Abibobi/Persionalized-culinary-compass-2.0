export type UserProfile = {
  diet_type: string;
  health_conditions: string[];
  allergies: string[];
  disliked_ingredients: string[];
  preferred_cuisines: string[];
  calorie_target: number | null;
  protein_target_g: number | null;
  carbs_target_g: number | null;
  fat_target_g: number | null;
  max_cooking_time_min: number | null;
  spice_tolerance: number | null;
  onboarding_completed: boolean;
};

export type RecipeSummary = {
  id: number;
  name: string;
  category: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  cooking_time: number;
  spicy_level: number;
  is_vegetarian: boolean;
};

export type RankedRecipe = RecipeSummary & {
  score: number;
  explanation: {
    why: string;
  };
};

export type SearchWarning = {
  recipe_id: number;
  warnings: Array<{ severity?: string; message?: string; rule_key?: string }>;
};

export type AISuggestion = {
  name: string;
  description: string;
  estimated_calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  cooking_time_min: number;
  ingredients: string;
  instructions: string;
};

export type SearchResponse = {
  search_log_id: number;
  normalized_query: string;
  parsed_filters: Record<string, string | number>;
  results: RankedRecipe[];
  warnings: SearchWarning[];
  ai_suggestions?: {
    source: string;
    recipes: AISuggestion[];
    note: string;
  };
};

export type RecipeDetail = RecipeSummary & {
  description: string;
  ingredients: string;
  instructions: string | null;
  fiber: number;
  vitamins: Record<string, number>;
};

export type UserRecipeInteraction = {
  id: number;
  interaction_type: "saved" | "liked" | "disliked" | "cooked";
  rating: number | null;
  note: string | null;
  created_at: string;
  recipe: RecipeSummary;
};

export type MealPlanItem = {
  id: number;
  meal_type: "breakfast" | "lunch" | "dinner" | "snack";
  recipe: number;
  recipe_name: string;
  servings: number;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
};

export type MealPlan = {
  id: number;
  date: string;
  day_type: "normal" | "workout" | "low_carb";
  num_meals: number;
  target_calories: number | null;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  warnings: string[];
  created_at: string;
  items: MealPlanItem[];
};

export type DashboardSummary = {
  user: { id: number; username: string; email: string };
  profile: {
    diet_type: string;
    onboarding_completed: boolean;
    calorie_target: number | null;
    max_cooking_time_min: number | null;
    allergies_count: number;
    health_conditions_count: number;
  };
  stats: {
    saved_recipes_count: number;
    recent_searches_count: number;
    active_meal_plan: number | null;
  };
};

export type SearchLogEntry = {
  id: number;
  raw_query: string;
  normalized_query: string;
  parsed_filters: Record<string, unknown>;
  result_count: number;
  latency_ms: number;
  created_at: string;
};
