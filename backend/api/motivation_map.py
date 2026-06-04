_NAMES: dict[str, dict[str, str]] = {
    "Career growth":                     {"en": "Career growth",                    "fr": "Évolution de carrière",              "de": "Karriereentwicklung",            "zh": "职业发展"},
    "Travel":                            {"en": "Travel",                            "fr": "Voyages",                            "de": "Reisen",                         "zh": "旅行"},
    "Relocating abroad":                 {"en": "Relocating abroad",                 "fr": "Déménagement à l'étranger",          "de": "Auswanderung",                   "zh": "出国定居"},
    "University studies":                {"en": "University studies",                "fr": "Études universitaires",              "de": "Universitätsstudium",            "zh": "大学学习"},
    "Business communication":            {"en": "Business communication",            "fr": "Communication professionnelle",      "de": "Geschäftskommunikation",         "zh": "商务沟通"},
    "Watching movies without subtitles": {"en": "Watching movies without subtitles", "fr": "Regarder des films sans sous-titres","de": "Filme ohne Untertitel schauen",  "zh": "无字幕看电影"},
    "Speaking with family":              {"en": "Speaking with family",              "fr": "Parler avec la famille",             "de": "Mit Familie sprechen",           "zh": "与家人交流"},
    "Personal interest":                 {"en": "Personal interest",                 "fr": "Intérêt personnel",                  "de": "Persönliches Interesse",         "zh": "个人兴趣"},
}


def localize_motivation(label: str, ui_lang: str) -> str:
    return _NAMES.get(label, {}).get(ui_lang.lower(), label)
