"""
script.py
─────────
Database utilities for lingua_ai.db.

Public API
──────────
    get_connection()       → sqlite3.Connection
    create_database()      → None   (tables + indexes)
    drop_database()        → None   (wipe everything)
    seed_languages(conn)   → None
    seed_hobbies(conn)     → None
    initialize_database()  → None   (full first-run setup)
"""

import json
import sqlite3
import os
from database.schema import create_tables, drop_tables

# ─── Configuration ────────────────────────────────────────────────────────────

_DB_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(_DB_DIR, "lingua_ai.db")


# ─── Seed data ────────────────────────────────────────────────────────────────

_LANGUAGES: list[tuple[str, str, str]] = [
    # (code, name, native_name)
    ("en", "English",    "English"),
    ("fr", "French",     "Français"),
    ("de", "German",     "Deutsch"),
    ("zh", "Chinese",    "中文"),
    # ("es", "Spanish",    "Español"),
    # ("pt", "Portuguese", "Português"),
    # ("it", "Italian",    "Italiano"),
    # ("nl", "Dutch",      "Nederlands"),
    # ("ja", "Japanese",   "日本語"),
    # ("ko", "Korean",     "한국어"),
    # ("ar", "Arabic",     "العربية"),
    # ("ru", "Russian",    "Русский"),
]

_HOBBIES: list[str] = [
    "Technology",
    "Gaming",
    "Football",
    "Basketball",
    "Anime",
    "Cooking",
    "Travel",
    "Reading",
    "Business",
    "Fitness",
    "Movies",
    "Music",
    "Photography",
]

_MOTIVATIONS: list[str] = [
    "Career growth",
    "Travel",
    "Relocating abroad",
    "University studies",
    "Business communication",
    "Watching movies without subtitles",
    "Speaking with family",
    "Personal interest",
]


# ─── Connection ───────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    """
    Open (or create) lingua_ai.db and return a connection.

    - Row factory set to sqlite3.Row for dict-like access.
    - Foreign key enforcement enabled on every connection.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")   # better concurrent read performance
    return conn


# ─── Create / Drop ────────────────────────────────────────────────────────────

def create_database() -> None:
    """Create all tables and indexes. Idempotent."""
    conn = get_connection()
    try:
        create_tables(conn)
        print(f"[db] Tables and indexes created → {DB_PATH}")
    finally:
        conn.close()


def drop_database() -> None:
    """
    Drop every table.  All data is permanently deleted.
    Use only in development / test resets.
    """
    conn = get_connection()
    try:
        drop_tables(conn)
        print(f"[db] All tables dropped → {DB_PATH}")
    finally:
        conn.close()


# ─── Seed data (continued) ───────────────────────────────────────────────────

# XP level bands — (level_no, label, xp_required, xp_to_next)
# Designed so that xp=8240 lands in level 5 (7000–10000), matching mock data.
_XP_LEVELS: list[tuple[int, str, int, int | None]] = [
    (1,  "Novice",            0,      1000),
    (2,  "Beginner",          1000,   1500),
    (3,  "Elementary",        2500,   2000),
    (4,  "Pre-Intermediate",  4500,   2500),
    (5,  "Intermediate",      7000,   3000),
    (6,  "Upper-Intermediate",10000,  3500),
    (7,  "Advanced",          13500,  4500),
    (8,  "Proficient",        18000,  6000),
    (9,  "Expert",            24000,  8000),
    (10, "Master",            32000,  None),
]

# Achievements — (name, description, xp_reward)
_ACHIEVEMENTS: list[tuple[str, str, int]] = [
    # ── Firsts ────────────────────────────────────────────────────────────────
    ("first_lesson",          "Complete your first lesson",                           50),
    ("first_convo",           "Complete your first conversation",                     50),
    ("first_assessment",      "Complete your first assessment",                       50),

    # ── Vocabulary ────────────────────────────────────────────────────────────
    ("hundred_words",         "Learn 100 vocabulary words",                           100),
    ("vocab_explorer",        "Learn 500 vocabulary words",                           200),
    ("vocab_master",          "Learn 1000 vocabulary words",                          500),

    # ── Streaks ───────────────────────────────────────────────────────────────
    ("streak_3",              "Study 3 days in a row",                                50),
    ("streak_7",              "Study 7 days in a row",                                100),
    ("streak_30",             "Study 30 days in a row",                               500),
    ("streak_100",            "Study 100 days in a row",                              1000),

    # ── Grammar ───────────────────────────────────────────────────────────────
    ("grammar_master",        "Master 10 grammar topics",                             200),
    ("grammar_expert",        "Master 25 grammar topics",                             500),

    # ── Skills ────────────────────────────────────────────────────────────────
    ("listening_specialist",  "Complete 20 listening exercises",                      200),
    ("reading_specialist",    "Complete 20 reading exercises",                        200),
    ("writing_specialist",    "Complete 20 writing exercises",                        200),
    ("speaking_specialist",   "Complete 20 speaking exercises",                       200),

    # ── Assessments ───────────────────────────────────────────────────────────
    ("assessment_champion",   "Complete 5 assessments",                               200),
    ("perfect_score",         "Score 100% on any assessment",                         500),

    # ── Levels ────────────────────────────────────────────────────────────────
    ("level_up",              "Reach app level 5 (Intermediate)",                     200),
    ("framework_advance",     "Advance one full framework level (e.g. A1 → A2)",      300),

    # ── Study time ────────────────────────────────────────────────────────────
    ("ten_hours",             "Accumulate 10 hours of study time",                    100),
    ("fifty_hours",           "Accumulate 50 hours of study time",                    300),
    ("hundred_hours",         "Accumulate 100 hours of study time",                   500),
]


# ─── French A1 curriculum ─────────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_FRENCH_A1_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Sounds and Letters",              "Master the French alphabet, pronunciation, and accent marks",    4),
    (2,  "Core Grammar Foundations",        "Learn subject pronouns, sentence structure, être and avoir",    4),
    (3,  "Numbers, Time, and Identity",     "Numbers, dates, time, nationalities, and occupations",          5),
    (4,  "Nouns and Articles",              "Gender, definite and indefinite articles, and plurals",          4),
    (5,  "Adjectives",                      "Descriptive adjectives, agreement, and possessives",             3),
    (6,  "Verbs",                           "Regular -er/-ir/-re verbs and key irregular verbs",              6),
    (7,  "Questions and Negation",          "Negation, interrogatives, question forms, and opinions",         4),
    (8,  "Modifiers",                       "Prepositions, adverbs, and object pronouns",                    3),
    (9,  "Past and Future Tenses",          "Introduction to passé composé and futur proche",                2),
    (10, "Communication in the Real World", "Self-introduction, family, routines, and written expression",   7),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives)
_FRENCH_A1_NODES: list[tuple[int, int, str, list, list]] = [
    (1,  1,  "Alphabet",
        ["phonetics"],
        ["Recognize all 26 French letters", "Understand basic French pronunciation rules"]),
    (1,  2,  "Pronunciation",
        ["pronunciation"],
        ["Pronounce basic French sounds correctly", "Identify key differences from English pronunciation"]),
    (1,  3,  "French accents and special characters",
        ["phonetics"],
        ["Recognize and write accents (é, è, ê, à, ù, ç)", "Understand how accents affect pronunciation"]),
    (1,  4,  "Basic greetings and introductions",
        ["speaking", "vocabulary"],
        ["Use common greetings in context", "Introduce yourself in French"]),

    (2,  5,  "Subject pronouns",
        ["grammar"],
        ["Identify and use je, tu, il, elle, nous, vous, ils, elles", "Match pronouns to people and contexts"]),
    (2,  6,  "Basic sentence structure",
        ["grammar"],
        ["Form simple subject-verb sentences", "Understand French word order"]),
    (2,  7,  "Être",
        ["grammar"],
        ["Conjugate être in the present tense", "Use être to describe identity and state"]),
    (2,  8,  "Avoir",
        ["grammar"],
        ["Conjugate avoir in the present tense", "Use avoir in common expressions"]),

    (3,  9,  "Numbers 0–100",
        ["vocabulary"],
        ["Count from 0 to 100 in French", "Use numbers in everyday contexts"]),
    (3,  10, "Days, months, dates",
        ["vocabulary"],
        ["Name the days of the week and months", "Express dates in French"]),
    (3,  11, "Time expressions",
        ["vocabulary", "grammar"],
        ["Tell the time in French", "Use common time phrases"]),
    (3,  12, "Nationalities",
        ["vocabulary"],
        ["Name nationalities in French", "Apply gender agreement to nationality adjectives"]),
    (3,  13, "Occupations",
        ["vocabulary"],
        ["Name common occupations in French", "Talk about what you or others do for work"]),

    (4,  14, "Gender of nouns",
        ["grammar"],
        ["Identify masculine and feminine nouns", "Apply gender rules to new vocabulary"]),
    (4,  15, "Definite articles",
        ["grammar"],
        ["Use le, la, les correctly", "Understand when to use definite articles"]),
    (4,  16, "Indefinite articles",
        ["grammar"],
        ["Use un, une, des correctly", "Distinguish between definite and indefinite articles"]),
    (4,  17, "Plurals",
        ["grammar"],
        ["Form regular noun plurals", "Recognize common irregular plurals"]),

    (5,  18, "Adjectives",
        ["grammar", "vocabulary"],
        ["Use common descriptive adjectives", "Place adjectives correctly in sentences"]),
    (5,  19, "Agreement of adjectives",
        ["grammar"],
        ["Apply gender and number agreement to adjectives", "Recognize adjective endings for masculine and feminine"]),
    (5,  20, "Possessive adjectives",
        ["grammar"],
        ["Use mon, ma, mes, ton, ta, tes, son, sa, ses correctly", "Express possession in French"]),

    (6,  21, "Regular -er verbs",
        ["grammar"],
        ["Conjugate regular -er verbs in the present tense", "Use common -er verbs in sentences"]),
    (6,  22, "Regular -ir verbs",
        ["grammar"],
        ["Conjugate regular -ir verbs in the present tense", "Distinguish -ir from -er verb patterns"]),
    (6,  23, "Regular -re verbs",
        ["grammar"],
        ["Conjugate regular -re verbs in the present tense", "Use common -re verbs correctly"]),
    (6,  24, "Aller",
        ["grammar"],
        ["Conjugate aller in the present tense", "Use aller to express going and movement"]),
    (6,  25, "Faire",
        ["grammar"],
        ["Conjugate faire in the present tense", "Use faire in common idiomatic expressions"]),
    (6,  26, "Common irregular verbs",
        ["grammar"],
        ["Recognize and conjugate key irregular verbs", "Use irregular verbs in everyday sentences"]),

    (7,  27, "Negation (ne...pas)",
        ["grammar"],
        ["Form negative sentences using ne...pas", "Apply negation to different verb types"]),
    (7,  28, "Interrogatives",
        ["grammar"],
        ["Use qui, que, où, quand, pourquoi, comment", "Form questions with interrogative words"]),
    (7,  29, "Question forms",
        ["grammar", "speaking"],
        ["Ask questions using inversion and est-ce que", "Choose the appropriate question structure"]),
    (7,  30, "Preferences and opinions",
        ["speaking", "vocabulary"],
        ["Express likes and dislikes in French", "Give simple opinions using aimer, préférer, détester"]),

    (8,  31, "Prepositions",
        ["grammar"],
        ["Use common prepositions of place and time", "Choose correct prepositions with transport and location"]),
    (8,  32, "Adverbs",
        ["grammar"],
        ["Use common frequency and manner adverbs", "Position adverbs correctly in sentences"]),
    (8,  33, "Object pronouns",
        ["grammar"],
        ["Use direct object pronouns le, la, les", "Position object pronouns correctly in simple sentences"]),

    (9,  34, "Passé composé introduction",
        ["grammar"],
        ["Form the passé composé with avoir", "Use passé composé to talk about past events"]),
    (9,  35, "Futur proche",
        ["grammar"],
        ["Form the futur proche with aller + infinitive", "Use futur proche to talk about near-future plans"]),

    (10, 36, "Self-introduction",
        ["speaking"],
        ["Introduce yourself with name, age, origin, and occupation", "Hold a short introductory conversation"]),
    (10, 37, "Family and friends",
        ["speaking", "vocabulary"],
        ["Name family members in French", "Describe relationships and talk about people you know"]),
    (10, 38, "Routines",
        ["speaking", "vocabulary"],
        ["Describe daily routines using reflexive verbs", "Talk about habitual activities"]),
    (10, 39, "Short messages",
        ["writing"],
        ["Write a simple text message or note in French", "Use appropriate informal register"]),
    (10, 40, "Simple paragraphs",
        ["writing"],
        ["Write 3–5 sentence paragraphs on familiar topics", "Connect sentences using simple connectors"]),
    (10, 41, "Talking about plans",
        ["speaking", "grammar"],
        ["Express future intentions using futur proche", "Discuss plans with a partner or in writing"]),
    (10, 42, "Past experiences",
        ["speaking", "grammar"],
        ["Describe a simple past event using passé composé", "Talk about things you have done"]),
]


