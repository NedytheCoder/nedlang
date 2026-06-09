_NAMES: dict[str, dict[str, str]] = {
    "technology":  {"en": "Technology",  "fr": "Technologie",   "de": "Technologie",   "zh": "科技",  "es": "Tecnología"},
    "gaming":      {"en": "Gaming",       "fr": "Jeux vidéo",    "de": "Gaming",        "zh": "游戏",  "es": "Videojuegos"},
    "football":    {"en": "Football",     "fr": "Football",      "de": "Fußball",       "zh": "足球",  "es": "Fútbol"},
    "basketball":  {"en": "Basketball",   "fr": "Basketball",    "de": "Basketball",    "zh": "篮球",  "es": "Baloncesto"},
    "anime":       {"en": "Anime",        "fr": "Animé",         "de": "Anime",         "zh": "动漫",  "es": "Anime"},
    "cooking":     {"en": "Cooking",      "fr": "Cuisine",       "de": "Kochen",        "zh": "烹饪",  "es": "Cocina"},
    "travel":      {"en": "Travel",       "fr": "Voyages",       "de": "Reisen",        "zh": "旅行",  "es": "Viajes"},
    "reading":     {"en": "Reading",      "fr": "Lecture",       "de": "Lesen",         "zh": "阅读",  "es": "Lectura"},
    "business":    {"en": "Business",     "fr": "Business",      "de": "Business",      "zh": "商业",  "es": "Negocios"},
    "fitness":     {"en": "Fitness",      "fr": "Fitness",       "de": "Fitness",       "zh": "健身",  "es": "Ejercicio"},
    "movies":      {"en": "Movies",       "fr": "Cinéma",        "de": "Filme",         "zh": "电影",  "es": "Cine"},
    "music":       {"en": "Music",        "fr": "Musique",       "de": "Musik",         "zh": "音乐",  "es": "Música"},
    "photography": {"en": "Photography",  "fr": "Photographie",  "de": "Fotografie",    "zh": "摄影",  "es": "Fotografía"},
}


def localize_hobby(name: str, ui_lang: str) -> str:
    return _NAMES.get(name.lower(), {}).get(ui_lang.lower(), name)
