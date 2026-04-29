"""
Gemini LLM fallback – used when the deterministic search returns zero results.

Calls Google Generative AI to suggest recipes matching the user's query,
then attempts to find similar recipes in the local database.
If no local matches, returns AI-generated suggestions clearly labelled.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    try:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return None
        _client = genai.Client(api_key=api_key)
        return _client
    except Exception as exc:
        logger.warning("Gemini client init failed: %s", exc)
        return None


SYSTEM_PROMPT = (
    "You are a culinary nutrition assistant. The user searched for recipes but "
    "got zero results from our database. Suggest 3-5 recipe ideas that match "
    "their query. Return ONLY a JSON array of objects with keys: "
    '"name", "description", "estimated_calories", "protein_g", "carbs_g", '
    '"fat_g", "cooking_time_min", "ingredients" (comma-separated string), '
    '"instructions" (brief). No markdown fences, just raw JSON.'
)


def gemini_recipe_suggestions(query, user_profile=None):
    """
    Ask Gemini for recipe suggestions. Returns a dict with 'source' and 'recipes'.
    Gracefully returns empty list if Gemini is unavailable.
    """
    client = _get_client()
    if client is None:
        return {"source": "gemini", "recipes": [], "note": "Gemini API not configured."}

    profile_context = ""
    if user_profile:
        parts = []
        if user_profile.diet_type and user_profile.diet_type != "omnivore":
            parts.append(f"Diet: {user_profile.diet_type}")
        if user_profile.allergies:
            parts.append(f"Allergies: {', '.join(user_profile.allergies)}")
        if user_profile.health_conditions:
            parts.append(f"Health conditions: {', '.join(user_profile.health_conditions)}")
        if user_profile.calorie_target:
            parts.append(f"Calorie target: {user_profile.calorie_target} kcal/day")
        if parts:
            profile_context = "\nUser profile: " + "; ".join(parts)

    prompt = f"User query: \"{query}\"{profile_context}"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.7,
                "max_output_tokens": 1500,
            },
        )
        text = response.text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        recipes = json.loads(text)
        return {
            "source": "gemini",
            "recipes": recipes,
            "note": "These are AI-generated suggestions, not from our recipe database.",
        }
    except Exception as exc:
        logger.error("Gemini fallback failed: %s", exc)
        return {"source": "gemini", "recipes": [], "note": f"AI suggestion failed: {exc}"}