# ─── French A2 curriculum ─────────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_FRENCH_A2_MODULES: list[tuple[int, str, str, int]] = [
    (11, "Talking About the Past",                     "Master past tenses and use them naturally in stories and conversations",             6),
    (12, "Talking About the Future",                   "Express future plans, predictions, and intentions using correct tenses",             6),
    (13, "Daily Life, Habits & Responsibilities",      "Describe daily routines and express obligations with reflexive verbs and modals",    8),
    (14, "Expressing Cause and Consequence",           "Link ideas by explaining reasons and consequences using connectors",                 7),
    (15, "Making Comparisons",                         "Compare people, places, and things using comparative and superlative forms",         6),
    (16, "Pronouns Expansion",                         "Use direct and indirect object pronouns and expand into Y and EN",                  6),
    (17, "Quantities, Adverbs & Precision",            "Add precision using quantity expressions and adverbs of manner",                    8),
    (18, "Building Longer Sentences",                  "Use relative pronouns to connect and enrich sentences",                             5),
    (19, "Time & Location Expressions",                "Express duration, timing, and location with advanced prepositions",                 6),
    (20, "Expanded Negation",                          "Use a full range of negative structures naturally in conversation",                 6),
    (21, "Conditional Present & Polite Communication", "Form the conditional and use it for polite requests, wishes, and hypotheticals",    9),
    (22, "Real-World Communication",                   "Handle everyday situations including shopping, travel, and appointments",           8),
    (23, "Communication Mastery",                      "Engage in sustained conversations: opinions, narratives, and preferences",          8),
    (24, "Writing & Interaction",                      "Write informal messages, emails, and short narratives combining grammar concepts",  6),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
