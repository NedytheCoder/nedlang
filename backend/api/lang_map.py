# Localized language names: _NAMES[language_code][ui_lang] = display name
# Add a new ui_lang column when a new UI language is supported.
# Add a new row when a new target/native language is added to the app.

_NAMES: dict[str, dict[str, str]] = {
    "en": {"en": "English",    "fr": "Anglais",      "de": "Englisch",      "zh": "英语"},
    "fr": {"en": "French",     "fr": "Français",     "de": "Französisch",   "zh": "法语"},
    "de": {"en": "German",     "fr": "Allemand",     "de": "Deutsch",       "zh": "德语"},
    "es": {"en": "Spanish",    "fr": "Espagnol",     "de": "Spanisch",      "zh": "西班牙语"},
    "pt": {"en": "Portuguese", "fr": "Portugais",    "de": "Portugiesisch", "zh": "葡萄牙语"},
    "it": {"en": "Italian",    "fr": "Italien",      "de": "Italienisch",   "zh": "意大利语"},
    "nl": {"en": "Dutch",      "fr": "Néerlandais",  "de": "Niederländisch","zh": "荷兰语"},
    "zh": {"en": "Chinese",    "fr": "Chinois",      "de": "Chinesisch",    "zh": "中文"},
    "ja": {"en": "Japanese",   "fr": "Japonais",     "de": "Japanisch",     "zh": "日语"},
    "ko": {"en": "Korean",     "fr": "Coréen",       "de": "Koreanisch",    "zh": "韩语"},
    "ar": {"en": "Arabic",     "fr": "Arabe",        "de": "Arabisch",      "zh": "阿拉伯语"},
    "ru": {"en": "Russian",    "fr": "Russe",        "de": "Russisch",      "zh": "俄语"},
}


def localize(code: str, ui_lang: str, fallback: str) -> str:
    return _NAMES.get(code.lower(), {}).get(ui_lang.lower(), fallback)
