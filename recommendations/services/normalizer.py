import re
from rapidfuzz import process, fuzz
from .ingredients_vocab import INGREDIENT_VOCAB

TYPO_MAP = {
    "protien": "protein",
    "vegn": "vegan",
    "vegitarian": "vegetarian",
    "lowcarb": "low carb",
}


def normalize_query(raw: str) -> str:
    text = raw.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # apply hard typo map
    for wrong, correct in TYPO_MAP.items():
        text = text.replace(wrong, correct)

    # fuzzy ingredient corrections
    corrected_tokens = []
    for token in text.split():
        match = process.extractOne(
            token,
            INGREDIENT_VOCAB,
            scorer=fuzz.ratio,
            score_cutoff=85,
        )
        corrected_tokens.append(match[0] if match else token)

    return " ".join(corrected_tokens)