# prereq_topics are resolved to node IDs during seeding (two-pass).
_FRENCH_A2_NODES: list[tuple[int, int, str, list, list, list]] = [
    # ── Module 11: Talking About the Past ──────────────────────────────────────
    (11, 1,  "Passé Composé Review",
        ["concept"],
        ["Conjugate regular and common irregular verbs in passé composé",
         "Use avoir and être correctly as auxiliaries"],
        []),
    (11, 2,  "Imparfait",
        ["concept"],
        ["Form the imparfait for all verb groups",
         "Describe habitual actions and states in the past"],
        []),
    (11, 3,  "Passé Composé vs Imparfait",
        ["concept"],
        ["Distinguish when to use passé composé vs imparfait",
         "Narrate past events combining both tenses"],
        ["Passé Composé Review", "Imparfait"]),
    (11, 4,  "Plus-que-parfait (Introduction)",
        ["concept"],
        ["Form the plus-que-parfait using imperfect auxiliary + past participle",
         "Express an action that occurred before another past action"],
        ["Passé Composé Review"]),
    (11, 5,  "Talking About Past Experiences",
        ["communication"],
        ["Describe personal past experiences using passé composé and imparfait",
         "Ask and answer questions about past experiences"],
        ["Passé Composé vs Imparfait"]),
    (11, 6,  "Storytelling in the Past",
        ["skill"],
        ["Tell a coherent short story using multiple past tenses",
         "Use time expressions to sequence events naturally"],
        ["Talking About Past Experiences", "Plus-que-parfait (Introduction)"]),

    # ── Module 12: Talking About the Future ────────────────────────────────────
    (12, 7,  "Futur Proche Review",
        ["concept"],
        ["Form futur proche using aller + infinitive",
         "Use it for immediate or planned future events"],
        []),
    (12, 8,  "Futur Simple",
        ["concept"],
        ["Conjugate regular and irregular verbs in futur simple",
         "Express future facts, predictions, and intentions"],
        []),
    (12, 9,  "Futur Proche vs Futur Simple",
        ["concept"],
        ["Choose the appropriate future tense based on context",
         "Distinguish near-future plans from general future statements"],
        ["Futur Proche Review", "Futur Simple"]),
    (12, 10, "Discussing Plans",
        ["communication"],
        ["Talk about upcoming plans and arrangements",
         "Ask and answer questions about future plans"],
        ["Futur Proche vs Futur Simple"]),
    (12, 11, "Making Predictions",
        ["communication"],
        ["Make predictions about events using futur simple",
         "Express certainty and probability about the future"],
        ["Futur Simple"]),
    (12, 12, "Talking About Goals and Intentions",
        ["communication"],
        ["Express personal goals and long-term intentions",
         "Use future tenses alongside intention phrases naturally"],
        ["Discussing Plans"]),

    # ── Module 13: Daily Life, Habits & Responsibilities ───────────────────────
    (13, 13, "Reflexive Verbs",
        ["concept"],
        ["Identify and conjugate common reflexive verbs",
         "Use reflexive pronouns correctly in the present tense"],
        []),
    (13, 14, "Reflexive Verbs in Compound Tenses",
        ["concept"],
        ["Conjugate reflexive verbs in passé composé with être",
         "Apply past participle agreement rules for reflexive verbs"],
        ["Reflexive Verbs", "Passé Composé Review"]),
    (13, 15, "Adverbs of Frequency",
        ["closed_set"],
        ["Use toujours, souvent, parfois, rarement, jamais correctly",
         "Position frequency adverbs accurately in a sentence"],
        []),
    (13, 16, "Daily Routines",
        ["communication"],
        ["Describe a full daily routine using reflexive verbs and time markers",
         "Ask and respond to questions about someone else's routine"],
        ["Reflexive Verbs", "Adverbs of Frequency"]),
    (13, 17, "Il faut",
        ["concept"],
        ["Use il faut + infinitive to express necessity",
         "Distinguish il faut from other obligation expressions"],
        []),
    (13, 18, "Devoir",
        ["concept"],
        ["Conjugate devoir in present and past tenses",
         "Express personal obligation using devoir"],
        []),
    (13, 19, "Avoir besoin de",
        ["concept"],
        ["Use avoir besoin de + noun or infinitive to express need",
         "Distinguish need from obligation in context"],
        ["Devoir"]),
    (13, 20, "Responsibilities and Obligations",
        ["communication"],
        ["Discuss responsibilities using il faut, devoir, and avoir besoin de",
         "Respond naturally to questions about obligations"],
        ["Il faut", "Devoir", "Avoir besoin de"]),

    # ── Module 14: Expressing Cause and Consequence ────────────────────────────
    (14, 21, "Parce que",
        ["concept"],
        ["Use parce que to give reasons in complete sentences",
         "Answer pourquoi questions naturally"],
        []),
    (14, 22, "Car",
        ["concept"],
        ["Use car as a formal alternative to parce que",
         "Distinguish car from parce que in register and position"],
        ["Parce que"]),
    (14, 23, "Donc",
        ["concept"],
        ["Use donc to express logical consequence",
         "Position donc correctly in spoken and written French"],
        []),
    (14, 24, "Alors",
        ["concept"],
        ["Use alors to express consequence and transition",
         "Distinguish alors from donc in context"],
        ["Donc"]),
    (14, 25, "Explaining Reasons",
        ["communication"],
        ["Give clear reasons for decisions and actions using parce que and car",
         "Respond naturally to pourquoi in conversation"],
        ["Parce que", "Car"]),
    (14, 26, "Describing Consequences",
        ["communication"],
        ["Describe the result of events using donc and alors",
         "Link cause and effect in a natural, flowing way"],
        ["Donc", "Alors"]),
    (14, 27, "Building Natural Explanations",
        ["skill"],
        ["Combine cause and consequence connectors in multi-sentence explanations",
         "Express reasoning fluently in conversation"],
        ["Explaining Reasons", "Describing Consequences"]),

    # ── Module 15: Making Comparisons ──────────────────────────────────────────
    (15, 28, "Comparative Forms",
        ["concept"],
        ["Form comparatives using plus...que, moins...que, aussi...que",
         "Apply comparatives to adjectives, adverbs, and nouns"],
        []),
    (15, 29, "Superlative Forms",
        ["concept"],
        ["Form superlatives using le plus and le moins",
         "Use superlatives correctly with nouns and adjectives"],
        ["Comparative Forms"]),
    (15, 30, "Comparing People",
        ["communication"],
        ["Compare physical and personality traits between people",
         "Use comparatives and superlatives naturally in conversation"],
        ["Comparative Forms"]),
    (15, 31, "Comparing Places",
        ["communication"],
        ["Compare cities, countries, and locations using comparatives",
         "Express preferences about places with supporting comparisons"],
        ["Comparative Forms"]),
    (15, 32, "Comparing Things",
        ["communication"],
        ["Compare objects, products, and options using superlatives",
         "Make recommendations based on comparisons"],
        ["Superlative Forms"]),
    (15, 33, "Expressing Opinions Through Comparison",
        ["skill"],
        ["Give structured opinions using comparative and superlative forms",
         "Sustain a comparison-based discussion naturally"],
        ["Comparing People", "Comparing Places", "Comparing Things"]),

    # ── Module 16: Pronouns Expansion ──────────────────────────────────────────
    (16, 34, "Direct Object Pronouns (le, la, les)",
        ["concept"],
        ["Replace direct object nouns with le, la, les",
         "Position object pronouns correctly before the verb"],
        []),
    (16, 35, "Indirect Object Pronouns (lui, leur)",
        ["concept"],
        ["Replace indirect object nouns with lui and leur",
         "Distinguish direct from indirect object pronouns"],
        []),
    (16, 36, "Combining Object Pronouns",
        ["concept"],
        ["Use two object pronouns together in correct order",
         "Apply pronoun combinations in affirmative and negative sentences"],
        ["Direct Object Pronouns (le, la, les)", "Indirect Object Pronouns (lui, leur)"]),
    (16, 37, "Introduction to Y",
        ["concept"],
        ["Use y to replace location phrases and complements with à",
         "Position y correctly in various sentence structures"],
        []),
    (16, 38, "Introduction to EN",
        ["concept"],
        ["Use en to replace partitive and de + noun phrases",
         "Distinguish en from other object pronouns"],
        []),
    (16, 39, "Natural Pronoun Usage in Conversation",
        ["communication"],
        ["Apply all learned pronouns fluidly in spoken interaction",
         "Avoid repeating nouns unnecessarily by using pronouns correctly"],
        ["Combining Object Pronouns", "Introduction to Y", "Introduction to EN"]),

    # ── Module 17: Quantities, Adverbs & Precision ─────────────────────────────
    (17, 40, "Beaucoup de",
        ["closed_set"],
        ["Use beaucoup de correctly before nouns without articles",
         "Integrate beaucoup de naturally in sentences about quantity"],
        []),
    (17, 41, "Peu de",
        ["closed_set"],
        ["Use peu de to express small quantity",
         "Contrast peu de with un peu de in context"],
        []),
    (17, 42, "Trop de",
        ["closed_set"],
        ["Use trop de to express excess",
         "Use trop de in complaints and evaluations"],
        []),
    (17, 43, "Assez de",
        ["closed_set"],
        ["Use assez de to express sufficiency",
         "Combine assez de in positive and negative contexts"],
        []),
    (17, 44, "Plusieurs",
        ["closed_set"],
        ["Use plusieurs correctly as an indefinite determiner",
         "Distinguish plusieurs from other plural quantity words"],
        []),
    (17, 45, "Adverbs of Quantity",
        ["closed_set"],
        ["Use beaucoup, peu, trop, assez, plusieurs fluently in context",
         "Select the most natural quantity expression for a given situation"],
        ["Beaucoup de", "Peu de", "Trop de", "Assez de"]),
    (17, 46, "Adverbs of Manner",
        ["closed_set"],
        ["Form and use adverbs of manner ending in -ment",
         "Position manner adverbs correctly in sentences"],
        []),
    (17, 47, "Adding Detail and Nuance",
        ["skill"],
        ["Enrich descriptions and narratives using adverbs of quantity and manner",
         "Add precision and nuance to spoken and written French"],
        ["Adverbs of Quantity", "Adverbs of Manner"]),

    # ── Module 18: Building Longer Sentences ───────────────────────────────────
    (18, 48, "Relative Pronoun Qui",
        ["concept"],
        ["Use qui as a subject relative pronoun to describe nouns",
         "Construct relative clauses with qui correctly"],
        []),
    (18, 49, "Relative Pronoun Que",
        ["concept"],
        ["Use que as an object relative pronoun in complex sentences",
         "Apply past participle agreement with que in compound tenses"],
        []),
    (18, 50, "Relative Pronoun Où",
        ["concept"],
        ["Use où to refer to location and time in relative clauses",
         "Distinguish où as a relative pronoun from où as a question word"],
        []),
    (18, 51, "Combining Ideas into Longer Sentences",
        ["skill"],
        ["Link clauses using qui, que, and où in multi-clause sentences",
         "Build complex sentences without losing grammatical accuracy"],
        ["Relative Pronoun Qui", "Relative Pronoun Que", "Relative Pronoun Où"]),
    (18, 52, "Describing People and Things in Greater Detail",
        ["communication"],
        ["Use relative pronouns to describe people and objects in extended detail",
         "Avoid sentence fragmentation by connecting ideas fluently"],
        ["Combining Ideas into Longer Sentences"]),

    # ── Module 19: Time & Location Expressions ─────────────────────────────────
    (19, 53, "Depuis",
        ["concept"],
        ["Use depuis + present tense to describe ongoing actions",
         "Express how long something has been happening"],
        []),
    (19, 54, "Pendant",
        ["concept"],
        ["Use pendant to describe the duration of a completed action",
         "Distinguish pendant from depuis in context"],
        []),
    (19, 55, "Pour",
        ["concept"],
        ["Use pour to express intended duration in the future",
         "Apply pour correctly in travel and planning contexts"],
        []),
    (19, 56, "Jusqu'à",
        ["concept"],
        ["Use jusqu'à to express up to a point in time or place",
         "Combine jusqu'à with other time expressions naturally"],
        []),
    (19, 57, "Advanced Prepositions in Context",
        ["communication"],
        ["Use depuis, pendant, pour, and jusqu'à accurately in varied contexts",
         "Choose the correct preposition based on temporal meaning"],
        ["Depuis", "Pendant", "Pour", "Jusqu'à"]),
    (19, 58, "Talking About Duration and Time Relationships",
        ["communication"],
        ["Discuss time spans, schedules, and durations naturally in conversation",
         "Respond accurately to questions about when and how long"],
        ["Advanced Prepositions in Context"]),

    # ── Module 20: Expanded Negation ───────────────────────────────────────────
    (20, 59, "Ne...jamais",
        ["concept"],
        ["Form and use ne...jamais to express never",
         "Use ne...jamais correctly across tenses"],
        []),
    (20, 60, "Ne...rien",
        ["concept"],
        ["Form and use ne...rien to express nothing",
         "Use rien as subject and object in negation"],
        ["Ne...jamais"]),
    (20, 61, "Ne...personne",
        ["concept"],
        ["Form and use ne...personne to express no one",
         "Use personne as subject and object in negation"],
        ["Ne...jamais"]),
    (20, 62, "Ne...plus",
        ["concept"],
        ["Form and use ne...plus to express no longer or not anymore",
         "Contrast ne...plus with ne...pas naturally"],
        ["Ne...jamais"]),
    (20, 63, "Other Common Negative Structures",
        ["concept"],
        ["Use ne...que, ni...ni, and ne...aucun correctly",
         "Recognise and produce a range of negative forms in French"],
        ["Ne...rien", "Ne...personne", "Ne...plus"]),
    (20, 64, "Using Negation Naturally",
        ["communication"],
        ["Use all learned negative structures fluidly in conversation",
         "Choose the most natural negative form for a given context"],
        ["Other Common Negative Structures"]),

    # ── Module 21: Conditional Present & Polite Communication ──────────────────
    (21, 65, "Forming the Conditional Present",
        ["concept"],
        ["Form the conditional present for regular and irregular verbs",
         "Understand when the conditional is used in French"],
        []),
    (21, 66, "Je voudrais...",
        ["communication"],
        ["Use je voudrais to make polite requests and express desires",
         "Apply je voudrais in real-world service and social situations"],
        ["Forming the Conditional Present"]),
    (21, 67, "J'aimerais...",
        ["communication"],
        ["Use j'aimerais to express wishes and preferences politely",
         "Contrast j'aimerais with j'aime in context"],
        ["Forming the Conditional Present"]),
    (21, 68, "Je préférerais...",
        ["communication"],
        ["Use je préférerais to express preference in polite contexts",
         "Apply je préférerais in decision-making conversations"],
        ["Forming the Conditional Present"]),
    (21, 69, "Pourriez-vous... ?",
        ["communication"],
        ["Use pourriez-vous to make formal polite requests",
         "Respond appropriately to formal conditional questions"],
        ["Forming the Conditional Present"]),
    (21, 70, "Polite Requests",
        ["communication"],
        ["Make polite requests using the conditional in various situations",
         "Combine je voudrais and pourriez-vous fluidly in real-life scenarios"],
        ["Je voudrais...", "Pourriez-vous... ?"]),
    (21, 71, "Expressing Wishes",
        ["communication"],
        ["Express wishes and desires using j'aimerais and je voudrais",
         "Sustain a natural conversation about personal wishes"],
        ["Je voudrais...", "J'aimerais..."]),
    (21, 72, "Expressing Preferences",
        ["communication"],
        ["Articulate preferences using je préférerais and j'aimerais in context",
         "Compare options and state a preference naturally"],
        ["Je préférerais...", "J'aimerais..."]),
    (21, 73, "Simple Hypothetical Situations",
        ["communication"],
        ["Discuss simple hypothetical scenarios using the conditional",
         "Respond to basic si + imparfait constructions"],
        ["Forming the Conditional Present"]),

    # ── Module 22: Real-World Communication ────────────────────────────────────
    (22, 74, "Weather Conversations",
        ["communication"],
        ["Describe current and forecast weather using common expressions",
         "Ask and respond to weather-related small talk naturally"],
        []),
    (22, 75, "Shopping Situations",
        ["communication"],
        ["Navigate shopping interactions: items, prices, and sizes",
         "Use polite expressions and quantities in a shop context"],
        []),
    (22, 76, "Travel Situations",
        ["communication"],
        ["Handle travel scenarios: tickets, directions, and check-in",
         "Use transport vocabulary and polite requests fluidly"],
        []),
    (22, 77, "Making Appointments",
        ["communication"],
        ["Schedule, confirm, and cancel appointments in French",
         "Use time expressions and polite language in appointment contexts"],
        []),
    (22, 78, "Telephone Conversations",
        ["communication"],
        ["Open, sustain, and close a basic telephone conversation in French",
         "Use telephone-specific phrases and responses naturally"],
        []),
    (22, 79, "Asking for Help",
        ["communication"],
        ["Request assistance politely in various real-world contexts",
         "Respond appropriately when someone asks for help"],
        []),
    (22, 80, "Asking for Information",
        ["communication"],
        ["Ask clear questions to obtain information in public and service contexts",
         "Process and respond to informational exchanges naturally"],
        []),
    (22, 81, "Handling Everyday Problems",
        ["communication"],
        ["Report a problem or misunderstanding politely in French",
         "Resolve everyday issues using known vocabulary and strategies"],
        ["Asking for Help", "Asking for Information"]),

    # ── Module 23: Communication Mastery ───────────────────────────────────────
    (23, 82, "Giving Opinions",
        ["communication"],
        ["Express opinions using je pense que, je crois que, and à mon avis",
         "Support opinions with brief reasons"],
        []),
    (23, 83, "Agreeing and Disagreeing",
        ["communication"],
        ["Agree and disagree politely using standard expressions",
         "Maintain a respectful exchange of views in conversation"],
        ["Giving Opinions"]),
    (23, 84, "Making Comparisons in Discussion",
        ["communication"],
        ["Use comparative and superlative forms to support arguments and opinions",
         "Compare options and people fluently in open conversation"],
        ["Comparative Forms", "Giving Opinions"]),
    (23, 85, "Describing Experiences",
        ["communication"],
        ["Narrate personal experiences in detail using past tenses",
         "Engage a listener with vivid, connected descriptions"],
        ["Talking About Past Experiences"]),
    (23, 86, "Narrating Events",
        ["skill"],
        ["Tell a structured account of events with clear sequencing",
         "Combine multiple past tenses and time expressions fluidly"],
        ["Describing Experiences", "Storytelling in the Past"]),
    (23, 87, "Expressing Preferences",   # builds on Module 21's Expressing Preferences
        ["communication"],
        ["State and justify preferences in extended conversation",
         "Compare options and explain reasoning behind preferences"],
        ["Expressing Preferences"]),
    (23, 88, "Explaining Decisions",
        ["communication"],
        ["Justify decisions using cause-and-effect structures and preference expressions",
         "Communicate reasoning clearly and naturally"],
        ["Giving Opinions", "Building Natural Explanations"]),
    (23, 89, "Sustaining a Multi-Minute Conversation",
        ["skill"],
        ["Maintain a conversation for several minutes on a familiar topic",
         "Use repairs, fillers, and turn-taking strategies naturally"],
        ["Agreeing and Disagreeing", "Describing Experiences", "Giving Opinions"]),

    # ── Module 24: Writing & Interaction ───────────────────────────────────────
    (24, 90, "Writing Longer Messages",
        ["skill"],
        ["Write multi-paragraph informal messages in French",
         "Use connectors and cohesive devices to link ideas"],
        []),
    (24, 91, "Writing Informal Emails",
        ["skill"],
        ["Structure and write an informal email with appropriate register",
         "Use greeting, body, and sign-off conventions for informal French email"],
        ["Writing Longer Messages"]),
    (24, 92, "Writing Short Narratives",
        ["skill"],
        ["Write a coherent short story or account using past tenses",
         "Organise a narrative with a clear beginning, middle, and end"],
        ["Writing Longer Messages", "Storytelling in the Past"]),
    (24, 93, "Responding to Invitations",
        ["communication"],
        ["Accept or decline invitations appropriately in written French",
         "Express enthusiasm, regret, and alternative suggestions politely"],
        ["Writing Informal Emails"]),
    (24, 94, "Describing Personal Experiences in Writing",
        ["skill"],
        ["Write a detailed personal account using multiple tenses and rich vocabulary",
         "Combine description, narrative, and reflection in a written text"],
        ["Writing Short Narratives", "Talking About Past Experiences"]),
    (24, 95, "Combining Multiple Grammar Concepts in Context",
        ["skill"],
        ["Produce a written text integrating pronouns, negation, comparatives, and tense variety",
         "Demonstrate A2-level grammatical range in a single coherent piece of writing"],
        ["Writing Short Narratives", "Natural Pronoun Usage in Conversation", "Using Negation Naturally"]),
]


