_NAMES: dict[str, dict[str, str]] = {
    "technology":  {"en": "Technology",  "fr": "Technologie",   "de": "Technologie",   "zh": "科技"},
    "gaming":      {"en": "Gaming",       "fr": "Jeux vidéo",    "de": "Gaming",        "zh": "游戏"},
    "football":    {"en": "Football",     "fr": "Football",      "de": "Fußball",       "zh": "足球"},
    "basketball":  {"en": "Basketball",   "fr": "Basketball",    "de": "Basketball",    "zh": "篮球"},
    "anime":       {"en": "Anime",        "fr": "Animé",         "de": "Anime",         "zh": "动漫"},
    "cooking":     {"en": "Cooking",      "fr": "Cuisine",       "de": "Kochen",        "zh": "烹饪"},
    "travel":      {"en": "Travel",       "fr": "Voyages",       "de": "Reisen",        "zh": "旅行"},
    "reading":     {"en": "Reading",      "fr": "Lecture",       "de": "Lesen",         "zh": "阅读"},
    "business":    {"en": "Business",     "fr": "Business",      "de": "Business",      "zh": "商业"},
    "fitness":     {"en": "Fitness",      "fr": "Fitness",       "de": "Fitness",       "zh": "健身"},
    "movies":      {"en": "Movies",       "fr": "Cinéma",        "de": "Filme",         "zh": "电影"},
    "music":       {"en": "Music",        "fr": "Musique",       "de": "Musik",         "zh": "音乐"},
    "photography": {"en": "Photography",  "fr": "Photographie",  "de": "Fotografie",    "zh": "摄影"},
}


def localize_hobby(name: str, ui_lang: str) -> str:
    return _NAMES.get(name.lower(), {}).get(ui_lang.lower(), name)