# ─── French B1 curriculum ─────────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_FRENCH_B1_MODULES: list[tuple[int, str, str, int]] = [
    (25, "Conditional Mastery & Hypothetical Speech", "Express politeness, possibility, and hypothetical reasoning using the conditional and si clauses",  6),
    (26, "Subjunctive & Subjectivity",                "Express feelings, doubt, and subjective meaning using the present subjunctive",                     7),
    (27, "Advanced Sentence Expansion",               "Build complex connected sentences using dont, lequel, and sentence embedding strategies",            5),
    (28, "Pronouns & Natural Speech Flow",            "Speak naturally without repetition using double pronouns, Y, EN, and pronoun chaining",             5),
    (29, "Reported Speech & Information Transfer",    "Transmit information accurately in conversation using direct and indirect speech",                   5),
    (30, "Time Logic & Narrative Control",            "Tell structured multi-time narratives using plus-que-parfait, futur antérieur, and sequencing",     5),
    (31, "Discourse Flow & Connectors",               "Speak fluently with natural idea transitions using logical connectors and the gérondif",            5),
    (32, "Argumentation & Opinion Building",          "Hold structured debates and discussions expressing and defending viewpoints clearly",               5),
    (33, "Real-World Society Topics",                 "Discuss abstract real-world topics across education, work, technology, and society",                7),
    (34, "Writing Mastery",                           "Produce structured written communication from paragraphs to formal and informal texts",             6),
    (35, "Conversation Mastery",                      "Sustain natural multi-turn conversations using suggestions, negotiation, and clarification",        6),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
# prereq_topics are resolved to node IDs during seeding (two-pass).
# Pass 2 queries ALL French nodes so cross-level A2 prereqs resolve correctly.
_FRENCH_B1_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 25: Conditional Mastery & Hypothetical Speech ──────────────────
    (25, 1,  "Conditional Present (core formation)",
        ["grammar"],
        ["Form the conditional present for all regular and key irregular verbs",
         "Express politeness, possibility, and hypothetical meaning using the conditional"],
        ["Forming the Conditional Present"]),
    (25, 2,  "Polite Requests (Je voudrais…, Pourriez-vous…)",
        ["communication"],
        ["Use je voudrais, j'aimerais, and pourriez-vous to make polite requests",
         "Navigate real-world service and social situations with appropriate register"],
        ["Conditional Present (core formation)"]),
    (25, 3,  "Advice & Suggestions",
        ["communication"],
        ["Give advice using vous devriez, tu devrais, and il vaudrait mieux",
         "Offer and respond to suggestions naturally in conversation"],
        ["Conditional Present (core formation)"]),
    (25, 4,  "Hypothetical Situations",
        ["communication"],
        ["Discuss hypothetical scenarios using the conditional",
         "Speculate about alternative outcomes and imagined situations"],
        ["Conditional Present (core formation)", "Simple Hypothetical Situations"]),
    (25, 5,  "Si Clauses (Present + Future)",
        ["grammar"],
        ["Form si + present + future clauses for real conditions",
         "Distinguish real conditions from hypothetical ones"],
        ["Conditional Present (core formation)"]),
    (25, 6,  "Si Clauses (Imperfect + Conditional)",
        ["grammar"],
        ["Form si + imparfait + conditional clauses for unreal conditions",
         "Use hypothetical si clauses naturally in spoken and written French"],
        ["Si Clauses (Present + Future)", "Conditional Present (core formation)"]),

    # ── Module 26: Subjunctive & Subjectivity ─────────────────────────────────
    (26, 7,  "Introduction to Subjunctive",
        ["concept"],
        ["Understand when the subjunctive mood is required in French",
         "Identify the subjunctive in written and spoken texts"],
        []),
    (26, 8,  "Formation of Present Subjunctive",
        ["grammar"],
        ["Form the present subjunctive for regular and common irregular verbs",
         "Apply subjunctive formation rules consistently across verb groups"],
        ["Introduction to Subjunctive"]),
    (26, 9,  "Emotion & Subjective Expression",
        ["communication"],
        ["Use the subjunctive after verbs of emotion (être content que, regretter que, avoir peur que)",
         "Express feelings and reactions about others' actions in French"],
        ["Formation of Present Subjunctive"]),
    (26, 10, "Desire & Preference",
        ["communication"],
        ["Use vouloir que, souhaiter que, and préférer que + subjunctive",
         "Express what you want or prefer others to do"],
        ["Formation of Present Subjunctive"]),
    (26, 11, "Necessity & Obligation",
        ["communication"],
        ["Use il faut que and il est nécessaire que + subjunctive",
         "Express obligation and necessity about third parties"],
        ["Formation of Present Subjunctive"]),
    (26, 12, "Doubt & Uncertainty",
        ["communication"],
        ["Use douter que, ne pas croire que, and ne pas penser que + subjunctive",
         "Express doubt and scepticism using the subjunctive mood"],
        ["Formation of Present Subjunctive"]),
    (26, 13, "Indicative vs Subjunctive Contrast",
        ["concept"],
        ["Choose between indicative and subjunctive based on meaning and trigger",
         "Avoid common errors when switching between moods"],
        ["Formation of Present Subjunctive", "Emotion & Subjective Expression"]),

    # ── Module 27: Advanced Sentence Expansion ────────────────────────────────
    (27, 14, "Qui / Que / Où Review",
        ["concept"],
        ["Reinforce accurate use of qui, que, and où as relative pronouns",
         "Build multi-clause sentences with confidence using the core relative pronouns"],
        ["Relative Pronoun Qui", "Relative Pronoun Que", "Relative Pronoun Où"]),
    (27, 15, "Dont",
        ["grammar"],
        ["Use dont to replace de + noun in relative clauses",
         "Apply dont with verbs and expressions that take de (parler de, avoir besoin de)"],
        []),
    (27, 16, "Lequel / Laquelle / Lesquels",
        ["grammar"],
        ["Use lequel, laquelle, lesquels, lesquelles as relative pronouns after prepositions",
         "Choose the correct form of lequel to agree in gender and number"],
        []),
    (27, 17, "Sentence Embedding Strategies",
        ["skill"],
        ["Combine multiple relative clauses to add depth and detail to sentences",
         "Avoid grammatical errors when embedding clauses within clauses"],
        ["Dont", "Lequel / Laquelle / Lesquels", "Qui / Que / Où Review"]),
    (27, 18, "Natural Sentence Merging",
        ["skill"],
        ["Merge short sentences into complex ones using all learned relative pronouns",
         "Produce connected, natural-sounding French at B1 complexity level"],
        ["Sentence Embedding Strategies"]),

    # ── Module 28: Pronouns & Natural Speech Flow ─────────────────────────────
    (28, 19, "Object Pronouns in Context",
        ["concept"],
        ["Revise and extend use of direct and indirect object pronouns in varied contexts",
         "Correctly position object pronouns in affirmative, negative, and imperative sentences"],
        ["Natural Pronoun Usage in Conversation"]),
    (28, 20, "Double Pronouns",
        ["grammar"],
        ["Use two object pronouns together in the correct order (me le, lui en, etc.)",
         "Apply double pronoun rules in both affirmative and negative sentences"],
        ["Object Pronouns in Context"]),
    (28, 21, "Pronoun Placement in Compound Tenses",
        ["grammar"],
        ["Position object pronouns correctly in passé composé and other compound tenses",
         "Avoid placement errors with double pronouns in compound verb structures"],
        ["Double Pronouns"]),
    (28, 22, "Y and EN in Natural Speech",
        ["communication"],
        ["Use y and en fluidly to avoid repetition in conversation",
         "Distinguish when y and en are required and position them accurately"],
        ["Introduction to Y", "Introduction to EN"]),
    (28, 23, "Fluid Pronoun Chaining",
        ["skill"],
        ["Chain multiple pronoun types across complex sentences without hesitation",
         "Speak naturally without noun repetition by selecting and sequencing pronouns correctly"],
        ["Double Pronouns", "Y and EN in Natural Speech"]),

    # ── Module 29: Reported Speech & Information Transfer ─────────────────────
    (29, 24, "Direct vs Indirect Speech",
        ["concept"],
        ["Identify the difference between direct and indirect speech in French",
         "Understand the structural changes when converting direct to indirect speech"],
        []),
    (29, 25, "Reporting Statements",
        ["grammar"],
        ["Convert direct statements to indirect using dire que and affirmer que",
         "Apply tense backshift rules when reporting past statements"],
        ["Direct vs Indirect Speech"]),
    (29, 26, "Reporting Questions",
        ["grammar"],
        ["Report yes/no questions using si and information questions using interrogative words",
         "Avoid common word-order errors in reported questions"],
        ["Direct vs Indirect Speech"]),
    (29, 27, "Tense Shifts in Narration",
        ["grammar"],
        ["Apply systematic tense backshift when reporting speech in the past",
         "Recognise and produce natural tense shifts in narration"],
        ["Reporting Statements", "Reporting Questions"]),
    (29, 28, "Real-World Retelling",
        ["skill"],
        ["Retell conversations, messages, and news using indirect speech fluently",
         "Transfer information accurately and naturally between interlocutors"],
        ["Tense Shifts in Narration"]),

    # ── Module 30: Time Logic & Narrative Control ─────────────────────────────
    (30, 29, "Plus-que-parfait Mastery",
        ["grammar"],
        ["Form and use the plus-que-parfait for all verb groups with full accuracy",
         "Express prior past events clearly in relation to other past actions"],
        ["Plus-que-parfait (Introduction)"]),
    (30, 30, "Futur Antérieur",
        ["grammar"],
        ["Form the futur antérieur using future of avoir/être + past participle",
         "Express future actions that will be completed before another future event"],
        ["Futur Simple"]),
    (30, 31, "Sequencing Events",
        ["skill"],
        ["Use temporal connectors (avant que, après avoir, dès que, une fois que) to sequence events",
         "Build logically ordered narratives with clear time relationships"],
        ["Plus-que-parfait Mastery"]),
    (30, 32, "Past Narrative Control",
        ["skill"],
        ["Tell a complex past narrative using passé composé, imparfait, and plus-que-parfait together",
         "Control narrative perspective and pace through tense choice"],
        ["Plus-que-parfait Mastery", "Sequencing Events"]),
    (30, 33, "Temporal Reasoning in Storytelling",
        ["skill"],
        ["Integrate all learned tenses including futur antérieur into coherent storytelling",
         "Reason about time relationships between events in extended spoken narratives"],
        ["Past Narrative Control", "Futur Antérieur"]),

    # ── Module 31: Discourse Flow & Connectors ────────────────────────────────
    (31, 34, "Logical Connectors",
        ["concept"],
        ["Use cependant, pourtant, néanmoins, and en revanche to express contrast",
         "Distinguish each connector by nuance and register"],
        []),
    (31, 35, "Cause & Consequence Structures",
        ["grammar"],
        ["Use puisque, étant donné que, c'est pourquoi, and par conséquent to link cause and result",
         "Build multi-clause arguments using cause-effect connectors"],
        ["Logical Connectors"]),
    (31, 36, "Argument Flow Markers",
        ["concept"],
        ["Use d'abord, ensuite, de plus, enfin, and en conclusion to structure arguments",
         "Guide the listener or reader through a structured line of reasoning"],
        ["Logical Connectors"]),
    (31, 37, "Sentence Linking in Real-Time Speech",
        ["skill"],
        ["Deploy connectors fluently in spontaneous spoken French without pausing",
         "Move smoothly between ideas using a range of linking expressions"],
        ["Cause & Consequence Structures", "Argument Flow Markers"]),
    (31, 38, "Gérondif (en + participe présent)",
        ["grammar"],
        ["Form the gérondif by combining en + present participle",
         "Use the gérondif to express simultaneous actions, manner, and condition"],
        []),

    # ── Module 32: Argumentation & Opinion Building ───────────────────────────
    (32, 39, "Expressing Opinions",
        ["communication"],
        ["Express nuanced opinions using selon moi, il me semble que, and j'estime que",
         "Go beyond basic opinion phrases to sound more sophisticated in B1 discussion"],
        ["Giving Opinions"]),
    (32, 40, "Agreeing and Disagreeing",
        ["communication"],
        ["Agree and disagree with precision using je suis (tout à fait) d'accord, certes mais, and je ne partage pas",
         "Maintain a respectful but assertive position in debate"],
        ["Expressing Opinions"]),
    (32, 41, "Justifying Arguments",
        ["skill"],
        ["Support a position with reasons, examples, and consequences",
         "Use justification language (car, en effet, à titre d'exemple) naturally"],
        ["Expressing Opinions"]),
    (32, 42, "Pros and Cons Discussions",
        ["communication"],
        ["Present both sides of an issue using d'un côté… de l'autre and pour/contre structures",
         "Weigh up advantages and disadvantages in structured spoken and written form"],
        ["Justifying Arguments"]),
    (32, 43, "Defending Viewpoints",
        ["skill"],
        ["Maintain and defend a position under challenge using reformulation and emphasis",
         "Respond to counterarguments confidently while staying on topic"],
        ["Pros and Cons Discussions", "Justifying Arguments"]),

    # ── Module 33: Real-World Society Topics ─────────────────────────────────
    (33, 44, "Education",
        ["communication"],
        ["Discuss the education system, learning experiences, and future academic plans",
         "Use relevant vocabulary and opinion structures in education-themed conversation"],
        []),
    (33, 45, "Work",
        ["communication"],
        ["Talk about jobs, work environments, career aspirations, and workplace issues",
         "Use work-related vocabulary and express opinions about professional life"],
        []),
    (33, 46, "Technology",
        ["communication"],
        ["Discuss the impact of technology, social media, and digital life on society",
         "Express opinions, concerns, and enthusiasm about technological change"],
        []),
    (33, 47, "Travel",
        ["communication"],
        ["Describe travel experiences, compare destinations, and discuss tourism",
         "Use travel vocabulary and narrative structures in extended conversation"],
        []),
    (33, 48, "Media",
        ["communication"],
        ["Discuss news, journalism, social media, and the role of media in society",
         "Express views on media consumption and its effects using B1 structures"],
        []),
    (33, 49, "Environment",
        ["communication"],
        ["Discuss environmental issues, sustainability, and personal responsibility",
         "Argue for or against environmental actions using appropriate vocabulary"],
        []),
    (33, 50, "Social Issues",
        ["communication"],
        ["Discuss social topics such as inequality, immigration, and community life",
         "Present and justify opinions on social issues with nuance and respect"],
        ["Expressing Opinions", "Justifying Arguments"]),

    # ── Module 34: Writing Mastery ────────────────────────────────────────────
    (34, 51, "Structured Paragraphs",
        ["writing"],
        ["Write well-organised paragraphs with a clear topic sentence, development, and conclusion",
         "Use cohesive devices to ensure logical flow within and between paragraphs"],
        []),
    (34, 52, "Opinion Essays",
        ["writing"],
        ["Write a structured opinion essay presenting and defending a clear argument",
         "Use introduction, body paragraphs, and conclusion effectively in French"],
        ["Structured Paragraphs", "Justifying Arguments"]),
    (34, 53, "Formal Emails",
        ["writing"],
        ["Write formal emails using appropriate register, salutations, and sign-offs",
         "Structure professional requests, complaints, and inquiries in French"],
        ["Structured Paragraphs"]),
    (34, 54, "Informal Emails",
        ["writing"],
        ["Write friendly emails and messages with natural informal register",
         "Use informal expressions, contractions, and conversational French in writing"],
        ["Structured Paragraphs"]),
    (34, 55, "Narrative Writing",
        ["writing"],
        ["Write a coherent narrative with vivid description, sequenced events, and tense control",
         "Combine past tenses effectively to tell a compelling story in writing"],
        ["Structured Paragraphs", "Past Narrative Control"]),
    (34, 56, "Extended Writing Tasks",
        ["writing"],
        ["Produce longer, multi-paragraph written texts combining multiple B1 grammar and vocabulary skills",
         "Demonstrate range and accuracy in extended written French"],
        ["Opinion Essays", "Narrative Writing"]),

    # ── Module 35: Conversation Mastery ──────────────────────────────────────
    (35, 57, "Making Suggestions",
        ["communication"],
        ["Suggest plans, activities, and solutions using si on + imparfait, pourquoi ne pas, and on pourrait",
         "Respond to and build on suggestions naturally in conversation"],
        []),
    (35, 58, "Negotiation Language",
        ["communication"],
        ["Use negotiation phrases to reach agreement and compromise in French",
         "Express flexibility and resistance politely in decision-making conversations"],
        ["Making Suggestions"]),
    (35, 59, "Problem Solving",
        ["communication"],
        ["Identify a problem, propose solutions, and evaluate options in French",
         "Use problem-solution discourse structure in collaborative spoken tasks"],
        ["Making Suggestions"]),
    (35, 60, "Clarification Strategies",
        ["communication"],
        ["Ask for clarification using pardon, vous voulez dire, and c'est-à-dire",
         "Rephrase and confirm meaning to avoid misunderstanding in conversation"],
        []),
    (35, 61, "Extended Conversations",
        ["skill"],
        ["Sustain a multi-minute conversation on a B1 topic with turn-taking and recovery strategies",
         "Maintain engagement and coherence across an extended spoken exchange"],
        ["Negotiation Language", "Problem Solving", "Clarification Strategies"]),
    (35, 62, "Managing Misunderstandings",
        ["communication"],
        ["Recognise and resolve misunderstandings using reformulation and confirmation checks",
         "Handle communication breakdowns gracefully and continue a conversation"],
        ["Clarification Strategies"]),
]


# ─── French B2 curriculum ─────────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_FRENCH_B2_MODULES: list[tuple[int, str, str, int]] = [
    (36, "Registers, Style & Natural Speech",         "Master formal and informal registers, idiomatic language, and natural spoken contractions",           7),
    (37, "Hypothesis & Conditional Systems",          "Express real and unreal conditions, mixed conditionals, and probability with precision",              6),
    (38, "Subjunctive Mastery System",                "Use the subjunctive for emotion, obligation, concession, and purpose with full control",              7),
    (39, "Passive Voice & Stylistic Control",         "Form passive structures across tenses and make informed stylistic choices between active and passive", 6),
    (40, "Advanced Relative Structures",              "Use auquel, duquel, and stacked relative clauses to express complex ideas naturally",                  6),
    (41, "Pronoun Mastery & Fluency Compression",     "Use pronouns at full B2 fluency including imperatives, chaining, and fast-speech compression",        6),
    (42, "Discourse Markers & Logical Flow",          "Link ideas in speech and writing using contrast, consequence, and reinforcement markers",              6),
    (43, "Argumentation & Critical Thinking",         "Build, defend, and counter arguments with critical reasoning and structured writing",                  7),
    (44, "Conversation Repair & Interaction Control", "Repair dialogue, interrupt politely, and maintain conversation flow under pressure",                   6),
    (45, "Real-World Writing Systems",                "Produce formal emails, letters, summaries, and reports with precise tone control",                     7),
    (46, "Listening & Interpretation Skills",         "Interpret fast native speech by extracting gist, opinion, attitude, and implied meaning",              6),
    (47, "Linguistic Nuance & Hedging",               "Express uncertainty, soften opinions, and communicate with precision and emotional moderation",        6),
    (48, "Society, Media & Abstract Topics",          "Discuss media, work, society, culture, and abstract ideas with B2 depth and vocabulary",               7),
    (49, "Real-Time Communication Pressure System",   "Develop instant-response fluency through drills, reaction tasks, and time-pressured speaking",         6),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
# prereq_topics are resolved to node IDs during seeding (two-pass).
# Pass 2 queries ALL French nodes so cross-level B1/A2 prereqs resolve correctly.
_FRENCH_B2_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 36: Registers, Style & Natural Speech ──────────────────────────
    (36, 1,  "Formal vs Informal Register",
        ["concept"],
        ["Distinguish formal and informal registers across spoken and written French",
         "Select the appropriate register for a given social context"],
        []),
    (36, 2,  "Politeness Strategies in Conversation",
        ["communication"],
        ["Apply politeness strategies beyond the conditional to soften requests and maintain rapport",
         "Adjust politeness level dynamically according to relationship and context"],
        ["Formal vs Informal Register"]),
    (36, 3,  "Idiomatic Expressions",
        ["vocabulary"],
        ["Use common idiomatic expressions naturally in conversation",
         "Recognise idioms in spoken and written French and infer meaning from context"],
        []),
    (36, 4,  "Slang vs Neutral Language",
        ["vocabulary"],
        ["Identify and use everyday slang in appropriate informal contexts",
         "Avoid register mismatches by distinguishing slang from neutral vocabulary"],
        ["Formal vs Informal Register"]),
    (36, 5,  "Tone Shifting in Speech",
        ["skill"],
        ["Shift between formal and casual tones smoothly within the same conversation",
         "Respond to tonal shifts from an interlocutor without losing fluency"],
        ["Formal vs Informal Register", "Politeness Strategies in Conversation"]),
    (36, 6,  "Natural Spoken Contractions",
        ["phonetics"],
        ["Recognise and produce common spoken contractions (j'sais pas, t'as, y'a, c'est)",
         "Sound natural in informal speech without over-applying formal pronunciation rules"],
        ["Slang vs Neutral Language"]),
    (36, 7,  "Emotional Tone in Speech",
        ["skill"],
        ["Convey a range of emotions through intonation, word choice, and pacing",
         "Interpret emotional subtext in native speech beyond literal meaning"],
        ["Tone Shifting in Speech"]),

    # ── Module 37: Hypothesis & Conditional Systems ───────────────────────────
    (37, 8,  "Real Conditions Review (si + présent → futur)",
        ["grammar"],
        ["Consolidate si + present tense + future tense for real conditions",
         "Apply real conditional structures accurately in complex multi-clause sentences"],
        ["Si Clauses (Present + Future)"]),
    (37, 9,  "Unreal Present Conditions (si + imparfait → conditionnel)",
        ["grammar"],
        ["Consolidate si + imparfait + conditional for currently unreal situations",
         "Use unreal present conditionals with irregular verbs at full accuracy"],
        ["Si Clauses (Imperfect + Conditional)"]),
    (37, 10, "Past Hypotheticals (si + plus-que-parfait → conditionnel passé)",
        ["grammar"],
        ["Form the conditional past and use it in third conditional constructions",
         "Express regret and counterfactual reasoning about past events"],
        ["Unreal Present Conditions (si + imparfait → conditionnel)", "Plus-que-parfait Mastery"]),
    (37, 11, "Mixed Conditionals",
        ["grammar"],
        ["Blend real and unreal conditions across time frames in a single sentence",
         "Recognise and produce mixed conditional forms in spontaneous speech"],
        ["Past Hypotheticals (si + plus-que-parfait → conditionnel passé)", "Unreal Present Conditions (si + imparfait → conditionnel)"]),
    (37, 12, "Hypothetical Regrets & Counterfactuals",
        ["communication"],
        ["Express regrets, wishes, and counterfactuals using the conditional past",
         "Sustain a conversation about hypothetical past outcomes naturally"],
        ["Mixed Conditionals", "Past Hypotheticals (si + plus-que-parfait → conditionnel passé)"]),
    (37, 13, "Probability vs Certainty Structures",
        ["communication"],
        ["Express varying degrees of likelihood using modal expressions and verb moods",
         "Distinguish certain, probable, and possible outcomes in speech and writing"],
        []),

    # ── Module 38: Subjunctive Mastery System ─────────────────────────────────
    (38, 14, "Present Subjunctive Review",
        ["grammar"],
        ["Recall and consolidate present subjunctive formation for all verb groups",
         "Use the subjunctive automatically after known triggers without hesitation"],
        ["Formation of Present Subjunctive"]),
    (38, 15, "Past Subjunctive Recognition",
        ["grammar"],
        ["Recognise the past subjunctive in literary and formal texts",
         "Understand its function as a stylistically elevated alternative to the conditional"],
        ["Present Subjunctive Review"]),
    (38, 16, "Emotion Triggers for Subjunctive",
        ["communication"],
        ["Use the subjunctive after a full range of emotion verbs (regretter, craindre, être ravi)",
         "Distinguish emotion-triggered subjunctive from indicative constructions naturally"],
        ["Present Subjunctive Review"]),
    (38, 17, "Necessity & Obligation in Subjunctive",
        ["communication"],
        ["Use il faut que, il est indispensable que, and il est essentiel que + subjunctive",
         "Go beyond basic necessity expressions to sound formal and precise"],
        ["Present Subjunctive Review"]),
    (38, 18, "Concession Clauses (bien que, quoique)",
        ["grammar"],
        ["Form and use bien que and quoique + subjunctive to express concession",
         "Distinguish these from coordinating concession markers (pourtant, malgré)"],
        ["Present Subjunctive Review"]),
    (38, 19, "Purpose Clauses (pour que, afin que)",
        ["grammar"],
        ["Use pour que and afin que + subjunctive to express purpose",
         "Choose correctly between pour + infinitive and pour que + subjunctive"],
        ["Present Subjunctive Review"]),
    (38, 20, "Impersonal Subjunctive Expressions",
        ["grammar"],
        ["Use a range of impersonal constructions triggering the subjunctive",
         "Produce formal and academic French by selecting impersonal subjunctive expressions"],
        ["Necessity & Obligation in Subjunctive", "Purpose Clauses (pour que, afin que)"]),

    # ── Module 39: Passive Voice & Stylistic Control ──────────────────────────
    (39, 21, "Present Passive Structures",
        ["grammar"],
        ["Form passive constructions in the present tense using être + past participle",
         "Apply agent introduction with par correctly in the passive"],
        []),
    (39, 22, "Past Passive Structures",
        ["grammar"],
        ["Form passive constructions in passé composé and imparfait",
         "Distinguish between the passive and adjectival use of être + past participle"],
        ["Present Passive Structures"]),
    (39, 23, "Multi-Tense Passive Transformations",
        ["grammar"],
        ["Produce passive forms across future, conditional, and subjunctive tenses",
         "Transform active sentences to passive across multiple tense and mood combinations"],
        ["Past Passive Structures"]),
    (39, 24, "Active to Passive Rewriting",
        ["skill"],
        ["Rewrite active sentences as passive with correct agreement and agent placement",
         "Identify when passive transformation changes the meaning or focus of a sentence"],
        ["Multi-Tense Passive Transformations"]),
    (39, 25, "Passive in Formal Writing",
        ["writing"],
        ["Use passive voice to create an impersonal, objective tone in formal and academic texts",
         "Recognise over-use of passive and revise for clarity"],
        ["Active to Passive Rewriting"]),
    (39, 26, "Stylistic Choice: Active vs Passive",
        ["skill"],
        ["Make informed decisions about when passive voice serves stylistic and communicative goals",
         "Edit texts to balance active and passive voice for maximum clarity and impact"],
        ["Passive in Formal Writing", "Active to Passive Rewriting"]),

    # ── Module 40: Advanced Relative Structures ───────────────────────────────
    (40, 27, "Complex Relative Clauses Review",
        ["concept"],
        ["Revise and consolidate qui, que, où, and dont in complex sentence contexts",
         "Produce multi-clause sentences with relative pronouns at B2 accuracy"],
        ["Natural Sentence Merging"]),
    (40, 28, "Lequel / Auquel / Duquel Forms",
        ["grammar"],
        ["Extend use of lequel to contracted forms auquel and duquel with prepositions",
         "Choose the correct form based on preposition and noun gender and number"],
        ["Lequel / Laquelle / Lesquels"]),
    (40, 29, "Embedded Relative Clauses",
        ["grammar"],
        ["Build sentences where one relative clause is embedded inside another",
         "Maintain grammatical accuracy and clarity in nested clause structures"],
        ["Complex Relative Clauses Review", "Lequel / Auquel / Duquel Forms"]),
    (40, 30, "Stacking Relative Clauses",
        ["skill"],
        ["Produce sentences that stack two or more relative clauses to express complex ideas",
         "Avoid ambiguity when stacking clauses through careful pronoun selection"],
        ["Embedded Relative Clauses"]),
    (40, 31, "Natural Omission in Spoken Relative Clauses",
        ["skill"],
        ["Recognise how relative clauses are reduced or omitted in natural spoken French",
         "Imitate native-level simplification strategies without losing meaning"],
        ["Stacking Relative Clauses"]),
    (40, 32, "Formal vs Spoken Relative Pronoun Usage",
        ["skill"],
        ["Adapt relative pronoun choices between formal written and casual spoken contexts",
         "Demonstrate register awareness in the selection and position of relative pronouns"],
        ["Natural Omission in Spoken Relative Clauses"]),

    # ── Module 41: Pronoun Mastery & Fluency Compression ─────────────────────
    (41, 33, "Y and EN Advanced Usage",
        ["grammar"],
        ["Extend y and en to complex and idiomatic constructions beyond B1",
         "Recognise and produce edge cases where y and en interact with other pronouns"],
        ["Fluid Pronoun Chaining"]),
    (41, 34, "Double Object Pronouns Review",
        ["grammar"],
        ["Consolidate double pronoun order across all tenses with full accuracy",
         "Produce double pronoun sequences fluently in affirmative and negative forms"],
        ["Pronoun Placement in Compound Tenses"]),
    (41, 35, "Pronoun Order Across All Tenses",
        ["grammar"],
        ["Master the complete pronoun order table including y and en across all tenses",
         "Avoid word-order errors in complex pronoun sequences involving multiple types"],
        ["Double Object Pronouns Review", "Y and EN Advanced Usage"]),
    (41, 36, "Pronouns in Imperatives",
        ["grammar"],
        ["Place object pronouns correctly in affirmative and negative imperatives",
         "Handle double pronouns in imperative forms including moi/toi stress forms"],
        ["Pronoun Order Across All Tenses"]),
    (41, 37, "Pronoun Chaining in Fast Speech",
        ["skill"],
        ["Produce pronoun sequences at natural conversational speed without hesitation",
         "Internalise pronoun order to the point of automatic application in real-time speech"],
        ["Pronouns in Imperatives"]),
    (41, 38, "Avoiding Repetition Through Pronouns",
        ["skill"],
        ["Replace nouns with the most precise pronoun to achieve natural, fluent French",
         "Edit spoken and written output to eliminate unnecessary noun repetition"],
        ["Pronoun Chaining in Fast Speech"]),

    # ── Module 42: Discourse Markers & Logical Flow ───────────────────────────
    (42, 39, "Contrast Markers (cependant, pourtant, en revanche)",
        ["concept"],
        ["Use cependant, pourtant, néanmoins, and en revanche at B2 register with full nuance",
         "Select the most precise contrast marker based on formality and implied meaning"],
        ["Sentence Linking in Real-Time Speech"]),
    (42, 40, "Consequence Markers (donc, par conséquent, ainsi)",
        ["concept"],
        ["Use donc, par conséquent, ainsi, and c'est ainsi que to express logical consequence",
         "Distinguish register differences between consequence markers in speech and writing"],
        ["Sentence Linking in Real-Time Speech"]),
    (42, 41, "Reinforcement Markers (d'ailleurs, en effet, notamment)",
        ["concept"],
        ["Use d'ailleurs, en effet, and notamment to add evidence and reinforce claims",
         "Position reinforcement markers accurately in spoken and written argument"],
        ["Contrast Markers (cependant, pourtant, en revanche)"]),
    (42, 42, "Structuring Arguments Orally",
        ["skill"],
        ["Organise a spoken argument using a range of discourse markers from introduction to conclusion",
         "Maintain logical flow and signpost transitions clearly in real-time speech"],
        ["Contrast Markers (cependant, pourtant, en revanche)", "Consequence Markers (donc, par conséquent, ainsi)"]),
    (42, 43, "Writing Cohesion Techniques",
        ["writing"],
        ["Use discourse markers and cohesive devices to ensure logical paragraph progression",
         "Avoid repetition and choppy structure by deploying linking language precisely"],
        ["Structuring Arguments Orally"]),
    (42, 44, "Linking Spoken Ideas Naturally",
        ["skill"],
        ["Deploy a full range of discourse markers spontaneously in fast conversational French",
         "Move between ideas without long pauses using markers as scaffolding"],
        ["Structuring Arguments Orally", "Reinforcement Markers (d'ailleurs, en effet, notamment)"]),

    # ── Module 43: Argumentation & Critical Thinking ──────────────────────────
    (43, 45, "Strong vs Soft Opinion Expression",
        ["communication"],
        ["Use a spectrum of opinion phrases from tentative (il me semble) to assertive (je suis convaincu)",
         "Calibrate opinion strength to context and audience for maximum rhetorical effect"],
        ["Defending Viewpoints"]),
    (43, 46, "Strategic Agreement & Disagreement",
        ["communication"],
        ["Agree and disagree with strategic precision without sounding blunt or evasive",
         "Use concession-then-refutation structures (certes… mais, il est vrai que… cependant)"],
        ["Strong vs Soft Opinion Expression"]),
    (43, 47, "Defending Arguments",
        ["skill"],
        ["Sustain and reinforce a position when challenged using elaboration and emphasis",
         "Avoid conceding too quickly by using restatement and clarification strategies"],
        ["Strong vs Soft Opinion Expression"]),
    (43, 48, "Constructing Counterarguments",
        ["skill"],
        ["Build counterarguments by identifying weaknesses in opposing claims",
         "Use concession structures to acknowledge the opposing view before refuting it"],
        ["Defending Arguments"]),
    (43, 49, "Critical Evaluation of Ideas",
        ["skill"],
        ["Evaluate the strength, relevance, and validity of arguments in French",
         "Identify bias, assumption, and logical gaps in spoken and written texts"],
        ["Constructing Counterarguments"]),
    (43, 50, "Expressing Abstract Reasoning",
        ["communication"],
        ["Articulate abstract concepts and theoretical ideas in clear, structured French",
         "Use appropriate vocabulary for academic and intellectual discourse"],
        ["Critical Evaluation of Ideas"]),
    (43, 51, "Structured Essay Writing",
        ["writing"],
        ["Write a structured argumentative essay with thesis, body, and conclusion in French",
         "Integrate discourse markers, opinion language, and evidence into a cohesive text"],
        ["Expressing Abstract Reasoning", "Extended Writing Tasks"]),

    # ── Module 44: Conversation Repair & Interaction Control ─────────────────
    (44, 52, "Asking for Clarification in Real Time",
        ["communication"],
        ["Request clarification on meaning, pronunciation, or reference using natural phrases",
         "Interrupt minimally and politely when clarification is needed during fast speech"],
        ["Managing Misunderstandings"]),
    (44, 53, "Rephrasing Misunderstood Ideas",
        ["communication"],
        ["Rephrase your own ideas when you sense a listener has not understood",
         "Choose simpler or more precise formulations without losing the original meaning"],
        ["Asking for Clarification in Real Time"]),
    (44, 54, "Interrupting Politely",
        ["communication"],
        ["Use softening phrases to interrupt without causing offence (excusez-moi, si je peux me permettre)",
         "Re-enter a conversation after an interruption with smooth turn-taking"],
        ["Asking for Clarification in Real Time"]),
    (44, 55, "Confirming Meaning",
        ["communication"],
        ["Check your own interpretation by paraphrasing back to the speaker",
         "Use confirmation techniques (vous voulez dire que…, si je comprends bien…) naturally"],
        ["Rephrasing Misunderstood Ideas"]),
    (44, 56, "Repairing Dialogue Breakdowns",
        ["skill"],
        ["Identify and recover from full communication breakdowns in conversation",
         "Use repair strategies (backtracking, topic restatement) to restore mutual understanding"],
        ["Confirming Meaning", "Interrupting Politely"]),
    (44, 57, "Maintaining Flow Under Confusion",
        ["skill"],
        ["Keep a conversation moving naturally even when partial understanding exists",
         "Deploy filler strategies and approximate responses to avoid prolonged silence"],
        ["Repairing Dialogue Breakdowns"]),

    # ── Module 45: Real-World Writing Systems ─────────────────────────────────
    (45, 58, "Formal Email Writing",
        ["writing"],
        ["Write professional emails with correct formal register, structure, and salutations",
         "Handle requests, complaints, and follow-ups in formal French email format"],
        ["Formal Emails"]),
    (45, 59, "Complaint Letters",
        ["writing"],
        ["Structure and write formal complaint letters with an assertive yet polite tone",
         "Use standard complaint language and logical sequencing to present a case clearly"],
        ["Formal Email Writing"]),
    (45, 60, "Informational Messages",
        ["writing"],
        ["Write clear, concise informational messages for professional and public contexts",
         "Prioritise key information and organise it for maximum reader clarity"],
        ["Formal Email Writing"]),
    (45, 61, "Article Summaries",
        ["writing"],
        ["Summarise a written article accurately and concisely in French",
         "Distinguish between the author's view and factual content in a summary"],
        ["Structured Paragraphs"]),
    (45, 62, "Structured Reports",
        ["writing"],
        ["Write a structured report with headings, introduction, findings, and conclusion",
         "Use impersonal and passive constructions appropriate to report register"],
        ["Article Summaries", "Structured Paragraphs"]),
    (45, 63, "Invitations & Responses",
        ["writing"],
        ["Write and respond to formal and informal invitations with appropriate tone and conventions",
         "Manage acceptance, refusal, and alternative suggestion in written French"],
        ["Informal Emails"]),
    (45, 64, "Tone Control in Writing",
        ["skill"],
        ["Adjust lexical and syntactic choices to shift tone from warm to neutral to formal",
         "Edit written texts to correct register mismatches and inconsistencies"],
        ["Formal Email Writing", "Invitations & Responses"]),

    # ── Module 46: Listening & Interpretation Skills ──────────────────────────
    (46, 65, "Understanding Fast Native Speech",
        ["listening"],
        ["Follow native-speed French conversations by predicting patterns and using context",
         "Identify key words through linking, elision, and reduction in rapid speech"],
        []),
    (46, 66, "Extracting Gist vs Detail",
        ["listening"],
        ["Listen for overall meaning (gist) without needing full word-by-word comprehension",
         "Switch between gist and detail listening modes depending on task requirements"],
        ["Understanding Fast Native Speech"]),
    (46, 67, "Identifying Opinion vs Fact",
        ["listening"],
        ["Distinguish factual statements from expressions of opinion in spoken French",
         "Recognise hedging language, assertion markers, and subjective vocabulary in speech"],
        ["Extracting Gist vs Detail"]),
    (46, 68, "Interpreting Implied Meaning",
        ["listening"],
        ["Infer what is not said explicitly by reading context, tone, and social cues",
         "Identify implication, irony, and understatement in native French speech"],
        ["Identifying Opinion vs Fact"]),
    (46, 69, "Understanding Attitude and Tone",
        ["listening"],
        ["Interpret a speaker's attitude (enthusiastic, sceptical, neutral) from prosody and word choice",
         "Use tone interpretation to guide appropriate responses in real-time conversation"],
        ["Interpreting Implied Meaning"]),
    (46, 70, "Handling Missing Information in Speech",
        ["listening"],
        ["Continue listening and comprehending when key words are missed",
         "Use redundancy, repetition, and inference to reconstruct incomplete input"],
        ["Understanding Fast Native Speech"]),

    # ── Module 47: Linguistic Nuance & Hedging ────────────────────────────────
    (47, 71, "Expressing Uncertainty",
        ["communication"],
        ["Use modal expressions (il se pourrait que, ça m'étonnerait, je ne suis pas sûr que) to convey uncertainty",
         "Select the appropriate level of certainty marker for spoken and written contexts"],
        []),
    (47, 72, "Softening Opinions",
        ["communication"],
        ["Soften opinions using hedges (à mon sens, il me semble, disons que) and mitigation strategies",
         "Reduce the force of assertions to maintain politeness and openness in debate"],
        ["Expressing Uncertainty"]),
    (47, 73, "Degrees of Certainty",
        ["communication"],
        ["Express a spectrum from strong certainty to vague possibility using precise vocabulary",
         "Match certainty expression to the evidence available and the social stakes of the claim"],
        ["Expressing Uncertainty"]),
    (47, 74, "Politeness in Disagreement",
        ["communication"],
        ["Disagree firmly without rudeness using concession-then-contrast structures",
         "Choose politeness-preserving forms for sensitive or high-stakes disagreements"],
        ["Strategic Agreement & Disagreement"]),
    (47, 75, "Emotional Moderation in Speech",
        ["communication"],
        ["Regulate emotional expression in speech to maintain credibility and respect",
         "Use distancing language when discussing emotive topics in professional contexts"],
        ["Softening Opinions"]),
    (47, 76, "Indirect Expression Strategies",
        ["skill"],
        ["Communicate meaning indirectly through implication, understatement, and suggestion",
         "Deploy indirect strategies to navigate sensitive topics without direct confrontation"],
        ["Softening Opinions", "Degrees of Certainty"]),

    # ── Module 48: Society, Media & Abstract Topics ───────────────────────────
    (48, 77, "Media & News Vocabulary",
        ["vocabulary"],
        ["Use precise vocabulary for discussing news sources, journalism, and media bias",
         "Describe and evaluate different media formats and their societal role"],
        []),
    (48, 78, "Workplace Discussions",
        ["communication"],
        ["Discuss professional environments, workplace dynamics, and career development in French",
         "Use formal and semi-formal register appropriately in workplace-themed conversation"],
        ["Strong vs Soft Opinion Expression"]),
    (48, 79, "Education Systems",
        ["communication"],
        ["Compare educational structures, discuss learning experiences, and evaluate teaching methods",
         "Use abstract vocabulary to discuss the purpose and reform of education"],
        []),
    (48, 80, "Environment & Society",
        ["communication"],
        ["Discuss environmental challenges, policy responses, and individual responsibility at B2 depth",
         "Support environmental arguments using abstract reasoning and precise vocabulary"],
        ["Strong vs Soft Opinion Expression"]),
    (48, 81, "Culture & Trends",
        ["communication"],
        ["Discuss cultural shifts, social trends, and their implications in French society",
         "Use nuanced vocabulary to describe and evaluate cultural phenomena"],
        []),
    (48, 82, "Technology in Daily Life",
        ["communication"],
        ["Debate the role of technology in work, relationships, and society with B2 sophistication",
         "Use advanced vocabulary for digital culture, AI, and technological ethics"],
        []),
    (48, 83, "Discussing Abstract Ideas",
        ["skill"],
        ["Articulate philosophical, ethical, and conceptual ideas in clear spoken and written French",
         "Move beyond concrete examples to engage with abstract argumentation fluently"],
        ["Expressing Abstract Reasoning"]),

    # ── Module 49: Real-Time Communication Pressure System ───────────────────
    (49, 84, "Instant Response Drills",
        ["skill"],
        ["Produce immediate, grammatically sound responses to prompts without preparation time",
         "Build automaticity in accessing learned structures under cognitive pressure"],
        ["Maintaining Flow Under Confusion"]),
    (49, 85, "Spontaneous Opinion Formation",
        ["communication"],
        ["Form and express an opinion on an unfamiliar topic in real time",
         "Use scaffolding phrases to buy thinking time while sounding fluent"],
        ["Strong vs Soft Opinion Expression"]),
    (49, 86, "Dialogue Continuation",
        ["skill"],
        ["Continue an unfinished dialogue naturally by inferring context and taking the next turn",
         "Maintain coherence and register when picking up a conversation mid-stream"],
        ["Instant Response Drills"]),
    (49, 87, "Incomplete Input Completion",
        ["skill"],
        ["Respond meaningfully when input is partial, unclear, or heavily accented",
         "Use inference and context to fill gaps and keep the exchange going"],
        ["Dialogue Continuation"]),
    (49, 88, "Reaction-Based Speaking",
        ["skill"],
        ["React authentically to unexpected statements, questions, and provocations in French",
         "Deploy agreement, surprise, doubt, and humour reactions naturally without scripting"],
        ["Incomplete Input Completion", "Spontaneous Opinion Formation"]),
    (49, 89, "Fluency Under Time Pressure",
        ["skill"],
        ["Sustain fluent, accurate French when speaking quickly or under social pressure",
         "Integrate all B2 skills into fully spontaneous, pressure-tested production"],
        ["Reaction-Based Speaking"]),
]


# ─── Seed helpers ─────────────────────────────────────────────────────────────

def seed_languages(conn: sqlite3.Connection) -> None:
    """
    Insert the canonical language list.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = """
        INSERT OR IGNORE INTO languages (code, name, native_name)
        VALUES (?, ?, ?)
    """
    conn.executemany(sql, _LANGUAGES)
    print(f"[db] Languages seeded ({len(_LANGUAGES)} rows)")


def seed_hobbies(conn: sqlite3.Connection) -> None:
    """
    Insert the canonical hobby list.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT OR IGNORE INTO hobbies (name) VALUES (?)"
    conn.executemany(sql, [(h,) for h in _HOBBIES])
    print(f"[db] Hobbies seeded ({len(_HOBBIES)} rows)")


def seed_motivations(conn: sqlite3.Connection) -> None:
    """
    Insert the canonical motivation list.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT OR IGNORE INTO motivations (label) VALUES (?)"
    conn.executemany(sql, [(m,) for m in _MOTIVATIONS])
    print(f"[db] Motivations seeded ({len(_MOTIVATIONS)} rows)")


def seed_xp_levels(conn: sqlite3.Connection) -> None:
    """
    Insert XP level threshold bands.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT OR IGNORE INTO xp_levels (level_no, label, xp_required, xp_to_next) VALUES (?, ?, ?, ?)"
    conn.executemany(sql, _XP_LEVELS)
    print(f"[db] XP levels seeded ({len(_XP_LEVELS)} rows)")


def seed_achievements(conn: sqlite3.Connection) -> None:
    """
    Insert the canonical achievement catalog.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT OR IGNORE INTO achievements (name, description, xp_reward) VALUES (?, ?, ?)"
    conn.executemany(sql, _ACHIEVEMENTS)
    print(f"[db] Achievements seeded ({len(_ACHIEVEMENTS)} rows)")


def seed_french_curriculum(conn: sqlite3.Connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for French A1.
    Uses INSERT OR IGNORE — safe to re-run at any time.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'fr'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("French language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT OR IGNORE INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (?, 'CEFR', 'A1', ?, ?, ?, ?)
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _FRENCH_A1_MODULES],
    )

    # Build unit → module_id map (needed for nodes FK)
    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = ? AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Nodes ─────────────────────────────────────────────────────────────────
    rows = []
    for unit, lesson_order, topic, skill_focus, objectives in _FRENCH_A1_NODES:
        module_id = unit_to_module_id[unit]
        rows.append((
            lang_id,
            module_id,
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),           # prerequisites — empty for now
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT OR IGNORE INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (?, ?, 'CEFR', 'A1', ?, ?, ?, ?, ?)
        """,
        rows,
    )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = ? AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = ? AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] French A1 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_french_a2_curriculum(conn: sqlite3.Connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for French A2.
    Uses INSERT OR IGNORE for modules and nodes, then resolves prerequisites
    by topic name in a second pass. Safe to re-run.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'fr'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("French language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT OR IGNORE INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (?, 'CEFR', 'A2', ?, ?, ?, ?)
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _FRENCH_A2_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = ? AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ──────────────────────────
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _FRENCH_A2_NODES:
        conn.execute(
            """
            INSERT OR IGNORE INTO curriculum_nodes
                (language_id, module_id, framework, level, lesson_order, topic,
                 skill_focus, prerequisites, learning_objectives)
            VALUES (?, ?, 'CEFR', 'A2', ?, ?, ?, ?, ?)
            """,
            (
                lang_id,
                unit_to_module_id[unit],
                lesson_order,
                topic,
                json.dumps(skill_focus),
                json.dumps([]),
                json.dumps(objectives),
            ),
        )

    # ── Pass 2: resolve prerequisite topic names → node IDs ───────────────────
    # Build topic → node_id map; first occurrence (lowest lesson_order) wins.
    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = ? AND framework = 'CEFR' AND level = 'A2' ORDER BY lesson_order",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for row in node_rows:
        if row["topic"] not in topic_to_id:
            topic_to_id[row["topic"]] = row["id"]

    for unit, lesson_order, topic, _sf, _obj, prereq_topics in _FRENCH_A2_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if prereq_ids:
            conn.execute(
                "UPDATE curriculum_nodes SET prerequisites = ? WHERE language_id = ? AND framework = 'CEFR' AND level = 'A2' AND lesson_order = ?",
                (json.dumps(prereq_ids), lang_id, lesson_order),
            )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = ? AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = ? AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] French A2 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_french_b1_curriculum(conn: sqlite3.Connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for French B1.
    Pass-2 prerequisite resolution covers ALL French nodes (A1 + A2 + B1)
    so that B1 nodes can reference A2 topic names as prerequisites.
    Uses INSERT OR IGNORE — safe to re-run.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'fr'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("French language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT OR IGNORE INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (?, 'CEFR', 'B1', ?, ?, ?, ?)
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _FRENCH_B1_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = ? AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ──────────────────────────
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _FRENCH_B1_NODES:
        conn.execute(
            """
            INSERT OR IGNORE INTO curriculum_nodes
                (language_id, module_id, framework, level, lesson_order, topic,
                 skill_focus, prerequisites, learning_objectives)
            VALUES (?, ?, 'CEFR', 'B1', ?, ?, ?, ?, ?)
            """,
            (
                lang_id,
                unit_to_module_id[unit],
                lesson_order,
                topic,
                json.dumps(skill_focus),
                json.dumps([]),
                json.dumps(objectives),
            ),
        )

    # ── Pass 2: resolve prerequisite topic names → node IDs ───────────────────
    # Query ALL French nodes (A1 + A2 + B1) ordered by id so earlier-inserted
    # nodes (A1/A2) take priority when the same topic name appears in multiple levels.
    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = ? AND framework = 'CEFR' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for row in node_rows:
        if row["topic"] not in topic_to_id:
            topic_to_id[row["topic"]] = row["id"]

    for unit, lesson_order, topic, _sf, _obj, prereq_topics in _FRENCH_B1_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if prereq_ids:
            conn.execute(
                "UPDATE curriculum_nodes SET prerequisites = ? WHERE language_id = ? AND framework = 'CEFR' AND level = 'B1' AND lesson_order = ?",
                (json.dumps(prereq_ids), lang_id, lesson_order),
            )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = ? AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = ? AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] French B1 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_french_b2_curriculum(conn: sqlite3.Connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for French B2.
    Pass-2 prerequisite resolution covers ALL French nodes (A1 + A2 + B1 + B2)
    so that B2 nodes can reference B1 and earlier topic names as prerequisites.
    Uses INSERT OR IGNORE — safe to re-run.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'fr'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("French language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT OR IGNORE INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (?, 'CEFR', 'B2', ?, ?, ?, ?)
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _FRENCH_B2_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = ? AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ──────────────────────────
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _FRENCH_B2_NODES:
        conn.execute(
            """
            INSERT OR IGNORE INTO curriculum_nodes
                (language_id, module_id, framework, level, lesson_order, topic,
                 skill_focus, prerequisites, learning_objectives)
            VALUES (?, ?, 'CEFR', 'B2', ?, ?, ?, ?, ?)
            """,
            (
                lang_id,
                unit_to_module_id[unit],
                lesson_order,
                topic,
                json.dumps(skill_focus),
                json.dumps([]),
                json.dumps(objectives),
            ),
        )

    # ── Pass 2: resolve prerequisite topic names → node IDs ───────────────────
    # Query ALL French nodes (A1 + A2 + B1 + B2) ordered by id so earlier-inserted
    # nodes take priority when the same topic name appears in multiple levels.
    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = ? AND framework = 'CEFR' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for row in node_rows:
        if row["topic"] not in topic_to_id:
            topic_to_id[row["topic"]] = row["id"]

    for unit, lesson_order, topic, _sf, _obj, prereq_topics in _FRENCH_B2_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if prereq_ids:
            conn.execute(
                "UPDATE curriculum_nodes SET prerequisites = ? WHERE language_id = ? AND framework = 'CEFR' AND level = 'B2' AND lesson_order = ?",
                (json.dumps(prereq_ids), lang_id, lesson_order),
            )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = ? AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = ? AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] French B2 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── Initialization ───────────────────────────────────────────────────────────

def initialize_database() -> None:
    """
    Full first-run setup:

    1. Open connection to lingua_ai.db (creates file if absent)
    2. Create all tables + indexes, migrate any missing columns
    3. Seed reference data (languages, hobbies, motivations, xp_levels, achievements)
    4. Commit and close
    """
    print(f"[db] Initializing database at {DB_PATH}")
    conn = get_connection()
    try:
        create_tables(conn)
        seed_languages(conn)
        seed_hobbies(conn)
        seed_motivations(conn)
        seed_xp_levels(conn)
        seed_achievements(conn)
        seed_french_curriculum(conn)
        seed_french_a2_curriculum(conn)
        seed_french_b1_curriculum(conn)
        seed_french_b2_curriculum(conn)
        conn.commit()
        print("[db] Initialization complete.")
    except Exception as exc:
        conn.rollback()
        print(f"[db] Initialization failed: {exc}")
        raise
    finally:
        conn.close()


# ─── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    commands = {
        "init":  initialize_database,
        "drop":  drop_database,
        "reset": lambda: (drop_database(), initialize_database()),
    }

    cmd = sys.argv[1] if len(sys.argv) > 1 else "init"
    action = commands.get(cmd)

    if action is None:
        print(f"Unknown command '{cmd}'. Use: init | drop | reset")
        sys.exit(1)

    action()
