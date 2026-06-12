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
# import sqlite3
import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

from database.schema import create_tables, drop_tables

load_dotenv()

# ─── Configuration ────────────────────────────────────────────────────────────

# _DB_DIR  = os.path.dirname(os.path.abspath(__file__))
# DB_PATH  = os.path.join(_DB_DIR, "lingua_ai.db")

_DATABASE_URL = os.getenv("DATABASE_URL")


# ─── Seed data ────────────────────────────────────────────────────────────────

_LANGUAGES: list[tuple[str, str, str, str]] = [
    # (code, name, native_name, framework)
    ("en", "English",    "English",  "CEFR"),
    ("fr", "French",     "Français", "CEFR"),
    ("de", "German",     "Deutsch",  "CEFR"),
    ("zh", "Chinese",    "中文",      "HSK"),
    ("es", "Spanish",    "Español",  "CEFR"),
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

# def get_connection() -> sqlite3.Connection:
#     """
#     Open (or create) lingua_ai.db and return a connection.
#
#     - Row factory set to sqlite3.Row for dict-like access.
#     - Foreign key enforcement enabled on every connection.
#     """
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     conn.execute("PRAGMA foreign_keys = ON")
#     conn.execute("PRAGMA journal_mode = WAL")   # better concurrent read performance
#     return conn

class _Connection:
    """
    Wraps a psycopg2 connection to expose the sqlite3-compatible
    conn.execute() / conn.executemany() shorthand used throughout the codebase.
    DictCursor is used so rows support both row["key"] and row[0] access.
    """

    def __init__(self, conn: psycopg2.extensions.connection) -> None:
        self._conn = conn

    def execute(self, sql: str, params=None):
        cur = self._conn.cursor()
        cur.execute(sql, params or ())
        return cur

    def executemany(self, sql: str, seq_of_params) -> None:
        cur = self._conn.cursor()
        cur.executemany(sql, seq_of_params)

    def cursor(self):
        return self._conn.cursor()

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()


def get_connection() -> _Connection:
    conn = psycopg2.connect(_DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)
    return _Connection(conn)


# ─── Create / Drop ────────────────────────────────────────────────────────────

def create_database() -> None:
    """Create all tables and indexes. Idempotent."""
    conn = get_connection()
    try:
        create_tables(conn)
        print(f"[db] Tables and indexes created → {_DATABASE_URL}")
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
        print(f"[db] All tables dropped → {_DATABASE_URL}")
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
    (1, "Talking About the Past",                     "Master past tenses and use them naturally in stories and conversations",             6),
    (2, "Talking About the Future",                   "Express future plans, predictions, and intentions using correct tenses",             6),
    (3, "Daily Life, Habits & Responsibilities",      "Describe daily routines and express obligations with reflexive verbs and modals",    8),
    (4, "Expressing Cause and Consequence",           "Link ideas by explaining reasons and consequences using connectors",                 7),
    (5, "Making Comparisons",                         "Compare people, places, and things using comparative and superlative forms",         6),
    (6, "Pronouns Expansion",                         "Use direct and indirect object pronouns and expand into Y and EN",                  6),
    (7, "Quantities, Adverbs & Precision",            "Add precision using quantity expressions and adverbs of manner",                    8),
    (8, "Building Longer Sentences",                  "Use relative pronouns to connect and enrich sentences",                             5),
    (9, "Time & Location Expressions",                "Express duration, timing, and location with advanced prepositions",                 6),
    (10, "Expanded Negation",                          "Use a full range of negative structures naturally in conversation",                 6),
    (11, "Conditional Present & Polite Communication", "Form the conditional and use it for polite requests, wishes, and hypotheticals",    9),
    (12, "Real-World Communication",                   "Handle everyday situations including shopping, travel, and appointments",           8),
    (13, "Communication Mastery",                      "Engage in sustained conversations: opinions, narratives, and preferences",          8),
    (14, "Writing & Interaction",                      "Write informal messages, emails, and short narratives combining grammar concepts",  6),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
# prereq_topics are resolved to node IDs during seeding (two-pass).
_FRENCH_A2_NODES: list[tuple[int, int, str, list, list, list]] = [
    # ── Module 11: Talking About the Past ──────────────────────────────────────
    (1, 1,  "Passé Composé Review",
        ["concept"],
        ["Conjugate regular and common irregular verbs in passé composé",
         "Use avoir and être correctly as auxiliaries"],
        []),
    (1, 2,  "Imparfait",
        ["concept"],
        ["Form the imparfait for all verb groups",
         "Describe habitual actions and states in the past"],
        []),
    (1, 3,  "Passé Composé vs Imparfait",
        ["concept"],
        ["Distinguish when to use passé composé vs imparfait",
         "Narrate past events combining both tenses"],
        ["Passé Composé Review", "Imparfait"]),
    (1, 4,  "Plus-que-parfait (Introduction)",
        ["concept"],
        ["Form the plus-que-parfait using imperfect auxiliary + past participle",
         "Express an action that occurred before another past action"],
        ["Passé Composé Review"]),
    (1, 5,  "Talking About Past Experiences",
        ["communication"],
        ["Describe personal past experiences using passé composé and imparfait",
         "Ask and answer questions about past experiences"],
        ["Passé Composé vs Imparfait"]),
    (1, 6,  "Storytelling in the Past",
        ["skill"],
        ["Tell a coherent short story using multiple past tenses",
         "Use time expressions to sequence events naturally"],
        ["Talking About Past Experiences", "Plus-que-parfait (Introduction)"]),

    # ── Module 12: Talking About the Future ────────────────────────────────────
    (2, 7,  "Futur Proche Review",
        ["concept"],
        ["Form futur proche using aller + infinitive",
         "Use it for immediate or planned future events"],
        []),
    (2, 8,  "Futur Simple",
        ["concept"],
        ["Conjugate regular and irregular verbs in futur simple",
         "Express future facts, predictions, and intentions"],
        []),
    (2, 9,  "Futur Proche vs Futur Simple",
        ["concept"],
        ["Choose the appropriate future tense based on context",
         "Distinguish near-future plans from general future statements"],
        ["Futur Proche Review", "Futur Simple"]),
    (2, 10, "Discussing Plans",
        ["communication"],
        ["Talk about upcoming plans and arrangements",
         "Ask and answer questions about future plans"],
        ["Futur Proche vs Futur Simple"]),
    (2, 11, "Making Predictions",
        ["communication"],
        ["Make predictions about events using futur simple",
         "Express certainty and probability about the future"],
        ["Futur Simple"]),
    (2, 12, "Talking About Goals and Intentions",
        ["communication"],
        ["Express personal goals and long-term intentions",
         "Use future tenses alongside intention phrases naturally"],
        ["Discussing Plans"]),

    # ── Module 13: Daily Life, Habits & Responsibilities ───────────────────────
    (3, 13, "Reflexive Verbs",
        ["concept"],
        ["Identify and conjugate common reflexive verbs",
         "Use reflexive pronouns correctly in the present tense"],
        []),
    (3, 14, "Reflexive Verbs in Compound Tenses",
        ["concept"],
        ["Conjugate reflexive verbs in passé composé with être",
         "Apply past participle agreement rules for reflexive verbs"],
        ["Reflexive Verbs", "Passé Composé Review"]),
    (3, 15, "Adverbs of Frequency",
        ["closed_set"],
        ["Use toujours, souvent, parfois, rarement, jamais correctly",
         "Position frequency adverbs accurately in a sentence"],
        []),
    (3, 16, "Daily Routines",
        ["communication"],
        ["Describe a full daily routine using reflexive verbs and time markers",
         "Ask and respond to questions about someone else's routine"],
        ["Reflexive Verbs", "Adverbs of Frequency"]),
    (3, 17, "Il faut",
        ["concept"],
        ["Use il faut + infinitive to express necessity",
         "Distinguish il faut from other obligation expressions"],
        []),
    (3, 18, "Devoir",
        ["concept"],
        ["Conjugate devoir in present and past tenses",
         "Express personal obligation using devoir"],
        []),
    (3, 19, "Avoir besoin de",
        ["concept"],
        ["Use avoir besoin de + noun or infinitive to express need",
         "Distinguish need from obligation in context"],
        ["Devoir"]),
    (3, 20, "Responsibilities and Obligations",
        ["communication"],
        ["Discuss responsibilities using il faut, devoir, and avoir besoin de",
         "Respond naturally to questions about obligations"],
        ["Il faut", "Devoir", "Avoir besoin de"]),

    # ── Module 14: Expressing Cause and Consequence ────────────────────────────
    (4, 21, "Parce que",
        ["concept"],
        ["Use parce que to give reasons in complete sentences",
         "Answer pourquoi questions naturally"],
        []),
    (4, 22, "Car",
        ["concept"],
        ["Use car as a formal alternative to parce que",
         "Distinguish car from parce que in register and position"],
        ["Parce que"]),
    (4, 23, "Donc",
        ["concept"],
        ["Use donc to express logical consequence",
         "Position donc correctly in spoken and written French"],
        []),
    (4, 24, "Alors",
        ["concept"],
        ["Use alors to express consequence and transition",
         "Distinguish alors from donc in context"],
        ["Donc"]),
    (4, 25, "Explaining Reasons",
        ["communication"],
        ["Give clear reasons for decisions and actions using parce que and car",
         "Respond naturally to pourquoi in conversation"],
        ["Parce que", "Car"]),
    (4, 26, "Describing Consequences",
        ["communication"],
        ["Describe the result of events using donc and alors",
         "Link cause and effect in a natural, flowing way"],
        ["Donc", "Alors"]),
    (4, 27, "Building Natural Explanations",
        ["skill"],
        ["Combine cause and consequence connectors in multi-sentence explanations",
         "Express reasoning fluently in conversation"],
        ["Explaining Reasons", "Describing Consequences"]),

    # ── Module 15: Making Comparisons ──────────────────────────────────────────
    (5, 28, "Comparative Forms",
        ["concept"],
        ["Form comparatives using plus...que, moins...que, aussi...que",
         "Apply comparatives to adjectives, adverbs, and nouns"],
        []),
    (5, 29, "Superlative Forms",
        ["concept"],
        ["Form superlatives using le plus and le moins",
         "Use superlatives correctly with nouns and adjectives"],
        ["Comparative Forms"]),
    (5, 30, "Comparing People",
        ["communication"],
        ["Compare physical and personality traits between people",
         "Use comparatives and superlatives naturally in conversation"],
        ["Comparative Forms"]),
    (5, 31, "Comparing Places",
        ["communication"],
        ["Compare cities, countries, and locations using comparatives",
         "Express preferences about places with supporting comparisons"],
        ["Comparative Forms"]),
    (5, 32, "Comparing Things",
        ["communication"],
        ["Compare objects, products, and options using superlatives",
         "Make recommendations based on comparisons"],
        ["Superlative Forms"]),
    (5, 33, "Expressing Opinions Through Comparison",
        ["skill"],
        ["Give structured opinions using comparative and superlative forms",
         "Sustain a comparison-based discussion naturally"],
        ["Comparing People", "Comparing Places", "Comparing Things"]),

    # ── Module 16: Pronouns Expansion ──────────────────────────────────────────
    (6, 34, "Direct Object Pronouns (le, la, les)",
        ["concept"],
        ["Replace direct object nouns with le, la, les",
         "Position object pronouns correctly before the verb"],
        []),
    (6, 35, "Indirect Object Pronouns (lui, leur)",
        ["concept"],
        ["Replace indirect object nouns with lui and leur",
         "Distinguish direct from indirect object pronouns"],
        []),
    (6, 36, "Combining Object Pronouns",
        ["concept"],
        ["Use two object pronouns together in correct order",
         "Apply pronoun combinations in affirmative and negative sentences"],
        ["Direct Object Pronouns (le, la, les)", "Indirect Object Pronouns (lui, leur)"]),
    (6, 37, "Introduction to Y",
        ["concept"],
        ["Use y to replace location phrases and complements with à",
         "Position y correctly in various sentence structures"],
        []),
    (6, 38, "Introduction to EN",
        ["concept"],
        ["Use en to replace partitive and de + noun phrases",
         "Distinguish en from other object pronouns"],
        []),
    (6, 39, "Natural Pronoun Usage in Conversation",
        ["communication"],
        ["Apply all learned pronouns fluidly in spoken interaction",
         "Avoid repeating nouns unnecessarily by using pronouns correctly"],
        ["Combining Object Pronouns", "Introduction to Y", "Introduction to EN"]),

    # ── Module 17: Quantities, Adverbs & Precision ─────────────────────────────
    (7, 40, "Beaucoup de",
        ["closed_set"],
        ["Use beaucoup de correctly before nouns without articles",
         "Integrate beaucoup de naturally in sentences about quantity"],
        []),
    (7, 41, "Peu de",
        ["closed_set"],
        ["Use peu de to express small quantity",
         "Contrast peu de with un peu de in context"],
        []),
    (7, 42, "Trop de",
        ["closed_set"],
        ["Use trop de to express excess",
         "Use trop de in complaints and evaluations"],
        []),
    (7, 43, "Assez de",
        ["closed_set"],
        ["Use assez de to express sufficiency",
         "Combine assez de in positive and negative contexts"],
        []),
    (7, 44, "Plusieurs",
        ["closed_set"],
        ["Use plusieurs correctly as an indefinite determiner",
         "Distinguish plusieurs from other plural quantity words"],
        []),
    (7, 45, "Adverbs of Quantity",
        ["closed_set"],
        ["Use beaucoup, peu, trop, assez, plusieurs fluently in context",
         "Select the most natural quantity expression for a given situation"],
        ["Beaucoup de", "Peu de", "Trop de", "Assez de"]),
    (7, 46, "Adverbs of Manner",
        ["closed_set"],
        ["Form and use adverbs of manner ending in -ment",
         "Position manner adverbs correctly in sentences"],
        []),
    (7, 47, "Adding Detail and Nuance",
        ["skill"],
        ["Enrich descriptions and narratives using adverbs of quantity and manner",
         "Add precision and nuance to spoken and written French"],
        ["Adverbs of Quantity", "Adverbs of Manner"]),

    # ── Module 18: Building Longer Sentences ───────────────────────────────────
    (8, 48, "Relative Pronoun Qui",
        ["concept"],
        ["Use qui as a subject relative pronoun to describe nouns",
         "Construct relative clauses with qui correctly"],
        []),
    (8, 49, "Relative Pronoun Que",
        ["concept"],
        ["Use que as an object relative pronoun in complex sentences",
         "Apply past participle agreement with que in compound tenses"],
        []),
    (8, 50, "Relative Pronoun Où",
        ["concept"],
        ["Use où to refer to location and time in relative clauses",
         "Distinguish où as a relative pronoun from où as a question word"],
        []),
    (8, 51, "Combining Ideas into Longer Sentences",
        ["skill"],
        ["Link clauses using qui, que, and où in multi-clause sentences",
         "Build complex sentences without losing grammatical accuracy"],
        ["Relative Pronoun Qui", "Relative Pronoun Que", "Relative Pronoun Où"]),
    (8, 52, "Describing People and Things in Greater Detail",
        ["communication"],
        ["Use relative pronouns to describe people and objects in extended detail",
         "Avoid sentence fragmentation by connecting ideas fluently"],
        ["Combining Ideas into Longer Sentences"]),

    # ── Module 19: Time & Location Expressions ─────────────────────────────────
    (9, 53, "Depuis",
        ["concept"],
        ["Use depuis + present tense to describe ongoing actions",
         "Express how long something has been happening"],
        []),
    (9, 54, "Pendant",
        ["concept"],
        ["Use pendant to describe the duration of a completed action",
         "Distinguish pendant from depuis in context"],
        []),
    (9, 55, "Pour",
        ["concept"],
        ["Use pour to express intended duration in the future",
         "Apply pour correctly in travel and planning contexts"],
        []),
    (9, 56, "Jusqu'à",
        ["concept"],
        ["Use jusqu'à to express up to a point in time or place",
         "Combine jusqu'à with other time expressions naturally"],
        []),
    (9, 57, "Advanced Prepositions in Context",
        ["communication"],
        ["Use depuis, pendant, pour, and jusqu'à accurately in varied contexts",
         "Choose the correct preposition based on temporal meaning"],
        ["Depuis", "Pendant", "Pour", "Jusqu'à"]),
    (9, 58, "Talking About Duration and Time Relationships",
        ["communication"],
        ["Discuss time spans, schedules, and durations naturally in conversation",
         "Respond accurately to questions about when and how long"],
        ["Advanced Prepositions in Context"]),

    # ── Module 20: Expanded Negation ───────────────────────────────────────────
    (10, 59, "Ne...jamais",
        ["concept"],
        ["Form and use ne...jamais to express never",
         "Use ne...jamais correctly across tenses"],
        []),
    (10, 60, "Ne...rien",
        ["concept"],
        ["Form and use ne...rien to express nothing",
         "Use rien as subject and object in negation"],
        ["Ne...jamais"]),
    (10, 61, "Ne...personne",
        ["concept"],
        ["Form and use ne...personne to express no one",
         "Use personne as subject and object in negation"],
        ["Ne...jamais"]),
    (10, 62, "Ne...plus",
        ["concept"],
        ["Form and use ne...plus to express no longer or not anymore",
         "Contrast ne...plus with ne...pas naturally"],
        ["Ne...jamais"]),
    (10, 63, "Other Common Negative Structures",
        ["concept"],
        ["Use ne...que, ni...ni, and ne...aucun correctly",
         "Recognise and produce a range of negative forms in French"],
        ["Ne...rien", "Ne...personne", "Ne...plus"]),
    (10, 64, "Using Negation Naturally",
        ["communication"],
        ["Use all learned negative structures fluidly in conversation",
         "Choose the most natural negative form for a given context"],
        ["Other Common Negative Structures"]),

    # ── Module 21: Conditional Present & Polite Communication ──────────────────
    (11, 65, "Forming the Conditional Present",
        ["concept"],
        ["Form the conditional present for regular and irregular verbs",
         "Understand when the conditional is used in French"],
        []),
    (11, 66, "Je voudrais...",
        ["communication"],
        ["Use je voudrais to make polite requests and express desires",
         "Apply je voudrais in real-world service and social situations"],
        ["Forming the Conditional Present"]),
    (11, 67, "J'aimerais...",
        ["communication"],
        ["Use j'aimerais to express wishes and preferences politely",
         "Contrast j'aimerais with j'aime in context"],
        ["Forming the Conditional Present"]),
    (11, 68, "Je préférerais...",
        ["communication"],
        ["Use je préférerais to express preference in polite contexts",
         "Apply je préférerais in decision-making conversations"],
        ["Forming the Conditional Present"]),
    (11, 69, "Pourriez-vous... %s",
        ["communication"],
        ["Use pourriez-vous to make formal polite requests",
         "Respond appropriately to formal conditional questions"],
        ["Forming the Conditional Present"]),
    (11, 70, "Polite Requests",
        ["communication"],
        ["Make polite requests using the conditional in various situations",
         "Combine je voudrais and pourriez-vous fluidly in real-life scenarios"],
        ["Je voudrais...", "Pourriez-vous... %s"]),
    (11, 71, "Expressing Wishes",
        ["communication"],
        ["Express wishes and desires using j'aimerais and je voudrais",
         "Sustain a natural conversation about personal wishes"],
        ["Je voudrais...", "J'aimerais..."]),
    (11, 72, "Expressing Preferences",
        ["communication"],
        ["Articulate preferences using je préférerais and j'aimerais in context",
         "Compare options and state a preference naturally"],
        ["Je préférerais...", "J'aimerais..."]),
    (11, 73, "Simple Hypothetical Situations",
        ["communication"],
        ["Discuss simple hypothetical scenarios using the conditional",
         "Respond to basic si + imparfait constructions"],
        ["Forming the Conditional Present"]),

    # ── Module 22: Real-World Communication ────────────────────────────────────
    (12, 74, "Weather Conversations",
        ["communication"],
        ["Describe current and forecast weather using common expressions",
         "Ask and respond to weather-related small talk naturally"],
        []),
    (12, 75, "Shopping Situations",
        ["communication"],
        ["Navigate shopping interactions: items, prices, and sizes",
         "Use polite expressions and quantities in a shop context"],
        []),
    (12, 76, "Travel Situations",
        ["communication"],
        ["Handle travel scenarios: tickets, directions, and check-in",
         "Use transport vocabulary and polite requests fluidly"],
        []),
    (12, 77, "Making Appointments",
        ["communication"],
        ["Schedule, confirm, and cancel appointments in French",
         "Use time expressions and polite language in appointment contexts"],
        []),
    (12, 78, "Telephone Conversations",
        ["communication"],
        ["Open, sustain, and close a basic telephone conversation in French",
         "Use telephone-specific phrases and responses naturally"],
        []),
    (12, 79, "Asking for Help",
        ["communication"],
        ["Request assistance politely in various real-world contexts",
         "Respond appropriately when someone asks for help"],
        []),
    (12, 80, "Asking for Information",
        ["communication"],
        ["Ask clear questions to obtain information in public and service contexts",
         "Process and respond to informational exchanges naturally"],
        []),
    (12, 81, "Handling Everyday Problems",
        ["communication"],
        ["Report a problem or misunderstanding politely in French",
         "Resolve everyday issues using known vocabulary and strategies"],
        ["Asking for Help", "Asking for Information"]),

    # ── Module 23: Communication Mastery ───────────────────────────────────────
    (13, 82, "Giving Opinions",
        ["communication"],
        ["Express opinions using je pense que, je crois que, and à mon avis",
         "Support opinions with brief reasons"],
        []),
    (13, 83, "Agreeing and Disagreeing",
        ["communication"],
        ["Agree and disagree politely using standard expressions",
         "Maintain a respectful exchange of views in conversation"],
        ["Giving Opinions"]),
    (13, 84, "Making Comparisons in Discussion",
        ["communication"],
        ["Use comparative and superlative forms to support arguments and opinions",
         "Compare options and people fluently in open conversation"],
        ["Comparative Forms", "Giving Opinions"]),
    (13, 85, "Describing Experiences",
        ["communication"],
        ["Narrate personal experiences in detail using past tenses",
         "Engage a listener with vivid, connected descriptions"],
        ["Talking About Past Experiences"]),
    (13, 86, "Narrating Events",
        ["skill"],
        ["Tell a structured account of events with clear sequencing",
         "Combine multiple past tenses and time expressions fluidly"],
        ["Describing Experiences", "Storytelling in the Past"]),
    (13, 87, "Expressing Preferences",   # builds on Module 21's Expressing Preferences
        ["communication"],
        ["State and justify preferences in extended conversation",
         "Compare options and explain reasoning behind preferences"],
        ["Expressing Preferences"]),
    (13, 88, "Explaining Decisions",
        ["communication"],
        ["Justify decisions using cause-and-effect structures and preference expressions",
         "Communicate reasoning clearly and naturally"],
        ["Giving Opinions", "Building Natural Explanations"]),
    (13, 89, "Sustaining a Multi-Minute Conversation",
        ["skill"],
        ["Maintain a conversation for several minutes on a familiar topic",
         "Use repairs, fillers, and turn-taking strategies naturally"],
        ["Agreeing and Disagreeing", "Describing Experiences", "Giving Opinions"]),

    # ── Module 24: Writing & Interaction ───────────────────────────────────────
    (14, 90, "Writing Longer Messages",
        ["skill"],
        ["Write multi-paragraph informal messages in French",
         "Use connectors and cohesive devices to link ideas"],
        []),
    (14, 91, "Writing Informal Emails",
        ["skill"],
        ["Structure and write an informal email with appropriate register",
         "Use greeting, body, and sign-off conventions for informal French email"],
        ["Writing Longer Messages"]),
    (14, 92, "Writing Short Narratives",
        ["skill"],
        ["Write a coherent short story or account using past tenses",
         "Organise a narrative with a clear beginning, middle, and end"],
        ["Writing Longer Messages", "Storytelling in the Past"]),
    (14, 93, "Responding to Invitations",
        ["communication"],
        ["Accept or decline invitations appropriately in written French",
         "Express enthusiasm, regret, and alternative suggestions politely"],
        ["Writing Informal Emails"]),
    (14, 94, "Describing Personal Experiences in Writing",
        ["skill"],
        ["Write a detailed personal account using multiple tenses and rich vocabulary",
         "Combine description, narrative, and reflection in a written text"],
        ["Writing Short Narratives", "Talking About Past Experiences"]),
    (14, 95, "Combining Multiple Grammar Concepts in Context",
        ["skill"],
        ["Produce a written text integrating pronouns, negation, comparatives, and tense variety",
         "Demonstrate A2-level grammatical range in a single coherent piece of writing"],
        ["Writing Short Narratives", "Natural Pronoun Usage in Conversation", "Using Negation Naturally"]),
]


# ─── French B1 curriculum ─────────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_FRENCH_B1_MODULES: list[tuple[int, str, str, int]] = [
    (1, "Conditional Mastery & Hypothetical Speech", "Express politeness, possibility, and hypothetical reasoning using the conditional and si clauses",  6),
    (2, "Subjunctive & Subjectivity",                "Express feelings, doubt, and subjective meaning using the present subjunctive",                     7),
    (3, "Advanced Sentence Expansion",               "Build complex connected sentences using dont, lequel, and sentence embedding strategies",            5),
    (4, "Pronouns & Natural Speech Flow",            "Speak naturally without repetition using double pronouns, Y, EN, and pronoun chaining",             5),
    (5, "Reported Speech & Information Transfer",    "Transmit information accurately in conversation using direct and indirect speech",                   5),
    (6, "Time Logic & Narrative Control",            "Tell structured multi-time narratives using plus-que-parfait, futur antérieur, and sequencing",     5),
    (7, "Discourse Flow & Connectors",               "Speak fluently with natural idea transitions using logical connectors and the gérondif",            5),
    (8, "Argumentation & Opinion Building",          "Hold structured debates and discussions expressing and defending viewpoints clearly",               5),
    (9, "Real-World Society Topics",                 "Discuss abstract real-world topics across education, work, technology, and society",                7),
    (10, "Writing Mastery",                           "Produce structured written communication from paragraphs to formal and informal texts",             6),
    (11, "Conversation Mastery",                      "Sustain natural multi-turn conversations using suggestions, negotiation, and clarification",        6),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
# prereq_topics are resolved to node IDs during seeding (two-pass).
# Pass 2 queries ALL French nodes so cross-level A2 prereqs resolve correctly.
_FRENCH_B1_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 25: Conditional Mastery & Hypothetical Speech ──────────────────
    (1, 1,  "Conditional Present (core formation)",
        ["grammar"],
        ["Form the conditional present for all regular and key irregular verbs",
         "Express politeness, possibility, and hypothetical meaning using the conditional"],
        ["Forming the Conditional Present"]),
    (1, 2,  "Polite Requests (Je voudrais…, Pourriez-vous…)",
        ["communication"],
        ["Use je voudrais, j'aimerais, and pourriez-vous to make polite requests",
         "Navigate real-world service and social situations with appropriate register"],
        ["Conditional Present (core formation)"]),
    (1, 3,  "Advice & Suggestions",
        ["communication"],
        ["Give advice using vous devriez, tu devrais, and il vaudrait mieux",
         "Offer and respond to suggestions naturally in conversation"],
        ["Conditional Present (core formation)"]),
    (1, 4,  "Hypothetical Situations",
        ["communication"],
        ["Discuss hypothetical scenarios using the conditional",
         "Speculate about alternative outcomes and imagined situations"],
        ["Conditional Present (core formation)", "Simple Hypothetical Situations"]),
    (1, 5,  "Si Clauses (Present + Future)",
        ["grammar"],
        ["Form si + present + future clauses for real conditions",
         "Distinguish real conditions from hypothetical ones"],
        ["Conditional Present (core formation)"]),
    (1, 6,  "Si Clauses (Imperfect + Conditional)",
        ["grammar"],
        ["Form si + imparfait + conditional clauses for unreal conditions",
         "Use hypothetical si clauses naturally in spoken and written French"],
        ["Si Clauses (Present + Future)", "Conditional Present (core formation)"]),

    # ── Module 26: Subjunctive & Subjectivity ─────────────────────────────────
    (2, 7,  "Introduction to Subjunctive",
        ["concept"],
        ["Understand when the subjunctive mood is required in French",
         "Identify the subjunctive in written and spoken texts"],
        []),
    (2, 8,  "Formation of Present Subjunctive",
        ["grammar"],
        ["Form the present subjunctive for regular and common irregular verbs",
         "Apply subjunctive formation rules consistently across verb groups"],
        ["Introduction to Subjunctive"]),
    (2, 9,  "Emotion & Subjective Expression",
        ["communication"],
        ["Use the subjunctive after verbs of emotion (être content que, regretter que, avoir peur que)",
         "Express feelings and reactions about others' actions in French"],
        ["Formation of Present Subjunctive"]),
    (2, 10, "Desire & Preference",
        ["communication"],
        ["Use vouloir que, souhaiter que, and préférer que + subjunctive",
         "Express what you want or prefer others to do"],
        ["Formation of Present Subjunctive"]),
    (2, 11, "Necessity & Obligation",
        ["communication"],
        ["Use il faut que and il est nécessaire que + subjunctive",
         "Express obligation and necessity about third parties"],
        ["Formation of Present Subjunctive"]),
    (2, 12, "Doubt & Uncertainty",
        ["communication"],
        ["Use douter que, ne pas croire que, and ne pas penser que + subjunctive",
         "Express doubt and scepticism using the subjunctive mood"],
        ["Formation of Present Subjunctive"]),
    (2, 13, "Indicative vs Subjunctive Contrast",
        ["concept"],
        ["Choose between indicative and subjunctive based on meaning and trigger",
         "Avoid common errors when switching between moods"],
        ["Formation of Present Subjunctive", "Emotion & Subjective Expression"]),

    # ── Module 27: Advanced Sentence Expansion ────────────────────────────────
    (3, 14, "Qui / Que / Où Review",
        ["concept"],
        ["Reinforce accurate use of qui, que, and où as relative pronouns",
         "Build multi-clause sentences with confidence using the core relative pronouns"],
        ["Relative Pronoun Qui", "Relative Pronoun Que", "Relative Pronoun Où"]),
    (3, 15, "Dont",
        ["grammar"],
        ["Use dont to replace de + noun in relative clauses",
         "Apply dont with verbs and expressions that take de (parler de, avoir besoin de)"],
        []),
    (3, 16, "Lequel / Laquelle / Lesquels",
        ["grammar"],
        ["Use lequel, laquelle, lesquels, lesquelles as relative pronouns after prepositions",
         "Choose the correct form of lequel to agree in gender and number"],
        []),
    (3, 17, "Sentence Embedding Strategies",
        ["skill"],
        ["Combine multiple relative clauses to add depth and detail to sentences",
         "Avoid grammatical errors when embedding clauses within clauses"],
        ["Dont", "Lequel / Laquelle / Lesquels", "Qui / Que / Où Review"]),
    (3, 18, "Natural Sentence Merging",
        ["skill"],
        ["Merge short sentences into complex ones using all learned relative pronouns",
         "Produce connected, natural-sounding French at B1 complexity level"],
        ["Sentence Embedding Strategies"]),

    # ── Module 28: Pronouns & Natural Speech Flow ─────────────────────────────
    (4, 19, "Object Pronouns in Context",
        ["concept"],
        ["Revise and extend use of direct and indirect object pronouns in varied contexts",
         "Correctly position object pronouns in affirmative, negative, and imperative sentences"],
        ["Natural Pronoun Usage in Conversation"]),
    (4, 20, "Double Pronouns",
        ["grammar"],
        ["Use two object pronouns together in the correct order (me le, lui en, etc.)",
         "Apply double pronoun rules in both affirmative and negative sentences"],
        ["Object Pronouns in Context"]),
    (4, 21, "Pronoun Placement in Compound Tenses",
        ["grammar"],
        ["Position object pronouns correctly in passé composé and other compound tenses",
         "Avoid placement errors with double pronouns in compound verb structures"],
        ["Double Pronouns"]),
    (4, 22, "Y and EN in Natural Speech",
        ["communication"],
        ["Use y and en fluidly to avoid repetition in conversation",
         "Distinguish when y and en are required and position them accurately"],
        ["Introduction to Y", "Introduction to EN"]),
    (4, 23, "Fluid Pronoun Chaining",
        ["skill"],
        ["Chain multiple pronoun types across complex sentences without hesitation",
         "Speak naturally without noun repetition by selecting and sequencing pronouns correctly"],
        ["Double Pronouns", "Y and EN in Natural Speech"]),

    # ── Module 29: Reported Speech & Information Transfer ─────────────────────
    (5, 24, "Direct vs Indirect Speech",
        ["concept"],
        ["Identify the difference between direct and indirect speech in French",
         "Understand the structural changes when converting direct to indirect speech"],
        []),
    (5, 25, "Reporting Statements",
        ["grammar"],
        ["Convert direct statements to indirect using dire que and affirmer que",
         "Apply tense backshift rules when reporting past statements"],
        ["Direct vs Indirect Speech"]),
    (5, 26, "Reporting Questions",
        ["grammar"],
        ["Report yes/no questions using si and information questions using interrogative words",
         "Avoid common word-order errors in reported questions"],
        ["Direct vs Indirect Speech"]),
    (5, 27, "Tense Shifts in Narration",
        ["grammar"],
        ["Apply systematic tense backshift when reporting speech in the past",
         "Recognise and produce natural tense shifts in narration"],
        ["Reporting Statements", "Reporting Questions"]),
    (5, 28, "Real-World Retelling",
        ["skill"],
        ["Retell conversations, messages, and news using indirect speech fluently",
         "Transfer information accurately and naturally between interlocutors"],
        ["Tense Shifts in Narration"]),

    # ── Module 30: Time Logic & Narrative Control ─────────────────────────────
    (6, 29, "Plus-que-parfait Mastery",
        ["grammar"],
        ["Form and use the plus-que-parfait for all verb groups with full accuracy",
         "Express prior past events clearly in relation to other past actions"],
        ["Plus-que-parfait (Introduction)"]),
    (6, 30, "Futur Antérieur",
        ["grammar"],
        ["Form the futur antérieur using future of avoir/être + past participle",
         "Express future actions that will be completed before another future event"],
        ["Futur Simple"]),
    (6, 31, "Sequencing Events",
        ["skill"],
        ["Use temporal connectors (avant que, après avoir, dès que, une fois que) to sequence events",
         "Build logically ordered narratives with clear time relationships"],
        ["Plus-que-parfait Mastery"]),
    (6, 32, "Past Narrative Control",
        ["skill"],
        ["Tell a complex past narrative using passé composé, imparfait, and plus-que-parfait together",
         "Control narrative perspective and pace through tense choice"],
        ["Plus-que-parfait Mastery", "Sequencing Events"]),
    (6, 33, "Temporal Reasoning in Storytelling",
        ["skill"],
        ["Integrate all learned tenses including futur antérieur into coherent storytelling",
         "Reason about time relationships between events in extended spoken narratives"],
        ["Past Narrative Control", "Futur Antérieur"]),

    # ── Module 31: Discourse Flow & Connectors ────────────────────────────────
    (7, 34, "Logical Connectors",
        ["concept"],
        ["Use cependant, pourtant, néanmoins, and en revanche to express contrast",
         "Distinguish each connector by nuance and register"],
        []),
    (7, 35, "Cause & Consequence Structures",
        ["grammar"],
        ["Use puisque, étant donné que, c'est pourquoi, and par conséquent to link cause and result",
         "Build multi-clause arguments using cause-effect connectors"],
        ["Logical Connectors"]),
    (7, 36, "Argument Flow Markers",
        ["concept"],
        ["Use d'abord, ensuite, de plus, enfin, and en conclusion to structure arguments",
         "Guide the listener or reader through a structured line of reasoning"],
        ["Logical Connectors"]),
    (7, 37, "Sentence Linking in Real-Time Speech",
        ["skill"],
        ["Deploy connectors fluently in spontaneous spoken French without pausing",
         "Move smoothly between ideas using a range of linking expressions"],
        ["Cause & Consequence Structures", "Argument Flow Markers"]),
    (7, 38, "Gérondif (en + participe présent)",
        ["grammar"],
        ["Form the gérondif by combining en + present participle",
         "Use the gérondif to express simultaneous actions, manner, and condition"],
        []),

    # ── Module 32: Argumentation & Opinion Building ───────────────────────────
    (8, 39, "Expressing Opinions",
        ["communication"],
        ["Express nuanced opinions using selon moi, il me semble que, and j'estime que",
         "Go beyond basic opinion phrases to sound more sophisticated in B1 discussion"],
        ["Giving Opinions"]),
    (8, 40, "Agreeing and Disagreeing",
        ["communication"],
        ["Agree and disagree with precision using je suis (tout à fait) d'accord, certes mais, and je ne partage pas",
         "Maintain a respectful but assertive position in debate"],
        ["Expressing Opinions"]),
    (8, 41, "Justifying Arguments",
        ["skill"],
        ["Support a position with reasons, examples, and consequences",
         "Use justification language (car, en effet, à titre d'exemple) naturally"],
        ["Expressing Opinions"]),
    (8, 42, "Pros and Cons Discussions",
        ["communication"],
        ["Present both sides of an issue using d'un côté… de l'autre and pour/contre structures",
         "Weigh up advantages and disadvantages in structured spoken and written form"],
        ["Justifying Arguments"]),
    (8, 43, "Defending Viewpoints",
        ["skill"],
        ["Maintain and defend a position under challenge using reformulation and emphasis",
         "Respond to counterarguments confidently while staying on topic"],
        ["Pros and Cons Discussions", "Justifying Arguments"]),

    # ── Module 33: Real-World Society Topics ─────────────────────────────────
    (9, 44, "Education",
        ["communication"],
        ["Discuss the education system, learning experiences, and future academic plans",
         "Use relevant vocabulary and opinion structures in education-themed conversation"],
        []),
    (9, 45, "Work",
        ["communication"],
        ["Talk about jobs, work environments, career aspirations, and workplace issues",
         "Use work-related vocabulary and express opinions about professional life"],
        []),
    (9, 46, "Technology",
        ["communication"],
        ["Discuss the impact of technology, social media, and digital life on society",
         "Express opinions, concerns, and enthusiasm about technological change"],
        []),
    (9, 47, "Travel",
        ["communication"],
        ["Describe travel experiences, compare destinations, and discuss tourism",
         "Use travel vocabulary and narrative structures in extended conversation"],
        []),
    (9, 48, "Media",
        ["communication"],
        ["Discuss news, journalism, social media, and the role of media in society",
         "Express views on media consumption and its effects using B1 structures"],
        []),
    (9, 49, "Environment",
        ["communication"],
        ["Discuss environmental issues, sustainability, and personal responsibility",
         "Argue for or against environmental actions using appropriate vocabulary"],
        []),
    (9, 50, "Social Issues",
        ["communication"],
        ["Discuss social topics such as inequality, immigration, and community life",
         "Present and justify opinions on social issues with nuance and respect"],
        ["Expressing Opinions", "Justifying Arguments"]),

    # ── Module 34: Writing Mastery ────────────────────────────────────────────
    (10, 51, "Structured Paragraphs",
        ["writing"],
        ["Write well-organised paragraphs with a clear topic sentence, development, and conclusion",
         "Use cohesive devices to ensure logical flow within and between paragraphs"],
        []),
    (10, 52, "Opinion Essays",
        ["writing"],
        ["Write a structured opinion essay presenting and defending a clear argument",
         "Use introduction, body paragraphs, and conclusion effectively in French"],
        ["Structured Paragraphs", "Justifying Arguments"]),
    (10, 53, "Formal Emails",
        ["writing"],
        ["Write formal emails using appropriate register, salutations, and sign-offs",
         "Structure professional requests, complaints, and inquiries in French"],
        ["Structured Paragraphs"]),
    (10, 54, "Informal Emails",
        ["writing"],
        ["Write friendly emails and messages with natural informal register",
         "Use informal expressions, contractions, and conversational French in writing"],
        ["Structured Paragraphs"]),
    (10, 55, "Narrative Writing",
        ["writing"],
        ["Write a coherent narrative with vivid description, sequenced events, and tense control",
         "Combine past tenses effectively to tell a compelling story in writing"],
        ["Structured Paragraphs", "Past Narrative Control"]),
    (10, 56, "Extended Writing Tasks",
        ["writing"],
        ["Produce longer, multi-paragraph written texts combining multiple B1 grammar and vocabulary skills",
         "Demonstrate range and accuracy in extended written French"],
        ["Opinion Essays", "Narrative Writing"]),

    # ── Module 35: Conversation Mastery ──────────────────────────────────────
    (11, 57, "Making Suggestions",
        ["communication"],
        ["Suggest plans, activities, and solutions using si on + imparfait, pourquoi ne pas, and on pourrait",
         "Respond to and build on suggestions naturally in conversation"],
        []),
    (11, 58, "Negotiation Language",
        ["communication"],
        ["Use negotiation phrases to reach agreement and compromise in French",
         "Express flexibility and resistance politely in decision-making conversations"],
        ["Making Suggestions"]),
    (11, 59, "Problem Solving",
        ["communication"],
        ["Identify a problem, propose solutions, and evaluate options in French",
         "Use problem-solution discourse structure in collaborative spoken tasks"],
        ["Making Suggestions"]),
    (11, 60, "Clarification Strategies",
        ["communication"],
        ["Ask for clarification using pardon, vous voulez dire, and c'est-à-dire",
         "Rephrase and confirm meaning to avoid misunderstanding in conversation"],
        []),
    (11, 61, "Extended Conversations",
        ["skill"],
        ["Sustain a multi-minute conversation on a B1 topic with turn-taking and recovery strategies",
         "Maintain engagement and coherence across an extended spoken exchange"],
        ["Negotiation Language", "Problem Solving", "Clarification Strategies"]),
    (11, 62, "Managing Misunderstandings",
        ["communication"],
        ["Recognise and resolve misunderstandings using reformulation and confirmation checks",
         "Handle communication breakdowns gracefully and continue a conversation"],
        ["Clarification Strategies"]),
]


# ─── French B2 curriculum ─────────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_FRENCH_B2_MODULES: list[tuple[int, str, str, int]] = [
    (1, "Registers, Style & Natural Speech",         "Master formal and informal registers, idiomatic language, and natural spoken contractions",           7),
    (2, "Hypothesis & Conditional Systems",          "Express real and unreal conditions, mixed conditionals, and probability with precision",              6),
    (3, "Subjunctive Mastery System",                "Use the subjunctive for emotion, obligation, concession, and purpose with full control",              7),
    (4, "Passive Voice & Stylistic Control",         "Form passive structures across tenses and make informed stylistic choices between active and passive", 6),
    (5, "Advanced Relative Structures",              "Use auquel, duquel, and stacked relative clauses to express complex ideas naturally",                  6),
    (6, "Pronoun Mastery & Fluency Compression",     "Use pronouns at full B2 fluency including imperatives, chaining, and fast-speech compression",        6),
    (7, "Discourse Markers & Logical Flow",          "Link ideas in speech and writing using contrast, consequence, and reinforcement markers",              6),
    (8, "Argumentation & Critical Thinking",         "Build, defend, and counter arguments with critical reasoning and structured writing",                  7),
    (9, "Conversation Repair & Interaction Control", "Repair dialogue, interrupt politely, and maintain conversation flow under pressure",                   6),
    (10, "Real-World Writing Systems",                "Produce formal emails, letters, summaries, and reports with precise tone control",                     7),
    (11, "Listening & Interpretation Skills",         "Interpret fast native speech by extracting gist, opinion, attitude, and implied meaning",              6),
    (12, "Linguistic Nuance & Hedging",               "Express uncertainty, soften opinions, and communicate with precision and emotional moderation",        6),
    (13, "Society, Media & Abstract Topics",          "Discuss media, work, society, culture, and abstract ideas with B2 depth and vocabulary",               7),
    (14, "Real-Time Communication Pressure System",   "Develop instant-response fluency through drills, reaction tasks, and time-pressured speaking",         6),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
# prereq_topics are resolved to node IDs during seeding (two-pass).
# Pass 2 queries ALL French nodes so cross-level B1/A2 prereqs resolve correctly.
_FRENCH_B2_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 36: Registers, Style & Natural Speech ──────────────────────────
    (1, 1,  "Formal vs Informal Register",
        ["concept"],
        ["Distinguish formal and informal registers across spoken and written French",
         "Select the appropriate register for a given social context"],
        []),
    (1, 2,  "Politeness Strategies in Conversation",
        ["communication"],
        ["Apply politeness strategies beyond the conditional to soften requests and maintain rapport",
         "Adjust politeness level dynamically according to relationship and context"],
        ["Formal vs Informal Register"]),
    (1, 3,  "Idiomatic Expressions",
        ["vocabulary"],
        ["Use common idiomatic expressions naturally in conversation",
         "Recognise idioms in spoken and written French and infer meaning from context"],
        []),
    (1, 4,  "Slang vs Neutral Language",
        ["vocabulary"],
        ["Identify and use everyday slang in appropriate informal contexts",
         "Avoid register mismatches by distinguishing slang from neutral vocabulary"],
        ["Formal vs Informal Register"]),
    (1, 5,  "Tone Shifting in Speech",
        ["skill"],
        ["Shift between formal and casual tones smoothly within the same conversation",
         "Respond to tonal shifts from an interlocutor without losing fluency"],
        ["Formal vs Informal Register", "Politeness Strategies in Conversation"]),
    (1, 6,  "Natural Spoken Contractions",
        ["phonetics"],
        ["Recognise and produce common spoken contractions (j'sais pas, t'as, y'a, c'est)",
         "Sound natural in informal speech without over-applying formal pronunciation rules"],
        ["Slang vs Neutral Language"]),
    (1, 7,  "Emotional Tone in Speech",
        ["skill"],
        ["Convey a range of emotions through intonation, word choice, and pacing",
         "Interpret emotional subtext in native speech beyond literal meaning"],
        ["Tone Shifting in Speech"]),

    # ── Module 37: Hypothesis & Conditional Systems ───────────────────────────
    (2, 8,  "Real Conditions Review (si + présent → futur)",
        ["grammar"],
        ["Consolidate si + present tense + future tense for real conditions",
         "Apply real conditional structures accurately in complex multi-clause sentences"],
        ["Si Clauses (Present + Future)"]),
    (2, 9,  "Unreal Present Conditions (si + imparfait → conditionnel)",
        ["grammar"],
        ["Consolidate si + imparfait + conditional for currently unreal situations",
         "Use unreal present conditionals with irregular verbs at full accuracy"],
        ["Si Clauses (Imperfect + Conditional)"]),
    (2, 10, "Past Hypotheticals (si + plus-que-parfait → conditionnel passé)",
        ["grammar"],
        ["Form the conditional past and use it in third conditional constructions",
         "Express regret and counterfactual reasoning about past events"],
        ["Unreal Present Conditions (si + imparfait → conditionnel)", "Plus-que-parfait Mastery"]),
    (2, 11, "Mixed Conditionals",
        ["grammar"],
        ["Blend real and unreal conditions across time frames in a single sentence",
         "Recognise and produce mixed conditional forms in spontaneous speech"],
        ["Past Hypotheticals (si + plus-que-parfait → conditionnel passé)", "Unreal Present Conditions (si + imparfait → conditionnel)"]),
    (2, 12, "Hypothetical Regrets & Counterfactuals",
        ["communication"],
        ["Express regrets, wishes, and counterfactuals using the conditional past",
         "Sustain a conversation about hypothetical past outcomes naturally"],
        ["Mixed Conditionals", "Past Hypotheticals (si + plus-que-parfait → conditionnel passé)"]),
    (2, 13, "Probability vs Certainty Structures",
        ["communication"],
        ["Express varying degrees of likelihood using modal expressions and verb moods",
         "Distinguish certain, probable, and possible outcomes in speech and writing"],
        []),

    # ── Module 38: Subjunctive Mastery System ─────────────────────────────────
    (3, 14, "Present Subjunctive Review",
        ["grammar"],
        ["Recall and consolidate present subjunctive formation for all verb groups",
         "Use the subjunctive automatically after known triggers without hesitation"],
        ["Formation of Present Subjunctive"]),
    (3, 15, "Past Subjunctive Recognition",
        ["grammar"],
        ["Recognise the past subjunctive in literary and formal texts",
         "Understand its function as a stylistically elevated alternative to the conditional"],
        ["Present Subjunctive Review"]),
    (3, 16, "Emotion Triggers for Subjunctive",
        ["communication"],
        ["Use the subjunctive after a full range of emotion verbs (regretter, craindre, être ravi)",
         "Distinguish emotion-triggered subjunctive from indicative constructions naturally"],
        ["Present Subjunctive Review"]),
    (3, 17, "Necessity & Obligation in Subjunctive",
        ["communication"],
        ["Use il faut que, il est indispensable que, and il est essentiel que + subjunctive",
         "Go beyond basic necessity expressions to sound formal and precise"],
        ["Present Subjunctive Review"]),
    (3, 18, "Concession Clauses (bien que, quoique)",
        ["grammar"],
        ["Form and use bien que and quoique + subjunctive to express concession",
         "Distinguish these from coordinating concession markers (pourtant, malgré)"],
        ["Present Subjunctive Review"]),
    (3, 19, "Purpose Clauses (pour que, afin que)",
        ["grammar"],
        ["Use pour que and afin que + subjunctive to express purpose",
         "Choose correctly between pour + infinitive and pour que + subjunctive"],
        ["Present Subjunctive Review"]),
    (3, 20, "Impersonal Subjunctive Expressions",
        ["grammar"],
        ["Use a range of impersonal constructions triggering the subjunctive",
         "Produce formal and academic French by selecting impersonal subjunctive expressions"],
        ["Necessity & Obligation in Subjunctive", "Purpose Clauses (pour que, afin que)"]),

    # ── Module 39: Passive Voice & Stylistic Control ──────────────────────────
    (4, 21, "Present Passive Structures",
        ["grammar"],
        ["Form passive constructions in the present tense using être + past participle",
         "Apply agent introduction with par correctly in the passive"],
        []),
    (4, 22, "Past Passive Structures",
        ["grammar"],
        ["Form passive constructions in passé composé and imparfait",
         "Distinguish between the passive and adjectival use of être + past participle"],
        ["Present Passive Structures"]),
    (4, 23, "Multi-Tense Passive Transformations",
        ["grammar"],
        ["Produce passive forms across future, conditional, and subjunctive tenses",
         "Transform active sentences to passive across multiple tense and mood combinations"],
        ["Past Passive Structures"]),
    (4, 24, "Active to Passive Rewriting",
        ["skill"],
        ["Rewrite active sentences as passive with correct agreement and agent placement",
         "Identify when passive transformation changes the meaning or focus of a sentence"],
        ["Multi-Tense Passive Transformations"]),
    (4, 25, "Passive in Formal Writing",
        ["writing"],
        ["Use passive voice to create an impersonal, objective tone in formal and academic texts",
         "Recognise over-use of passive and revise for clarity"],
        ["Active to Passive Rewriting"]),
    (4, 26, "Stylistic Choice: Active vs Passive",
        ["skill"],
        ["Make informed decisions about when passive voice serves stylistic and communicative goals",
         "Edit texts to balance active and passive voice for maximum clarity and impact"],
        ["Passive in Formal Writing", "Active to Passive Rewriting"]),

    # ── Module 40: Advanced Relative Structures ───────────────────────────────
    (5, 27, "Complex Relative Clauses Review",
        ["concept"],
        ["Revise and consolidate qui, que, où, and dont in complex sentence contexts",
         "Produce multi-clause sentences with relative pronouns at B2 accuracy"],
        ["Natural Sentence Merging"]),
    (5, 28, "Lequel / Auquel / Duquel Forms",
        ["grammar"],
        ["Extend use of lequel to contracted forms auquel and duquel with prepositions",
         "Choose the correct form based on preposition and noun gender and number"],
        ["Lequel / Laquelle / Lesquels"]),
    (5, 29, "Embedded Relative Clauses",
        ["grammar"],
        ["Build sentences where one relative clause is embedded inside another",
         "Maintain grammatical accuracy and clarity in nested clause structures"],
        ["Complex Relative Clauses Review", "Lequel / Auquel / Duquel Forms"]),
    (5, 30, "Stacking Relative Clauses",
        ["skill"],
        ["Produce sentences that stack two or more relative clauses to express complex ideas",
         "Avoid ambiguity when stacking clauses through careful pronoun selection"],
        ["Embedded Relative Clauses"]),
    (5, 31, "Natural Omission in Spoken Relative Clauses",
        ["skill"],
        ["Recognise how relative clauses are reduced or omitted in natural spoken French",
         "Imitate native-level simplification strategies without losing meaning"],
        ["Stacking Relative Clauses"]),
    (5, 32, "Formal vs Spoken Relative Pronoun Usage",
        ["skill"],
        ["Adapt relative pronoun choices between formal written and casual spoken contexts",
         "Demonstrate register awareness in the selection and position of relative pronouns"],
        ["Natural Omission in Spoken Relative Clauses"]),

    # ── Module 41: Pronoun Mastery & Fluency Compression ─────────────────────
    (6, 33, "Y and EN Advanced Usage",
        ["grammar"],
        ["Extend y and en to complex and idiomatic constructions beyond B1",
         "Recognise and produce edge cases where y and en interact with other pronouns"],
        ["Fluid Pronoun Chaining"]),
    (6, 34, "Double Object Pronouns Review",
        ["grammar"],
        ["Consolidate double pronoun order across all tenses with full accuracy",
         "Produce double pronoun sequences fluently in affirmative and negative forms"],
        ["Pronoun Placement in Compound Tenses"]),
    (6, 35, "Pronoun Order Across All Tenses",
        ["grammar"],
        ["Master the complete pronoun order table including y and en across all tenses",
         "Avoid word-order errors in complex pronoun sequences involving multiple types"],
        ["Double Object Pronouns Review", "Y and EN Advanced Usage"]),
    (6, 36, "Pronouns in Imperatives",
        ["grammar"],
        ["Place object pronouns correctly in affirmative and negative imperatives",
         "Handle double pronouns in imperative forms including moi/toi stress forms"],
        ["Pronoun Order Across All Tenses"]),
    (6, 37, "Pronoun Chaining in Fast Speech",
        ["skill"],
        ["Produce pronoun sequences at natural conversational speed without hesitation",
         "Internalise pronoun order to the point of automatic application in real-time speech"],
        ["Pronouns in Imperatives"]),
    (6, 38, "Avoiding Repetition Through Pronouns",
        ["skill"],
        ["Replace nouns with the most precise pronoun to achieve natural, fluent French",
         "Edit spoken and written output to eliminate unnecessary noun repetition"],
        ["Pronoun Chaining in Fast Speech"]),

    # ── Module 42: Discourse Markers & Logical Flow ───────────────────────────
    (7, 39, "Contrast Markers (cependant, pourtant, en revanche)",
        ["concept"],
        ["Use cependant, pourtant, néanmoins, and en revanche at B2 register with full nuance",
         "Select the most precise contrast marker based on formality and implied meaning"],
        ["Sentence Linking in Real-Time Speech"]),
    (7, 40, "Consequence Markers (donc, par conséquent, ainsi)",
        ["concept"],
        ["Use donc, par conséquent, ainsi, and c'est ainsi que to express logical consequence",
         "Distinguish register differences between consequence markers in speech and writing"],
        ["Sentence Linking in Real-Time Speech"]),
    (7, 41, "Reinforcement Markers (d'ailleurs, en effet, notamment)",
        ["concept"],
        ["Use d'ailleurs, en effet, and notamment to add evidence and reinforce claims",
         "Position reinforcement markers accurately in spoken and written argument"],
        ["Contrast Markers (cependant, pourtant, en revanche)"]),
    (7, 42, "Structuring Arguments Orally",
        ["skill"],
        ["Organise a spoken argument using a range of discourse markers from introduction to conclusion",
         "Maintain logical flow and signpost transitions clearly in real-time speech"],
        ["Contrast Markers (cependant, pourtant, en revanche)", "Consequence Markers (donc, par conséquent, ainsi)"]),
    (7, 43, "Writing Cohesion Techniques",
        ["writing"],
        ["Use discourse markers and cohesive devices to ensure logical paragraph progression",
         "Avoid repetition and choppy structure by deploying linking language precisely"],
        ["Structuring Arguments Orally"]),
    (7, 44, "Linking Spoken Ideas Naturally",
        ["skill"],
        ["Deploy a full range of discourse markers spontaneously in fast conversational French",
         "Move between ideas without long pauses using markers as scaffolding"],
        ["Structuring Arguments Orally", "Reinforcement Markers (d'ailleurs, en effet, notamment)"]),

    # ── Module 43: Argumentation & Critical Thinking ──────────────────────────
    (8, 45, "Strong vs Soft Opinion Expression",
        ["communication"],
        ["Use a spectrum of opinion phrases from tentative (il me semble) to assertive (je suis convaincu)",
         "Calibrate opinion strength to context and audience for maximum rhetorical effect"],
        ["Defending Viewpoints"]),
    (8, 46, "Strategic Agreement & Disagreement",
        ["communication"],
        ["Agree and disagree with strategic precision without sounding blunt or evasive",
         "Use concession-then-refutation structures (certes… mais, il est vrai que… cependant)"],
        ["Strong vs Soft Opinion Expression"]),
    (8, 47, "Defending Arguments",
        ["skill"],
        ["Sustain and reinforce a position when challenged using elaboration and emphasis",
         "Avoid conceding too quickly by using restatement and clarification strategies"],
        ["Strong vs Soft Opinion Expression"]),
    (8, 48, "Constructing Counterarguments",
        ["skill"],
        ["Build counterarguments by identifying weaknesses in opposing claims",
         "Use concession structures to acknowledge the opposing view before refuting it"],
        ["Defending Arguments"]),
    (8, 49, "Critical Evaluation of Ideas",
        ["skill"],
        ["Evaluate the strength, relevance, and validity of arguments in French",
         "Identify bias, assumption, and logical gaps in spoken and written texts"],
        ["Constructing Counterarguments"]),
    (8, 50, "Expressing Abstract Reasoning",
        ["communication"],
        ["Articulate abstract concepts and theoretical ideas in clear, structured French",
         "Use appropriate vocabulary for academic and intellectual discourse"],
        ["Critical Evaluation of Ideas"]),
    (8, 51, "Structured Essay Writing",
        ["writing"],
        ["Write a structured argumentative essay with thesis, body, and conclusion in French",
         "Integrate discourse markers, opinion language, and evidence into a cohesive text"],
        ["Expressing Abstract Reasoning", "Extended Writing Tasks"]),

    # ── Module 44: Conversation Repair & Interaction Control ─────────────────
    (9, 52, "Asking for Clarification in Real Time",
        ["communication"],
        ["Request clarification on meaning, pronunciation, or reference using natural phrases",
         "Interrupt minimally and politely when clarification is needed during fast speech"],
        ["Managing Misunderstandings"]),
    (9, 53, "Rephrasing Misunderstood Ideas",
        ["communication"],
        ["Rephrase your own ideas when you sense a listener has not understood",
         "Choose simpler or more precise formulations without losing the original meaning"],
        ["Asking for Clarification in Real Time"]),
    (9, 54, "Interrupting Politely",
        ["communication"],
        ["Use softening phrases to interrupt without causing offence (excusez-moi, si je peux me permettre)",
         "Re-enter a conversation after an interruption with smooth turn-taking"],
        ["Asking for Clarification in Real Time"]),
    (9, 55, "Confirming Meaning",
        ["communication"],
        ["Check your own interpretation by paraphrasing back to the speaker",
         "Use confirmation techniques (vous voulez dire que…, si je comprends bien…) naturally"],
        ["Rephrasing Misunderstood Ideas"]),
    (9, 56, "Repairing Dialogue Breakdowns",
        ["skill"],
        ["Identify and recover from full communication breakdowns in conversation",
         "Use repair strategies (backtracking, topic restatement) to restore mutual understanding"],
        ["Confirming Meaning", "Interrupting Politely"]),
    (9, 57, "Maintaining Flow Under Confusion",
        ["skill"],
        ["Keep a conversation moving naturally even when partial understanding exists",
         "Deploy filler strategies and approximate responses to avoid prolonged silence"],
        ["Repairing Dialogue Breakdowns"]),

    # ── Module 45: Real-World Writing Systems ─────────────────────────────────
    (10, 58, "Formal Email Writing",
        ["writing"],
        ["Write professional emails with correct formal register, structure, and salutations",
         "Handle requests, complaints, and follow-ups in formal French email format"],
        ["Formal Emails"]),
    (10, 59, "Complaint Letters",
        ["writing"],
        ["Structure and write formal complaint letters with an assertive yet polite tone",
         "Use standard complaint language and logical sequencing to present a case clearly"],
        ["Formal Email Writing"]),
    (10, 60, "Informational Messages",
        ["writing"],
        ["Write clear, concise informational messages for professional and public contexts",
         "Prioritise key information and organise it for maximum reader clarity"],
        ["Formal Email Writing"]),
    (10, 61, "Article Summaries",
        ["writing"],
        ["Summarise a written article accurately and concisely in French",
         "Distinguish between the author's view and factual content in a summary"],
        ["Structured Paragraphs"]),
    (10, 62, "Structured Reports",
        ["writing"],
        ["Write a structured report with headings, introduction, findings, and conclusion",
         "Use impersonal and passive constructions appropriate to report register"],
        ["Article Summaries", "Structured Paragraphs"]),
    (10, 63, "Invitations & Responses",
        ["writing"],
        ["Write and respond to formal and informal invitations with appropriate tone and conventions",
         "Manage acceptance, refusal, and alternative suggestion in written French"],
        ["Informal Emails"]),
    (10, 64, "Tone Control in Writing",
        ["skill"],
        ["Adjust lexical and syntactic choices to shift tone from warm to neutral to formal",
         "Edit written texts to correct register mismatches and inconsistencies"],
        ["Formal Email Writing", "Invitations & Responses"]),

    # ── Module 46: Listening & Interpretation Skills ──────────────────────────
    (11, 65, "Understanding Fast Native Speech",
        ["listening"],
        ["Follow native-speed French conversations by predicting patterns and using context",
         "Identify key words through linking, elision, and reduction in rapid speech"],
        []),
    (11, 66, "Extracting Gist vs Detail",
        ["listening"],
        ["Listen for overall meaning (gist) without needing full word-by-word comprehension",
         "Switch between gist and detail listening modes depending on task requirements"],
        ["Understanding Fast Native Speech"]),
    (11, 67, "Identifying Opinion vs Fact",
        ["listening"],
        ["Distinguish factual statements from expressions of opinion in spoken French",
         "Recognise hedging language, assertion markers, and subjective vocabulary in speech"],
        ["Extracting Gist vs Detail"]),
    (11, 68, "Interpreting Implied Meaning",
        ["listening"],
        ["Infer what is not said explicitly by reading context, tone, and social cues",
         "Identify implication, irony, and understatement in native French speech"],
        ["Identifying Opinion vs Fact"]),
    (11, 69, "Understanding Attitude and Tone",
        ["listening"],
        ["Interpret a speaker's attitude (enthusiastic, sceptical, neutral) from prosody and word choice",
         "Use tone interpretation to guide appropriate responses in real-time conversation"],
        ["Interpreting Implied Meaning"]),
    (11, 70, "Handling Missing Information in Speech",
        ["listening"],
        ["Continue listening and comprehending when key words are missed",
         "Use redundancy, repetition, and inference to reconstruct incomplete input"],
        ["Understanding Fast Native Speech"]),

    # ── Module 47: Linguistic Nuance & Hedging ────────────────────────────────
    (12, 71, "Expressing Uncertainty",
        ["communication"],
        ["Use modal expressions (il se pourrait que, ça m'étonnerait, je ne suis pas sûr que) to convey uncertainty",
         "Select the appropriate level of certainty marker for spoken and written contexts"],
        []),
    (12, 72, "Softening Opinions",
        ["communication"],
        ["Soften opinions using hedges (à mon sens, il me semble, disons que) and mitigation strategies",
         "Reduce the force of assertions to maintain politeness and openness in debate"],
        ["Expressing Uncertainty"]),
    (12, 73, "Degrees of Certainty",
        ["communication"],
        ["Express a spectrum from strong certainty to vague possibility using precise vocabulary",
         "Match certainty expression to the evidence available and the social stakes of the claim"],
        ["Expressing Uncertainty"]),
    (12, 74, "Politeness in Disagreement",
        ["communication"],
        ["Disagree firmly without rudeness using concession-then-contrast structures",
         "Choose politeness-preserving forms for sensitive or high-stakes disagreements"],
        ["Strategic Agreement & Disagreement"]),
    (12, 75, "Emotional Moderation in Speech",
        ["communication"],
        ["Regulate emotional expression in speech to maintain credibility and respect",
         "Use distancing language when discussing emotive topics in professional contexts"],
        ["Softening Opinions"]),
    (12, 76, "Indirect Expression Strategies",
        ["skill"],
        ["Communicate meaning indirectly through implication, understatement, and suggestion",
         "Deploy indirect strategies to navigate sensitive topics without direct confrontation"],
        ["Softening Opinions", "Degrees of Certainty"]),

    # ── Module 48: Society, Media & Abstract Topics ───────────────────────────
    (13, 77, "Media & News Vocabulary",
        ["vocabulary"],
        ["Use precise vocabulary for discussing news sources, journalism, and media bias",
         "Describe and evaluate different media formats and their societal role"],
        []),
    (13, 78, "Workplace Discussions",
        ["communication"],
        ["Discuss professional environments, workplace dynamics, and career development in French",
         "Use formal and semi-formal register appropriately in workplace-themed conversation"],
        ["Strong vs Soft Opinion Expression"]),
    (13, 79, "Education Systems",
        ["communication"],
        ["Compare educational structures, discuss learning experiences, and evaluate teaching methods",
         "Use abstract vocabulary to discuss the purpose and reform of education"],
        []),
    (13, 80, "Environment & Society",
        ["communication"],
        ["Discuss environmental challenges, policy responses, and individual responsibility at B2 depth",
         "Support environmental arguments using abstract reasoning and precise vocabulary"],
        ["Strong vs Soft Opinion Expression"]),
    (13, 81, "Culture & Trends",
        ["communication"],
        ["Discuss cultural shifts, social trends, and their implications in French society",
         "Use nuanced vocabulary to describe and evaluate cultural phenomena"],
        []),
    (13, 82, "Technology in Daily Life",
        ["communication"],
        ["Debate the role of technology in work, relationships, and society with B2 sophistication",
         "Use advanced vocabulary for digital culture, AI, and technological ethics"],
        []),
    (13, 83, "Discussing Abstract Ideas",
        ["skill"],
        ["Articulate philosophical, ethical, and conceptual ideas in clear spoken and written French",
         "Move beyond concrete examples to engage with abstract argumentation fluently"],
        ["Expressing Abstract Reasoning"]),

    # ── Module 49: Real-Time Communication Pressure System ───────────────────
    (14, 84, "Instant Response Drills",
        ["skill"],
        ["Produce immediate, grammatically sound responses to prompts without preparation time",
         "Build automaticity in accessing learned structures under cognitive pressure"],
        ["Maintaining Flow Under Confusion"]),
    (14, 85, "Spontaneous Opinion Formation",
        ["communication"],
        ["Form and express an opinion on an unfamiliar topic in real time",
         "Use scaffolding phrases to buy thinking time while sounding fluent"],
        ["Strong vs Soft Opinion Expression"]),
    (14, 86, "Dialogue Continuation",
        ["skill"],
        ["Continue an unfinished dialogue naturally by inferring context and taking the next turn",
         "Maintain coherence and register when picking up a conversation mid-stream"],
        ["Instant Response Drills"]),
    (14, 87, "Incomplete Input Completion",
        ["skill"],
        ["Respond meaningfully when input is partial, unclear, or heavily accented",
         "Use inference and context to fill gaps and keep the exchange going"],
        ["Dialogue Continuation"]),
    (14, 88, "Reaction-Based Speaking",
        ["skill"],
        ["React authentically to unexpected statements, questions, and provocations in French",
         "Deploy agreement, surprise, doubt, and humour reactions naturally without scripting"],
        ["Incomplete Input Completion", "Spontaneous Opinion Formation"]),
    (14, 89, "Fluency Under Time Pressure",
        ["skill"],
        ["Sustain fluent, accurate French when speaking quickly or under social pressure",
         "Integrate all B2 skills into fully spontaneous, pressure-tested production"],
        ["Reaction-Based Speaking"]),
]


# ─── Spanish A1 curriculum ────────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_SPANISH_A1_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Sounds & Writing System",           "Master the Spanish alphabet, pronunciation rules, and accent marks",                          4),
    (2,  "Core Survival Vocabulary",          "Build essential vocabulary sets for numbers, dates, colours, and everyday objects",           6),
    (3,  "Gender & Noun System",              "Understand masculine and feminine nouns with definite, indefinite articles, and plurals",      4),
    (4,  "Subject Pronouns & Identity",       "Use subject pronouns and build basic self-identification sentences",                          3),
    (5,  "Sentence Construction Basics",      "Form correct Spanish sentences using subject-verb-object structure and word order",           4),
    (6,  "Present Tense Core System",         "Conjugate regular and high-frequency irregular verbs in the present tense",                  10),
    (7,  "Adjectives & Description",          "Use adjectives with correct gender and number agreement and proper placement",                4),
    (8,  "Questions & Negation System",       "Ask questions using interrogative words and form basic negative sentences",                   4),
    (9,  "Prepositions (Functional Use)",     "Use core prepositions en, a, de, con, and para for spatial and directional meaning",         6),
    (10, "Real-Life Communication Scenarios", "Apply Spanish in greetings, food, directions, shopping, and everyday interactions",          12),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives)
_SPANISH_A1_NODES: list[tuple[int, int, str, list, list]] = [

    # ── Module 1: Sounds & Writing System ─────────────────────────────────────
    (1,  1,  "Alphabet (A–Z)",
        ["phonetics"],
        ["Recognise all Spanish letters and their pronunciation differences from English",
         "Produce correct Spanish letter names and sounds in sequence"]),
    (1,  2,  "Accent Marks (á, é, í, ó, ú)",
        ["phonetics"],
        ["Identify the five Spanish accent marks and understand their function",
         "Recognise how accents affect stress and meaning in Spanish words"]),
    (1,  3,  "Basic Pronunciation Rules",
        ["phonetics"],
        ["Apply core Spanish pronunciation rules including ll, rr, ñ, j, and h",
         "Distinguish Spanish phonemes that differ significantly from English equivalents"]),
    (1,  4,  "Sound-to-Letter Mapping",
        ["phonetics"],
        ["Convert spoken Spanish sounds to correct written letters consistently",
         "Read aloud basic Spanish words using learned pronunciation rules"]),

    # ── Module 2: Core Survival Vocabulary ────────────────────────────────────
    (2,  5,  "Numbers 0–20",
        ["vocabulary"],
        ["Count and name numbers 0–20 in Spanish",
         "Use numbers 0–20 in basic spoken and written contexts"]),
    (2,  6,  "Numbers 21–100",
        ["vocabulary"],
        ["Count and name numbers 21–100 including compound forms",
         "Apply numbers to prices, quantities, and ages in simple sentences"]),
    (2,  7,  "Days of the Week",
        ["vocabulary"],
        ["Name all seven days of the week in Spanish",
         "Use days of the week in simple scheduling expressions"]),
    (2,  8,  "Months of the Year",
        ["vocabulary"],
        ["Name all twelve months of the year in Spanish",
         "Express dates using months and numbers in spoken and written form"]),
    (2,  9,  "Colours",
        ["vocabulary"],
        ["Name common colours in Spanish with correct gender agreement",
         "Use colour vocabulary in descriptive sentences"]),
    (2,  10, "Everyday Objects",
        ["vocabulary"],
        ["Name common household, school, and food items in Spanish",
         "Use everyday object vocabulary in simple descriptive and transactional sentences"]),

    # ── Module 3: Gender & Noun System ────────────────────────────────────────
    (3,  11, "Masculine vs Feminine Nouns",
        ["grammar"],
        ["Identify whether a Spanish noun is masculine or feminine",
         "Apply common gender rules and recognise exceptions"]),
    (3,  12, "Definite Articles (el, la, los, las)",
        ["grammar"],
        ["Use el, la, los, and las correctly with nouns",
         "Match definite articles to noun gender and number consistently"]),
    (3,  13, "Indefinite Articles (un, una, unos, unas)",
        ["grammar"],
        ["Use un, una, unos, and unas correctly with nouns",
         "Distinguish between definite and indefinite articles in context"]),
    (3,  14, "Plural Formation",
        ["grammar"],
        ["Form regular noun plurals by adding -s or -es",
         "Recognise common irregular plurals and apply plural articles correctly"]),

    # ── Module 4: Subject Pronouns & Identity ─────────────────────────────────
    (4,  15, "Subject Pronouns",
        ["grammar"],
        ["Identify and use yo, tú, él, ella, nosotros, vosotros, ellos, ellas, usted, ustedes",
         "Match subject pronouns to people and contexts including formal usted"]),
    (4,  16, "Basic Self-Identification",
        ["speaking"],
        ["Introduce yourself with name, age, origin, and nationality using subject pronouns",
         "Build short self-description sentences using ser and basic vocabulary"]),
    (4,  17, "Introduction to Object Pronouns",
        ["grammar"],
        ["Recognise direct object pronouns (me, te, lo, la) in simple sentences",
         "Understand the function of object pronouns without active production"]),

    # ── Module 5: Sentence Construction Basics ────────────────────────────────
    (5,  18, "Subject-Verb-Object Structure",
        ["grammar"],
        ["Understand the default S-V-O word order in Spanish sentences",
         "Build simple sentences by placing subject, verb, and object in correct order"]),
    (5,  19, "Spanish Word Order",
        ["grammar"],
        ["Recognise how Spanish word order differs from English in questions and negation",
         "Adjust word order correctly when forming questions and negative sentences"]),
    (5,  20, "Simple Descriptive Sentences",
        ["grammar"],
        ["Write and say simple sentences describing people, places, and objects",
         "Combine nouns, adjectives, and verbs into clear descriptive statements"]),
    (5,  21, "Affirmative Sentence Building",
        ["skill"],
        ["Construct varied affirmative sentences using different verbs and vocabulary",
         "Produce fluent short sentences without translation hesitation"]),

    # ── Module 6: Present Tense Core System ───────────────────────────────────
    (6,  22, "Regular -ar Verbs",
        ["grammar"],
        ["Conjugate regular -ar verbs in the present tense for all subject pronouns",
         "Use common -ar verbs (hablar, trabajar, escuchar) in sentences"]),
    (6,  23, "Regular -er Verbs",
        ["grammar"],
        ["Conjugate regular -er verbs in the present tense for all subject pronouns",
         "Use common -er verbs (comer, beber, leer) in sentences"]),
    (6,  24, "Regular -ir Verbs",
        ["grammar"],
        ["Conjugate regular -ir verbs in the present tense for all subject pronouns",
         "Use common -ir verbs (vivir, escribir, abrir) in sentences"]),
    (6,  25, "Ser vs Estar (Introduction)",
        ["grammar"],
        ["Understand that Spanish has two verbs for 'to be': ser and estar",
         "Distinguish the core uses of ser (identity, origin) from estar (state, location)"]),
    (6,  26, "Ser",
        ["grammar"],
        ["Conjugate ser in the present tense for all subject pronouns",
         "Use ser to express identity, nationality, profession, and permanent characteristics"]),
    (6,  27, "Estar",
        ["grammar"],
        ["Conjugate estar in the present tense for all subject pronouns",
         "Use estar to express location, feelings, and temporary states"]),
    (6,  28, "Tener",
        ["grammar"],
        ["Conjugate tener in the present tense including the irregular yo form (tengo)",
         "Use tener in common expressions (tener hambre, tener años, tener que)"]),
    (6,  29, "Ir",
        ["grammar"],
        ["Conjugate ir in the present tense (voy, vas, va, vamos, vais, van)",
         "Use ir + a + infinitive to express near-future plans"]),
    (6,  30, "Hacer",
        ["grammar"],
        ["Conjugate hacer in the present tense including the irregular yo form (hago)",
         "Use hacer in common expressions and questions (¿Qué haces?)"]),
    (6,  31, "Poder",
        ["grammar"],
        ["Conjugate poder as a stem-changing verb (puedo, puedes, puede…)",
         "Use poder + infinitive to express ability and possibility"]),

    # ── Module 7: Adjectives & Description ────────────────────────────────────
    (7,  32, "Basic Adjectives",
        ["vocabulary"],
        ["Use common descriptive adjectives for size, appearance, and personality",
         "Select appropriate adjectives to describe people, places, and things"]),
    (7,  33, "Adjective Gender Agreement",
        ["grammar"],
        ["Change adjective endings to agree with masculine and feminine nouns",
         "Recognise adjectives that have the same form for both genders"]),
    (7,  34, "Adjective Number Agreement",
        ["grammar"],
        ["Apply singular and plural forms to adjectives in agreement with nouns",
         "Produce noun-adjective combinations with correct gender and number agreement"]),
    (7,  35, "Adjective Placement",
        ["grammar"],
        ["Place most adjectives after the noun in Spanish",
         "Recognise common adjectives that precede the noun and change meaning by position"]),

    # ── Module 8: Questions & Negation System ─────────────────────────────────
    (8,  36, "Question Words",
        ["grammar"],
        ["Use ¿qué?, ¿quién?, ¿dónde?, ¿cuándo?, ¿cómo?, and ¿por qué? correctly",
         "Form information questions using interrogative words with correct accent marks"]),
    (8,  37, "Yes/No Questions",
        ["grammar"],
        ["Form yes/no questions by inversion or rising intonation in Spanish",
         "Answer yes/no questions using sí, no, and short affirmative or negative responses"]),
    (8,  38, "Basic Negation",
        ["grammar"],
        ["Form negative sentences by placing no before the conjugated verb",
         "Use negation consistently across different verb types and tenses"]),
    (8,  39, "Short Answer Formation",
        ["speaking"],
        ["Give short, natural answers to common questions in Spanish",
         "Avoid over-literal translation by producing idiomatic short responses"]),

    # ── Module 9: Prepositions (Functional Use) ───────────────────────────────
    (9,  40, "Preposition en",
        ["grammar"],
        ["Use en to express location, time, and means of transport",
         "Distinguish en from other location prepositions in context"]),
    (9,  41, "Preposition a",
        ["grammar"],
        ["Use a to express direction, destination, and the personal a",
         "Apply ir + a + place and the personal a before human direct objects"]),
    (9,  42, "Preposition de",
        ["grammar"],
        ["Use de to express origin, possession, and material",
         "Form expressions with ser + de to describe origin and material"]),
    (9,  43, "Preposition con",
        ["grammar"],
        ["Use con to express accompaniment and manner",
         "Build common phrases with con (con leche, con amigos, conmigo)"]),
    (9,  44, "Preposition para",
        ["grammar"],
        ["Use para to express purpose, destination, and recipient",
         "Distinguish para from por in simple, common contexts"]),
    (9,  45, "Spatial vs Directional Prepositions",
        ["grammar"],
        ["Choose the correct preposition to describe static location vs movement",
         "Apply en, a, and de accurately in direction and location sentences"]),

    # ── Module 10: Real-Life Communication Scenarios ──────────────────────────
    (10, 46, "Greetings & Introductions (Vocabulary)",
        ["vocabulary"],
        ["Learn and recognise greetings, farewells, and introductory phrases in Spanish",
         "Identify formal vs informal greeting forms (tú vs usted)"]),
    (10, 47, "Greetings & Introductions (Dialogue)",
        ["speaking"],
        ["Hold a short introductory conversation including name, origin, and occupation",
         "Respond naturally to greetings and introductory questions"]),
    (10, 48, "Ordering Food (Vocabulary)",
        ["vocabulary"],
        ["Name common food and drink items and use restaurant vocabulary in Spanish",
         "Use quisiera and me gustaría to order politely"]),
    (10, 49, "Ordering Food (Dialogue)",
        ["communication"],
        ["Navigate a restaurant interaction from greeting to ordering to paying",
         "Use numbers, quantities, and polite expressions in a food-ordering context"]),
    (10, 50, "Asking for Directions (Vocabulary)",
        ["vocabulary"],
        ["Learn direction vocabulary (izquierda, derecha, recto, cerca, lejos)",
         "Name common location types (la calle, la plaza, el banco, la farmacia)"]),
    (10, 51, "Asking for Directions (Dialogue)",
        ["communication"],
        ["Ask for and give basic directions in Spanish using learned vocabulary",
         "Use prepositions and imperatives to guide someone to a destination"]),
    (10, 52, "Shopping Basics (Vocabulary)",
        ["vocabulary"],
        ["Use shopping vocabulary including item names, prices, and quantities",
         "Apply numbers and colours in a shopping context"]),
    (10, 53, "Shopping Basics (Dialogue)",
        ["communication"],
        ["Navigate a basic shopping interaction asking for items, prices, and quantities",
         "Use ¿Cuánto cuesta?, quiero, and tengo in a transactional dialogue"]),
    (10, 54, "Talking About Yourself (Vocabulary)",
        ["vocabulary"],
        ["Build personal vocabulary for age, nationality, profession, and family",
         "Select the correct vocabulary to describe yourself accurately in Spanish"]),
    (10, 55, "Talking About Yourself (Extended)",
        ["speaking"],
        ["Give an extended self-introduction covering personal details, likes, and daily life",
         "Combine ser, estar, tener, and regular verbs to produce a fluent personal description"]),
    (10, 56, "Polite Expressions (Vocabulary)",
        ["vocabulary"],
        ["Learn essential polite expressions: por favor, gracias, de nada, perdón, disculpe",
         "Recognise the social function of polite language in Spanish interactions"]),
    (10, 57, "Polite Expressions (Dialogue)",
        ["communication"],
        ["Use polite expressions naturally within greetings, requests, and apologies",
         "Avoid common politeness errors made by English speakers in Spanish"]),
]


_SPANISH_A2_MODULES: list[tuple[int, str, str, int]] = [
    (1, "Talking About the Past",           "Master Pretérito Perfecto and Indefinido to discuss past experiences and stories",                      8),
    (2, "Talking About the Future",         "Use ir + a + infinitive and future expressions to discuss plans and predictions",                        7),
    (3, "Daily Life & Reflexive Verbs",     "Use reflexive pronouns and verbs to describe daily routines, habits, and schedules",                    7),
    (4, "Direct & Indirect Objects",        "Use direct and indirect object pronouns to speak more naturally without repeating nouns",                7),
    (5, "Comparisons & Descriptions",       "Compare people, places, and objects using más que, menos que, tan...como, and superlatives",             8),
    (6, "Obligation, Need & Responsibility","Express obligations and needs using tener que, hay que, and necesitar",                                  7),
    (7, "Preferences, Opinions & Wishes",   "Share opinions, preferences, and desires using gustar, querer, preferir, and me gustaría",              8),
    (8, "Expanded Negation",                "Express negative ideas naturally using nunca, nadie, nada, and tampoco",                                8),
    (9, "Connecting Ideas",                 "Build longer, more coherent sentences using porque, pero, entonces, además, and aunque",                9),
    (10, "Building Longer Sentences",        "Use relative pronouns que and donde to create richer, more detailed sentences",                         6),
    (11, "Adverbs & Precision",              "Add precision and detail to communication using frequency, quantity, and manner adverbs",               7),
    (12, "Time & Prepositions",              "Express duration and time relationships using desde, durante, hasta, para, por, hace, and desde hace",  9),
    (13, "Real-Life Situations",             "Function independently in travel, hospitality, social, and everyday service situations",               14),
    (14, "Communication Skills",             "Produce connected speech and writing while understanding everyday Spanish communication",              12),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_SPANISH_A2_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 11: Talking About the Past ────────────────────────────────────────
    (1, 1,  "Pretérito Perfecto",
        ["grammar"],
        ["Form the Pretérito Perfecto using haber + past participle for all subjects",
         "Use the Pretérito Perfecto to describe recent or life experiences"],
        ["Regular -ar Verbs", "Regular -er Verbs", "Regular -ir Verbs"]),
    (1, 2,  "Common Perfecto Participles",
        ["grammar"],
        ["Produce regular and high-frequency irregular past participles",
         "Recognise common irregular participles: hecho, dicho, visto, ido, sido, escrito"],
        ["Pretérito Perfecto"]),
    (1, 3,  "Pretérito Indefinido",
        ["grammar"],
        ["Conjugate regular -ar, -er, and -ir verbs in the Pretérito Indefinido",
         "Use the Pretérito Indefinido for completed past actions with a defined time"],
        ["Regular -ar Verbs", "Regular -er Verbs", "Regular -ir Verbs"]),
    (1, 4,  "Common Irregular Past Forms",
        ["grammar"],
        ["Produce irregular Indefinido forms for ser/ir, tener, hacer, estar, and venir",
         "Apply irregular stems and endings in past-tense sentences"],
        ["Pretérito Indefinido"]),
    (1, 5,  "Pretérito Perfecto vs Indefinido",
        ["grammar"],
        ["Distinguish when to use Pretérito Perfecto versus Pretérito Indefinido by region and time marker",
         "Apply hoy/esta semana (Perfecto) vs ayer/el año pasado (Indefinido) correctly"],
        ["Pretérito Perfecto", "Pretérito Indefinido"]),
    (1, 6,  "Talking About Recent Experiences",
        ["communication"],
        ["Describe things you have done recently using Pretérito Perfecto",
         "Use time markers like hoy, esta semana, and alguna vez in conversation"],
        ["Pretérito Perfecto", "Common Perfecto Participles"]),
    (1, 7,  "Talking About Completed Events",
        ["communication"],
        ["Describe specific completed past events using Pretérito Indefinido",
         "Use past time expressions (ayer, la semana pasada, en 2020) accurately"],
        ["Pretérito Indefinido", "Common Irregular Past Forms"]),
    (1, 8,  "Storytelling in the Past",
        ["communication"],
        ["Narrate a short past event using both past tenses appropriately",
         "Sequence events with linking words (primero, luego, después, finalmente)"],
        ["Pretérito Perfecto vs Indefinido"]),

    # ── Module 12: Talking About the Future ──────────────────────────────────────
    (2, 9,  "Ir + a + Infinitive (Extended)",
        ["grammar"],
        ["Use ir + a + infinitive confidently for plans and intentions in all persons",
         "Combine ir + a + infinitive with a range of verbs beyond A1 level"],
        ["Ir"]),
    (2, 10, "Future Time Expressions",
        ["grammar"],
        ["Use mañana, la semana que viene, el próximo mes, and similar expressions accurately",
         "Combine future time markers with ir + a + infinitive in sentences"],
        ["Ir + a + Infinitive (Extended)", "Days of the Week", "Months of the Year"]),
    (2, 11, "Talking About Intentions",
        ["communication"],
        ["Express personal intentions using ir + a + infinitive and querer + infinitive",
         "Distinguish plans (ir + a) from wishes (querer) in natural conversation"],
        ["Ir + a + Infinitive (Extended)", "Future Time Expressions"]),
    (2, 12, "Talking About Predictions",
        ["communication"],
        ["Make predictions about future events using ir + a + infinitive",
         "Use probability expressions (creo que va a..., seguramente va a...) in speech"],
        ["Ir + a + Infinitive (Extended)"]),
    (2, 13, "Making Plans",
        ["communication"],
        ["Make and discuss plans with others using ir + a + infinitive and future time expressions",
         "Negotiate arrangements including time, place, and activity"],
        ["Ir + a + Infinitive (Extended)", "Future Time Expressions"]),
    (2, 14, "Discussing Future Goals",
        ["communication"],
        ["Talk about personal goals and ambitions using ir + a + infinitive and querer",
         "Produce extended turns about your future plans including reasons"],
        ["Making Plans", "Talking About Intentions"]),
    (2, 15, "Talking About Upcoming Events",
        ["communication"],
        ["Describe scheduled or upcoming events using future expressions",
         "Use event vocabulary (un concierto, una boda, un examen) in context"],
        ["Making Plans", "Future Time Expressions"]),

    # ── Module 13: Daily Life & Reflexive Verbs ───────────────────────────────────
    (3, 16, "Reflexive Pronouns",
        ["grammar"],
        ["Identify and use me, te, se, nos, os, se as reflexive pronouns",
         "Place reflexive pronouns correctly before conjugated verbs or attached to infinitives"],
        ["Subject Pronouns", "Introduction to Object Pronouns"]),
    (3, 17, "Reflexive Verbs",
        ["grammar"],
        ["Conjugate common reflexive verbs (levantarse, ducharse, llamarse) in the present tense",
         "Distinguish reflexive from non-reflexive usage of the same verb"],
        ["Reflexive Pronouns", "Regular -ar Verbs"]),
    (3, 18, "Common Daily Routine Verbs",
        ["vocabulary"],
        ["Name and use daily routine verbs: despertarse, lavarse, vestirse, acostarse, etc.",
         "Apply daily routine vocabulary in simple present-tense descriptions"],
        ["Reflexive Verbs"]),
    (3, 19, "Reflexive Verbs in Context",
        ["grammar"],
        ["Use reflexive verbs in full sentences describing morning and evening routines",
         "Combine reflexive verbs with time expressions and adverbs"],
        ["Reflexive Verbs", "Common Daily Routine Verbs"]),
    (3, 20, "Describing Daily Routines",
        ["communication"],
        ["Describe your own daily routine from morning to night in accurate Spanish",
         "Ask and answer questions about another person's daily routine"],
        ["Reflexive Verbs in Context"]),
    (3, 21, "Describing Habits",
        ["communication"],
        ["Express habitual actions using present tense and frequency adverbs",
         "Contrast your habits with those of others using comparison structures"],
        ["Describing Daily Routines"]),
    (3, 22, "Talking About Schedules",
        ["communication"],
        ["Describe a weekly schedule using days of the week and time expressions",
         "Use tener que and ir + a to discuss planned vs obligatory activities"],
        ["Describing Daily Routines", "Days of the Week"]),

    # ── Module 14: Direct & Indirect Objects ──────────────────────────────────────
    (4, 23, "Direct Object Pronouns",
        ["grammar"],
        ["Use lo, la, los, las as direct object pronouns to replace noun objects",
         "Place direct object pronouns correctly in affirmative, negative, and infinitive constructions"],
        ["Introduction to Object Pronouns", "Subject Pronouns"]),
    (4, 24, "Indirect Object Pronouns",
        ["grammar"],
        ["Use me, te, le, nos, os, les as indirect object pronouns",
         "Identify indirect objects and substitute them with the correct pronoun"],
        ["Direct Object Pronouns"]),
    (4, 25, "Pronoun Placement Rules",
        ["grammar"],
        ["Place direct and indirect object pronouns before conjugated verbs",
         "Attach pronouns to infinitives and present participles where applicable"],
        ["Direct Object Pronouns", "Indirect Object Pronouns"]),
    (4, 26, "Pronouns with Infinitives",
        ["grammar"],
        ["Attach direct and indirect object pronouns to infinitives in verbal constructions",
         "Choose between pre-verb placement and infinitive attachment correctly"],
        ["Pronoun Placement Rules"]),
    (4, 27, "Replacing Repeated Nouns",
        ["communication"],
        ["Replace repeated noun objects with the correct direct or indirect pronoun",
         "Produce natural spoken Spanish by eliminating unnecessary noun repetition"],
        ["Direct Object Pronouns", "Indirect Object Pronouns"]),
    (4, 28, "Giving and Receiving Things",
        ["communication"],
        ["Use indirect object pronouns in giving and receiving contexts (te doy, me das)",
         "Combine direct and indirect pronouns in simple double-pronoun sentences"],
        ["Indirect Object Pronouns", "Replacing Repeated Nouns"]),
    (4, 29, "Talking About People and Objects",
        ["communication"],
        ["Use direct and indirect object pronouns to discuss people and objects in conversation",
         "Produce natural responses to questions without repeating the noun object"],
        ["Direct Object Pronouns", "Indirect Object Pronouns"]),

    # ── Module 15: Comparisons & Descriptions ────────────────────────────────────
    (5, 30, "Más... que (Comparatives)",
        ["grammar"],
        ["Form comparative sentences using más + adjective/adverb + que",
         "Use más que correctly with adjectives, adverbs, and nouns"],
        ["Basic Adjectives", "Adjective Gender Agreement"]),
    (5, 31, "Menos... que",
        ["grammar"],
        ["Form comparative sentences using menos + adjective/adverb + que",
         "Distinguish más que from menos que in comparative structures"],
        ["Más... que (Comparatives)"]),
    (5, 32, "Tan... como (Equality)",
        ["grammar"],
        ["Form equality comparisons using tan + adjective/adverb + como",
         "Use tanto/a/os/as + noun + como for noun-based equality comparisons"],
        ["Más... que (Comparatives)"]),
    (5, 33, "Superlatives",
        ["grammar"],
        ["Form superlatives using el/la/los/las + más/menos + adjective",
         "Use irregular superlatives: el mejor, el peor, el mayor, el menor"],
        ["Más... que (Comparatives)", "Definite Articles (el, la, los, las)"]),
    (5, 34, "Comparing People",
        ["communication"],
        ["Compare two or more people using comparative and superlative structures",
         "Use physical and personality adjectives in comparative sentences"],
        ["Más... que (Comparatives)", "Tan... como (Equality)"]),
    (5, 35, "Comparing Places",
        ["communication"],
        ["Compare cities, countries, and locations using comparatives and superlatives",
         "Produce extended comparisons with multiple adjectives"],
        ["Más... que (Comparatives)", "Superlatives"]),
    (5, 36, "Comparing Objects",
        ["communication"],
        ["Compare products and objects using comparatives and superlatives",
         "Apply comparison structures in shopping and consumer contexts"],
        ["Más... que (Comparatives)", "Menos... que"]),
    (5, 37, "Expressing Opinions Through Comparison",
        ["communication"],
        ["Share opinions by comparing two options or ideas",
         "Use creo que, pienso que, and comparison structures together"],
        ["Comparing People", "Superlatives"]),

    # ── Module 16: Obligation, Need & Responsibility ──────────────────────────────
    (6, 38, "Tener que + Infinitive",
        ["grammar"],
        ["Use tener que + infinitive to express personal obligation",
         "Conjugate tener correctly in all persons before using the construction"],
        ["Tener", "Regular -ar Verbs"]),
    (6, 39, "Hay que + Infinitive",
        ["grammar"],
        ["Use the impersonal hay que + infinitive to express general necessity",
         "Distinguish hay que (impersonal) from tener que (personal obligation)"],
        ["Tener que + Infinitive"]),
    (6, 40, "Necesitar",
        ["grammar"],
        ["Conjugate and use necesitar + infinitive or noun to express need",
         "Apply necesitar in personal statements about requirements and desires"],
        ["Regular -ar Verbs", "Tener que + Infinitive"]),
    (6, 41, "Talking About Responsibilities",
        ["communication"],
        ["Describe your personal and professional responsibilities using tener que",
         "Ask about and understand others' obligations in conversation"],
        ["Tener que + Infinitive", "Hay que + Infinitive"]),
    (6, 42, "Explaining Requirements",
        ["communication"],
        ["Explain rules, requirements, and conditions using hay que and necesitar",
         "Describe what is needed for a task, trip, or event"],
        ["Hay que + Infinitive", "Necesitar"]),
    (6, 43, "Discussing Personal Needs",
        ["communication"],
        ["Express and discuss your personal needs and necessities",
         "Combine necesitar and tener que with a range of infinitives"],
        ["Necesitar", "Talking About Responsibilities"]),
    (6, 44, "Giving Basic Advice",
        ["communication"],
        ["Give simple advice using hay que, debes, and tienes que",
         "Respond to problems by offering practical suggestions in Spanish"],
        ["Hay que + Infinitive", "Explaining Requirements"]),

    # ── Module 17: Preferences, Opinions & Wishes ────────────────────────────────
    (7, 45, "Gustar (Expanded Usage)",
        ["grammar"],
        ["Use gustar with all indirect object pronouns (me, te, le, nos, os, les)",
         "Apply gustar with nouns and infinitives in statements and questions"],
        ["Ordering Food (Dialogue)", "Adjective Gender Agreement"]),
    (7, 46, "Querer + Infinitive",
        ["grammar"],
        ["Use querer + infinitive to express desires and wants",
         "Conjugate querer correctly including the stem change e→ie"],
        ["Regular -er Verbs"]),
    (7, 47, "Preferir (Stem-Changing)",
        ["grammar"],
        ["Conjugate the stem-changing verb preferir (e→ie) in the present tense",
         "Use preferir to express preferences between two or more options"],
        ["Poder", "Regular -ir Verbs"]),
    (7, 48, "Me gustaría",
        ["grammar"],
        ["Use me gustaría + infinitive to make polite wishes and requests",
         "Distinguish me gustaría (conditional wish) from me gusta (present preference)"],
        ["Gustar (Expanded Usage)", "Polite Expressions (Vocabulary)"]),
    (7, 49, "Giving Opinions",
        ["communication"],
        ["Express opinions using creo que, pienso que, and en mi opinión",
         "Support opinions with simple reasons using porque"],
        ["Gustar (Expanded Usage)", "Querer + Infinitive"]),
    (7, 50, "Expressing Preferences",
        ["communication"],
        ["State preferences and explain why using preferir, gustar, and comparison structures",
         "Compare two options and express a preference clearly"],
        ["Preferir (Stem-Changing)", "Gustar (Expanded Usage)"]),
    (7, 51, "Expressing Wishes",
        ["communication"],
        ["Express wishes and desires using querer + infinitive and me gustaría",
         "Talk about things you would like to do, have, or experience"],
        ["Me gustaría", "Querer + Infinitive"]),
    (7, 52, "Making Polite Requests",
        ["communication"],
        ["Make polite requests using me gustaría, ¿podría?, and ¿puede usted?",
         "Navigate formal and informal request contexts appropriately"],
        ["Me gustaría", "Polite Expressions (Dialogue)"]),

    # ── Module 18: Expanded Negation ─────────────────────────────────────────────
    (8, 53, "Nunca (Frequency Adverb)",
        ["grammar"],
        ["Use nunca before or after the verb to express never in Spanish",
         "Understand the double negation rule: no + verb + nunca vs nunca + verb"],
        ["Basic Negation"]),
    (8, 54, "Nadie",
        ["grammar"],
        ["Use nadie as a negative subject or object to mean nobody",
         "Apply double negation with no + verb + nadie correctly"],
        ["Basic Negation", "Subject Pronouns"]),
    (8, 55, "Nada",
        ["grammar"],
        ["Use nada as a negative object to mean nothing",
         "Form sentences with no + verb + nada and nada + verb"],
        ["Basic Negation", "Everyday Objects"]),
    (8, 56, "Tampoco",
        ["grammar"],
        ["Use tampoco to express neither/not either in responses and statements",
         "Apply tampoco correctly after negative statements to agree negatively"],
        ["Basic Negation", "Nunca (Frequency Adverb)"]),
    (8, 57, "Expressing Absence",
        ["communication"],
        ["Express the absence of people and things using nadie and nada",
         "Produce natural negative responses to questions about who and what"],
        ["Nadie", "Nada"]),
    (8, 58, "Disagreeing Naturally",
        ["communication"],
        ["Disagree with statements using no, tampoco, and negative word combinations",
         "Respond to positive statements with appropriate negative counterparts"],
        ["Tampoco", "Basic Negation"]),
    (8, 59, "Correcting Information",
        ["communication"],
        ["Correct false or mistaken information using no... sino and negative structures",
         "Clarify misunderstandings in conversation with confidence"],
        ["Disagreeing Naturally", "Nadie"]),
    (8, 60, "Talking About What Does Not Exist",
        ["communication"],
        ["Describe the absence or non-existence of things using nada, nadie, and no hay",
         "Respond to questions about availability or presence with correct negation"],
        ["Nada", "Nadie"]),

    # ── Module 19: Connecting Ideas ───────────────────────────────────────────────
    (9, 61, "Porque (Because)",
        ["grammar"],
        ["Use porque to connect a statement with its reason",
         "Construct answer sentences using porque in response to ¿por qué? questions"],
        ["Affirmative Sentence Building", "Question Words"]),
    (9, 62, "Pero (But)",
        ["grammar"],
        ["Use pero to contrast two ideas within or across sentences",
         "Distinguish pero (contrast) from sino (replacement) in basic usage"],
        ["Affirmative Sentence Building"]),
    (9, 63, "Entonces (So/Then)",
        ["grammar"],
        ["Use entonces to show a logical consequence or to sequence events",
         "Apply entonces at the start of a clause to link cause and effect"],
        ["Porque (Because)"]),
    (9, 64, "Además (Furthermore)",
        ["grammar"],
        ["Use además to add supplementary information to a statement",
         "Produce compound sentences with además to strengthen an argument or description"],
        ["Entonces (So/Then)"]),
    (9, 65, "Aunque (Basic Concession)",
        ["grammar"],
        ["Use aunque + indicative to introduce a concession (even though/although)",
         "Distinguish aunque from pero in contrastive usage"],
        ["Pero (But)", "Affirmative Sentence Building"]),
    (9, 66, "Explaining Reasons",
        ["communication"],
        ["Answer ¿por qué? questions with full because-clauses using porque",
         "Give reasons for plans, opinions, and decisions in extended speech"],
        ["Porque (Because)"]),
    (9, 67, "Contrasting Ideas",
        ["communication"],
        ["Present two contrasting points using pero and aunque in conversation",
         "Use contrast connectors to add nuance to opinions and descriptions"],
        ["Pero (But)", "Aunque (Basic Concession)"]),
    (9, 68, "Showing Consequences",
        ["communication"],
        ["Link actions and their results using entonces and por eso",
         "Build cause-and-effect chains in storytelling and explanation"],
        ["Entonces (So/Then)"]),
    (9, 69, "Adding Information",
        ["communication"],
        ["Expand sentences by adding extra information using además and también",
         "Produce multi-clause sentences that flow naturally"],
        ["Además (Furthermore)", "Explaining Reasons"]),

    # ── Module 20: Building Longer Sentences ─────────────────────────────────────
    (10, 70, "Relative Pronoun Que",
        ["grammar"],
        ["Use que to introduce relative clauses modifying people and things",
         "Combine two short sentences into one using que as a connector"],
        ["Spanish Word Order", "Subject-Verb-Object Structure"]),
    (10, 71, "Relative Pronoun Donde",
        ["grammar"],
        ["Use donde to introduce relative clauses describing places",
         "Distinguish que (person/thing) from donde (place) in relative clauses"],
        ["Relative Pronoun Que", "Preposition en"]),
    (10, 72, "Describing People with Que",
        ["communication"],
        ["Describe people using relative clauses: la persona que trabaja, el hombre que tiene...",
         "Produce natural descriptions by embedding information in relative clauses"],
        ["Relative Pronoun Que", "Basic Adjectives"]),
    (10, 73, "Describing Places with Donde",
        ["communication"],
        ["Describe locations using relative clauses with donde",
         "Combine place descriptions with additional information clauses"],
        ["Relative Pronoun Donde"]),
    (10, 74, "Connecting Multiple Ideas",
        ["communication"],
        ["Build multi-clause sentences combining connectors and relative clauses",
         "Produce fluent sentences that link more than two pieces of information"],
        ["Relative Pronoun Que", "Porque (Because)", "Pero (But)"]),
    (10, 75, "Creating Detailed Descriptions",
        ["communication"],
        ["Write and say detailed descriptions of people, places, and situations",
         "Use relative clauses, adjectives, and connectors together in extended descriptions"],
        ["Describing People with Que", "Describing Places with Donde"]),

    # ── Module 21: Adverbs & Precision ───────────────────────────────────────────
    (11, 76, "Frequency Adverbs (Siempre, A menudo, Nunca)",
        ["grammar"],
        ["Use siempre, a menudo, a veces, and nunca to express frequency",
         "Place frequency adverbs correctly in sentences relative to the verb"],
        ["Affirmative Sentence Building", "Nunca (Frequency Adverb)"]),
    (11, 77, "Quantity Adverbs (Mucho, Poco, Bastante)",
        ["grammar"],
        ["Use mucho, poco, bastante, and demasiado to quantify verbs and adjectives",
         "Distinguish mucho as adverb (invariable) from mucho as adjective (variable)"],
        ["Affirmative Sentence Building", "Numbers 0–20"]),
    (11, 78, "Manner Adverbs (Rápidamente, Lentamente)",
        ["grammar"],
        ["Form manner adverbs by adding -mente to the feminine adjective form",
         "Use common manner adverbs to describe how an action is performed"],
        ["Adjective Gender Agreement"]),
    (11, 79, "Describing Habits with Adverbs",
        ["communication"],
        ["Enrich descriptions of habits and routines by adding frequency adverbs",
         "Produce natural answers to ¿con qué frecuencia? questions"],
        ["Frequency Adverbs (Siempre, A menudo, Nunca)", "Describing Daily Routines"]),
    (11, 80, "Adding Detail with Adverbs",
        ["communication"],
        ["Add quantity and manner adverbs to existing sentences for precision",
         "Transform basic sentences into richer descriptions using adverbs"],
        ["Quantity Adverbs (Mucho, Poco, Bastante)", "Manner Adverbs (Rápidamente, Lentamente)"]),
    (11, 81, "Expressing Quantity",
        ["communication"],
        ["Express how much or how many using quantity adverbs in real contexts",
         "Use bastante, demasiado, and suficiente in practical communication"],
        ["Quantity Adverbs (Mucho, Poco, Bastante)"]),
    (11, 82, "Modifying Actions",
        ["communication"],
        ["Use manner adverbs to describe how actions are done in conversation",
         "Combine adverbs with verbs to produce more expressive and accurate Spanish"],
        ["Manner Adverbs (Rápidamente, Lentamente)", "Adding Detail with Adverbs"]),

    # ── Module 22: Time & Prepositions ────────────────────────────────────────────
    (12, 83, "Desde (Since/From)",
        ["grammar"],
        ["Use desde to express a starting point in time or space",
         "Combine desde with time expressions to say how long something has been happening"],
        ["Preposition de", "Days of the Week"]),
    (12, 84, "Durante (During)",
        ["grammar"],
        ["Use durante to express a duration of time for a completed action",
         "Distinguish durante (completed duration) from desde hace (ongoing duration)"],
        ["Preposition en"]),
    (12, 85, "Hasta (Until/Up to)",
        ["grammar"],
        ["Use hasta to express a time or spatial endpoint",
         "Combine desde and hasta to express time spans (desde las 3 hasta las 5)"],
        ["Desde (Since/From)"]),
    (12, 86, "Para (Purpose & Deadline)",
        ["grammar"],
        ["Use para to express purpose (para estudiar) and deadline (para el lunes)",
         "Distinguish para from por in purpose and exchange contexts"],
        ["Preposition para"]),
    (12, 87, "Por (Exchange & Duration)",
        ["grammar"],
        ["Use por to express exchange, cause, and duration (por dos horas)",
         "Apply por in common fixed expressions (por favor, por eso, por fin)"],
        ["Preposition para"]),
    (12, 88, "Hace + Time",
        ["grammar"],
        ["Use hace + time expression + que to express how long ago something happened",
         "Form hace + time to answer ¿cuánto tiempo hace que...? questions"],
        ["Hacer", "Numbers 21–100"]),
    (12, 89, "Desde hace (Duration)",
        ["grammar"],
        ["Use desde hace + time to express how long something has been happening",
         "Distinguish desde hace (ongoing) from hace que (completed past)"],
        ["Desde (Since/From)", "Hace + Time"]),
    (12, 90, "Talking About Duration",
        ["communication"],
        ["Express how long activities last or have lasted using hace, desde hace, and durante",
         "Answer ¿cuánto tiempo llevas...? and similar duration questions naturally"],
        ["Hace + Time", "Desde hace (Duration)", "Durante (During)"]),
    (12, 91, "Talking About Time Relationships",
        ["communication"],
        ["Express start points, endpoints, and deadlines accurately using desde, hasta, and para",
         "Describe schedules, plans, and events using multiple time prepositions"],
        ["Desde (Since/From)", "Hasta (Until/Up to)", "Para (Purpose & Deadline)"]),

    # ── Module 23: Real-Life Situations ──────────────────────────────────────────
    (13, 92,  "Travel & Transport Vocabulary",
        ["vocabulary"],
        ["Use vocabulary for transport types, tickets, and travel actions in Spanish",
         "Name common travel locations (la estación, el aeropuerto, la parada)"],
        ["Asking for Directions (Vocabulary)", "Ir"]),
    (13, 93,  "Hotel Interactions",
        ["communication"],
        ["Navigate a hotel check-in and check-out interaction in Spanish",
         "Ask about room availability, price, and facilities using learned structures"],
        ["Travel & Transport Vocabulary", "Polite Expressions (Dialogue)"]),
    (13, 94,  "Restaurant Interactions (Extended)",
        ["communication"],
        ["Handle a full restaurant interaction including ordering, asking questions, and paying",
         "Use me gustaría, ¿tienen?, and quisiera in a formal dining context"],
        ["Ordering Food (Dialogue)", "Me gustaría"]),
    (13, 95,  "Shopping (Extended)",
        ["communication"],
        ["Navigate extended shopping interactions including complaints, returns, and bargaining",
         "Use direct object pronouns to refer to products without repetition"],
        ["Shopping Basics (Dialogue)", "Direct Object Pronouns"]),
    (13, 96,  "Healthcare Basics",
        ["communication"],
        ["Describe symptoms and health problems using tener + pain expressions",
         "Understand and use basic healthcare vocabulary (el médico, la farmacia, me duele)"],
        ["Basic Self-Identification", "Tener que + Infinitive"]),
    (13, 97,  "Telephone Conversations",
        ["communication"],
        ["Open, conduct, and close a basic phone conversation in Spanish",
         "Use telephone-specific phrases (¿Diga?, un momento, le llamo más tarde)"],
        ["Polite Expressions (Dialogue)", "Giving and Receiving Things"]),
    (13, 98,  "Asking for Information",
        ["communication"],
        ["Ask for information about places, events, and services using question words and relative clauses",
         "Formulate clear, polite information requests in varied real-life contexts"],
        ["Question Words", "Relative Pronoun Que"]),
    (13, 99,  "Asking for Help",
        ["communication"],
        ["Request assistance in different contexts using ¿me puede ayudar?, necesito, and tener que",
         "Respond to and offer help naturally in everyday Spanish situations"],
        ["Polite Expressions (Dialogue)", "Tener que + Infinitive"]),
    (13, 100, "Making Appointments",
        ["communication"],
        ["Schedule appointments using days, dates, times, and future expressions",
         "Confirm, change, and cancel arrangements in spoken and written Spanish"],
        ["Days of the Week", "Months of the Year", "Talking About Schedules"]),
    (13, 101, "Accepting Invitations",
        ["communication"],
        ["Accept invitations naturally using claro que sí, con mucho gusto, and me encantaría",
         "Ask clarifying questions about an invitation before accepting"],
        ["Making Plans", "Polite Expressions (Dialogue)"]),
    (13, 102, "Declining Invitations",
        ["communication"],
        ["Decline invitations politely using lo siento, no puedo, and tener que",
         "Give brief reasons for declining without sounding rude"],
        ["Accepting Invitations", "Disagreeing Naturally"]),
    (13, 103, "Making Suggestions",
        ["communication"],
        ["Make suggestions using ¿por qué no...?, ¿qué tal si...?, and hay que",
         "Respond to suggestions positively and negatively in group discussions"],
        ["Hay que + Infinitive", "Making Plans"]),
    (13, 104, "Arranging Activities",
        ["communication"],
        ["Negotiate and finalise plans for shared activities including time, place, and participants",
         "Use future expressions, polite requests, and obligation structures together"],
        ["Making Plans", "Talking About Schedules"]),
    (13, 105, "Social Interaction in Context",
        ["communication"],
        ["Handle a range of social situations from meeting to farewell in natural Spanish",
         "Combine learned structures for invitations, suggestions, and arrangements smoothly"],
        ["Accepting Invitations", "Making Suggestions"]),

    # ── Module 24: Communication Skills ──────────────────────────────────────────
    (14, 106, "Storytelling Practice",
        ["speaking"],
        ["Narrate a personal story or past event using both past tenses and sequencing connectors",
         "Sustain a spoken narrative for at least 6–8 sentences with logical flow"],
        ["Storytelling in the Past", "Connecting Multiple Ideas"]),
    (14, 107, "Describing Experiences Orally",
        ["speaking"],
        ["Describe personal experiences using past tenses, adjectives, and relative clauses",
         "Respond to follow-up questions about experiences with detail"],
        ["Talking About Completed Events", "Creating Detailed Descriptions"]),
    (14, 108, "Giving Opinions (Extended)",
        ["speaking"],
        ["Express and justify opinions using creo que, pienso que, and porque in extended turns",
         "Agree and disagree politely with other opinions in conversation"],
        ["Giving Opinions", "Expressing Opinions Through Comparison"]),
    (14, 109, "Making Comparisons in Speech",
        ["speaking"],
        ["Make multi-point comparisons of people, places, and experiences in spoken Spanish",
         "Use comparatives and superlatives together in natural conversation"],
        ["Comparing People", "Comparing Places"]),
    (14, 110, "Discussing Plans in Detail",
        ["speaking"],
        ["Discuss future plans in detail including who, what, when, where, and why",
         "Combine future structures, time expressions, and reasons in extended speech"],
        ["Discussing Future Goals", "Talking About Upcoming Events"]),
    (14, 111, "Writing Informal Emails",
        ["writing"],
        ["Write an informal email including greeting, body paragraphs, and sign-off in Spanish",
         "Use connectors (además, pero, porque) to produce a cohesive written text"],
        ["Explaining Reasons", "Adding Information"]),
    (14, 112, "Writing Short Messages",
        ["writing"],
        ["Write short informal messages (WhatsApp, SMS) in natural Spanish",
         "Use appropriate informal register and common text conventions in Spanish"],
        ["Writing Informal Emails"]),
    (14, 113, "Writing Short Narratives",
        ["writing"],
        ["Write a short narrative paragraph about a past event using past tenses",
         "Sequence events with linking words and include descriptive details"],
        ["Storytelling Practice", "Writing Informal Emails"]),
    (14, 114, "Describing Personal Experiences in Writing",
        ["writing"],
        ["Write a structured personal account using past tenses, adjectives, and connectors",
         "Include a beginning, middle, and end in a short written narrative"],
        ["Writing Short Narratives", "Describing Experiences Orally"]),
    (14, 115, "Understanding Slow Native Speech",
        ["listening"],
        ["Identify key words and phrases when listening to slow, clear Spanish speech",
         "Extract the main topic and supporting details from a short spoken passage"],
        ["Greetings & Introductions (Dialogue)", "Ordering Food (Dialogue)"]),
    (14, 116, "Identifying Main Ideas",
        ["listening"],
        ["Identify the main idea and key supporting points in a short audio passage",
         "Distinguish main information from details and background when listening"],
        ["Understanding Slow Native Speech"]),
    (14, 117, "Following Everyday Conversations",
        ["listening"],
        ["Follow the thread of an everyday conversation between two or more speakers",
         "Understand greetings, transitions, and conclusions in natural spoken Spanish"],
        ["Identifying Main Ideas", "Giving Opinions (Extended)"]),
]


_SPANISH_B1_MODULES: list[tuple[int, str, str, int]] = [
    (1, "Mastering Past Tenses",         "Master Pretérito Imperfecto and Pluscuamperfecto to narrate events, describe situations, and tell coherent stories",          9),
    (2, "Future & Conditional",           "Use Futuro Simple and Conditional Present to discuss plans, predictions, and hypothetical situations",                       8),
    (3, "Subjunctive Foundations",        "Express emotions, doubt, desire, and necessity using the present subjunctive mood",                                          8),
    (4, "Relative Clauses (Extended)",    "Build complex connected sentences using a full range of relative pronouns including quien and cuyo",                         5),
    (5, "Reported Speech",                "Accurately relay conversations, statements, and requests using reported speech and tense backshifting",                      5),
    (6, "Pronoun Expansion",              "Use double object pronouns fluently to avoid repetition and speak more naturally",                                           6),
    (7, "Connectors & Flow",              "Use a rich range of discourse connectors to speak and write fluently and cohesively",                                        6),
    (8, "Opinions & Argumentation",       "Express, justify, and defend opinions clearly and naturally in discussion contexts",                                         6),
    (9, "Society & Topics",               "Discuss real-world themes including education, work, technology, travel, and society",                                       6),
    (10, "Real-World Communication",       "Function independently in daily life by making complaints, negotiating, and solving practical problems",                     6),
    (11, "Writing Skills",                 "Produce structured multi-paragraph written texts across informal, formal, narrative, and opinion registers",                 6),
    (12, "Extended Conversation",          "Sustain extended conversations on varied topics with natural flow and effective conversation management skills",              6),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_SPANISH_B1_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 25: Mastering Past Tenses ─────────────────────────────────────
    (1, 1,  "Pretérito Indefinido Review",
        ["grammar"],
        ["Review and consolidate regular and irregular Pretérito Indefinido conjugations",
         "Use Pretérito Indefinido confidently for completed past actions in extended speech"],
        ["Pretérito Indefinido", "Common Irregular Past Forms"]),
    (1, 2,  "Advanced Uses of Pretérito Indefinido",
        ["grammar"],
        ["Apply Pretérito Indefinido in complex sentences including sequential narration",
         "Use irregular Indefinido verbs (querer, poder, saber) with their past-specific meanings"],
        ["Pretérito Indefinido Review"]),
    (1, 3,  "Pretérito Imperfecto (Core Usage)",
        ["grammar"],
        ["Conjugate all regular and common irregular verbs in the Pretérito Imperfecto",
         "Use the Imperfecto for ongoing past states, habitual past actions, and background descriptions"],
        ["Regular -ar Verbs", "Regular -er Verbs", "Regular -ir Verbs"]),
    (1, 4,  "Habitual Actions in the Past",
        ["grammar"],
        ["Use Pretérito Imperfecto to describe actions that used to happen regularly in the past",
         "Apply time expressions (antes, cuando era niño, siempre que) with the Imperfecto"],
        ["Pretérito Imperfecto (Core Usage)"]),
    (1, 5,  "Background Descriptions in the Past",
        ["grammar"],
        ["Use Pretérito Imperfecto to set the scene and provide background in past narratives",
         "Contrast the descriptive function of Imperfecto with the event function of Indefinido"],
        ["Pretérito Imperfecto (Core Usage)"]),
    (1, 6,  "Indefinido vs Imperfecto Comparison",
        ["grammar"],
        ["Distinguish and correctly use Indefinido (completed events) vs Imperfecto (background/habit) in narration",
         "Identify the correct tense trigger from context and time expressions in complex sentences"],
        ["Advanced Uses of Pretérito Indefinido", "Pretérito Imperfecto (Core Usage)"]),
    (1, 7,  "Storytelling with Mixed Past Tenses",
        ["communication"],
        ["Narrate a coherent story combining Indefinido for events and Imperfecto for background and habit",
         "Produce a sustained narrative of 8–10 sentences using both past tenses accurately"],
        ["Indefinido vs Imperfecto Comparison"]),
    (1, 8,  "Pluscuamperfecto (Introduction)",
        ["grammar"],
        ["Form the Pluscuamperfecto using imperfect haber + past participle",
         "Use the Pluscuamperfecto to express actions completed before another past event"],
        ["Common Perfecto Participles", "Pretérito Indefinido Review"]),
    (1, 9,  "Sequencing Events in Narratives",
        ["communication"],
        ["Sequence past events clearly using the three past tenses and sequence connectors",
         "Use antes de que, después de que, cuando, and ya había to order events precisely"],
        ["Storytelling with Mixed Past Tenses", "Pluscuamperfecto (Introduction)"]),

    # ── Module 26: Future & Conditional ──────────────────────────────────────
    (2, 10, "Futuro Simple Formation",
        ["grammar"],
        ["Form the Futuro Simple for all regular verbs using the infinitive + future endings",
         "Distinguish Futuro Simple (prediction/certainty) from ir + a + infinitive (planned intention)"],
        ["Ir + a + Infinitive (Extended)"]),
    (2, 11, "Regular Future Forms",
        ["grammar"],
        ["Conjugate all regular -ar, -er, and -ir verbs in the Futuro Simple across all persons",
         "Use regular Futuro Simple forms in predictions and future statements"],
        ["Futuro Simple Formation"]),
    (2, 12, "Irregular Future Forms",
        ["grammar"],
        ["Produce irregular future stems for high-frequency verbs (tener, poder, venir, hacer, decir, saber)",
         "Apply irregular future stems with standard future endings correctly"],
        ["Regular Future Forms"]),
    (2, 13, "Making Predictions",
        ["communication"],
        ["Make confident predictions about the future using Futuro Simple",
         "Use probability expressions (supongo que, creo que, seguramente) with Futuro Simple"],
        ["Regular Future Forms", "Irregular Future Forms"]),
    (2, 14, "Conditional Present Formation",
        ["grammar"],
        ["Form the Conditional Present using the infinitive + conditional endings for all verbs",
         "Produce irregular conditional stems (the same as future irregulars) correctly"],
        ["Regular Future Forms"]),
    (2, 15, "Giving Advice with Conditional",
        ["communication"],
        ["Give advice using yo que tú/él, debería, and podría + infinitive",
         "Respond to problems with polite conditional suggestions in conversation"],
        ["Conditional Present Formation", "Giving Basic Advice"]),
    (2, 16, "Hypothetical Situations (Si Clauses)",
        ["grammar"],
        ["Form Type 1 si clauses using si + present + future to express real conditions",
         "Produce both clauses of a conditional sentence accurately in speech and writing"],
        ["Conditional Present Formation", "Futuro Simple Formation"]),
    (2, 17, "Future vs Conditional Contrast",
        ["communication"],
        ["Distinguish future (what will happen) from conditional (what would happen) in context",
         "Switch naturally between Futuro Simple and Conditional Present in conversation"],
        ["Making Predictions", "Conditional Present Formation"]),

    # ── Module 27: Subjunctive Foundations ───────────────────────────────────
    (3, 18, "What Is the Subjunctive?",
        ["grammar"],
        ["Understand the function of the subjunctive as a mood expressing subjectivity rather than fact",
         "Identify contexts that trigger the subjunctive versus the indicative mood"],
        ["Affirmative Sentence Building", "Spanish Word Order"]),
    (3, 19, "Present Subjunctive Formation",
        ["grammar"],
        ["Form the present subjunctive for all regular verbs using the yo-form stem flip rule",
         "Produce subjunctive forms for common irregular verbs (ser, ir, haber, estar, saber)"],
        ["What Is the Subjunctive?", "Regular -ar Verbs", "Regular -er Verbs", "Regular -ir Verbs"]),
    (3, 20, "Expressing Desire with Subjunctive",
        ["grammar"],
        ["Use querer que, desear que, and esperar que + subjunctive to express desire",
         "Distinguish querer + infinitive (same subject) from querer que + subjunctive (different subject)"],
        ["Present Subjunctive Formation", "Querer + Infinitive"]),
    (3, 21, "Expressing Emotion with Subjunctive",
        ["grammar"],
        ["Use emotion verbs (alegrarse de que, sentir que, sorprender que) + subjunctive",
         "Construct sentences expressing feelings about others' actions using the subjunctive"],
        ["Present Subjunctive Formation"]),
    (3, 22, "Expressing Necessity with Subjunctive",
        ["grammar"],
        ["Use impersonal expressions (es necesario que, es importante que) + subjunctive",
         "Compare hay que + infinitive (impersonal) with es necesario que + subjunctive (personal)"],
        ["Present Subjunctive Formation", "Hay que + Infinitive"]),
    (3, 23, "Expressing Doubt with Subjunctive",
        ["grammar"],
        ["Use dudar que, no creer que, and no estar seguro de que + subjunctive to express doubt",
         "Contrast doubt triggers (subjunctive) with certainty triggers (indicative)"],
        ["Present Subjunctive Formation"]),
    (3, 24, "Expressing Recommendations with Subjunctive",
        ["grammar"],
        ["Use recomendar que, sugerir que, and aconsejar que + subjunctive for recommendations",
         "Apply recommendation structures naturally in giving and receiving advice contexts"],
        ["Expressing Necessity with Subjunctive", "Giving Basic Advice"]),
    (3, 25, "Indicative vs Subjunctive Contrast",
        ["grammar"],
        ["Identify and apply the correct mood (indicative or subjunctive) based on trigger verbs and expressions",
         "Produce pairs of sentences demonstrating the indicative/subjunctive contrast clearly"],
        ["Present Subjunctive Formation", "Expressing Doubt with Subjunctive"]),

    # ── Module 28: Relative Clauses (Extended) ────────────────────────────────
    (4, 26, "Relative Pronoun QUE (Extended)",
        ["grammar"],
        ["Use que to introduce relative clauses for both people and things at a B1 level of complexity",
         "Embed multiple relative clauses within a single sentence naturally"],
        ["Relative Pronoun Que"]),
    (4, 27, "Relative Pronoun QUIEN",
        ["grammar"],
        ["Use quien/quienes exclusively with people to introduce relative clauses",
         "Distinguish que (people and things) from quien (people only) in relative clause usage"],
        ["Relative Pronoun QUE (Extended)"]),
    (4, 28, "Relative Pronoun DONDE (Extended)",
        ["grammar"],
        ["Use donde in relative clauses to describe locations with precision",
         "Combine donde clauses with other relative pronouns in complex sentences"],
        ["Relative Pronoun Donde"]),
    (4, 29, "Relative Pronoun CUYO",
        ["grammar"],
        ["Use cuyo/cuya/cuyos/cuyas as a relative possessive pronoun agreeing with the noun it modifies",
         "Produce sentences using cuyo in formal and written Spanish correctly"],
        ["Relative Pronoun QUIEN"]),
    (4, 30, "Combining Relative Clauses in Speech",
        ["communication"],
        ["Build complex spoken sentences combining multiple relative pronouns naturally",
         "Use relative clauses to describe people, places, and things in extended conversation"],
        ["Relative Pronoun QUE (Extended)", "Relative Pronoun QUIEN", "Relative Pronoun DONDE (Extended)"]),

    # ── Module 29: Reported Speech ────────────────────────────────────────────
    (5, 31, "Reporting Statements",
        ["grammar"],
        ["Report what someone said using decir que + indicative clause",
         "Construct reported statements accurately with appropriate tense and pronoun changes"],
        ["Creating Detailed Descriptions", "Storytelling with Mixed Past Tenses"]),
    (5, 32, "Reporting Questions",
        ["grammar"],
        ["Report yes/no questions using preguntar si and open questions using preguntar + question word",
         "Apply correct word order in reported questions without question marks"],
        ["Reporting Statements", "Question Words"]),
    (5, 33, "Basic Tense Backshifting",
        ["grammar"],
        ["Apply basic tense backshifting rules when the reporting verb is in a past tense",
         "Shift present → imperfect, Indefinido → Pluscuamperfecto in reported clauses"],
        ["Reporting Statements", "Indefinido vs Imperfecto Comparison"]),
    (5, 34, "Reporting Requests",
        ["grammar"],
        ["Report requests and instructions using pedir que + subjunctive",
         "Relay reported requests accurately shifting imperative forms to subjunctive"],
        ["Basic Tense Backshifting", "Making Polite Requests"]),
    (5, 35, "Natural Reported Speech in Conversation",
        ["communication"],
        ["Use reported speech naturally in conversation to relay what others have said or asked",
         "Switch fluently between direct and reported speech in storytelling contexts"],
        ["Reporting Questions", "Reporting Requests"]),

    # ── Module 30: Pronoun Expansion ──────────────────────────────────────────
    (6, 36, "Direct Object Pronouns Review",
        ["grammar"],
        ["Review and consolidate direct object pronoun usage (lo, la, los, las) at B1 level",
         "Use direct object pronouns fluently in complex sentences with multiple clauses"],
        ["Direct Object Pronouns"]),
    (6, 37, "Indirect Object Pronouns Review",
        ["grammar"],
        ["Review and consolidate indirect object pronoun usage (me, te, le, nos, os, les) at B1 level",
         "Use indirect object pronouns in communicative contexts without hesitation"],
        ["Indirect Object Pronouns"]),
    (6, 38, "Double Object Pronouns",
        ["grammar"],
        ["Combine direct and indirect object pronouns in the correct order (indirect before direct)",
         "Apply the le/les → se rule when both pronouns begin with l in double pronoun usage"],
        ["Direct Object Pronouns Review", "Indirect Object Pronouns Review"]),
    (6, 39, "Pronoun Placement Rules (Extended)",
        ["grammar"],
        ["Apply all pronoun placement rules including double pronouns in affirmative, negative, and infinitive constructions",
         "Attach double object pronouns to infinitives and gerunds correctly"],
        ["Pronoun Placement Rules", "Double Object Pronouns"]),
    (6, 40, "Pronouns in Compound Tenses",
        ["grammar"],
        ["Place object pronouns correctly before auxiliary haber in compound tenses",
         "Use double object pronouns with Pretérito Perfecto and Pluscuamperfecto accurately"],
        ["Double Object Pronouns", "Pluscuamperfecto (Introduction)"]),
    (6, 41, "Natural Pronoun Flow in Speech",
        ["communication"],
        ["Replace nouns with correct pronoun combinations without pausing or hesitating",
         "Produce natural spoken Spanish by using pronouns to avoid noun repetition across turns"],
        ["Double Object Pronouns", "Pronoun Placement Rules (Extended)"]),

    # ── Module 31: Connectors & Flow ──────────────────────────────────────────
    (7, 42, "Porque / Ya que",
        ["grammar"],
        ["Use porque and ya que interchangeably to express reason, understanding their register difference",
         "Choose between porque and ya que appropriately in spoken and written contexts"],
        ["Porque (Because)", "Explaining Reasons"]),
    (7, 43, "Aunque / Sin embargo",
        ["grammar"],
        ["Use aunque + indicative and sin embargo to introduce concessions and contrasts",
         "Distinguish aunque (clause connector) from sin embargo (sentence connector) in usage"],
        ["Aunque (Basic Concession)", "Contrasting Ideas"]),
    (7, 44, "Además / También (Extended)",
        ["grammar"],
        ["Use además and también to add information, understanding their positional differences",
         "Combine además with other connectors to build multi-point arguments naturally"],
        ["Además (Furthermore)", "Adding Information"]),
    (7, 45, "Por lo tanto / Así que",
        ["grammar"],
        ["Use por lo tanto and así que to draw conclusions and express consequences",
         "Distinguish the register difference between formal por lo tanto and informal así que"],
        ["Showing Consequences", "Entonces (So/Then)"]),
    (7, 46, "Mientras / Cuando",
        ["grammar"],
        ["Use mientras and cuando to express simultaneous and sequential events",
         "Apply mientras + imperfect and cuando + indefinido in past narrative contexts"],
        ["Affirmative Sentence Building", "Storytelling with Mixed Past Tenses"]),
    (7, 47, "Structuring Discourse Naturally",
        ["communication"],
        ["Open, develop, and close extended spoken or written discourse using a range of connectors",
         "Produce coherent multi-turn conversation or multi-paragraph text using discourse markers fluently"],
        ["Porque / Ya que", "Aunque / Sin embargo", "Por lo tanto / Así que"]),

    # ── Module 32: Opinions & Argumentation ──────────────────────────────────
    (8, 48, "Advanced Opinion Giving",
        ["communication"],
        ["Express opinions with nuance using creo que, me parece que, en mi opinión, and desde mi punto de vista",
         "Calibrate certainty level using expressions like supongo que, es posible que, and está claro que"],
        ["Giving Opinions"]),
    (8, 49, "Agreeing Naturally",
        ["communication"],
        ["Agree with statements using a range of expressions beyond sí (tienes razón, estoy de acuerdo, exacto)",
         "Produce natural agreement responses that extend and build on what the other person said"],
        ["Accepting Invitations", "Giving Opinions"]),
    (8, 50, "Disagreeing Politely",
        ["communication"],
        ["Disagree respectfully using bueno pero, no estoy del todo de acuerdo, and entiendo pero",
         "Soften disagreement with hedging expressions to maintain constructive dialogue"],
        ["Disagreeing Naturally", "Pero (But)"]),
    (8, 51, "Justifying Opinions",
        ["communication"],
        ["Support opinions with reasons, examples, and evidence using porque, ya que, and por ejemplo",
         "Construct a two-part opinion + justification turn naturally in conversation"],
        ["Advanced Opinion Giving", "Porque / Ya que"]),
    (8, 52, "Advantages and Disadvantages",
        ["communication"],
        ["Present balanced arguments discussing both sides using por un lado / por otro lado",
         "Weigh advantages and disadvantages before reaching a conclusion in structured speech"],
        ["Justifying Opinions", "Más... que (Comparatives)"]),
    (8, 53, "Defending a Position",
        ["communication"],
        ["Maintain and defend an opinion under challenge using counter-arguments and evidence",
         "Acknowledge other views while consistently returning to your own position"],
        ["Justifying Opinions", "Disagreeing Politely"]),

    # ── Module 33: Society & Topics ───────────────────────────────────────────
    (9, 54, "Education Vocabulary and Discussion",
        ["communication"],
        ["Discuss education systems, experiences, and opinions using topic vocabulary",
         "Express views on learning, studying, and education using learned structures"],
        ["Giving Opinions (Extended)", "Creating Detailed Descriptions"]),
    (9, 55, "Work and Careers Discussion",
        ["communication"],
        ["Discuss jobs, career paths, and workplace experiences using appropriate vocabulary",
         "Express ambitions, describe work responsibilities, and discuss workplace challenges"],
        ["Talking About Responsibilities", "Discussing Plans in Detail"]),
    (9, 56, "Technology Discussion",
        ["communication"],
        ["Discuss technology, social media, and digital life using relevant vocabulary",
         "Express opinions on how technology affects daily life and society"],
        ["Following Everyday Conversations", "Advanced Opinion Giving"]),
    (9, 57, "Travel Experiences Discussion",
        ["communication"],
        ["Narrate travel experiences using past tenses and travel vocabulary",
         "Describe destinations, compare experiences, and share recommendations"],
        ["Storytelling Practice", "Travel & Transport Vocabulary"]),
    (9, 58, "Environmental Issues Discussion",
        ["communication"],
        ["Discuss environmental problems and solutions using relevant vocabulary",
         "Express concern, propose solutions, and support arguments with evidence"],
        ["Structuring Discourse Naturally", "Advantages and Disadvantages"]),
    (9, 59, "Media and Communication Discussion",
        ["communication"],
        ["Discuss media, communication channels, and their impact using appropriate vocabulary",
         "Express and defend opinions on media consumption and information sources"],
        ["Advanced Opinion Giving", "Defending a Position"]),

    # ── Module 34: Real-World Communication ──────────────────────────────────
    (10, 60, "Making Complaints",
        ["communication"],
        ["Make complaints formally and informally using appropriate language and tone",
         "Use quisiera reclamar, estoy insatisfecho, and resulta que to articulate complaints clearly"],
        ["Disagreeing Politely", "Polite Expressions (Dialogue)"]),
    (10, 61, "Solving Problems",
        ["communication"],
        ["Propose and evaluate solutions to practical problems in conversation",
         "Use podríamos and por qué no to negotiate solutions collaboratively"],
        ["Making Complaints", "Giving Basic Advice"]),
    (10, 62, "Negotiation Language",
        ["communication"],
        ["Use negotiation expressions to reach agreements in transactional and social contexts",
         "Apply compromise language naturally to find common ground"],
        ["Disagreeing Politely", "Justifying Opinions"]),
    (10, 63, "Giving Advice (Extended)",
        ["communication"],
        ["Give nuanced advice using conditional (yo en tu lugar, deberías) and subjunctive structures",
         "Tailor advice to the context — personal, professional, or problem-solving situations"],
        ["Giving Basic Advice", "Conditional Present Formation"]),
    (10, 64, "Making Suggestions (Extended)",
        ["communication"],
        ["Make suggestions in varied registers using podría + infinitive and sería bueno que",
         "Evaluate, accept, and refine suggestions in group discussion contexts"],
        ["Making Suggestions", "Structuring Discourse Naturally"]),
    (10, 65, "Handling Everyday Situations",
        ["communication"],
        ["Navigate a range of complex everyday situations combining complaint, negotiation, and advice skills",
         "Manage unexpected problems in service, social, and official contexts independently"],
        ["Making Complaints", "Solving Problems"]),

    # ── Module 35: Writing Skills ─────────────────────────────────────────────
    (11, 66, "Informal Emails (Extended)",
        ["writing"],
        ["Write a well-structured informal email with opening, body, and closing using natural B1 language",
         "Use a range of connectors and idiomatic expressions to produce a fluent informal written text"],
        ["Writing Informal Emails"]),
    (11, 67, "Formal Emails",
        ["writing"],
        ["Write a formal email using appropriate salutations, formal register, and polite closing formulae",
         "Adapt vocabulary and tone from informal to formal written Spanish effectively"],
        ["Informal Emails (Extended)", "Polite Expressions (Dialogue)"]),
    (11, 68, "Narrative Writing",
        ["writing"],
        ["Write a structured narrative using Indefinido and Imperfecto for events and background",
         "Include scene-setting, rising action, and resolution in a coherent written narrative"],
        ["Writing Short Narratives", "Storytelling with Mixed Past Tenses"]),
    (11, 69, "Opinion Writing",
        ["writing"],
        ["Write a structured opinion text with introduction, argument, counter-argument, and conclusion",
         "Use discourse connectors and opinion expressions to produce a cohesive written argument"],
        ["Writing Informal Emails", "Justifying Opinions"]),
    (11, 70, "Describing Events in Writing",
        ["writing"],
        ["Write a detailed description of an event using past tenses, adjectives, and time expressions",
         "Structure an event description with clear sequencing and vivid detail"],
        ["Narrative Writing", "Describing Personal Experiences in Writing"]),
    (11, 71, "Multi-Paragraph Structure",
        ["writing"],
        ["Plan and produce a multi-paragraph written text with clear structure and cohesion",
         "Use topic sentences, supporting points, and concluding statements in each paragraph"],
        ["Narrative Writing", "Opinion Writing"]),

    # ── Module 36: Extended Conversation ─────────────────────────────────────
    (12, 72, "Narrating Personal Experiences (Extended)",
        ["speaking"],
        ["Narrate extended personal stories using both past tenses with fluency and detail",
         "Hold the floor for an extended turn while narrating, managing questions and reactions"],
        ["Storytelling Practice", "Storytelling with Mixed Past Tenses"]),
    (12, 73, "Defending Opinions in Speech",
        ["speaking"],
        ["Maintain and defend a position orally when challenged, using counter-arguments",
         "Recover from interruptions and return to your argument naturally in debate-style conversation"],
        ["Defending a Position", "Giving Opinions (Extended)"]),
    (12, 74, "Discussing Future Plans (Extended)",
        ["speaking"],
        ["Discuss complex future plans including contingencies using Futuro Simple and si clauses",
         "Sustain an extended spoken discussion about goals, plans, and hypothetical futures"],
        ["Discussing Plans in Detail", "Hypothetical Situations (Si Clauses)"]),
    (12, 75, "Talking About Abstract Topics",
        ["speaking"],
        ["Discuss abstract topics (justice, success, happiness) using opinion and subjunctive structures",
         "Engage in philosophical or open-ended conversation beyond concrete everyday topics"],
        ["Media and Communication Discussion", "Advanced Opinion Giving"]),
    (12, 76, "Maintaining Long Conversations",
        ["speaking"],
        ["Sustain a conversation for several minutes using turn-taking, repair, and elaboration strategies",
         "Avoid silence breaks using filler expressions and elaboration techniques"],
        ["Narrating Personal Experiences (Extended)", "Defending Opinions in Speech"]),
    (12, 77, "Conversation Management Skills",
        ["speaking"],
        ["Use conversation management strategies: opening topics, shifting topics, and closing conversations",
         "Manage conversation flow through interruption, clarification requests, and back-channelling"],
        ["Maintaining Long Conversations", "Structuring Discourse Naturally"]),
]


_SPANISH_B2_MODULES: list[tuple[int, str, str, int]] = [
    (1, "Subjunctive System (Core to Advanced)", "Master the full present and imperfect subjunctive system across all trigger categories and past contexts",           10),
    (2, "Hypothetical Language",                  "Use all three conditional types and mixed conditionals to discuss unreal and hypothetical situations with precision", 8),
    (3, "Reported Speech & Information Flow",      "Relay speech, opinions, and questions accurately across all tense shifts using full reported speech structures",     7),
    (4, "Relative Clauses & Sentence Expansion",  "Build highly complex sentences using el que, el cual, prepositional relatives, and embedded clauses",               7),
    (5, "Pronouns & Cohesion Mastery",            "Master double object pronouns, se lo constructions, pronoun chains, and all strategies for avoiding repetition",    6),
    (6, "Discourse & Connectors",                 "Use the full range of academic and formal discourse connectors to structure arguments and essays with precision",    7),
    (7, "Formal & Impersonal Structures",         "Use passive voice, se constructions, and impersonal expressions to control register in formal and academic Spanish", 6),
    (8, "Advanced Vocabulary Domains",            "Develop topic-specific vocabulary across society, technology, environment, media, and abstract domains",             7),
    (9, "Argumentation & Critical Thinking",      "Build, support, counter, and defend arguments with sophisticated opinion, persuasion, and debate techniques",        7),
    (10, "Writing Mastery",                        "Produce polished opinion, argumentative, and comparative essays as well as formal reports with cohesion and precision", 7),
    (11, "Listening & Reading Comprehension",      "Understand natural-speed Spanish including news, podcasts, interviews, and texts with implicit and abstract meaning",  7),
    (12, "Real-World Fluency",                     "Operate independently in professional, social, and high-stakes Spanish communication contexts with full competence",   7),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_SPANISH_B2_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 37: Subjunctive System ─────────────────────────────────────────
    (1, 1,  "Present Subjunctive Overview",
        ["grammar"],
        ["Review and consolidate all present subjunctive forms including irregular verbs",
         "Identify trigger categories that require the subjunctive across complex sentences"],
        ["Present Subjunctive Formation"]),
    (1, 2,  "Emotion Triggers (Subjunctive)",
        ["grammar"],
        ["Use a wide range of emotion verbs and expressions + subjunctive with accuracy",
         "Produce complex sentences expressing nuanced emotional reactions using the subjunctive"],
        ["Present Subjunctive Overview", "Expressing Emotion with Subjunctive"]),
    (1, 3,  "Doubt and Uncertainty Triggers",
        ["grammar"],
        ["Use doubt and uncertainty expressions including no parece que and es dudoso que + subjunctive",
         "Distinguish certainty (indicative) from doubt (subjunctive) in complex sentences"],
        ["Present Subjunctive Overview", "Expressing Doubt with Subjunctive"]),
    (1, 4,  "Necessity and Obligation (Subjunctive)",
        ["grammar"],
        ["Use a full range of impersonal necessity expressions + subjunctive at B2 level",
         "Contrast personal and impersonal obligation structures in formal and informal registers"],
        ["Present Subjunctive Overview", "Expressing Necessity with Subjunctive"]),
    (1, 5,  "Influence and Recommendations (Subjunctive)",
        ["grammar"],
        ["Use verbs of influence and preference (querer que, preferir que, insistir en que) + subjunctive",
         "Produce natural recommendations and instructions using the subjunctive in varied contexts"],
        ["Present Subjunctive Overview", "Expressing Recommendations with Subjunctive"]),
    (1, 6,  "Purpose Clauses (Subjunctive)",
        ["grammar"],
        ["Use para que and a fin de que + subjunctive to express purpose",
         "Distinguish purpose clauses requiring subjunctive from those using infinitive (same subject)"],
        ["Present Subjunctive Overview"]),
    (1, 7,  "Restriction and Concession (Subjunctive)",
        ["grammar"],
        ["Use concessive and restrictive conjunctions (aunque, a menos que, con tal de que) + subjunctive",
         "Apply aunque + subjunctive (unverified information) vs aunque + indicative (known fact) correctly"],
        ["Purpose Clauses (Subjunctive)", "Aunque / Sin embargo"]),
    (1, 8,  "Imperfect Subjunctive Introduction",
        ["grammar"],
        ["Form the imperfect subjunctive from the third-person plural Pretérito Indefinido stem",
         "Use the imperfect subjunctive in past-context trigger sentences and polite requests (quisiera)"],
        ["Present Subjunctive Formation", "Pretérito Imperfecto (Core Usage)"]),
    (1, 9,  "Subjunctive in Past Contexts",
        ["grammar"],
        ["Use imperfect subjunctive in past reported speech, conditional, and past-trigger sentences",
         "Match sequence of tenses between main and subordinate clauses in past contexts correctly"],
        ["Imperfect Subjunctive Introduction"]),
    (1, 10, "Subjunctive vs Indicative Nuance",
        ["grammar"],
        ["Select the correct mood based on subtle nuance in meaning, not just surface trigger words",
         "Produce minimal pairs demonstrating indicative/subjunctive contrasts in complex sentences"],
        ["Indicative vs Subjunctive Contrast", "Emotion Triggers (Subjunctive)", "Doubt and Uncertainty Triggers"]),

    # ── Module 38: Hypothetical Language ─────────────────────────────────────
    (2, 11, "Conditional Present Review",
        ["grammar"],
        ["Review and consolidate all Conditional Present forms including irregular stems",
         "Use Conditional Present for polite requests and hypothetical situations with full accuracy"],
        ["Conditional Present Formation"]),
    (2, 12, "Conditional Perfect Formation",
        ["grammar"],
        ["Form the Conditional Perfect using habría + past participle for all verbs",
         "Use the Conditional Perfect to express what would have happened under past conditions"],
        ["Conditional Present Review", "Common Perfecto Participles"]),
    (2, 13, "Si Clauses Type 1 Review",
        ["grammar"],
        ["Review and consolidate Type 1 si clauses (si + present + future) for real conditions",
         "Produce both clause types fluently in spontaneous speech and writing"],
        ["Hypothetical Situations (Si Clauses)"]),
    (2, 14, "Si Clauses Type 2 (Imperfect Subjunctive)",
        ["grammar"],
        ["Form Type 2 si clauses using si + imperfect subjunctive + conditional for unlikely conditions",
         "Express hypothetical present/future situations accurately using Type 2 structure"],
        ["Si Clauses Type 1 Review", "Imperfect Subjunctive Introduction"]),
    (2, 15, "Si Clauses Type 3 (Pluperfect Subjunctive)",
        ["grammar"],
        ["Form Type 3 si clauses using si + pluperfect subjunctive + conditional perfect for impossible past conditions",
         "Express regret and past hypotheticals accurately using Type 3 structure"],
        ["Si Clauses Type 2 (Imperfect Subjunctive)", "Conditional Perfect Formation"]),
    (2, 16, "Mixed Conditionals",
        ["grammar"],
        ["Form mixed conditional sentences combining Type 2 and Type 3 elements",
         "Express situations where a past condition affects the present or vice versa"],
        ["Si Clauses Type 2 (Imperfect Subjunctive)", "Si Clauses Type 3 (Pluperfect Subjunctive)"]),
    (2, 17, "Expressing Unreal Situations",
        ["communication"],
        ["Describe unreal, imagined, or counterfactual situations using all conditional structures",
         "Produce natural sentences expressing wishes, regrets, and hypothetical worlds"],
        ["Si Clauses Type 2 (Imperfect Subjunctive)", "Imperfect Subjunctive Introduction"]),
    (2, 18, "Hypothetical Chains and Scenarios",
        ["communication"],
        ["Build extended hypothetical chains linking multiple conditional clauses",
         "Sustain a conversation about complex what-if scenarios using mixed conditional structures"],
        ["Mixed Conditionals", "Expressing Unreal Situations"]),

    # ── Module 39: Reported Speech & Information Flow ────────────────────────
    (3, 19, "Direct vs Reported Speech",
        ["grammar"],
        ["Understand and apply the structural and tense differences between direct and reported speech",
         "Convert direct speech to reported speech making all necessary changes"],
        ["Natural Reported Speech in Conversation"]),
    (3, 20, "Present to Imperfect Shift",
        ["grammar"],
        ["Shift present tense verbs to imperfect when reporting with a past reporting verb",
         "Apply the present → imperfect backshift accurately across all persons"],
        ["Direct vs Reported Speech", "Basic Tense Backshifting"]),
    (3, 21, "Future to Conditional Shift",
        ["grammar"],
        ["Shift future tense verbs to conditional when reporting with a past reporting verb",
         "Apply the future → conditional backshift in complex reported sentences"],
        ["Direct vs Reported Speech", "Conditional Present Formation"]),
    (3, 22, "Past to Pluperfect Shift",
        ["grammar"],
        ["Shift Indefinido and Perfecto to Pluscuamperfecto in full reported speech",
         "Apply all three tense backshifts together in extended reported speech passages"],
        ["Present to Imperfect Shift", "Pluscuamperfecto (Introduction)"]),
    (3, 23, "Reporting Questions",
        ["grammar"],
        ["Report both yes/no and information questions with full tense and structure adjustments",
         "Produce reported questions accurately without direct speech word order or intonation markers"],
        ["Direct vs Reported Speech"]),
    (3, 24, "Reporting Opinions",
        ["grammar"],
        ["Report opinions and beliefs using decir que, pensar que, and creer que with correct backshifting",
         "Convey reported opinions with appropriate hedging and attribution in written and spoken Spanish"],
        ["Direct vs Reported Speech", "Advanced Opinion Giving"]),
    (3, 25, "Summarising Arguments",
        ["communication"],
        ["Summarise a spoken or written argument accurately in reported form",
         "Produce a neutral summary of another person's position using reporting structures fluently"],
        ["Reporting Opinions", "Structuring Discourse Naturally"]),

    # ── Module 40: Relative Clauses & Sentence Expansion ─────────────────────
    (4, 26, "Relative Pronoun Review (que, quien, cuyo)",
        ["grammar"],
        ["Review and consolidate que, quien, and cuyo in complex sentences at B2 level",
         "Identify the correct relative pronoun based on antecedent type and clause function"],
        ["Combining Relative Clauses in Speech", "Relative Pronoun CUYO"]),
    (4, 27, "El que / La que System",
        ["grammar"],
        ["Use el que, la que, los que, las que to introduce relative clauses with a specific antecedent",
         "Choose between que and el que based on the presence or absence of a determiner"],
        ["Relative Pronoun Review (que, quien, cuyo)"]),
    (4, 28, "El cual System",
        ["grammar"],
        ["Use el cual, la cual, los cuales, las cuales as formal alternatives to que and el que",
         "Apply el cual correctly in formal written Spanish and after multi-syllable prepositions"],
        ["Relative Pronoun Review (que, quien, cuyo)"]),
    (4, 29, "Prepositional Relatives",
        ["grammar"],
        ["Form prepositional relative clauses using a/de/en/con + el que/el cual",
         "Produce complex sentences where the relative pronoun is the object of a preposition"],
        ["El que / La que System", "El cual System"]),
    (4, 30, "Embedded Clauses",
        ["grammar"],
        ["Embed subordinate clauses within relative clauses to build multi-layer sentences",
         "Maintain grammatical agreement and clarity in sentences with deeply embedded structures"],
        ["Prepositional Relatives", "What Is the Subjunctive?"]),
    (4, 31, "Multi-Clause Sentence Building",
        ["communication"],
        ["Construct sentences with three or more clauses linked by relative pronouns and connectors",
         "Produce B2-level complex sentences in both speech and writing with clarity and accuracy"],
        ["Embedded Clauses", "Structuring Discourse Naturally"]),
    (4, 32, "Reduced Relative Structures",
        ["grammar"],
        ["Use participial and infinitive phrases as reduced relative clauses",
         "Simplify full relative clauses to reduced forms appropriately in formal written Spanish"],
        ["Multi-Clause Sentence Building"]),

    # ── Module 41: Pronouns & Cohesion Mastery ───────────────────────────────
    (5, 33, "Double Object Pronouns Review",
        ["grammar"],
        ["Review and consolidate all double object pronoun combinations at B2 level",
         "Use double object pronouns flawlessly in complex sentences including compound tenses"],
        ["Double Object Pronouns", "Natural Pronoun Flow in Speech"]),
    (5, 34, "Se lo / Se la / Se los / Se las",
        ["grammar"],
        ["Master the le/les → se substitution rule in all double pronoun contexts",
         "Apply se lo, se la, se los, se las accurately when both pronouns begin with l"],
        ["Double Object Pronouns Review"]),
    (5, 35, "Pronoun Chains",
        ["grammar"],
        ["Handle sequences of object pronouns across multiple clauses without repetition",
         "Track pronoun reference across long passages of spoken and written Spanish"],
        ["Se lo / Se la / Se los / Se las"]),
    (5, 36, "Y and En Abstract Usage",
        ["grammar"],
        ["Use the adverbial pronouns y (there/to it) and en (of it/from it) in abstract contexts",
         "Recognise and produce y and en in idiomatic expressions and natural speech"],
        ["Double Object Pronouns Review"]),
    (5, 37, "Avoiding Repetition Strategies",
        ["communication"],
        ["Apply the full range of pronoun, ellipsis, and reference strategies to avoid lexical repetition",
         "Produce cohesive spoken and written text by substituting repeated elements with pronouns"],
        ["Pronoun Chains", "Y and En Abstract Usage"]),
    (5, 38, "Sentence Restructuring Fluency",
        ["communication"],
        ["Restructure sentences for emphasis, cohesion, or register using topicalisation and pronoun placement",
         "Transform sentences fluently between structures without loss of meaning"],
        ["Avoiding Repetition Strategies", "Multi-Clause Sentence Building"]),

    # ── Module 42: Discourse & Connectors ────────────────────────────────────
    (6, 39, "Contrast Connectors (Sin embargo, No obstante)",
        ["grammar"],
        ["Use sin embargo and no obstante to introduce contrast between clauses or sentences",
         "Distinguish these formal contrast connectors from pero and aunque in register and usage"],
        ["Aunque / Sin embargo", "Structuring Discourse Naturally"]),
    (6, 40, "Consequence Connectors (Por consiguiente)",
        ["grammar"],
        ["Use por consiguiente, por tanto, and de ahí que to draw formal consequences",
         "Apply formal consequence connectors in academic and professional written Spanish"],
        ["Por lo tanto / Así que", "Structuring Discourse Naturally"]),
    (6, 41, "Concession Connectors (A pesar de)",
        ["grammar"],
        ["Use a pesar de (que), pese a (que), and aun así to introduce concessions",
         "Distinguish concession connectors by structure: a pesar de + noun/infinitive vs a pesar de que + clause"],
        ["Contrast Connectors (Sin embargo, No obstante)"]),
    (6, 42, "Argument Sequencing",
        ["communication"],
        ["Use sequencing connectors (en primer lugar, por un lado, además, por último) to order arguments",
         "Build a multi-point argument using sequencing markers naturally in speech and writing"],
        ["Contrast Connectors (Sin embargo, No obstante)", "Consequence Connectors (Por consiguiente)"]),
    (6, 43, "Introducing Ideas",
        ["communication"],
        ["Use opening and framing expressions (en cuanto a, respecto a, en lo que se refiere a) to introduce topics",
         "Frame new information and perspectives clearly at the start of paragraphs or turns"],
        ["Argument Sequencing"]),
    (6, 44, "Concluding Arguments",
        ["communication"],
        ["Use closing connectors (en conclusión, en definitiva, en resumen, por lo tanto) to close arguments",
         "Write and speak effective conclusions that synthesise prior points"],
        ["Argument Sequencing", "Consequence Connectors (Por consiguiente)"]),
    (6, 45, "Essay Flow Structuring",
        ["writing"],
        ["Structure a multi-paragraph essay using opening, development, and conclusion connectors cohesively",
         "Produce an essay outline and full draft with natural discourse flow using formal Spanish connectors"],
        ["Introducing Ideas", "Concluding Arguments"]),

    # ── Module 43: Formal & Impersonal Structures ────────────────────────────
    (7, 46, "Passive Voice Formation",
        ["grammar"],
        ["Form the passive voice using ser + past participle in the present and simple past tenses",
         "Agree the past participle with the grammatical subject in passive constructions"],
        ["Common Perfecto Participles", "Adjective Gender Agreement"]),
    (7, 47, "Passive in Multiple Tenses",
        ["grammar"],
        ["Extend passive voice to Imperfecto, Futuro, Condicional, and Subjuntivo",
         "Select the appropriate passive tense based on context and meaning"],
        ["Passive Voice Formation", "Pretérito Indefinido Review"]),
    (7, 48, "Se Passive Constructions",
        ["grammar"],
        ["Use se + third-person verb as an alternative passive to avoid naming the agent",
         "Distinguish se passive (no agent possible) from ser passive (agent can be introduced with por)"],
        ["Passive Voice Formation", "Reflexive Pronouns"]),
    (7, 49, "Impersonal Expressions (Se dice que)",
        ["grammar"],
        ["Use impersonal se constructions (se dice que, se cree que, se considera que) in formal Spanish",
         "Apply impersonal constructions to distance the speaker from a statement appropriately"],
        ["Se Passive Constructions"]),
    (7, 50, "Formal Tone Control",
        ["communication"],
        ["Identify and apply formal lexical and syntactic features that raise register in Spanish",
         "Rewrite informal sentences in formal register using passive, impersonal, and formal connectors"],
        ["Impersonal Expressions (Se dice que)"]),
    (7, 51, "Academic vs Neutral Register",
        ["communication"],
        ["Distinguish academic, professional, neutral, and informal registers in Spanish text",
         "Adapt a piece of writing fluidly between registers appropriate to different audiences and purposes"],
        ["Formal Tone Control"]),

    # ── Module 44: Advanced Vocabulary Domains ───────────────────────────────
    (8, 52, "Society and Politics Vocabulary",
        ["vocabulary"],
        ["Use advanced vocabulary for discussing social issues, politics, and civic life in Spanish",
         "Discuss political systems, social inequality, and civic engagement with precision"],
        ["Media and Communication Discussion"]),
    (8, 53, "Technology and AI Vocabulary",
        ["vocabulary"],
        ["Use advanced vocabulary for discussing technology, AI, and digital society",
         "Discuss the impact of technological change on society with appropriate terminology"],
        ["Technology Discussion"]),
    (8, 54, "Environment and Climate Vocabulary",
        ["vocabulary"],
        ["Use advanced vocabulary for environmental science, climate change, and sustainability",
         "Discuss environmental policy and climate solutions with precise technical language"],
        ["Environmental Issues Discussion"]),
    (8, 55, "Education Systems Vocabulary",
        ["vocabulary"],
        ["Use vocabulary for comparing and critiquing education systems at an advanced level",
         "Discuss educational reform, inequality, and innovation using appropriate terminology"],
        ["Education Vocabulary and Discussion"]),
    (8, 56, "Advanced Media and Communication Vocabulary",
        ["vocabulary"],
        ["Use advanced vocabulary for discussing media influence, journalism, and information literacy",
         "Analyse media bias and communication strategies using precise academic vocabulary"],
        ["Media and Communication Discussion"]),
    (8, 57, "Work and Economy Vocabulary",
        ["vocabulary"],
        ["Use vocabulary for discussing labour markets, economic systems, and professional contexts",
         "Discuss economic trends, employment, and professional life with appropriate terminology"],
        ["Work and Careers Discussion"]),
    (8, 58, "Abstract Conceptual Vocabulary",
        ["vocabulary"],
        ["Use abstract vocabulary for discussing concepts like justice, identity, freedom, and power",
         "Apply abstract conceptual vocabulary in philosophical discussion and written argumentation"],
        ["Talking About Abstract Topics"]),

    # ── Module 45: Argumentation & Critical Thinking ─────────────────────────
    (9, 59, "Expressing Opinions (Advanced)",
        ["communication"],
        ["Express nuanced opinions using a full range of epistemic expressions and modal hedges",
         "Calibrate opinion strength from strong assertion to tentative suggestion using appropriate forms"],
        ["Advanced Opinion Giving", "Subjunctive vs Indicative Nuance"]),
    (9, 60, "Thesis Building",
        ["communication"],
        ["Construct a clear thesis statement that takes a specific position on a debatable topic",
         "Develop a thesis with supporting sub-points that can be expanded in an argument"],
        ["Expressing Opinions (Advanced)"]),
    (9, 61, "Supporting Arguments",
        ["communication"],
        ["Support a thesis with evidence, examples, and expert opinion using formal Spanish structures",
         "Develop each supporting point with reasoning and illustration in speech and writing"],
        ["Thesis Building", "Argument Sequencing"]),
    (9, 62, "Counterarguments",
        ["communication"],
        ["Anticipate and address counterarguments using concession and rebuttal structures",
         "Use a pesar de que, aunque, and sin embargo to acknowledge then override opposing views"],
        ["Supporting Arguments", "Contrast Connectors (Sin embargo, No obstante)"]),
    (9, 63, "Persuasion Techniques",
        ["communication"],
        ["Apply rhetorical techniques including rhetorical questions, repetition, and tricolon in Spanish",
         "Calibrate persuasive language to audience and context in formal and semi-formal registers"],
        ["Counterarguments"]),
    (9, 64, "Emphasis and Rhetorical Balance",
        ["communication"],
        ["Use emphasis structures (lo que es cierto es que, lo que importa es) to foreground key points",
         "Balance argument structure so each section receives proportionate development"],
        ["Persuasion Techniques", "Essay Flow Structuring"]),
    (9, 65, "Debate Simulation",
        ["speaking"],
        ["Participate in a structured debate defending a position against active challenge",
         "Use the full B2 argumentation toolkit in real-time spoken interaction under pressure"],
        ["Emphasis and Rhetorical Balance", "Defending a Position"]),

    # ── Module 46: Writing Mastery ────────────────────────────────────────────
    (10, 66, "Opinion Essays",
        ["writing"],
        ["Write a structured opinion essay with clear thesis, development, and conclusion",
         "Use formal Spanish essay conventions including impersonal structures and discourse connectors"],
        ["Opinion Writing", "Thesis Building"]),
    (10, 67, "Argumentative Essays",
        ["writing"],
        ["Write a balanced argumentative essay presenting and evaluating multiple positions",
         "Integrate counterarguments and rebuttals within a cohesive written structure"],
        ["Opinion Essays", "Supporting Arguments", "Counterarguments"]),
    (10, 68, "Comparative Essays",
        ["writing"],
        ["Write a comparative essay analysing similarities and differences between two positions or subjects",
         "Use comparative structures and sequencing connectors to organise the comparison effectively"],
        ["Opinion Essays", "Expressing Opinions (Advanced)"]),
    (10, 69, "Formal Reports",
        ["writing"],
        ["Write a formal report with sections including introduction, findings, and recommendations",
         "Use passive voice, impersonal constructions, and formal register throughout"],
        ["Formal Emails", "Academic vs Neutral Register"]),
    (10, 70, "Structured Analysis Writing",
        ["writing"],
        ["Write an analytical text examining a text, image, or data set using formal Spanish",
         "Develop an analytical argument with evidence, interpretation, and conclusion"],
        ["Argumentative Essays", "Essay Flow Structuring"]),
    (10, 71, "Cohesion in Paragraphs",
        ["writing"],
        ["Ensure each paragraph has a clear topic sentence, development, and link to the next paragraph",
         "Use cohesive devices including pronoun reference, lexical chains, and connectors within paragraphs"],
        ["Multi-Paragraph Structure", "Essay Flow Structuring"]),
    (10, 72, "Tone Adaptation",
        ["writing"],
        ["Adapt vocabulary, syntax, and register to suit a range of audiences and text types",
         "Rewrite the same content in formal, neutral, and informal registers accurately"],
        ["Formal Tone Control", "Cohesion in Paragraphs"]),

    # ── Module 47: Listening & Reading Comprehension ─────────────────────────
    (11, 73, "Natural-Speed Speech Comprehension",
        ["listening"],
        ["Follow extended discourse at natural speed with occasional use of formal and technical vocabulary",
         "Extract main and supporting ideas from unscripted native-speaker speech"],
        ["Following Everyday Conversations", "Conversation Management Skills"]),
    (11, 74, "News Comprehension",
        ["listening"],
        ["Understand broadcast and online news in Spanish including complex political and social topics",
         "Identify the main story, key facts, and speaker's stance in a news report"],
        ["Natural-Speed Speech Comprehension", "Society and Politics Vocabulary"]),
    (11, 75, "Podcast-Style Listening",
        ["listening"],
        ["Follow extended informal and semi-formal spoken discourse in podcast format",
         "Track the development of an argument or narrative across a 5–10 minute audio segment"],
        ["Natural-Speed Speech Comprehension"]),
    (11, 76, "Interview Understanding",
        ["listening"],
        ["Follow an interview including turn-taking, interruptions, and complex vocabulary",
         "Identify the interviewer's questions and the interviewee's main positions accurately"],
        ["Podcast-Style Listening", "Work and Economy Vocabulary"]),
    (11, 77, "Implicit Meaning Inference",
        ["listening"],
        ["Infer meaning not directly stated including irony, implication, and attitude",
         "Interpret implicit meaning in authentic audio using contextual and pragmatic cues"],
        ["Podcast-Style Listening", "Subjunctive vs Indicative Nuance"]),
    (11, 78, "Abstract Topic Comprehension",
        ["listening"],
        ["Understand extended discourse on abstract, philosophical, or technical topics",
         "Follow a logical argument on an abstract subject including supporting evidence"],
        ["Implicit Meaning Inference", "Abstract Conceptual Vocabulary"]),
    (11, 79, "Multi-Layer Interpretation",
        ["listening"],
        ["Interpret texts and audio at multiple levels: surface, inferential, and critical",
         "Evaluate the purpose, audience, and effect of a spoken or written text critically"],
        ["Abstract Topic Comprehension", "Implicit Meaning Inference"]),

    # ── Module 48: Real-World Fluency ─────────────────────────────────────────
    (12, 80, "Negotiation Language (B2)",
        ["communication"],
        ["Use advanced negotiation structures including conditional and subjunctive forms",
         "Negotiate complex agreements in professional and formal social contexts in Spanish"],
        ["Negotiation Language", "Hypothetical Chains and Scenarios"]),
    (12, 81, "Professional Communication",
        ["communication"],
        ["Communicate effectively in professional contexts including meetings, presentations, and correspondence",
         "Use formal register, impersonal structures, and technical vocabulary in professional Spanish"],
        ["Negotiation Language (B2)", "Formal Tone Control"]),
    (12, 82, "Conflict Resolution",
        ["communication"],
        ["Manage and de-escalate conflict using diplomatic language, concession, and compromise strategies",
         "Navigate disagreements and tensions in professional and social contexts with confidence"],
        ["Negotiation Language (B2)", "Counterarguments"]),
    (12, 83, "Complaints Handling",
        ["communication"],
        ["Make and respond to formal complaints in writing and speech with appropriate register",
         "Use passive voice, impersonal expressions, and formal connectors in complaint contexts"],
        ["Making Complaints", "Professional Communication"]),
    (12, 84, "Social Nuance",
        ["communication"],
        ["Navigate subtle social norms, indirect communication, and pragmatic conventions in Spanish",
         "Interpret and produce socially appropriate language across formal and informal situations"],
        ["Conversation Management Skills", "Subjunctive vs Indicative Nuance"]),
    (12, 85, "Public Speaking Basics",
        ["speaking"],
        ["Deliver a structured spoken presentation in Spanish with introduction, body, and conclusion",
         "Use discourse markers, rhetorical techniques, and body language conventions in public speaking"],
        ["Emphasis and Rhetorical Balance", "Maintaining Long Conversations"]),
    (12, 86, "High-Context Conversation Management",
        ["speaking"],
        ["Manage extended high-stakes conversations using all conversation management skills at B2 level",
         "Navigate implicit cultural references, register shifts, and complex social dynamics in Spanish"],
        ["Social Nuance", "Professional Communication"]),
]


# ─── German CEFR A1 curriculum ───────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_GERMAN_A1_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Sound System & Pronunciation Layer",      "Produce intelligible German with correct pronunciation foundations",                        6),
    (2,  "Sentence Engine (Word Order System)",     "Build grammatically correct sentences under real-time pressure",                            5),
    (3,  "Personal Pronouns & Identity Speech",     "Refer to self and others naturally in conversation",                                        3),
    (4,  "Present Tense Core System",               "Describe actions, identity, and states in present time",                                    4),
    (5,  "Articles & Gender System",                "Correctly label nouns in structured speech",                                                4),
    (6,  "Plural Formation System",                 "Refer to multiple objects and people accurately",                                           4),
    (7,  "Case System Introduction",                "Understand how meaning changes with sentence roles",                                        5),
    (8,  "Negation System",                         "Express absence, refusal, and contradiction clearly",                                       4),
    (9,  "Question & Information System",           "Ask and answer basic real-world questions",                                                 4),
    (10, "Core Vocabulary Domains",                 "Build functional vocabulary for daily life",                                                5),
    (11, "Numbers, Time & Daily Structure",         "Talk about time, dates, and routines",                                                      4),
    (12, "Preposition System",                      "Describe location and simple relationships",                                                5),
    (13, "Modal Verb System",                       "Express ability, necessity, permission, and desire",                                        4),
    (14, "Everyday Communication System",           "Survive real-world basic interactions",                                                     5),
    (15, "Descriptive Language System",             "Describe people, objects, and situations simply",                                           4),
    (16, "Functional Sentence Patterns",            "Use fixed expressions for real communication without translation",                          5),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_GERMAN_A1_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 1: Sound System & Pronunciation Layer ──────────────────────────
    (1, 1, "German alphabet (A–Z + ä, ö, ü, ß)",
        ["pronunciation"],
        ["Name and produce all 26 base letters plus the four special characters ä, ö, ü, ß",
         "Distinguish German letter sounds from English equivalents in isolation and in words"],
        []),
    (1, 2, "Core pronunciation rules",
        ["pronunciation"],
        ["Apply German letter-to-sound rules consistently for vowels, consonants, and digraphs",
         "Decode unfamiliar German words using phonetic rules rather than guessing from spelling"],
        ["German alphabet (A–Z + ä, ö, ü, ß)"]),
    (1, 3, "ch variation (ich vs ach)",
        ["pronunciation"],
        ["Produce the front palatal [ç] (ich) and back velar [x] (ach) accurately",
         "Select the correct ch variant automatically based on the preceding vowel"],
        ["Core pronunciation rules"]),
    (1, 4, "w/v confusion patterns",
        ["pronunciation"],
        ["Produce German w as [v] and German v as [f] without native-language interference",
         "Self-correct w/v confusion errors in real-time speech"],
        ["Core pronunciation rules"]),
    (1, 5, "r pronunciation variation",
        ["pronunciation"],
        ["Produce the uvular German r at the start of syllables and in vocalic final position",
         "Distinguish the two main German r realisations and apply them in natural speech"],
        ["Core pronunciation rules"]),
    (1, 6, "Basic syllable stress patterns",
        ["pronunciation"],
        ["Apply German default stress (first syllable of root) across common vocabulary",
         "Identify and produce correct stress in words with prefixes and in loanwords"],
        ["Core pronunciation rules"]),

    # ── Module 2: Sentence Engine (Word Order System) ─────────────────────────
    (2, 7, "Basic SVO structure",
        ["grammar"],
        ["Produce correct subject–verb–object sentences in German",
         "Identify and place subject, verb, and object in the correct positions"],
        ["Basic syllable stress patterns"]),
    (2, 8, "Verb-second (V2) rule mastery",
        ["grammar"],
        ["Apply the V2 rule: the finite verb always occupies second position in a main clause",
         "Invert subject and verb correctly when a non-subject element begins the sentence"],
        ["Basic SVO structure"]),
    (2, 9, "Yes/No questions (verb-first)",
        ["grammar"],
        ["Form yes/no questions by moving the finite verb to first position",
         "Answer yes/no questions accurately using ja, nein, and doch"],
        ["Verb-second (V2) rule mastery"]),
    (2, 10, "WH-questions (question word + verb position)",
        ["grammar"],
        ["Form WH-questions with the question word in position one and the verb in position two",
         "Produce fluent WH-questions without pausing to recall word order"],
        ["Yes/No questions (verb-first)"]),
    (2, 11, "Sentence building from fragments",
        ["skill"],
        ["Assemble grammatically complete sentences from vocabulary fragments under time pressure",
         "Self-monitor sentence structure and correct V2 violations in real time"],
        ["WH-questions (question word + verb position)"]),

    # ── Module 3: Personal Pronouns & Identity Speech ─────────────────────────
    (3, 12, "Subject pronouns (ich, du, er/sie/es, wir, ihr, Sie)",
        ["grammar"],
        ["Identify and produce all German subject pronouns with correct gender and number",
         "Select the correct pronoun automatically when referring to people and objects"],
        ["Basic SVO structure"]),
    (3, 13, "Subject usage in real sentences",
        ["skill"],
        ["Use all subject pronouns fluently in full sentences without pronoun-dropping",
         "Substitute nouns with pronouns accurately to avoid repetition in speech"],
        ["Subject pronouns (ich, du, er/sie/es, wir, ihr, Sie)"]),
    (3, 14, "Informal vs formal address (du vs Sie)",
        ["communication"],
        ["Distinguish when to use du (informal) and Sie (formal) in German social contexts",
         "Apply formal Sie with correct verb conjugation in professional and unfamiliar social situations"],
        ["Subject usage in real sentences"]),

    # ── Module 4: Present Tense Core System ───────────────────────────────────
    (4, 15, "Regular verb conjugation (-en verbs)",
        ["grammar"],
        ["Conjugate regular -en verbs across all six persons in the present tense",
         "Apply the correct ending automatically without conscious rule recall"],
        ["Subject pronouns (ich, du, er/sie/es, wir, ihr, Sie)"]),
    (4, 16, "sein / haben conjugation",
        ["grammar"],
        ["Conjugate sein and haben across all persons in the present tense",
         "Use sein and haben as main verbs expressing identity, existence, and possession"],
        ["Regular verb conjugation (-en verbs)"]),
    (4, 17, "High-frequency verb automation (gehen / machen / lernen / kommen / heißen)",
        ["vocabulary"],
        ["Conjugate and use the five highest-frequency German verbs automatically in present tense",
         "Deploy these verbs in natural sentences without consciously retrieving their forms"],
        ["sein / haben conjugation"]),
    (4, 18, "Sentence integration with V2 rule",
        ["skill"],
        ["Produce present-tense sentences that automatically obey the V2 constraint",
         "Combine subject pronouns, present-tense verbs, and objects into fluent V2-compliant output"],
        ["High-frequency verb automation (gehen / machen / lernen / kommen / heißen)", "Verb-second (V2) rule mastery"]),

    # ── Module 5: Articles & Gender System ───────────────────────────────────
    (5, 19, "der / die / das system",
        ["grammar"],
        ["Identify the three grammatical genders in German and their corresponding definite articles",
         "Produce der, die, das with common nouns without pausing to recall gender"],
        ["Regular verb conjugation (-en verbs)"]),
    (5, 20, "Indefinite articles (ein / eine)",
        ["grammar"],
        ["Produce ein (masculine/neuter) and eine (feminine) with nouns in nominative case",
         "Distinguish when to use definite vs indefinite articles in German sentences"],
        ["der / die / das system"]),
    (5, 21, "Gender memorisation patterns",
        ["vocabulary"],
        ["Apply common gender-suffix patterns (-ung → die, -chen → das, -er/-ling → der) to new nouns",
         "Use gender-predictive strategies to reduce cognitive load when encountering new vocabulary"],
        ["Indefinite articles (ein / eine)"]),
    (5, 22, "Article usage in sentences",
        ["skill"],
        ["Use the correct article automatically when producing German noun phrases in sentences",
         "Self-correct article-gender mismatches in spoken and written output"],
        ["Gender memorisation patterns"]),

    # ── Module 6: Plural Formation System ────────────────────────────────────
    (6, 23, "Standard plural patterns (-e, -en, -er, -s)",
        ["grammar"],
        ["Identify and produce the four main German plural suffixes with common nouns",
         "Select the correct plural pattern based on noun class with reasonable accuracy"],
        ["der / die / das system"]),
    (6, 24, "Umlaut changes in plural forms",
        ["grammar"],
        ["Produce plural forms that add umlaut (a→ä, o→ö, u→ü) accurately",
         "Identify which nouns take umlaut plurals and self-correct umlaut omissions"],
        ["Standard plural patterns (-e, -en, -er, -s)"]),
    (6, 25, "Irregular plural exposure",
        ["vocabulary"],
        ["Recognise and produce the most frequent irregular plural forms (das Kind → die Kinder, etc.)",
         "Store irregular plurals as paired units with the singular in lexical memory"],
        ["Umlaut changes in plural forms"]),
    (6, 26, "Noun-number agreement",
        ["grammar"],
        ["Match article and verb forms to singular vs plural nouns consistently",
         "Self-monitor number agreement errors across full sentences"],
        ["Irregular plural exposure"]),

    # ── Module 7: Case System Introduction (Nominative → Accusative) ──────────
    (7, 27, "Nominative case (subject role)",
        ["grammar"],
        ["Identify the nominative case as the subject role in a German sentence",
         "Use correct nominative articles (der, die, das, ein, eine) for the subject noun phrase"],
        ["Article usage in sentences"]),
    (7, 28, "Accusative case (direct object role)",
        ["grammar"],
        ["Identify the accusative case as the direct object role in a German sentence",
         "Understand that the direct object receives the action of the verb"],
        ["Nominative case (subject role)"]),
    (7, 29, "der → den transformation",
        ["grammar"],
        ["Apply the masculine accusative change: der → den and ein → einen",
         "Produce den/einen automatically for masculine direct objects without conscious recall"],
        ["Accusative case (direct object role)"]),
    (7, 30, "Basic object marking awareness",
        ["skill"],
        ["Identify which noun phrase is the subject and which is the direct object in German sentences",
         "Correctly mark direct objects with accusative articles in structured production tasks"],
        ["der → den transformation"]),
    (7, 31, "Sentence role identification",
        ["skill"],
        ["Classify noun phrases as subject, verb, or object in increasingly complex sentences",
         "Use case awareness to disambiguate sentence meaning when word order varies"],
        ["Basic object marking awareness"]),

    # ── Module 8: Negation System ─────────────────────────────────────────────
    (8, 32, "nicht (sentence negation)",
        ["grammar"],
        ["Place nicht correctly to negate verbs, adjectives, and adverbs in German sentences",
         "Distinguish nicht placement rules for different target elements"],
        ["Sentence role identification"]),
    (8, 33, "kein / keine (noun negation)",
        ["grammar"],
        ["Use kein/keine to negate nouns where the English equivalent uses 'no' or 'not a'",
         "Select kein vs keine based on noun gender and case automatically"],
        ["nicht (sentence negation)"]),
    (8, 34, "Negation placement rules",
        ["grammar"],
        ["Apply systematic negation placement: nicht after conjugated verb, before adjective/adverb",
         "Produce correctly negated sentences under conversation speed without positional errors"],
        ["kein / keine (noun negation)"]),
    (8, 35, "Negation interaction with V2 structure",
        ["skill"],
        ["Produce negated V2-compliant sentences without disrupting verb-second word order",
         "Self-correct negation placement errors while maintaining natural sentence flow"],
        ["Negation placement rules", "Verb-second (V2) rule mastery"]),

    # ── Module 9: Question & Information System ───────────────────────────────
    (9, 36, "WH-question words (wer / was / wo / wann / warum / wie)",
        ["vocabulary"],
        ["Produce and recognise the six core German question words with their English equivalents",
         "Select the appropriate question word automatically based on the type of information sought"],
        ["WH-questions (question word + verb position)"]),
    (9, 37, "Yes/No inversion questions",
        ["grammar"],
        ["Form inversion questions automatically to check facts and request confirmation",
         "Distinguish inversion questions from declarative sentences by verb-first position"],
        ["Yes/No questions (verb-first)"]),
    (9, 38, "Information-seeking sentence structure",
        ["skill"],
        ["Produce natural WH-questions to gather real-world information",
         "Combine question words with appropriate verb forms in fluent real-time speech"],
        ["WH-question words (wer / was / wo / wann / warum / wie)", "Yes/No inversion questions"]),
    (9, 39, "Question-response patterns",
        ["communication"],
        ["Respond accurately to WH and yes/no questions with complete and short-form answers",
         "Use ja, nein, doch, and short-answer patterns naturally in conversation"],
        ["Information-seeking sentence structure"]),

    # ── Module 10: Core Vocabulary Domains ───────────────────────────────────
    (10, 40, "People & relationships vocabulary",
        ["vocabulary"],
        ["Produce vocabulary for family members, friends, colleagues, and social relationships",
         "Use people vocabulary in simple descriptive and conversational sentences"],
        ["Subject usage in real sentences"]),
    (10, 41, "Places vocabulary (Haus, Schule, Stadt, Land)",
        ["vocabulary"],
        ["Produce the most frequent place nouns in German with correct articles",
         "Use place vocabulary in basic location sentences"],
        ["Article usage in sentences"]),
    (10, 42, "Objects vocabulary (Buch, Essen, Wasser, Auto)",
        ["vocabulary"],
        ["Produce the 30 most common everyday object nouns with correct gender",
         "Use object vocabulary as direct objects in accusative-marked sentences"],
        ["Basic object marking awareness"]),
    (10, 43, "High-frequency verbs (second tier)",
        ["vocabulary"],
        ["Automate the next 15 most common German verbs in present tense conjugation",
         "Use these verbs fluently in sentences alongside already-automated core verbs"],
        ["High-frequency verb automation (gehen / machen / lernen / kommen / heißen)"]),
    (10, 44, "Survival nouns",
        ["vocabulary"],
        ["Produce 20 survival nouns needed for daily life (Wasser, Toilette, Hilfe, etc.)",
         "Deploy survival nouns in fixed emergency and basic communication phrases"],
        ["Objects vocabulary (Buch, Essen, Wasser, Auto)"]),

    # ── Module 11: Numbers, Time & Daily Structure ────────────────────────────
    (11, 45, "Numbers 0–100+",
        ["vocabulary"],
        ["Produce all German cardinal numbers from 0 to 100 without hesitation",
         "Use numbers in prices, quantities, addresses, and phone numbers"],
        ["Core pronunciation rules"]),
    (11, 46, "Days and months",
        ["vocabulary"],
        ["Produce all seven days of the week and twelve months in German",
         "Use days and months in date expressions and scheduling sentences"],
        ["Numbers 0–100+"]),
    (11, 47, "Time expressions (Uhrzeit)",
        ["vocabulary"],
        ["Tell and ask the time using the 12-hour and 24-hour formats in German",
         "Use time expressions in scheduling sentences with um, von, bis"],
        ["Days and months"]),
    (11, 48, "Temporal sentence markers (heute, morgen, gestern, jetzt)",
        ["vocabulary"],
        ["Use common time adverbs to anchor sentences in past, present, and future reference",
         "Combine temporal markers with present-tense sentences to imply time naturally"],
        ["Time expressions (Uhrzeit)"]),

    # ── Module 12: Preposition System ────────────────────────────────────────
    (12, 49, "Locative prepositions (in, auf, an, bei, neben)",
        ["grammar"],
        ["Use the five most common locative prepositions to describe position and location",
         "Produce simple location sentences: Das Buch liegt auf dem Tisch"],
        ["Accusative case (direct object role)"]),
    (12, 50, "Functional prepositions (mit, für, von, zu)",
        ["grammar"],
        ["Use mit (with), für (for), von (from/of), and zu (to) in basic sentence contexts",
         "Distinguish the meaning changes these prepositions introduce"],
        ["Locative prepositions (in, auf, an, bei, neben)"]),
    (12, 51, "Preposition + accusative awareness (für, durch, ohne)",
        ["grammar"],
        ["Identify that für, durch, and ohne always trigger accusative case on the following noun phrase",
         "Apply accusative article forms after these prepositions in basic sentences"],
        ["Functional prepositions (mit, für, von, zu)", "der → den transformation"]),
    (12, 52, "Spatial relationship sentences",
        ["skill"],
        ["Produce accurate sentences describing the spatial relationship between objects and people",
         "Use location prepositions to give and understand directions at A1 level"],
        ["Preposition + accusative awareness (für, durch, ohne)"]),
    (12, 53, "Functional sentence linking with prepositions",
        ["skill"],
        ["Link clauses and phrases using prepositions to express purpose, origin, and accompaniment",
         "Build multi-element sentences using preposition phrases without word order errors"],
        ["Spatial relationship sentences"]),

    # ── Module 13: Modal Verb System ──────────────────────────────────────────
    (13, 54, "können (ability)",
        ["grammar"],
        ["Conjugate können across all persons and use it to express ability and possibility",
         "Form sentences with können + infinitive in correct verb-final position"],
        ["Regular verb conjugation (-en verbs)"]),
    (13, 55, "müssen / dürfen (necessity and permission)",
        ["grammar"],
        ["Conjugate müssen and dürfen and distinguish necessity from permission/prohibition",
         "Use müssen and dürfen + infinitive in sentences without verb-position errors"],
        ["können (ability)"]),
    (13, 56, "wollen / möchten (desire and preference)",
        ["grammar"],
        ["Conjugate wollen and möchten and use them to express wants and preferences",
         "Distinguish wollen (strong desire) from möchten (polite wish) in real contexts"],
        ["müssen / dürfen (necessity and permission)"]),
    (13, 57, "Verb cluster positioning (modal + infinitive final)",
        ["grammar"],
        ["Place the infinitive at the end of the clause after a modal verb automatically",
         "Produce full modal sentences — Ich kann Deutsch sprechen — without verb-placement errors"],
        ["wollen / möchten (desire and preference)", "Verb-second (V2) rule mastery"]),

    # ── Module 14: Everyday Communication System ─────────────────────────────
    (14, 58, "Greetings & introductions",
        ["communication"],
        ["Use formal and informal German greetings and farewells appropriately",
         "Introduce yourself and ask for others' names, origin, and occupation"],
        ["Informal vs formal address (du vs Sie)"]),
    (14, 59, "Ordering food and drink",
        ["communication"],
        ["Order food and drink in a restaurant or café using polite German",
         "Ask about the menu, state preferences, and pay using ich hätte gern and ich möchte"],
        ["wollen / möchten (desire and preference)"]),
    (14, 60, "Shopping interactions",
        ["communication"],
        ["Ask for items, state sizes and quantities, ask prices, and complete a purchase in German",
         "Use wie viel kostet, ich nehme, and haben Sie in shopping contexts"],
        ["Ordering food and drink", "Numbers 0–100+"]),
    (14, 61, "Asking for directions",
        ["communication"],
        ["Ask for and understand basic directions using links, rechts, geradeaus, and landmark references",
         "Produce polite direction-seeking questions and respond to direction-giving"],
        ["Spatial relationship sentences"]),
    (14, 62, "Polite expressions",
        ["communication"],
        ["Use bitte, danke, entschuldigung, es tut mir leid, and other politeness markers naturally",
         "Apply politeness levels (formal/informal) consistently throughout an interaction"],
        ["Greetings & introductions"]),

    # ── Module 15: Descriptive Language System ───────────────────────────────
    (15, 63, "Basic adjectives (gut, groß, klein, alt, neu, schön)",
        ["vocabulary"],
        ["Produce and understand the 15 most common German descriptive adjectives",
         "Use adjectives predicatively (Das Haus ist groß) without inflection errors"],
        ["Noun-number agreement"]),
    (15, 64, "Predicate adjective sentences",
        ["grammar"],
        ["Form sentences using adjectives predicatively with sein and werden",
         "Apply predicate adjectives correctly without case inflection at A1 level"],
        ["Basic adjectives (gut, groß, klein, alt, neu, schön)"]),
    (15, 65, "Attributive adjective introduction (nominative only)",
        ["grammar"],
        ["Produce adjectives in attributive position with nominative case endings",
         "Apply -e/-er/-es endings for nominative attributive adjectives with definite articles"],
        ["Predicate adjective sentences", "Nominative case (subject role)"]),
    (15, 66, "Simple descriptive sentences",
        ["skill"],
        ["Produce multi-element descriptive sentences combining noun, article, adjective, and verb",
         "Describe people, objects, and places using German adjectives in natural speech"],
        ["Attributive adjective introduction (nominative only)"]),

    # ── Module 16: Functional Sentence Patterns (Survival Blocks) ────────────
    (16, 67, "Ich hätte gern… / Ich möchte…",
        ["communication"],
        ["Use ich hätte gern and ich möchte as automatic request formulas in service interactions",
         "Distinguish the register of these two forms and apply them appropriately"],
        ["Ordering food and drink"]),
    (16, 68, "Können Sie mir helfen? / Entschuldigung…",
        ["communication"],
        ["Use können Sie mir helfen and entschuldigung as automatic help-seeking openers",
         "Extend these openers with specific requests using modal and present-tense structures"],
        ["Polite expressions", "können (ability)"]),
    (16, 69, "Wie viel kostet das? / Was kostet…?",
        ["communication"],
        ["Ask about prices using wie viel kostet and was kostet as automatic formulas",
         "Understand and respond to price information in shopping and service contexts"],
        ["Shopping interactions"]),
    (16, 70, "Ich komme aus… / Ich wohne in…",
        ["communication"],
        ["Use ich komme aus and ich wohne in as automatic self-introduction formulas",
         "Extend these patterns to ask about others' origin and residence"],
        ["Greetings & introductions"]),
    (16, 71, "Fixed survival block automation",
        ["skill"],
        ["Deploy all A1 fixed-expression survival blocks automatically under real conversation pressure",
         "Combine survival blocks with core grammar patterns to handle novel real-world A1 situations"],
        ["Ich hätte gern… / Ich möchte…", "Können Sie mir helfen? / Entschuldigung…",
         "Wie viel kostet das? / Was kostet…?", "Ich komme aus… / Ich wohne in…"]),
]


def seed_german_a1_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for German CEFR A1.
    Two-pass: Pass 1 inserts nodes, Pass 2 resolves prereq topic names → IDs
    across ALL German CEFR nodes.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'de'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("German language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'A1', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _GERMAN_A1_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _GERMAN_A1_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'CEFR', 'A1', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _GERMAN_A1_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'CEFR' AND level = 'A1' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] German A1 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── German CEFR A2 curriculum ───────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_GERMAN_A2_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Past Tense Foundation (Perfekt)",      "Talk about past experiences in everyday spoken German",                        5),
    (2,  "Präteritum Introduction",              "Recognise written past tense in simple texts",                                 4),
    (3,  "Time Expression & Story Sequencing",   "Narrate simple chronological events",                                          6),
    (4,  "Modal Verbs Expansion",                "Express ability, obligation, permission, and intention at A2 depth",           6),
    (5,  "Reflexive Verbs (Daily Life Core)",    "Describe personal daily routines naturally",                                   5),
    (6,  "Case System Expansion",                "Use basic case distinction in real communication",                             6),
    (7,  "Prepositions + Case Mapping",          "Use prepositions naturally with correct case",                                 6),
    (8,  "Comparisons & Adjective Inflection",   "Compare people, objects, and situations",                                     5),
    (9,  "Subordinate Clauses",                  "Connect ideas into complex sentences",                                         4),
    (10, "Negation Expansion",                   "Express absence, denial, and contradiction correctly",                         4),
    (11, "Everyday Communication Scenarios",     "Function independently in real-life situations",                               5),
    (12, "Describing People, Life & Habits",     "Describe self and others in detail",                                           4),
    (13, "Pronouns Expansion",                   "Avoid repetition and sound more natural",                                      4),
    (14, "Writing Skills Foundation",            "Produce connected written German",                                             4),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_GERMAN_A2_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 1: Past Tense Foundation (Perfekt) ─────────────────────────────
    (1, 1, "Perfekt (spoken past mastery)",
        ["grammar"],
        ["Understand that Perfekt is the standard spoken past tense in German",
         "Produce Perfekt sentences using haben/sein + past participle automatically"],
        ["sein / haben conjugation"]),
    (1, 2, "Regular past participles (ge- + stem + -t)",
        ["grammar"],
        ["Form regular past participles using the ge-…-t pattern (machen → gemacht)",
         "Produce regular Perfekt sentences without pausing to recall the participle form"],
        ["Perfekt (spoken past mastery)"]),
    (1, 3, "Irregular past participles",
        ["grammar"],
        ["Produce the 20 most common irregular past participles (gehen → gegangen, essen → gegessen)",
         "Store irregular participles as paired units with their infinitive in memory"],
        ["Regular past participles (ge- + stem + -t)"]),
    (1, 4, "haben vs sein auxiliary selection",
        ["grammar"],
        ["Select haben or sein as the Perfekt auxiliary based on verb type",
         "Apply the motion/change-of-state rule for sein verbs automatically"],
        ["Irregular past participles"]),
    (1, 5, "Basic past narration",
        ["skill"],
        ["Narrate a simple sequence of past events using Perfekt in natural spoken German",
         "Combine regular and irregular participles with correct auxiliary selection in extended speech"],
        ["haben vs sein auxiliary selection"]),

    # ── Module 2: Präteritum Introduction ─────────────────────────────────────
    (2, 6, "sein → war (Präteritum)",
        ["grammar"],
        ["Produce and recognise war (I/he/she was) and waren (we/they were) in the Präteritum",
         "Use war and waren in written and formal spoken contexts"],
        ["sein / haben conjugation"]),
    (2, 7, "haben → hatte (Präteritum)",
        ["grammar"],
        ["Produce and recognise hatte and hatten in the Präteritum",
         "Use hatte in written and formal spoken past reference"],
        ["sein → war (Präteritum)"]),
    (2, 8, "Modal Präteritum (konnte, musste, wollte, durfte)",
        ["grammar"],
        ["Produce the Präteritum forms of können, müssen, wollen, and dürfen",
         "Prefer modal Präteritum over Perfekt for modals in both spoken and written German"],
        ["haben → hatte (Präteritum)", "Verb cluster positioning (modal + infinitive final)"]),
    (2, 9, "Recognition vs production distinction",
        ["skill"],
        ["Identify which verbs are typically Präteritum-preferred vs Perfekt-preferred",
         "Read Präteritum forms in simple texts with full comprehension without producing errors"],
        ["Modal Präteritum (konnte, musste, wollte, durfte)"]),

    # ── Module 3: Time Expression & Story Sequencing ──────────────────────────
    (3, 10, "Past time adverbs (gestern, letzte Woche, letzten Monat)",
        ["vocabulary"],
        ["Use gestern, vorgestern, letzte Woche, letzten Monat, and letztes Jahr in past sentences",
         "Combine past time adverbs with Perfekt to anchor narration in specific time"],
        ["Temporal sentence markers (heute, morgen, gestern, jetzt)"]),
    (3, 11, "vor + time expressions",
        ["grammar"],
        ["Use vor + dative time phrase (vor drei Tagen, vor einer Woche) to express elapsed time",
         "Distinguish vor (ago) from seit (since/for) in time expression contexts"],
        ["Past time adverbs (gestern, letzte Woche, letzten Monat)"]),
    (3, 12, "Future time expressions (morgen, nächste Woche, bald)",
        ["vocabulary"],
        ["Use morgen, übermorgen, nächste Woche, nächsten Monat, and bald in future sentences",
         "Combine future time adverbs with present tense or werden to express future plans"],
        ["vor + time expressions"]),
    (3, 13, "Sequencing markers (zuerst, dann, danach, später, schließlich)",
        ["vocabulary"],
        ["Use zuerst, dann, danach, später, and schließlich to sequence events in a narrative",
         "Produce naturally flowing chronological narration using sequencing markers with Perfekt"],
        ["Basic past narration", "Future time expressions (morgen, nächste Woche, bald)"]),
    (3, 14, "Temporal connectors (bevor, nachdem — introduction)",
        ["grammar"],
        ["Use bevor (before) and nachdem (after) to link two events in time",
         "Recognise the verb-final subordinate clause triggered by bevor and nachdem"],
        ["Sequencing markers (zuerst, dann, danach, später, schließlich)"]),
    (3, 15, "Simple chronological narration",
        ["skill"],
        ["Produce a 5–8 sentence spoken or written narrative describing a sequence of past events",
         "Use time adverbs, sequencing markers, and Perfekt together fluently"],
        ["Temporal connectors (bevor, nachdem — introduction)"]),

    # ── Module 4: Modal Verbs Expansion ───────────────────────────────────────
    (4, 16, "können (A2 expansion)",
        ["grammar"],
        ["Use können to express general and context-specific ability at A2 complexity",
         "Form können sentences with reflexive verbs, separable verbs, and object phrases"],
        ["können (ability)"]),
    (4, 17, "müssen (A2 expansion)",
        ["grammar"],
        ["Use müssen to express necessity, logical deduction, and strong obligation",
         "Distinguish nicht müssen (don't have to) from nicht dürfen (must not)"],
        ["müssen / dürfen (necessity and permission)"]),
    (4, 18, "wollen / möchten (A2 expansion)",
        ["grammar"],
        ["Use wollen and möchten to express plans, desires, and polite requests at A2 level",
         "Combine wollen/möchten with infinitive phrases in extended sentences"],
        ["wollen / möchten (desire and preference)"]),
    (4, 19, "dürfen (A2 expansion)",
        ["grammar"],
        ["Use dürfen to express permission and prohibition in real social contexts",
         "Produce nicht dürfen for prohibition accurately and distinguish it from nicht müssen"],
        ["müssen (A2 expansion)"]),
    (4, 20, "sollen (obligation from external source)",
        ["grammar"],
        ["Use sollen to express an obligation or instruction given by another person",
         "Distinguish sollen (told to by someone else) from müssen (internal necessity)"],
        ["dürfen (A2 expansion)"]),
    (4, 21, "Modal verb sentence structure automation",
        ["skill"],
        ["Produce all five modals with infinitive-final placement automatically under conversation speed",
         "Switch between modals mid-sentence to adjust meaning without word order errors"],
        ["sollen (obligation from external source)", "Verb cluster positioning (modal + infinitive final)"]),

    # ── Module 5: Reflexive Verbs (Daily Life Core) ───────────────────────────
    (5, 22, "Reflexive pronouns (mich, dich, sich, uns, euch)",
        ["grammar"],
        ["Produce the accusative reflexive pronouns for all persons",
         "Place reflexive pronouns correctly after the conjugated verb in main clauses"],
        ["Subject pronouns (ich, du, er/sie/es, wir, ihr, Sie)"]),
    (5, 23, "Core reflexive verbs (sich waschen, sich anziehen, sich setzen)",
        ["vocabulary"],
        ["Conjugate and use the 10 most frequent daily-routine reflexive verbs",
         "Produce reflexive verb sentences automatically for morning and evening routine descriptions"],
        ["Reflexive pronouns (mich, dich, sich, uns, euch)"]),
    (5, 24, "Emotional reflexive verbs (sich freuen, sich ärgern, sich fühlen)",
        ["vocabulary"],
        ["Use emotional reflexive verbs to express feelings and reactions",
         "Combine emotional reflexives with über + accusative and auf + accusative"],
        ["Core reflexive verbs (sich waschen, sich anziehen, sich setzen)"]),
    (5, 25, "Interest and engagement reflexives (sich interessieren, sich beschäftigen)",
        ["vocabulary"],
        ["Use sich interessieren für and sich beschäftigen mit to express interests",
         "Produce natural statements about personal interests using reflexive + preposition patterns"],
        ["Emotional reflexive verbs (sich freuen, sich ärgern, sich fühlen)"]),
    (5, 26, "Daily routine narration with reflexives",
        ["skill"],
        ["Produce a complete A2-level daily routine description using reflexive verbs throughout",
         "Combine reflexive verbs with time expressions and sequencing markers fluently"],
        ["Interest and engagement reflexives (sich interessieren, sich beschäftigen)", "Simple chronological narration"]),

    # ── Module 6: Case System Expansion (Accusative + Dative) ────────────────
    (6, 27, "Accusative review (den / einen / keinen)",
        ["grammar"],
        ["Produce masculine accusative forms den, einen, and keinen automatically in full sentences",
         "Self-correct nominative/accusative confusion for masculine nouns under conversation speed"],
        ["der → den transformation"]),
    (6, 28, "Dative introduction (dem / einem / keinem)",
        ["grammar"],
        ["Identify the dative case as the indirect object role in German sentences",
         "Produce dative article forms dem (m/n) and der (f) in basic indirect object contexts"],
        ["Accusative review (den / einen / keinen)"]),
    (6, 29, "Dative verbs (helfen, geben, zeigen, sagen, erklären)",
        ["grammar"],
        ["Identify and use the five most common dative-taking verbs with correct case marking",
         "Produce double-object sentences (Ich gebe dem Mann das Buch) without case errors"],
        ["Dative introduction (dem / einem / keinem)"]),
    (6, 30, "Indirect object sentence structure",
        ["skill"],
        ["Produce sentences with both a dative indirect object and an accusative direct object",
         "Order dative and accusative noun phrases correctly when both appear in the same sentence"],
        ["Dative verbs (helfen, geben, zeigen, sagen, erklären)"]),
    (6, 31, "Feminine and plural dative forms",
        ["grammar"],
        ["Produce dative forms for feminine nouns (der Frau) and plural nouns (den Kindern + -n)",
         "Apply the plural dative -n suffix rule consistently"],
        ["Indirect object sentence structure"]),
    (6, 32, "Case distinction in real communication",
        ["skill"],
        ["Select nominative, accusative, or dative automatically based on sentence role",
         "Self-monitor case errors in real-time speech without disrupting fluency"],
        ["Feminine and plural dative forms", "Sentence role identification"]),

    # ── Module 7: Prepositions + Case Mapping ─────────────────────────────────
    (7, 33, "Accusative prepositions (für, durch, ohne, gegen)",
        ["grammar"],
        ["Identify that für, durch, ohne, and gegen always take accusative case",
         "Produce accusative-marked noun phrases after these four prepositions automatically"],
        ["Preposition + accusative awareness (für, durch, ohne)", "Accusative review (den / einen / keinen)"]),
    (7, 34, "Dative prepositions (mit, bei, nach, seit, von, zu)",
        ["grammar"],
        ["Identify that mit, bei, nach, seit, von, and zu always take dative case",
         "Produce dative-marked noun phrases after these six prepositions automatically"],
        ["Dative introduction (dem / einem / keinem)"]),
    (7, 35, "Contraction forms (zum, zur, beim, vom, im, ins)",
        ["grammar"],
        ["Produce the standard preposition + article contractions automatically",
         "Apply contractions in natural speech without pausing to recall the full form"],
        ["Accusative prepositions (für, durch, ohne, gegen)", "Dative prepositions (mit, bei, nach, seit, von, zu)"]),
    (7, 36, "Two-way prepositions — location (Dative)",
        ["grammar"],
        ["Use in, auf, an, über, unter, vor, hinter, neben, zwischen with dative for static location",
         "Produce Wo? (dative) questions and answers automatically"],
        ["Contraction forms (zum, zur, beim, vom, im, ins)"]),
    (7, 37, "Two-way prepositions — direction (Accusative)",
        ["grammar"],
        ["Use in, auf, an, etc. with accusative for directional movement",
         "Distinguish Wo? (dative) from Wohin? (accusative) and apply the correct case"],
        ["Two-way prepositions — location (Dative)"]),
    (7, 38, "seit + dative (duration since a point in time)",
        ["grammar"],
        ["Use seit + dative to express an action that started in the past and continues now",
         "Distinguish seit (since/for with present tense) from vor (ago with past tense)"],
        ["Two-way prepositions — direction (Accusative)", "vor + time expressions"]),

    # ── Module 8: Comparisons & Adjective Inflection ──────────────────────────
    (8, 39, "Komparativ formation (größer, schneller, besser)",
        ["grammar"],
        ["Form comparative adjectives using the -er suffix and apply umlaut where required",
         "Produce the irregular comparatives (gut → besser, viel → mehr, gern → lieber) automatically"],
        ["Basic adjectives (gut, groß, klein, alt, neu, schön)"]),
    (8, 40, "Superlativ formation (am größten, am besten)",
        ["grammar"],
        ["Form superlative adjectives using am …-sten and the irregular forms",
         "Use superlatives predicatively in statements about extreme qualities"],
        ["Komparativ formation (größer, schneller, besser)"]),
    (8, 41, "Comparison structures (so … wie / als)",
        ["grammar"],
        ["Use so … wie for equality comparisons and als for inequality comparisons correctly",
         "Produce both comparison types automatically without als/wie confusion"],
        ["Superlativ formation (am größten, am besten)"]),
    (8, 42, "Attributive adjective inflection (nominative + accusative)",
        ["grammar"],
        ["Apply adjective endings for nominative and accusative cases with definite and indefinite articles",
         "Produce attributive adjective phrases without ending omission errors"],
        ["Attributive adjective introduction (nominative only)", "Accusative review (den / einen / keinen)"]),
    (8, 43, "Adjective comparison in context",
        ["skill"],
        ["Use comparative and superlative adjectives attributively and predicatively in real sentences",
         "Produce natural comparison sentences describing people, places, and objects"],
        ["Comparison structures (so … wie / als)", "Attributive adjective inflection (nominative + accusative)"]),

    # ── Module 9: Subordinate Clauses ─────────────────────────────────────────
    (9, 44, "weil (verb-final subordinate clause)",
        ["grammar"],
        ["Form weil-clauses with the conjugated verb moved to final position",
         "Produce weil-sentences automatically to give reasons without verb-position errors"],
        ["Verb-second (V2) rule mastery"]),
    (9, 45, "dass (complement clause)",
        ["grammar"],
        ["Form dass-clauses with verb-final word order after main clause verbs like sagen, glauben, wissen",
         "Use dass-clauses to report speech, beliefs, and facts in natural German"],
        ["weil (verb-final subordinate clause)"]),
    (9, 46, "wenn (conditional / temporal)",
        ["grammar"],
        ["Use wenn to express both conditional (if) and repeated temporal (when/whenever) meanings",
         "Form wenn-clauses with verb-final order and attach them to main clauses correctly"],
        ["dass (complement clause)"]),
    (9, 47, "Subordinate clause automation",
        ["skill"],
        ["Produce weil, dass, and wenn clauses automatically under real conversation speed",
         "Self-correct verb-final placement errors in subordinate clauses without disrupting fluency"],
        ["wenn (conditional / temporal)"]),

    # ── Module 10: Negation Expansion ────────────────────────────────────────
    (10, 48, "Negation expansion: nicht vs kein review",
        ["grammar"],
        ["Distinguish nicht (verb/adjective/adverb negation) from kein (noun negation) consistently",
         "Self-correct nicht/kein confusion errors in real-time production"],
        ["Negation placement rules"]),
    (10, 49, "Negation in Perfekt sentences",
        ["grammar"],
        ["Place nicht correctly in Perfekt sentences (before past participle)",
         "Produce negated Perfekt sentences without word order disruption"],
        ["Negation expansion: nicht vs kein review", "Basic past narration"]),
    (10, 50, "Negation in modal verb sentences",
        ["grammar"],
        ["Place nicht correctly in modal verb sentences (before the infinitive)",
         "Produce nicht müssen (don't have to) and nicht dürfen (must not) accurately"],
        ["Negation in Perfekt sentences", "Modal verb sentence structure automation"]),
    (10, 51, "Negation in subordinate clauses",
        ["grammar"],
        ["Apply negation in verb-final subordinate clauses without disrupting clause-final position",
         "Produce naturally negated weil, dass, and wenn clauses fluently"],
        ["Negation in modal verb sentences", "Subordinate clause automation"]),

    # ── Module 11: Everyday Communication Scenarios ───────────────────────────
    (11, 52, "Shopping at A2 level",
        ["communication"],
        ["Handle complete shopping interactions: browsing, asking for sizes/colours, price negotiation, payment",
         "Use comparative adjectives, accusative objects, and polite expressions in shopping contexts"],
        ["Comparison structures (so … wie / als)", "Shopping interactions"]),
    (11, 53, "Restaurant conversations at A2 level",
        ["communication"],
        ["Order food and drink, ask about ingredients, make complaints, and pay in German",
         "Use ich hätte gern, ich möchte, and könnte ich in restaurant interactions fluently"],
        ["Ordering food and drink", "können (A2 expansion)"]),
    (11, 54, "Doctor and pharmacy visits",
        ["communication"],
        ["Describe symptoms, understand basic medical instructions, and ask clarifying questions",
         "Use body vocabulary, seit + dative for duration, and modal verbs in medical contexts"],
        ["seit + dative (duration since a point in time)", "Everyday Communication System"]),
    (11, 55, "Travel situations (tickets, hotels, transport)",
        ["communication"],
        ["Book tickets, check in, ask about transport options, and handle travel problems in German",
         "Use two-way prepositions, direction vocabulary, and modal verbs in travel contexts"],
        ["Two-way prepositions — direction (Accusative)", "Doctor and pharmacy visits"]),
    (11, 56, "Appointment booking and scheduling",
        ["communication"],
        ["Make, change, and cancel appointments by phone or in person in German",
         "Use time expressions, modal verbs, and polite request forms in scheduling interactions"],
        ["Time expressions (Uhrzeit)", "Travel situations (tickets, hotels, transport)"]),

    # ── Module 12: Describing People, Life & Habits ───────────────────────────
    (12, 57, "Appearance vocabulary",
        ["vocabulary"],
        ["Produce vocabulary for describing physical appearance: height, build, hair, eyes, clothing",
         "Use adjective + noun phrases and predicate adjectives to describe appearance naturally"],
        ["Attributive adjective inflection (nominative + accusative)"]),
    (12, 58, "Personality traits vocabulary",
        ["vocabulary"],
        ["Produce the 20 most common personality adjectives in German",
         "Use personality vocabulary in sentences with sein, wirken, and scheinen"],
        ["Appearance vocabulary"]),
    (12, 59, "Routines and frequency expressions (immer, oft, manchmal, selten, nie)",
        ["vocabulary"],
        ["Use frequency adverbs accurately to describe how often something happens",
         "Place frequency adverbs correctly in German sentences"],
        ["Daily routine narration with reflexives"]),
    (12, 60, "Emotional states vocabulary",
        ["vocabulary"],
        ["Produce vocabulary for emotions and feelings: froh, traurig, aufgeregt, müde, gestresst",
         "Describe emotional states using sein + adjective and emotional reflexive verbs"],
        ["Emotional reflexive verbs (sich freuen, sich ärgern, sich fühlen)", "Personality traits vocabulary"]),

    # ── Module 13: Pronouns Expansion (Object + Dative) ──────────────────────
    (13, 61, "Accusative object pronouns (mich, dich, ihn, sie, es, uns, euch, sie)",
        ["grammar"],
        ["Produce accusative personal pronouns for all persons and genders",
         "Replace accusative noun phrases with pronouns automatically to avoid repetition"],
        ["Accusative review (den / einen / keinen)"]),
    (13, 62, "Dative object pronouns (mir, dir, ihm, ihr, uns, euch, ihnen)",
        ["grammar"],
        ["Produce dative personal pronouns for all persons",
         "Use dative pronouns after dative verbs and dative prepositions automatically"],
        ["Dative verbs (helfen, geben, zeigen, sagen, erklären)", "Accusative object pronouns (mich, dich, ihn, sie, es, uns, euch, sie)"]),
    (13, 63, "Pronoun ordering (dative before accusative)",
        ["grammar"],
        ["Apply the rule: dative pronoun precedes accusative pronoun in the German middle field",
         "Produce sentences with two pronouns (Ich gebe es ihm) without ordering errors"],
        ["Dative object pronouns (mir, dir, ihm, ihr, uns, euch, ihnen)"]),
    (13, 64, "Pronoun substitution in natural speech",
        ["skill"],
        ["Replace full noun phrases with correct pronouns automatically in connected speech",
         "Self-monitor for pronoun case and gender errors in real-time conversation"],
        ["Pronoun ordering (dative before accusative)"]),

    # ── Module 14: Writing Skills Foundation ─────────────────────────────────
    (14, 65, "Short messages and texts (SMS/WhatsApp style)",
        ["skill"],
        ["Write short informal messages in German using A2 vocabulary and grammar",
         "Apply appropriate informal register and common message conventions"],
        ["Negation in subordinate clauses"]),
    (14, 66, "Informal emails",
        ["skill"],
        ["Write a complete informal email in German with greeting, body, and closing",
         "Use subordinate clauses, Perfekt, and A2 vocabulary to produce connected email prose"],
        ["Short messages and texts (SMS/WhatsApp style)"]),
    (14, 67, "Personal stories (written Perfekt narration)",
        ["skill"],
        ["Write a 100–150 word personal anecdote using Perfekt and sequencing markers",
         "Maintain narrative coherence and tense consistency throughout a written story"],
        ["Simple chronological narration", "Informal emails"]),
    (14, 68, "Simple narrative structure",
        ["skill"],
        ["Produce a structured short narrative with introduction, events, and conclusion in German",
         "Use all A2 grammar systems — Perfekt, subordinate clauses, pronouns, case — in written output"],
        ["Personal stories (written Perfekt narration)", "Pronoun substitution in natural speech"]),
]


def seed_german_a2_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for German CEFR A2.
    Two-pass: Pass 1 inserts nodes, Pass 2 resolves prereq topic names → IDs
    across ALL German CEFR nodes so A1 topics can be used as prereqs.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'de'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("German language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'A2', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _GERMAN_A2_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _GERMAN_A2_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'CEFR', 'A2', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _GERMAN_A2_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] German A2 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── German CEFR B1 curriculum ───────────────────────────────────────────────

_GERMAN_B1_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Narrative Mastery (Past Tense Integration)",  "Tell clear, structured stories about past experiences",                         5),
    (2,  "Separable & Inseparable Verbs",               "Master prefix verb behaviour across all clause types",                          4),
    (3,  "Advanced Sentence Structure",                  "Build longer, logically connected sentences",                                   5),
    (4,  "zu-Infinitive Constructions",                  "Express purpose, intent, and complement clauses using zu-infinitives",          4),
    (5,  "Modal System Expansion",                       "Express obligation, advice, and intention with full nuance",                    5),
    (6,  "Relative Clauses",                             "Describe people and things with detail and precision",                         5),
    (7,  "Full Adjective Declension System",             "Produce correct adjective endings across all cases and article types",         5),
    (8,  "Genitiv Case",                                 "Use genitive case for possession and with genitive prepositions",              4),
    (9,  "Passive Voice",                                "Understand and produce passive structures in present and past",                5),
    (10, "Indirect Speech",                              "Report information naturally using reported speech structures",                4),
    (11, "Konjunktiv II System",                         "Express hypothetical reasoning, politeness, and unreal conditions",           5),
    (12, "Future & Conditional Expansion",               "Talk about future plans, predictions, and hypothetical conditions",           4),
    (13, "Opinion & Argument Language",                  "Express and defend opinions with structured reasoning",                       5),
    (14, "Connectors & Discourse Flow",                  "Speak in flowing, logically connected discourse",                            5),
    (15, "Verb + Preposition Combinations",              "Use fixed verb-preposition pairings naturally",                               5),
    (16, "Time & Abstract Expression",                   "Express complex time relationships naturally",                                5),
    (17, "Everyday Life Expansion",                      "Handle real-world situations with confidence",                                5),
    (18, "Vocabulary Expansion Domains",                 "Expand beyond daily survival topics",                                         4),
    (19, "Writing Development",                          "Write connected multi-paragraph text",                                        5),
    (20, "Listening & Reading Growth",                   "Move beyond textbook German into real input",                                 4),
    (21, "Conversation Fluency",                         "Sustain natural conversations for minutes at a time",                         5),
]

_GERMAN_B1_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 1: Narrative Mastery (Past Tense Integration) ──────────────────
    (1, 1, "Perfekt vs Präteritum contrast",
        ["grammar"],
        ["Distinguish spoken (Perfekt) from written/formal (Präteritum) past tense registers automatically",
         "Select the appropriate past tense form based on context, medium, and register"],
        ["Basic past narration", "Modal Präteritum (konnte, musste, wollte, durfte)"]),
    (1, 2, "Storytelling fluency across tenses",
        ["skill"],
        ["Narrate a complete story using Perfekt, Präteritum, and present tense naturally",
         "Sustain tense consistency within each register without shifting mid-narrative"],
        ["Perfekt vs Präteritum contrast"]),
    (1, 3, "Narrative sequencing (multi-event chains)",
        ["skill"],
        ["Chain five or more past events in sequence using tense and time markers together",
         "Produce natural multi-event narratives without losing chronological clarity"],
        ["Simple chronological narration", "Storytelling fluency across tenses"]),
    (1, 4, "Time anchoring in stories (damals, währenddessen, später)",
        ["vocabulary"],
        ["Use damals, währenddessen, inzwischen, später, and unterdessen to anchor events in a story",
         "Apply these time anchors to control narrative pacing and temporal layering"],
        ["Narrative sequencing (multi-event chains)"]),
    (1, 5, "Plusquamperfekt (past perfect introduction)",
        ["grammar"],
        ["Form the Plusquamperfekt using hatte/war + past participle to express the earlier of two past events",
         "Use Plusquamperfekt to establish background events before a main narrative moment"],
        ["Time anchoring in stories (damals, währenddessen, später)", "haben vs sein auxiliary selection"]),

    # ── Module 2: Separable & Inseparable Verbs ───────────────────────────────
    (2, 6, "Separable verbs: prefix detachment in main clauses",
        ["grammar"],
        ["Detach the prefix of separable verbs and move it to final position in main clauses",
         "Produce aufstehen, anrufen, mitkommen, anfangen with correct prefix placement automatically"],
        ["Verb-second (V2) rule mastery"]),
    (2, 7, "Common separable verbs (aufstehen, anrufen, mitkommen, anfangen, ausgehen)",
        ["vocabulary"],
        ["Conjugate and use the 15 most frequent separable verbs in present and Perfekt tenses",
         "Form Perfekt with separable verbs: ge- inserted between prefix and stem (aufgestanden)"],
        ["Separable verbs: prefix detachment in main clauses"]),
    (2, 8, "Inseparable prefixes (be-, ge-, er-, ver-, ent-, zer-)",
        ["grammar"],
        ["Identify inseparable verb prefixes that never detach and have no ge- in Perfekt",
         "Produce Perfekt forms of inseparable verbs without incorrectly adding ge- (verstehen → verstanden)"],
        ["Common separable verbs (aufstehen, anrufen, mitkommen, anfangen, ausgehen)"]),
    (2, 9, "Separable verbs in subordinate clauses",
        ["grammar"],
        ["Keep the prefix attached in subordinate clauses where the full verb moves to final position",
         "Produce correct separable verb placement in weil, dass, and wenn clauses automatically"],
        ["Inseparable prefixes (be-, ge-, er-, ver-, ent-, zer-)", "Subordinate clause automation"]),

    # ── Module 3: Advanced Sentence Structure ─────────────────────────────────
    (3, 10, "Subordinate clause review and extension (weil, dass, wenn)",
        ["grammar"],
        ["Produce weil, dass, and wenn clauses with automatic verb-final placement at B1 speed",
         "Extend A2 clause types with greater lexical complexity and embedded noun phrases"],
        ["Subordinate clause automation"]),
    (3, 11, "obwohl (concessive clause)",
        ["grammar"],
        ["Form obwohl-clauses to express concession (even though) with verb-final word order",
         "Use obwohl to contrast two ideas — acknowledging an obstacle while asserting a conclusion"],
        ["Subordinate clause review and extension (weil, dass, wenn)"]),
    (3, 12, "als vs wenn (single past event vs repeated/present)",
        ["grammar"],
        ["Use als for single completed past events and wenn for repeated or present/future conditions",
         "Self-correct als/wenn confusion in natural speech without slowing down"],
        ["obwohl (concessive clause)"]),
    (3, 13, "Multi-clause sentence construction",
        ["skill"],
        ["Build sentences containing two or more subordinate clauses linked to a main clause",
         "Maintain verb-final order in each subordinate clause independently when stacking clauses"],
        ["als vs wenn (single past event vs repeated/present)"]),
    (3, 14, "Sentence embedding (clause within clause)",
        ["skill"],
        ["Produce sentences where one subordinate clause is embedded inside another",
         "Parse and produce two-level embedded clause structures without word order errors"],
        ["Multi-clause sentence construction"]),

    # ── Module 4: zu-Infinitive Constructions ─────────────────────────────────
    (4, 15, "zu + infinitive (basic infinitive clause)",
        ["grammar"],
        ["Form infinitive clauses with zu placed immediately before the infinitive",
         "Use zu-infinitive clauses after verbs like versuchen, hoffen, beginnen, planen"],
        ["Sentence embedding (clause within clause)"]),
    (4, 16, "um…zu (purpose clauses)",
        ["grammar"],
        ["Form um…zu clauses to express purpose (in order to)",
         "Produce um…zu clauses with the correct subject-sharing constraint"],
        ["zu + infinitive (basic infinitive clause)"]),
    (4, 17, "ohne…zu / anstatt…zu",
        ["grammar"],
        ["Use ohne…zu (without doing) and anstatt…zu (instead of doing) accurately",
         "Produce these negative and substitution infinitive clauses in natural spoken and written German"],
        ["um…zu (purpose clauses)"]),
    (4, 18, "Verbs taking zu-infinitive (versuchen, hoffen, vergessen, anfangen)",
        ["vocabulary"],
        ["Identify and use the 12 most common verbs that take a zu-infinitive complement",
         "Produce zu-infinitive clauses automatically after these verbs without pausing"],
        ["ohne…zu / anstatt…zu", "Separable verbs: prefix detachment in main clauses"]),

    # ── Module 5: Modal System Expansion ──────────────────────────────────────
    (5, 19, "Modal verbs: full nuance usage (B1)",
        ["grammar"],
        ["Use all five modals to express nuanced shades of obligation, ability, permission, and desire",
         "Distinguish near-synonymous modals (müssen vs sollen, können vs dürfen) in context"],
        ["Modal verb sentence structure automation"]),
    (5, 20, "Obligation vs advice vs expectation (müssen vs sollen vs sollte)",
        ["grammar"],
        ["Distinguish müssen (internal necessity), sollen (external instruction), and sollte (advice/expectation)",
         "Select the correct modal automatically based on the source and strength of the obligation"],
        ["Modal verbs: full nuance usage (B1)"]),
    (5, 21, "man sollte / man kann / man muss (generalised social pressure)",
        ["grammar"],
        ["Use man + modal to express generalised social norms, expectations, and possibilities",
         "Produce man-modal sentences to give advice, state norms, and describe social expectations"],
        ["Obligation vs advice vs expectation (müssen vs sollen vs sollte)"]),
    (5, 22, "Modal verbs in Perfekt (hat … müssen / haben … können)",
        ["grammar"],
        ["Form modal Perfekt using haben + infinitive + modal infinitive (double infinitive construction)",
         "Produce Ich habe gehen müssen and similar double-infinitive sentences accurately"],
        ["man sollte / man kann / man muss (generalised social pressure)", "Plusquamperfekt (past perfect introduction)"]),
    (5, 23, "Modal particles (doch, mal, ja, eigentlich, wohl)",
        ["grammar"],
        ["Use the five most common German modal particles to add nuance, softening, and stance",
         "Place modal particles correctly in the German middle field without disrupting word order"],
        ["Modal verbs in Perfekt (hat … müssen / haben … können)"]),

    # ── Module 6: Relative Clauses ─────────────────────────────────────────────
    (6, 24, "Relative clauses: nominative and accusative (der/die/das)",
        ["grammar"],
        ["Form relative clauses using der, die, das as relative pronouns in nominative and accusative",
         "Produce relative clauses with correct pronoun gender/number agreement and verb-final order"],
        ["Case distinction in real communication"]),
    (6, 25, "Relative clauses in dative (dem/der/denen)",
        ["grammar"],
        ["Form relative clauses where the relative pronoun is in dative case",
         "Produce dative relative pronouns dem (m/n), der (f), and denen (plural) accurately"],
        ["Relative clauses: nominative and accusative (der/die/das)", "Dative introduction (dem / einem / keinem)"]),
    (6, 26, "wo / was / wer as relative pronouns",
        ["grammar"],
        ["Use wo (place antecedent), was (indefinite/das antecedent), and wer (person without antecedent) as relative pronouns",
         "Select the correct non-standard relative pronoun based on the antecedent type"],
        ["Relative clauses in dative (dem/der/denen)"]),
    (6, 27, "Clause embedding for noun modification",
        ["skill"],
        ["Attach relative clauses to noun phrases to create precise descriptions",
         "Produce fluent noun + relative clause combinations without insertion-point errors"],
        ["wo / was / wer as relative pronouns", "Sentence embedding (clause within clause)"]),
    (6, 28, "Natural noun modification chains",
        ["skill"],
        ["Build noun phrases with both attributive adjectives and relative clauses",
         "Produce complex NPs in natural speech without over-long hesitation pauses"],
        ["Clause embedding for noun modification"]),

    # ── Module 7: Full Adjective Declension System ────────────────────────────
    (7, 29, "Weak adjective declension (definite article + adjective, all cases)",
        ["grammar"],
        ["Produce weak adjective endings (-e/-en) across all four cases with definite articles",
         "Apply weak declension automatically in all nominative, accusative, dative, and genitive contexts"],
        ["Attributive adjective introduction (nominative only)"]),
    (7, 30, "Mixed adjective declension (indefinite article + adjective, all cases)",
        ["grammar"],
        ["Produce mixed adjective endings across all four cases with indefinite articles and kein/mein",
         "Distinguish when an ending must carry case information (strong slot) vs follow weak pattern"],
        ["Weak adjective declension (definite article + adjective, all cases)"]),
    (7, 31, "Strong adjective declension (no article)",
        ["grammar"],
        ["Produce strong adjective endings when no article precedes the noun",
         "Apply strong endings that carry the full case signal independently of any article"],
        ["Mixed adjective declension (indefinite article + adjective, all cases)"]),
    (7, 32, "Adjective declension across all four cases",
        ["skill"],
        ["Select the correct declension pattern (weak/mixed/strong) automatically based on the determiner",
         "Self-correct adjective ending errors in real-time speech without disrupting fluency"],
        ["Strong adjective declension (no article)", "Feminine and plural dative forms"]),
    (7, 33, "Adjective declension automation",
        ["skill"],
        ["Produce attributive adjective phrases in any case without conscious rule retrieval",
         "Use adjective phrases in relative clauses, genitive constructions, and prepositional phrases"],
        ["Adjective declension across all four cases"]),

    # ── Module 8: Genitiv Case ─────────────────────────────────────────────────
    (8, 34, "Genitiv case introduction (des/der/eines/einer)",
        ["grammar"],
        ["Identify and produce definite and indefinite genitive article forms for all genders",
         "Use genitive noun phrases to express possession in formal written and spoken German"],
        ["Adjective declension automation"]),
    (8, 35, "Masculine/neuter genitive noun ending (-s/-es suffix)",
        ["grammar"],
        ["Add the -s or -es suffix to masculine and neuter nouns in genitive case",
         "Apply -es before nouns ending in sibilants and in monosyllables automatically"],
        ["Genitiv case introduction (des/der/eines/einer)"]),
    (8, 36, "Possessive genitive in noun phrases (das Haus meines Vaters)",
        ["skill"],
        ["Produce genitive noun phrases expressing ownership and relationship naturally",
         "Prefer genitive over von + dative in formal writing contexts"],
        ["Masculine/neuter genitive noun ending (-s/-es suffix)"]),
    (8, 37, "Genitiv prepositions (wegen, trotz, während, innerhalb, außerhalb)",
        ["grammar"],
        ["Identify that wegen, trotz, während, innerhalb, and außerhalb govern genitive case",
         "Produce noun phrases in genitive after these five prepositions automatically"],
        ["Possessive genitive in noun phrases (das Haus meines Vaters)"]),

    # ── Module 9: Passive Voice ────────────────────────────────────────────────
    (9, 38, "werden passive: present tense (wird gemacht)",
        ["grammar"],
        ["Form the present passive using wird/werden + past participle",
         "Transform active sentences into passive and identify the agent with von + dative"],
        ["Regular past participles (ge- + stem + -t)", "Irregular past participles"]),
    (9, 39, "werden passive: Präteritum (wurde gemacht)",
        ["grammar"],
        ["Form the past passive using wurde/wurden + past participle",
         "Use the past passive in written narratives and formal reporting"],
        ["werden passive: present tense (wird gemacht)", "sein → war (Präteritum)"]),
    (9, 40, "Active vs passive transformation",
        ["skill"],
        ["Transform any active sentence into its passive equivalent and vice versa",
         "Identify when passive is preferred (agent unknown/unimportant) and apply it appropriately"],
        ["werden passive: Präteritum (wurde gemacht)"]),
    (9, 41, "Impersonal passive (es wird getanzt / man wird gebeten)",
        ["grammar"],
        ["Form impersonal passives for subjectless events and generalised actions",
         "Use impersonal passive in social norms and formal announcements"],
        ["Active vs passive transformation"]),
    (9, 42, "sein-passive (state passive: ist geöffnet)",
        ["grammar"],
        ["Distinguish the sein-passive (resultant state) from the werden-passive (process)",
         "Use sein + past participle to describe the result of a completed action"],
        ["Impersonal passive (es wird getanzt / man wird gebeten)"]),

    # ── Module 10: Indirect Speech ─────────────────────────────────────────────
    (10, 43, "Reported speech with dass-clauses",
        ["grammar"],
        ["Use dass-clauses to report what someone said, thought, or believed",
         "Apply verb-final order in the dass-clause and match the tense to the reporting context"],
        ["dass (complement clause)"]),
    (10, 44, "Reported questions (ob-clauses)",
        ["grammar"],
        ["Use ob-clauses to report yes/no questions in indirect speech",
         "Form ob-clauses with verb-final order and distinguish them from direct questions"],
        ["Reported speech with dass-clauses"]),
    (10, 45, "Konjunktiv I: introduction (er sei, er habe, er werde)",
        ["grammar"],
        ["Recognise Konjunktiv I forms of sein, haben, and werden in written reported speech",
         "Produce basic Konjunktiv I forms for formal/journalistic indirect speech contexts"],
        ["Reported questions (ob-clauses)"]),
    (10, 46, "Summarising and paraphrasing what others said",
        ["skill"],
        ["Summarise a conversation or text using reported speech structures naturally",
         "Paraphrase using laut + dative, zufolge, and nach + dative as reported speech introducers"],
        ["Konjunktiv I: introduction (er sei, er habe, er werde)"]),

    # ── Module 11: Konjunktiv II System ───────────────────────────────────────
    (11, 47, "Konjunktiv II: würde + infinitive",
        ["grammar"],
        ["Form hypothetical and polite statements using würde + infinitive for most verbs",
         "Use würde constructions as the standard Konjunktiv II in everyday spoken German"],
        ["Modal verb sentence structure automation"]),
    (11, 48, "Konjunktiv II: hätte and wäre (past hypothetical)",
        ["grammar"],
        ["Produce hätte and wäre as the Konjunktiv II forms of haben and sein",
         "Use hätte + past participle and wäre + past participle to describe unreal past situations"],
        ["Konjunktiv II: würde + infinitive", "haben vs sein auxiliary selection"]),
    (11, 49, "Konjunktiv II modal forms (könnte, müsste, sollte, dürfte)",
        ["grammar"],
        ["Produce Konjunktiv II forms of the four main modals automatically",
         "Distinguish Konjunktiv II modals from their indicative counterparts in context"],
        ["Konjunktiv II: hätte and wäre (past hypothetical)"]),
    (11, 50, "Hypothetical reasoning (wenn…dann + Konjunktiv II)",
        ["grammar"],
        ["Form wenn-clauses with Konjunktiv II to express unreal conditions and their consequences",
         "Produce Wenn ich Zeit hätte, würde ich… sentences automatically"],
        ["Konjunktiv II modal forms (könnte, müsste, sollte, dürfte)"]),
    (11, 51, "Polite requests and wishes with Konjunktiv II",
        ["communication"],
        ["Use Konjunktiv II to soften requests and express wishes politely",
         "Produce Könnten Sie…, Ich hätte gern…, and Dürfte ich… in formal and informal contexts"],
        ["Hypothetical reasoning (wenn…dann + Konjunktiv II)"]),

    # ── Module 12: Future & Conditional Expansion ─────────────────────────────
    (12, 52, "werden + infinitive (Futur I)",
        ["grammar"],
        ["Form the future tense using werden + infinitive for all persons",
         "Use Futur I for predictions, promises, and future plans in formal contexts"],
        ["Regular verb conjugation (-en verbs)"]),
    (12, 53, "Present tense as future (with time markers)",
        ["grammar"],
        ["Use present tense + future time marker as the natural spoken German future",
         "Distinguish when present-as-future is preferred over Futur I"],
        ["werden + infinitive (Futur I)", "Temporal sentence markers (heute, morgen, gestern, jetzt)"]),
    (12, 54, "wenn-clauses for future conditions (B1)",
        ["grammar"],
        ["Form wenn-clauses with present tense to express real future conditions",
         "Distinguish real future wenn-conditions from Konjunktiv II unreal wenn-conditions"],
        ["Present tense as future (with time markers)", "wenn (conditional / temporal)"]),
    (12, 55, "Predictions vs intentions: werden vs wollen vs möchten",
        ["skill"],
        ["Select werden (prediction/promise), wollen (strong intention), or möchten (wish) based on meaning",
         "Produce future-reference sentences with the correct modal or tense form automatically"],
        ["wenn-clauses for future conditions (B1)"]),

    # ── Module 13: Opinion & Argument Language ────────────────────────────────
    (13, 56, "Opinion starters (ich denke, ich glaube, meiner Meinung nach)",
        ["communication"],
        ["Use ich denke, ich glaube, meiner Meinung nach, and ich finde as natural opinion openers",
         "Vary opinion starters to avoid repetition in extended spoken or written argument"],
        ["Subordinate clause review and extension (weil, dass, wenn)"]),
    (13, 57, "Agreement and disagreement language",
        ["communication"],
        ["Express agreement and disagreement with natural German phrases across formal and informal registers",
         "Respond to others' opinions with Stimmt, Das sehe ich anders, Ich bin anderer Meinung naturally"],
        ["Opinion starters (ich denke, ich glaube, meiner Meinung nach)"]),
    (13, 58, "Justification structures (weil vs denn)",
        ["grammar"],
        ["Distinguish weil (verb-final subordinating conjunction) from denn (coordinating, V2 kept)",
         "Use weil and denn accurately to give reasons in both formal and informal contexts"],
        ["Agreement and disagreement language"]),
    (13, 59, "Structured opinion (introduction → reason → conclusion)",
        ["skill"],
        ["Produce a three-part opinion statement: position, supporting reason, concluding sentence",
         "Use opinion starters, weil/denn, and conclusion markers (deshalb, also) in a structured output"],
        ["Justification structures (weil vs denn)"]),
    (13, 60, "Concession in argument (zwar…aber, obwohl)",
        ["skill"],
        ["Use zwar…aber and obwohl to acknowledge counterpoints while maintaining a position",
         "Integrate concession structures into structured opinions to produce balanced argument"],
        ["Structured opinion (introduction → reason → conclusion)", "obwohl (concessive clause)"]),

    # ── Module 14: Connectors & Discourse Flow ────────────────────────────────
    (14, 61, "Causal connectors (deshalb, deswegen, darum)",
        ["vocabulary"],
        ["Use deshalb, deswegen, and darum as result/conclusion connectors in V2 position",
         "Distinguish causal connectors (deshalb) from causal subordinators (weil) in production"],
        ["Justification structures (weil vs denn)"]),
    (14, 62, "Adversative connectors (trotzdem, jedoch, allerdings)",
        ["vocabulary"],
        ["Use trotzdem, jedoch, and allerdings to introduce a contrasting or unexpected result",
         "Place these connectors in V2 position or after the subject without word order errors"],
        ["Causal connectors (deshalb, deswegen, darum)"]),
    (14, 63, "Additive connectors (außerdem, zusätzlich, darüber hinaus)",
        ["vocabulary"],
        ["Use außerdem, zusätzlich, and darüber hinaus to add supporting points in an argument",
         "Produce multi-point arguments by chaining additive connectors with new information"],
        ["Adversative connectors (trotzdem, jedoch, allerdings)"]),
    (14, 64, "Temporal subordinators at B1 level (seitdem, während, sobald)",
        ["grammar"],
        ["Use seitdem, während, and sobald as temporal subordinating conjunctions with verb-final order",
         "Distinguish seitdem (since then), während (while/whereas), and sobald (as soon as) in context"],
        ["Additive connectors (außerdem, zusätzlich, darüber hinaus)", "Temporal connectors (bevor, nachdem — introduction)"]),
    (14, 65, "Discourse flow in extended speech",
        ["skill"],
        ["Link clauses and sentences into extended spoken discourse using the full B1 connector inventory",
         "Produce two-minute+ monologues with natural logical and temporal flow"],
        ["Temporal subordinators at B1 level (seitdem, während, sobald)"]),

    # ── Module 15: Verb + Preposition Combinations ────────────────────────────
    (15, 66, "Accusative verb-preposition pairs (warten auf, denken an, sich freuen auf)",
        ["vocabulary"],
        ["Produce the 10 most common accusative verb-preposition combinations automatically",
         "Use these pairs in full sentences without preposition-selection errors"],
        ["Accusative prepositions (für, durch, ohne, gegen)", "Interest and engagement reflexives (sich interessieren, sich beschäftigen)"]),
    (15, 67, "Dative verb-preposition pairs (gehören zu, bestehen aus, leiden unter)",
        ["vocabulary"],
        ["Produce the 10 most common dative verb-preposition combinations automatically",
         "Use leiden unter, profitieren von, teilnehmen an, and similar in natural sentences"],
        ["Dative prepositions (mit, bei, nach, seit, von, zu)", "Accusative verb-preposition pairs (warten auf, denken an, sich freuen auf)"]),
    (15, 68, "da-compounds (darauf, davon, damit, daran, darüber)",
        ["grammar"],
        ["Form da-compounds by combining da- with a preposition to replace prepositional phrases with non-human referents",
         "Use da-compounds naturally to avoid repeating full prepositional phrases in discourse"],
        ["Dative verb-preposition pairs (gehören zu, bestehen aus, leiden unter)"]),
    (15, 69, "wo-compounds for questions (worauf, wovon, womit, woran)",
        ["grammar"],
        ["Form wo-compounds to ask about prepositional objects (Worauf wartest du?)",
         "Use wo-compounds automatically instead of auf + was / von + was in standard German"],
        ["da-compounds (darauf, davon, damit, daran, darüber)"]),
    (15, 70, "Verb-preposition automation in natural speech",
        ["skill"],
        ["Deploy verb-preposition pairs, da-compounds, and wo-compounds fluently under conversation speed",
         "Self-correct preposition-selection and da-/wo-compound errors in real-time"],
        ["wo-compounds for questions (worauf, wovon, womit, woran)"]),

    # ── Module 16: Time & Abstract Expression ─────────────────────────────────
    (16, 71, "seitdem + present tense (B1 duration expression)",
        ["grammar"],
        ["Use seitdem + present tense to express an action that started in the past and continues now",
         "Distinguish seitdem (subordinator) from seit (preposition) in sentence structure"],
        ["seit + dative (duration since a point in time)", "Temporal subordinators at B1 level (seitdem, während, sobald)"]),
    (16, 72, "sobald (as soon as — immediate sequence)",
        ["grammar"],
        ["Use sobald to express that one event happens immediately after another",
         "Form sobald-clauses with future or present tense to express a trigger-response chain"],
        ["seitdem + present tense (B1 duration expression)"]),
    (16, 73, "während (simultaneous events in extended discourse)",
        ["grammar"],
        ["Use während as both a temporal (while) and adversative (whereas) subordinator",
         "Distinguish the two meanings of während from context and use each deliberately"],
        ["sobald (as soon as — immediate sequence)"]),
    (16, 74, "Abstract time structures (je…desto, kaum…als)",
        ["grammar"],
        ["Form je…desto (the more…the more) comparative time structures",
         "Use kaum…als (hardly…when) to express near-simultaneous past events"],
        ["während (simultaneous events in extended discourse)"]),
    (16, 75, "Frequency vs duration distinction (wie oft vs wie lange)",
        ["skill"],
        ["Produce and respond to wie oft (frequency) and wie lange (duration) questions accurately",
         "Use frequency and duration expressions together to describe habits and events precisely"],
        ["Abstract time structures (je…desto, kaum…als)", "Routines and frequency expressions (immer, oft, manchmal, selten, nie)"]),

    # ── Module 17: Everyday Life Expansion ───────────────────────────────────
    (17, 76, "Extended health and medical conversations (B1)",
        ["communication"],
        ["Describe symptoms in detail, understand diagnoses, ask for explanations, and discuss treatment options",
         "Use passive voice, modal verbs, and B1 vocabulary in medical consultation contexts"],
        ["Doctor and pharmacy visits"]),
    (17, 77, "Work routines and professional vocabulary",
        ["vocabulary"],
        ["Produce B1-level vocabulary for workplace contexts: tasks, colleagues, meetings, deadlines",
         "Use professional German in work-related conversations and short written messages"],
        ["Extended health and medical conversations (B1)"]),
    (17, 78, "Housing and living situations vocabulary",
        ["vocabulary"],
        ["Produce vocabulary for renting, buying, describing a home, and dealing with neighbours",
         "Use housing vocabulary in complaint, inquiry, and description contexts"],
        ["Work routines and professional vocabulary"]),
    (17, 79, "Bureaucracy basics (forms, appointments, official language)",
        ["communication"],
        ["Navigate German bureaucratic language: forms, official letters, and administrative appointments",
         "Understand and produce formal register in official communication contexts"],
        ["Housing and living situations vocabulary", "Appointment booking and scheduling"]),
    (17, 80, "Problem-solving dialogues",
        ["communication"],
        ["Handle unexpected problems in German: complaints, misunderstandings, requests for help",
         "Use Konjunktiv II, modal particles, and polite indirect language in problem-resolution scenarios"],
        ["Bureaucracy basics (forms, appointments, official language)", "Polite requests and wishes with Konjunktiv II"]),

    # ── Module 18: Vocabulary Expansion Domains ───────────────────────────────
    (18, 81, "Education and learning vocabulary",
        ["vocabulary"],
        ["Produce B1-level vocabulary for school, university, learning, and qualifications",
         "Use education vocabulary in descriptions, comparisons, and opinion contexts"],
        ["Problem-solving dialogues"]),
    (18, 82, "Technology and media vocabulary",
        ["vocabulary"],
        ["Produce vocabulary for digital technology, social media, news media, and communication tools",
         "Use technology and media vocabulary in discussion and opinion texts"],
        ["Education and learning vocabulary"]),
    (18, 83, "Environment and nature vocabulary",
        ["vocabulary"],
        ["Produce B1-level vocabulary for environment, climate, nature, and ecological topics",
         "Use environment vocabulary in argument and opinion texts"],
        ["Technology and media vocabulary"]),
    (18, 84, "Travel, culture, and society vocabulary",
        ["vocabulary"],
        ["Produce vocabulary for travel, cultural practices, social issues, and community",
         "Use this domain vocabulary in structured opinions and extended descriptions"],
        ["Environment and nature vocabulary"]),

    # ── Module 19: Writing Development ───────────────────────────────────────
    (19, 85, "Structured paragraph writing",
        ["skill"],
        ["Write a coherent paragraph with a topic sentence, supporting detail, and concluding sentence",
         "Maintain thematic focus and sentence-level cohesion across a 100–150 word paragraph"],
        ["Simple narrative structure"]),
    (19, 86, "Informal emails (B1 level)",
        ["skill"],
        ["Write B1-level informal emails using subordinate clauses, Konjunktiv II, and connectors",
         "Produce natural-sounding informal emails with appropriate register and structure"],
        ["Structured paragraph writing"]),
    (19, 87, "Simple formal messages and letters",
        ["skill"],
        ["Write formal German letters and messages using correct opening/closing formulas and formal register",
         "Apply formal vocabulary and passive constructions in complaint, request, and inquiry letters"],
        ["Informal emails (B1 level)"]),
    (19, 88, "Describing experiences in detail (B1 written)",
        ["skill"],
        ["Write 150–200 word experience descriptions using Perfekt, Präteritum, and sequencing markers",
         "Maintain narrative tense consistency and use time anchors throughout a written account"],
        ["Simple formal messages and letters", "Perfekt vs Präteritum contrast"]),
    (19, 89, "Opinion paragraphs",
        ["skill"],
        ["Write a structured opinion paragraph with position, justification, concession, and conclusion",
         "Integrate connectors, opinion starters, and argument language into a coherent written opinion"],
        ["Describing experiences in detail (B1 written)", "Structured opinion (introduction → reason → conclusion)"]),

    # ── Module 20: Listening & Reading Growth ────────────────────────────────
    (20, 90, "Slower native speech comprehension (B1)",
        ["skill"],
        ["Comprehend native German speech at reduced speed (e.g. news broadcasts, podcasts) with full understanding",
         "Identify main ideas and supporting details in authentic slower-paced spoken German"],
        ["Discourse flow in extended speech"]),
    (20, 91, "Simple news articles and reports",
        ["skill"],
        ["Read B1-level news articles and extract key information about events, people, and issues",
         "Distinguish factual reporting from opinion and identify text structure in German news texts"],
        ["Slower native speech comprehension (B1)"]),
    (20, 92, "Extracting key information from texts",
        ["skill"],
        ["Locate and extract specific information from B1-level written texts efficiently",
         "Scan and skim German texts for relevant details without reading every word"],
        ["Simple news articles and reports"]),
    (20, 93, "Inference from context in real input",
        ["skill"],
        ["Infer the meaning of unfamiliar words and implied information from surrounding context",
         "Sustain comprehension in authentic B1 input despite encountering unknown vocabulary"],
        ["Extracting key information from texts"]),

    # ── Module 21: Conversation Fluency ──────────────────────────────────────
    (21, 94, "Extended dialogues at B1 level",
        ["communication"],
        ["Sustain a conversation on a B1 topic for two or more minutes without major breakdowns",
         "Manage topic transitions, respond to unexpected questions, and maintain coherence"],
        ["Problem-solving dialogues", "Discourse flow in extended speech"]),
    (21, 95, "Giving explanations and elaborating",
        ["communication"],
        ["Expand single-sentence answers into multi-sentence explanations using connectors and subordinate clauses",
         "Avoid one-word answers by using also, nämlich, und zwar, and weil to elaborate naturally"],
        ["Extended dialogues at B1 level"]),
    (21, 96, "Asking follow-up questions naturally",
        ["communication"],
        ["Ask natural follow-up questions to maintain conversation and show engagement",
         "Use Inwiefern, Was meinst du damit, Kannst du das erklären and similar clarification prompts"],
        ["Giving explanations and elaborating"]),
    (21, 97, "Handling misunderstandings (clarification strategies)",
        ["communication"],
        ["Use clarification strategies when you don't understand: Wie bitte, Könnten Sie das wiederholen, Ich verstehe nicht ganz",
         "Rephrase your own utterances when a communication breakdown occurs"],
        ["Asking follow-up questions naturally"]),
    (21, 98, "Sustained conversation flow at B1 level",
        ["skill"],
        ["Sustain a 5-minute unscripted conversation using all B1 grammar and vocabulary systems",
         "Monitor and self-repair fluency breakdowns without losing the conversational thread"],
        ["Handling misunderstandings (clarification strategies)", "Opinion paragraphs"]),
]


def seed_german_b1_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for German CEFR B1.
    Two-pass: Pass 1 inserts nodes, Pass 2 resolves prereq topic names → IDs
    across ALL German CEFR nodes so A1/A2 topics can be used as prereqs.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'de'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("German language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'B1', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _GERMAN_B1_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _GERMAN_B1_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'CEFR', 'B1', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _GERMAN_B1_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] German B1 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── German CEFR B2 curriculum ───────────────────────────────────────────────

_GERMAN_B2_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Advanced Grammar System Integration",       "Control grammar flexibly, not mechanically",                                      6),
    (2,  "Complex Subordinate Clause Systems",         "Build and control long, natural sentences without breaking flow",                 5),
    (3,  "Partizipialattribute",                       "Compress dense information into natural German noun phrases",                     4),
    (4,  "Passive & Impersonal Mastery",               "Describe events objectively and formally across all tenses",                     5),
    (5,  "Konjunktiv I (Full System)",                 "Produce Konjunktiv I fluently in journalistic and formal contexts",              5),
    (6,  "Reported Speech & Information Transfer",     "Accurately transmit information, ideas, and opinions",                           5),
    (7,  "Argumentation & Critical Expression",        "Debate, argue, and explain ideas clearly",                                       5),
    (8,  "Advanced Connectors & Discourse Architecture","Produce structured, professional speech and writing",                           5),
    (9,  "Relative Clause Mastery",                    "Pack dense meaning into natural sentences",                                      5),
    (10, "Modal Nuance & Epistemic Language",          "Express uncertainty, probability, and inference naturally",                       5),
    (11, "Wortbildung (Word Formation)",               "Expand vocabulary through morphological awareness",                              5),
    (12, "Extended Genitiv & Complex Noun Phrases",   "Use genitive in formal, complex, and multi-layer noun constructions",            4),
    (13, "Professional & Academic Communication",      "Function in workplace and academic environments",                                5),
    (14, "Real-World Interaction Mastery",             "Handle real-life German environments confidently",                               5),
    (15, "Reading Comprehension (Authentic Input)",    "Understand real German media beyond simplified texts",                           5),
    (16, "Writing Mastery",                            "Write structured, persuasive multi-paragraph texts",                             5),
    (17, "Listening Comprehension (Natural Speed)",    "Understand real spoken German in natural conditions",                            4),
    (18, "Stylistic Control (Fluency Layer)",          "Sound flexible, not repetitive or textbook-like",                                5),
    (19, "Abstract & Societal Topics",                 "Discuss complex topics with clarity and structure",                              5),
    (20, "Conversation Mastery (Extended Fluency)",    "Sustain natural conversation for long periods",                                  5),
]

_GERMAN_B2_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 1: Advanced Grammar System Integration ─────────────────────────
    (1, 1, "Full tense interplay at B2 (all tenses in context)",
        ["grammar"],
        ["Deploy all German tenses — Präsens, Perfekt, Präteritum, Plusquamperfekt, Futur I — fluidly in a single narrative",
         "Select the stylistically appropriate tense for each context without conscious deliberation"],
        ["Storytelling fluency across tenses", "Plusquamperfekt (past perfect introduction)"]),
    (1, 2, "Futur II (Ich werde es gemacht haben)",
        ["grammar"],
        ["Form Futur II using werden + past participle + haben/sein for all verbs",
         "Use Futur II for completed-future predictions and confident assertions about past events"],
        ["Full tense interplay at B2 (all tenses in context)", "haben vs sein auxiliary selection"]),
    (1, 3, "Stylistic tense choice (spoken vs written vs narrative register)",
        ["grammar"],
        ["Choose tense based on register — Perfekt for spoken, Präteritum for written, with deliberate stylistic intent",
         "Switch tense register mid-text to control narrative tone without inconsistency"],
        ["Futur II (Ich werde es gemacht haben)"]),
    (1, 4, "Complex sentence restructuring (inversion and emphasis shifting)",
        ["grammar"],
        ["Use fronting and inversion to shift emphasis and create information-structure contrast",
         "Produce emphasis inversions (Erst jetzt verstand er…, Kaum hatte er…) naturally"],
        ["Stylistic tense choice (spoken vs written vs narrative register)", "Discourse flow in extended speech"]),
    (1, 5, "Nominalisation expansion (verbal to nominal style)",
        ["grammar"],
        ["Transform verb-heavy spoken sentences into nominally-dense formal written German",
         "Reverse-transform nominal academic prose back into spoken equivalents"],
        ["Complex sentence restructuring (inversion and emphasis shifting)"]),
    (1, 6, "n-Deklination mastery (der Mensch → dem Menschen)",
        ["grammar"],
        ["Identify all masculine n-Deklination nouns and apply the -(e)n suffix in all non-nominative cases",
         "Self-correct n-Deklination errors in Herr, Mensch, Kollege, Name automatically"],
        ["Adjective declension automation"]),

    # ── Module 2: Complex Subordinate Clause Systems ──────────────────────────
    (2, 7, "Advanced weil / dass / wenn at B2 nuance level",
        ["grammar"],
        ["Use weil, dass, and wenn with the full range of B2-level lexical and structural complexity",
         "Embed these clause types within other subordinate clauses without word order errors"],
        ["Subordinate clause review and extension (weil, dass, wenn)"]),
    (2, 8, "Concessive and temporal clause chains (obwohl, während, sobald, nachdem, bevor)",
        ["grammar"],
        ["Chain concessive and temporal subordinate clauses fluidly in extended discourse",
         "Maintain verb-final order in each clause independently across multi-clause sequences"],
        ["Advanced weil / dass / wenn at B2 nuance level", "Temporal subordinators at B1 level (seitdem, während, sobald)"]),
    (2, 9, "Multi-clause dependency chains",
        ["skill"],
        ["Produce sentences with three or more layered subordinate clauses without collapsing into fragments",
         "Parse multi-clause sentences in real input and replicate their structure in production"],
        ["Concessive and temporal clause chains (obwohl, während, sobald, nachdem, bevor)"]),
    (2, 10, "Sentence compression vs expansion strategies",
        ["skill"],
        ["Compress complex ideas into single dense sentences and expand them into flowing multi-clause prose",
         "Control information density deliberately based on audience and register"],
        ["Multi-clause dependency chains", "Nominalisation expansion (verbal to nominal style)"]),
    (2, 11, "Long-form spoken syntax control",
        ["skill"],
        ["Sustain grammatical accuracy across 20+ word spoken sentences without restructuring mid-utterance",
         "Recover from syntactic errors mid-sentence without restarting"],
        ["Sentence compression vs expansion strategies"]),

    # ── Module 3: Partizipialattribute ────────────────────────────────────────
    (3, 12, "Present participle as attributive modifier (das laufende Projekt)",
        ["grammar"],
        ["Form present participle attributive phrases by adding -d to the infinitive and inflecting as an adjective",
         "Use present participial attributes for ongoing processes and active states"],
        ["Long-form spoken syntax control"]),
    (3, 13, "Past participle as attributive modifier (das beschlossene Gesetz)",
        ["grammar"],
        ["Form past participial attributes by inflecting the past participle as an adjective",
         "Use past participial attributes for completed actions and resultant states"],
        ["Present participle as attributive modifier (das laufende Projekt)"]),
    (3, 14, "Extended participial phrases (das gestern verabschiedete Gesetz)",
        ["grammar"],
        ["Build extended participial phrases by inserting adverbs, objects, and prepositional phrases before the participle",
         "Recognise and parse extended participial attributes in German newspaper and academic texts"],
        ["Past participle as attributive modifier (das beschlossene Gesetz)"]),
    (3, 15, "Partizipialattribut vs relative clause (compression choice)",
        ["skill"],
        ["Choose between a participial attribute and a relative clause based on register and information density",
         "Transform relative clauses into participial attributes and vice versa in both directions"],
        ["Extended participial phrases (das gestern verabschiedete Gesetz)", "Natural noun modification chains"]),

    # ── Module 4: Passive & Impersonal Mastery ────────────────────────────────
    (4, 16, "werden-passive across all tenses (Präsens to Futur II)",
        ["grammar"],
        ["Form the werden-passive in all six tenses including Futur I and Futur II",
         "Select the correct tense of werden automatically when passivising any active sentence"],
        ["werden passive: Präteritum (wurde gemacht)", "Full tense interplay at B2 (all tenses in context)"]),
    (4, 17, "sein-passive mastery (resultant state in full context)",
        ["grammar"],
        ["Use sein-passive consistently to describe resultant states across formal registers",
         "Distinguish werden-passive (process) from sein-passive (state) in ambiguous contexts"],
        ["sein-passive (state passive: ist geöffnet)", "werden-passive across all tenses (Präsens to Futur II)"]),
    (4, 18, "Impersonal and agentless passive (B2 mastery)",
        ["grammar"],
        ["Produce impersonal passives with and without es for subjectless events",
         "Use agentless passive to suppress the agent deliberately in formal and neutral reporting"],
        ["sein-passive mastery (resultant state in full context)"]),
    (4, 19, "Formal written passive usage (news, academic, official)",
        ["grammar"],
        ["Apply passive constructions in formal written genres: reports, articles, official documents",
         "Maintain stylistic consistency when using passive across an extended formal text"],
        ["Impersonal and agentless passive (B2 mastery)"]),
    (4, 20, "Neutral reporting style with passive constructions",
        ["skill"],
        ["Produce extended neutral reporting using passive, nominalisation, and impersonal constructions",
         "Write or speak about events without assigning agency, matching formal news register"],
        ["Formal written passive usage (news, academic, official)"]),

    # ── Module 5: Konjunktiv I (Full System) ──────────────────────────────────
    (5, 21, "Konjunktiv I formation (all verbs, all persons)",
        ["grammar"],
        ["Form Konjunktiv I for all regular and irregular verbs across all six persons",
         "Identify when Konjunktiv II substitutes for Konjunktiv I when forms are identical to indicative"],
        ["Konjunktiv I: introduction (er sei, er habe, er werde)"]),
    (5, 22, "Konjunktiv I in journalistic reported speech",
        ["skill"],
        ["Use Konjunktiv I to report speech in newspaper articles and news broadcasts",
         "Produce journalistic reported speech that signals non-commitment to the reported content"],
        ["Konjunktiv I formation (all verbs, all persons)"]),
    (5, 23, "Konjunktiv I vs Konjunktiv II disambiguation",
        ["grammar"],
        ["Choose between Konjunktiv I and Konjunktiv II for indirect speech when forms collide",
         "Apply the rule: use Konjunktiv II when Konjunktiv I is identical to the indicative form"],
        ["Konjunktiv I in journalistic reported speech", "Konjunktiv II: würde + infinitive"]),
    (5, 24, "Konjunktiv I in academic and legal texts",
        ["skill"],
        ["Read and produce Konjunktiv I in academic papers, legal documents, and official statements",
         "Sustain Konjunktiv I consistently across a full formal text without reverting to indicative"],
        ["Konjunktiv I vs Konjunktiv II disambiguation"]),
    (5, 25, "Konjunktiv I production under pressure",
        ["skill"],
        ["Produce Konjunktiv I in spoken reported speech without hesitation",
         "Self-correct Konjunktiv I form errors in real-time formal speech"],
        ["Konjunktiv I in academic and legal texts"]),

    # ── Module 6: Reported Speech & Information Transfer ──────────────────────
    (6, 26, "Indirect speech with dass and ob (B2 depth)",
        ["grammar"],
        ["Report complex multi-clause statements using dass and ob at full B2 complexity",
         "Embed reported questions, commands, and statements within a single extended passage"],
        ["Summarising and paraphrasing what others said", "Konjunktiv I production under pressure"]),
    (6, 27, "Question embedding in indirect speech",
        ["grammar"],
        ["Embed direct questions as indirect ob-clauses or WH-word subordinate clauses",
         "Transform any direct question into its indirect equivalent without word order errors"],
        ["Indirect speech with dass and ob (B2 depth)"]),
    (6, 28, "Tense backshifting in formal reported speech",
        ["grammar"],
        ["Apply systematic tense backshifting when reporting past speech in formal written German",
         "Use Konjunktiv I and Konjunktiv II consistently for tense backshifting in extended reported passages"],
        ["Question embedding in indirect speech"]),
    (6, 29, "Summarising and paraphrasing arguments (B2 level)",
        ["skill"],
        ["Summarise complex spoken or written arguments accurately in concise German prose",
         "Paraphrase while preserving the original speaker's meaning and stance"],
        ["Tense backshifting in formal reported speech"]),
    (6, 30, "Indirect reporting in formal written contexts",
        ["skill"],
        ["Produce extended passages of formal indirect reporting — meeting minutes, academic summaries, press releases",
         "Maintain Konjunktiv I and appropriate formality throughout a full indirect report"],
        ["Summarising and paraphrasing arguments (B2 level)"]),

    # ── Module 7: Argumentation & Critical Expression ─────────────────────────
    (7, 31, "Structured argument (claim → reason → evidence → conclusion)",
        ["skill"],
        ["Produce a four-stage written or spoken argument with distinct claim, reason, evidence, and conclusion",
         "Maintain logical progression without digression across all four stages"],
        ["Structured opinion (introduction → reason → conclusion)", "Concession in argument (zwar…aber, obwohl)"]),
    (7, 32, "Nuance expression (einerseits…andererseits, zwar…aber)",
        ["skill"],
        ["Use einerseits…andererseits and zwar…aber to present balanced, nuanced positions",
         "Integrate nuance markers naturally without making the argument seem indecisive"],
        ["Structured argument (claim → reason → evidence → conclusion)"]),
    (7, 33, "Counter-argument integration (B2 level)",
        ["skill"],
        ["Introduce, state, and rebut counter-arguments within a structured B2-level argument",
         "Use concession-refutation patterns to strengthen rather than weaken the main claim"],
        ["Nuance expression (einerseits…andererseits, zwar…aber)"]),
    (7, 34, "Rhetorical balancing in extended argument",
        ["skill"],
        ["Balance emotional, logical, and ethical appeals across an extended argument",
         "Adjust rhetorical weight at each stage — claim, evidence, concession, conclusion"],
        ["Counter-argument integration (B2 level)"]),
    (7, 35, "Persuasive vs neutral tone control",
        ["skill"],
        ["Switch between persuasive and neutral register deliberately within a single text",
         "Signal tone shifts explicitly using lexical and syntactic markers"],
        ["Rhetorical balancing in extended argument"]),

    # ── Module 8: Advanced Connectors & Discourse Architecture ───────────────
    (8, 36, "Logical result connectors (folglich, daher, somit, infolgedessen)",
        ["vocabulary"],
        ["Use folglich, daher, somit, and infolgedessen as formal result markers in V2 position",
         "Distinguish these four near-synonyms by register — somit and infolgedessen are more formal"],
        ["Causal connectors (deshalb, deswegen, darum)"]),
    (8, 37, "Contrast layering (dennoch, hingegen, allerdings, wohingegen)",
        ["vocabulary"],
        ["Use dennoch, hingegen, allerdings, and wohingegen to layer contrastive information",
         "Place these connectors correctly — V2 for dennoch/allerdings, clause-internal for hingegen/wohingegen"],
        ["Adversative connectors (trotzdem, jedoch, allerdings)", "Logical result connectors (folglich, daher, somit, infolgedessen)"]),
    (8, 38, "Additive and enumerative discourse markers (erstens, zweitens, abschließend)",
        ["vocabulary"],
        ["Structure multi-point arguments using ordinal discourse markers: erstens, zweitens, darüber hinaus, abschließend",
         "Apply these markers consistently to guide the reader/listener through an argument's structure"],
        ["Contrast layering (dennoch, hingegen, allerdings, wohingegen)"]),
    (8, 39, "Paragraph cohesion techniques",
        ["skill"],
        ["Use lexical chains, pronoun reference, and connector variation to create cohesive paragraphs",
         "Identify and correct cohesion breaks in written and spoken German discourse"],
        ["Additive and enumerative discourse markers (erstens, zweitens, abschließend)"]),
    (8, 40, "Discourse architecture in extended speech and writing",
        ["skill"],
        ["Structure five-paragraph or longer texts with consistent macrostructure: introduction, body, conclusion",
         "Signal discourse structure explicitly so the listener/reader can follow the argument's shape"],
        ["Paragraph cohesion techniques"]),

    # ── Module 9: Relative Clause Mastery (Full System) ───────────────────────
    (9, 41, "Prepositional relative clauses (mit dem, für die, zu dem)",
        ["grammar"],
        ["Form relative clauses where the relative pronoun is governed by a preposition",
         "Place the preposition before the relative pronoun (not at the end) automatically"],
        ["Relative clauses in dative (dem/der/denen)"]),
    (9, 42, "Advanced wo / was / wer relative pronoun usage",
        ["grammar"],
        ["Use wo, was, and wer as relative pronouns for place antecedents, indefinite referents, and person-general clauses",
         "Distinguish advanced relative pronoun choice from the simpler A2-B1 uses"],
        ["Prepositional relative clauses (mit dem, für die, zu dem)", "wo / was / wer as relative pronouns"]),
    (9, 43, "Reduced relative clauses",
        ["grammar"],
        ["Reduce full relative clauses to participial attributes when the subject matches the antecedent",
         "Identify which relative clauses can be reduced and apply the reduction accurately"],
        ["Advanced wo / was / wer relative pronoun usage", "Partizipialattribut vs relative clause (compression choice)"]),
    (9, 44, "Sentence compression via relative clause reduction",
        ["skill"],
        ["Compress extended relative clause sentences into dense participial or adjective constructions",
         "Apply relative clause reduction to produce journalism-register text compression"],
        ["Reduced relative clauses"]),
    (9, 45, "Natural relative clause embedding in discourse",
        ["skill"],
        ["Embed relative clauses in spontaneous speech without interrupting discourse flow",
         "Self-repair misplaced or unclosed relative clauses in real-time conversation"],
        ["Sentence compression via relative clause reduction"]),

    # ── Module 10: Modal Nuance & Epistemic Language ──────────────────────────
    (10, 46, "Epistemic müssen (logical deduction: das muss wahr sein)",
        ["grammar"],
        ["Use müssen in epistemic (deductive) sense to express logical necessity",
         "Distinguish epistemic müssen (must be true) from deontic müssen (must do)"],
        ["Modal verbs: full nuance usage (B1)"]),
    (10, 47, "Epistemic können (possibility: das kann sein)",
        ["grammar"],
        ["Use können in epistemic sense to express genuine possibility",
         "Distinguish epistemic können (might) from deontic können (is allowed to / is able to)"],
        ["Epistemic müssen (logical deduction: das muss wahr sein)"]),
    (10, 48, "Epistemic dürfte (probability: das dürfte stimmen)",
        ["grammar"],
        ["Use dürfte as a formal probability modal meaning 'is likely to'",
         "Apply dürfte in written and formal spoken German for hedged assertions"],
        ["Epistemic können (possibility: das kann sein)"]),
    (10, 49, "Hedging language (vielleicht, vermutlich, anscheinend, offenbar)",
        ["vocabulary"],
        ["Use hedging adverbs to express degrees of certainty from speculation to near-certainty",
         "Choose the appropriate hedging adverb based on the evidence strength being signalled"],
        ["Epistemic dürfte (probability: das dürfte stimmen)"]),
    (10, 50, "Certainty spectrum: assertion to speculation",
        ["skill"],
        ["Produce language anywhere on the certainty spectrum — from definite claim to mere guess — naturally",
         "Combine epistemic modals, hedging adverbs, and Konjunktiv II to calibrate expressed certainty"],
        ["Hedging language (vielleicht, vermutlich, anscheinend, offenbar)"]),

    # ── Module 11: Wortbildung (Word Formation) ───────────────────────────────
    (11, 51, "Verb prefix meaning shifts (ver-, ent-, be-, zer-, er- semantics)",
        ["vocabulary"],
        ["Map each inseparable prefix to its core semantic effect on verb meaning",
         "Infer the meaning of unfamiliar ver-/ent-/be-/zer-/er- verbs from root + prefix logic"],
        ["Inseparable prefixes (be-, ge-, er-, ver-, ent-, zer-)"]),
    (11, 52, "Nominal suffixes (-heit/-keit, -ung, -schaft, -tum, -ling)",
        ["vocabulary"],
        ["Identify nominal suffixes and their gender, meaning class, and register",
         "Form nouns from verbs and adjectives using the appropriate suffix productively"],
        ["Verb prefix meaning shifts (ver-, ent-, be-, zer-, er- semantics)"]),
    (11, 53, "Compound noun logic and construction",
        ["vocabulary"],
        ["Parse multi-part German compound nouns by identifying the base noun and each modifier",
         "Construct compound nouns to express novel concepts naturally in German"],
        ["Nominal suffixes (-heit/-keit, -ung, -schaft, -tum, -ling)"]),
    (11, 54, "Adjective suffixes (-lich, -ig, -isch, -los, -voll, -bar)",
        ["vocabulary"],
        ["Identify adjective suffixes and apply them to derive adjectives from nouns and verbs",
         "Infer the meaning and register of unfamiliar adjectives from their suffix"],
        ["Compound noun logic and construction"]),
    (11, 55, "Productive morphology in reading and listening",
        ["skill"],
        ["Use morphological knowledge to decode unfamiliar words in authentic German input",
         "Expand active vocabulary exponentially by applying word formation rules to known roots"],
        ["Adjective suffixes (-lich, -ig, -isch, -los, -voll, -bar)"]),

    # ── Module 12: Extended Genitiv & Complex Noun Phrases ────────────────────
    (12, 56, "Genitiv in complex noun phrases (multi-level possession chains)",
        ["grammar"],
        ["Parse and produce multi-level genitive noun phrases (die Ergebnisse der Studie der Universität)",
         "Maintain correct gender agreement across stacked genitive modifiers"],
        ["Possessive genitive in noun phrases (das Haus meines Vaters)"]),
    (12, 57, "Genitive vs von + dative: register and stylistic choice",
        ["grammar"],
        ["Choose genitive for formal written German and von + dative for spoken and informal contexts",
         "Identify register mismatches when genitive/von mixing occurs in a text"],
        ["Genitiv in complex noun phrases (multi-level possession chains)"]),
    (12, 58, "Genitiv in formal written German (news, academic, legal)",
        ["skill"],
        ["Sustain genitive construction use across a full formal text without reverting to von + dative",
         "Apply genitive prepositions (wegen, trotz, während) and noun-phrase genitives consistently"],
        ["Genitive vs von + dative: register and stylistic choice"]),
    (12, 59, "Complex NP: article + adjective + noun + genitiv modifier",
        ["skill"],
        ["Build fully-inflected complex noun phrases with multiple modifiers in correct case",
         "Produce and parse dense NPs of the type found in German legal and academic prose"],
        ["Genitiv in formal written German (news, academic, legal)", "Adjective declension automation"]),

    # ── Module 13: Professional & Academic Communication ──────────────────────
    (13, 60, "Meetings and workplace dialogue (B2 level)",
        ["communication"],
        ["Lead and participate in workplace meetings in German: agendas, proposals, objections, decisions",
         "Use modal particles, epistemic language, and indirect speech in meeting contexts"],
        ["Discourse architecture in extended speech and writing"]),
    (13, 61, "Presentations and structured public speech",
        ["communication"],
        ["Deliver a structured 5-minute presentation in German with introduction, body, and Q&A",
         "Use discourse markers, signposting language, and emphasis structures in public speech"],
        ["Meetings and workplace dialogue (B2 level)"]),
    (13, 62, "Formal and semi-formal email writing (B2)",
        ["skill"],
        ["Write formal emails in German using correct register, structure, and closing formulas",
         "Distinguish formal from semi-formal email conventions and apply them consistently"],
        ["Presentations and structured public speech"]),
    (13, 63, "Reporting results and findings in formal German",
        ["skill"],
        ["Write and present results using passive constructions, nominalisations, and formal connectors",
         "Apply neutral reporting style in academic and professional result summaries"],
        ["Formal and semi-formal email writing (B2)", "Neutral reporting style with passive constructions"]),
    (13, 64, "Decision summaries and recommendations",
        ["skill"],
        ["Write decision summaries that capture context, options, rationale, and recommended action",
         "Use formal German including Konjunktiv II, passive, and advanced connectors in decision documents"],
        ["Reporting results and findings in formal German"]),

    # ── Module 14: Real-World Interaction Mastery ─────────────────────────────
    (14, 65, "Negotiation language (B2 level)",
        ["communication"],
        ["Use B2-level German to negotiate outcomes: make offers, counter-offer, reach agreement",
         "Apply Konjunktiv II, modal particles, and hedging language in negotiation contexts"],
        ["Polite requests and wishes with Konjunktiv II"]),
    (14, 66, "Conflict resolution strategies",
        ["communication"],
        ["De-escalate and resolve conflicts in German using indirect language, concession, and reframing",
         "Maintain face-saving register while addressing disagreement directly"],
        ["Negotiation language (B2 level)"]),
    (14, 67, "Customer service interactions at B2 complexity",
        ["communication"],
        ["Handle complex customer service scenarios: complaints, escalations, policy explanations",
         "Use formal register, passive, and modal nuance in service-interaction contexts"],
        ["Conflict resolution strategies"]),
    (14, 68, "Bureaucratic communication mastery",
        ["communication"],
        ["Navigate complex German bureaucratic language: official letters, application forms, authority correspondence",
         "Produce formal German in compliance, request, and appeal documents"],
        ["Customer service interactions at B2 complexity", "Bureaucracy basics (forms, appointments, official language)"]),
    (14, 69, "Problem-solving dialogues under pressure (B2)",
        ["skill"],
        ["Handle unexpected problems in German under real-time pressure with fluency and accuracy",
         "Deploy the full B2 grammar and vocabulary toolkit in unscripted problem-solving scenarios"],
        ["Bureaucratic communication mastery"]),

    # ── Module 15: Reading Comprehension (Authentic Input) ────────────────────
    (15, 70, "Newspaper articles at native reading speed",
        ["skill"],
        ["Read German newspaper articles with full comprehension at normal native reading pace",
         "Identify article structure, main claim, and supporting evidence in news texts"],
        ["Simple news articles and reports"]),
    (15, 71, "Editorials and opinion pieces",
        ["skill"],
        ["Distinguish editorial opinion from factual reporting in German media texts",
         "Identify the author's stance, rhetorical strategy, and target audience in editorials"],
        ["Newspaper articles at native reading speed"]),
    (15, 72, "Blog and commentary texts",
        ["skill"],
        ["Read informal argumentative texts including blogs, online commentary, and reader responses",
         "Identify register, bias, and implied meaning in informal written German"],
        ["Editorials and opinion pieces"]),
    (15, 73, "Implicit meaning and bias detection in texts",
        ["skill"],
        ["Detect implied meaning, presupposition, and ideological framing in German texts",
         "Analyse lexical choice and discourse structure for evidence of authorial bias"],
        ["Blog and commentary texts"]),
    (15, 74, "Text type identification and structure analysis",
        ["skill"],
        ["Identify the genre, purpose, and target audience of a German text from structural cues",
         "Map text structure against genre conventions to set appropriate reading expectations"],
        ["Implicit meaning and bias detection in texts"]),

    # ── Module 16: Writing Mastery ────────────────────────────────────────────
    (16, 75, "Argumentative essays (multi-layer structure)",
        ["skill"],
        ["Write a 300+ word argumentative essay with layered sub-arguments and integrated counter-arguments",
         "Sustain logical progression and argument coherence across five or more paragraphs"],
        ["Rhetorical balancing in extended argument", "Paragraph cohesion techniques"]),
    (16, 76, "Structured reports and formal documents",
        ["skill"],
        ["Write structured German reports with section headings, passive voice, and nominalised style",
         "Apply formal documentation conventions consistently across an extended report"],
        ["Argumentative essays (multi-layer structure)", "Decision summaries and recommendations"]),
    (16, 77, "Opinion essays with nuance and concession",
        ["skill"],
        ["Write opinion essays that present a position, integrate concession, and return to the main claim",
         "Use einerseits…andererseits, zwar…aber, and dennoch to create nuanced written opinion"],
        ["Structured reports and formal documents"]),
    (16, 78, "Paragraph cohesion and flow control",
        ["skill"],
        ["Maintain lexical, grammatical, and topical cohesion across paragraphs in extended texts",
         "Use connector variation, pronoun chains, and lexical repetition to build cohesive long texts"],
        ["Opinion essays with nuance and concession"]),
    (16, 79, "Stylistic self-editing for formal writing",
        ["skill"],
        ["Edit own written texts for register consistency, repetition, and stylistic appropriateness",
         "Transform spoken-register drafts into formal written German through systematic revision"],
        ["Paragraph cohesion and flow control"]),

    # ── Module 17: Listening Comprehension (Natural Speed) ────────────────────
    (17, 80, "Native-speed conversations (B2 comprehension)",
        ["skill"],
        ["Comprehend unscripted native German conversation at full natural speed",
         "Identify topic, speaker stance, and key information in fast spontaneous speech"],
        ["Inference from context in real input"]),
    (17, 81, "Podcasts and interviews at natural speed",
        ["skill"],
        ["Comprehend German podcasts and interviews with varied speakers and topics",
         "Extract main ideas, supporting details, and speaker positions from audio at B2 level"],
        ["Native-speed conversations (B2 comprehension)"]),
    (17, 82, "Regional variation and dialect awareness",
        ["skill"],
        ["Recognise common German regional accents and dialectal features without full comprehension loss",
         "Adjust comprehension strategies when encountering Bavarian, Austrian, Swiss, or Northern German speech"],
        ["Podcasts and interviews at natural speed"]),
    (17, 83, "Inference from incomplete or fast input (B2)",
        ["skill"],
        ["Reconstruct meaning when input is partially unclear — speed, noise, or unfamiliar vocabulary",
         "Use context and pragmatic knowledge to fill comprehension gaps in real B2 listening conditions"],
        ["Regional variation and dialect awareness"]),

    # ── Module 18: Stylistic Control (Fluency Layer) ──────────────────────────
    (18, 84, "Register switching: spoken / written / formal / academic (B2)",
        ["skill"],
        ["Switch between spoken, written, formal, and academic registers automatically and accurately",
         "Identify and correct register mismatches in your own output in real time"],
        ["Stylistic self-editing for formal writing", "Inference from incomplete or fast input (B2)"]),
    (18, 85, "Tone control: polite / neutral / persuasive / critical",
        ["skill"],
        ["Maintain polite, neutral, persuasive, or critical tone consistently across extended discourse",
         "Modulate tone mid-text or mid-speech in response to context or audience reaction"],
        ["Register switching: spoken / written / formal / academic (B2)"]),
    (18, 86, "Sentence rhythm and emphasis control",
        ["skill"],
        ["Use information structure, sentence length variation, and stress to control discourse rhythm",
         "Avoid monotonous sentence structure by varying clause length and type deliberately"],
        ["Tone control: polite / neutral / persuasive / critical"]),
    (18, 87, "Variation in expression (avoiding repetition)",
        ["skill"],
        ["Replace repeated words, structures, and connector types with varied alternatives",
         "Edit for stylistic repetition and produce the same content with genuine linguistic variation"],
        ["Sentence rhythm and emphasis control"]),
    (18, 88, "Stylistic self-monitoring and real-time correction",
        ["skill"],
        ["Monitor your own output for stylistic problems and self-correct during speech or writing",
         "Maintain stylistic targets (formal, persuasive, etc.) for five minutes or more without drift"],
        ["Variation in expression (avoiding repetition)"]),

    # ── Module 19: Abstract & Societal Topics ─────────────────────────────────
    (19, 89, "Education systems vocabulary and discourse",
        ["vocabulary"],
        ["Discuss education systems, structures, and policies in German with B2-level vocabulary",
         "Use education vocabulary in argument, comparison, and critical evaluation contexts"],
        ["Certainty spectrum: assertion to speculation"]),
    (19, 90, "Technology and AI vocabulary and argumentation",
        ["vocabulary"],
        ["Discuss technology, digital society, and AI in German using appropriate B2 vocabulary",
         "Produce structured argument about technology topics using the full B2 argumentation system"],
        ["Education systems vocabulary and discourse"]),
    (19, 91, "Climate and environment discourse (B2)",
        ["vocabulary"],
        ["Discuss climate change, sustainability, and environmental policy in German",
         "Use scientific hedging language and structured argument for environment topic debates"],
        ["Technology and AI vocabulary and argumentation"]),
    (19, 92, "Political discourse (non-technical B2)",
        ["communication"],
        ["Discuss political systems, current events, and civic issues in German without technical jargon",
         "Engage with political topics using evidence, nuance, and appropriate register"],
        ["Climate and environment discourse (B2)"]),
    (19, 93, "Ethics and social issues at B2 depth",
        ["communication"],
        ["Discuss ethical dilemmas, social inequality, and human rights in structured German argument",
         "Deploy the full B2 argumentation toolkit on abstract ethical and societal topics"],
        ["Political discourse (non-technical B2)", "Persuasive vs neutral tone control"]),

    # ── Module 20: Conversation Mastery (Extended Fluency) ────────────────────
    (20, 94, "Multi-turn discussions (B2 level)",
        ["communication"],
        ["Sustain a structured discussion on a B2 topic for five or more turns without topic collapse",
         "Respond to unexpected questions and new angles without losing coherence or accuracy"],
        ["Sustained conversation flow at B1 level", "Stylistic self-monitoring and real-time correction"]),
    (20, 95, "Interruption handling and turn management (B2)",
        ["communication"],
        ["Handle interruptions gracefully: hold the floor, yield, and reclaim your speaking turn",
         "Use interruption markers (Moment mal, darf ich kurz…, wenn ich darf…) naturally"],
        ["Multi-turn discussions (B2 level)"]),
    (20, 96, "Topic shifting and topic maintenance",
        ["communication"],
        ["Shift topics smoothly using explicit discourse signals and maintain topics across multiple turns",
         "Use Apropos, Das erinnert mich an…, and similar topic-shift markers naturally"],
        ["Interruption handling and turn management (B2)"]),
    (20, 97, "Spontaneous explanation under pressure",
        ["skill"],
        ["Give clear, structured explanations on unfamiliar topics in real time without preparation",
         "Use connectors, examples, and elaboration strategies to produce coherent spontaneous speech"],
        ["Topic shifting and topic maintenance"]),
    (20, 98, "Sustained coherence in extended conversation",
        ["skill"],
        ["Sustain a 10-minute unscripted conversation using all B2 grammar and vocabulary systems",
         "Self-monitor and repair coherence breaks without losing the conversational thread"],
        ["Spontaneous explanation under pressure", "Ethics and social issues at B2 depth"]),
]


def seed_german_b2_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for German CEFR B2.
    Two-pass: Pass 1 inserts nodes, Pass 2 resolves prereq topic names → IDs
    across ALL German CEFR nodes so A1/A2/B1 topics can be used as prereqs.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'de'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("German language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'B2', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _GERMAN_B2_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _GERMAN_B2_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'CEFR', 'B2', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _GERMAN_B2_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] German B2 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


_CHINESE_HSK1_MODULES: list[tuple[int, str, str, int]] = [
    (1, "Pronunciation Foundations",  "Master the pinyin romanization system, initials, finals, and the four tones essential for correct Mandarin pronunciation", 7),
    (2, "Characters & Writing",       "Learn stroke types, stroke order, and recognise common radicals and character components used throughout HSK 1",            5),
    (3, "Core Grammar Patterns",      "Build the fundamental SVO sentence structure and master 是, 有, negation, and question patterns",                           7),
    (4, "Greetings & Social Language","Use essential greetings, farewells, polite expressions, and introduce yourself in Mandarin Chinese",                       6),
    (5, "Numbers, Time & Dates",      "Use numbers 1–100, express dates, tell the time, and discuss days and months in Mandarin",                                6),
    (6, "People & Family",            "Talk about family members, nationalities, ages, and basic descriptions of people",                                         6),
    (7, "Everyday Vocabulary",        "Use key vocabulary for actions, food, objects, colours, location, and weather",                                            6),
    (8, "Basic Communication",        "Express likes, wants, and requests and handle simple clarification in everyday Mandarin conversations",                    6),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_CHINESE_HSK1_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 1: Pronunciation Foundations ──────────────────────────────────
    (1, 1,  "Pinyin System",
        ["pronunciation"],
        ["Understand the purpose and structure of pinyin as the romanization system for Mandarin",
         "Identify the three components of a pinyin syllable: initial, final, and tone mark"],
        []),
    (1, 2,  "Initial Consonants",
        ["pronunciation"],
        ["Produce all 21 Mandarin initial consonants accurately, distinguishing aspirated pairs (b/p, d/t, g/k, j/q, zh/ch, z/c)",
         "Recognise and practise the retroflex (zh, ch, sh, r) and sibilant (z, c, s) distinctions"],
        ["Pinyin System"]),
    (1, 3,  "Simple Finals",
        ["pronunciation"],
        ["Pronounce the six simple finals (a, o, e, i, u, ü) correctly with proper mouth shape",
         "Combine simple finals with initials to form basic pinyin syllables"],
        ["Pinyin System"]),
    (1, 4,  "Compound Finals",
        ["pronunciation"],
        ["Pronounce common compound finals including ai, ei, ao, ou, ia, ie, ua, uo, üe, and nasal endings (an, en, in, un, ün, ang, eng, ing, ong)",
         "Apply pinyin spelling rules including the j/q/x + ü rule and w/y medial rules"],
        ["Simple Finals", "Initial Consonants"]),
    (1, 5,  "The Four Tones",
        ["pronunciation"],
        ["Produce the four tones accurately: high-level (1st), rising (2nd), dipping (3rd), and falling (4th)",
         "Identify tones by their tone marks and distinguish minimal pairs differing only in tone"],
        ["Pinyin System"]),
    (1, 6,  "Third Tone Sandhi",
        ["pronunciation"],
        ["Apply the third tone sandhi rule: 3rd tone + 3rd tone → 2nd tone + 3rd tone",
         "Produce common third-tone pairs (你好, 也好, 可以) with the correct sandhi change"],
        ["The Four Tones"]),
    (1, 7,  "Neutral Tone and Tone Practice",
        ["pronunciation"],
        ["Identify and produce the neutral (unstressed) tone on grammatical particles (吗, 呢, 的, 了)",
         "Practise all four tones fluently across a range of HSK 1 vocabulary items"],
        ["The Four Tones", "Third Tone Sandhi"]),

    # ── Module 2: Characters & Writing ───────────────────────────────────────
    (2, 8,  "Stroke Types",
        ["writing"],
        ["Identify the eight basic stroke types: 横 héng, 竖 shù, 撇 piě, 捺 nà, 点 diǎn, 折 zhé, 钩 gōu, 提 tí",
         "Recognise each stroke type in common HSK 1 characters"],
        []),
    (2, 9,  "Stroke Order Rules",
        ["writing"],
        ["Apply the seven core stroke order rules: top to bottom, left to right, horizontal before vertical, outside before inside, etc.",
         "Write basic characters following correct stroke order"],
        ["Stroke Types"]),
    (2, 10, "Number Characters (1–10)",
        ["writing"],
        ["Write and recognise the characters for numbers 1–10: 一二三四五六七八九十",
         "Use these characters as building blocks for larger numbers and compound characters"],
        ["Stroke Order Rules"]),
    (2, 11, "Common Radicals",
        ["writing"],
        ["Recognise and write 12 common radicals: 人 口 日 月 木 水 火 土 手 目 耳 心",
         "Understand how radicals provide semantic clues about a character's meaning"],
        ["Stroke Types"]),
    (2, 12, "Character Components",
        ["writing"],
        ["Identify how radicals and phonetic components combine to form compound characters",
         "Recognise 20 common HSK 1 characters by breaking them into known components"],
        ["Common Radicals", "Stroke Order Rules"]),

    # ── Module 3: Core Grammar Patterns ──────────────────────────────────────
    (3, 13, "Subject-Verb-Object Order",
        ["grammar"],
        ["Understand that Mandarin follows subject-verb-object (SVO) order",
         "Produce simple SVO sentences using HSK 1 vocabulary with correct word order"],
        ["Pinyin System", "Simple Finals"]),
    (3, 14, "是 (shì) Sentences",
        ["grammar"],
        ["Use 是 to express identity and classification: 我是学生, 他是中国人",
         "Form affirmative and negative 不是 sentences across all persons"],
        ["Subject-Verb-Object Order"]),
    (3, 15, "Negation with 不 (bù)",
        ["grammar"],
        ["Use 不 before verbs and adjectives to express negation",
         "Apply the tone change rule: 不 (4th tone) becomes 2nd tone before another 4th-tone syllable"],
        ["Subject-Verb-Object Order", "The Four Tones"]),
    (3, 16, "有 (yǒu) Sentences",
        ["grammar"],
        ["Use 有 to express possession (我有一本书) and existence (那里有一个人)",
         "Distinguish the possessive and existential functions of 有 in natural sentences"],
        ["Subject-Verb-Object Order"]),
    (3, 17, "Negation with 没 (méi)",
        ["grammar"],
        ["Use 没 (not 不) to negate 有 in both possession and existence sentences",
         "Produce correct negative sentences with 没有 across varied contexts"],
        ["有 (yǒu) Sentences", "Negation with 不 (bù)"]),
    (3, 18, "吗 (ma) Questions",
        ["grammar"],
        ["Form yes/no questions by adding the particle 吗 to the end of a statement",
         "Answer 吗 questions affirmatively and negatively using correct short-form responses"],
        ["是 (shì) Sentences"]),
    (3, 19, "Question Words",
        ["grammar"],
        ["Use 什么 (shénme), 谁 (shuí), 哪 (nǎ), 哪儿 (nǎr), 几 (jǐ), and 多少 (duōshao) in questions",
         "Understand that question words occupy the same position as their answers in Chinese word order"],
        ["吗 (ma) Questions"]),

    # ── Module 4: Greetings & Social Language ────────────────────────────────
    (4, 20, "Basic Greetings",
        ["communication"],
        ["Use 你好, 您好, 早上好, 下午好, and 晚上好 appropriately by time of day and formality level",
         "Respond to greetings naturally and initiate greetings in new conversations"],
        ["The Four Tones", "Pinyin System"]),
    (4, 21, "Farewells",
        ["communication"],
        ["Use 再见, 明天见, 回头见, and 拜拜 in appropriate farewell contexts",
         "Choose the right farewell based on when you will next meet the person"],
        ["Basic Greetings"]),
    (4, 22, "Polite Expressions",
        ["communication"],
        ["Use 谢谢, 不客气, 对不起, and 没关系 in their correct social contexts",
         "Respond appropriately when someone thanks you or apologises to you"],
        ["Basic Greetings"]),
    (4, 23, "Personal Pronouns",
        ["grammar"],
        ["Use singular pronouns (我, 你, 他, 她, 它) and plural pronouns (我们, 你们, 他们) correctly",
         "Understand that Chinese pronouns do not inflect for grammatical case"],
        ["Subject-Verb-Object Order"]),
    (4, 24, "Self-Introduction",
        ["communication"],
        ["Introduce yourself giving your name, nationality, and occupation using 我叫…, 我是…",
         "Use 是 and personal pronouns together in a complete self-introduction"],
        ["是 (shì) Sentences", "Personal Pronouns"]),
    (4, 25, "Asking for Names and Origins",
        ["communication"],
        ["Ask and answer 你叫什么名字? and 你是哪国人? naturally in conversation",
         "Use question words to gather personal information politely"],
        ["Self-Introduction", "Question Words"]),

    # ── Module 5: Numbers, Time & Dates ──────────────────────────────────────
    (5, 26, "Numbers 1–100",
        ["vocabulary"],
        ["Form and say all numbers from 1 to 100 using 十 and 百 as base units",
         "Understand the pattern for numbers 11–19 (十一, 十二…) and multiples of ten (二十, 三十…)"],
        ["Number Characters (1–10)"]),
    (5, 27, "Money and Prices",
        ["communication"],
        ["Use 元 (yuán), 角 (jiǎo), and 分 (fēn) to express prices",
         "Ask 多少钱? and understand price answers in everyday shopping contexts"],
        ["Numbers 1–100"]),
    (5, 28, "Days and Months",
        ["vocabulary"],
        ["Name all days of the week (星期一 to 星期日) and all months (一月 to 十二月)",
         "Use these expressions to discuss schedules, plans, and dates"],
        ["Numbers 1–100", "Number Characters (1–10)"]),
    (5, 29, "Telling the Time",
        ["communication"],
        ["Ask 现在几点? and express hours and half-hours (三点, 三点半, 三点一刻)",
         "Use 上午, 下午, and 晚上 with time expressions to clarify AM/PM"],
        ["Numbers 1–100", "吗 (ma) Questions"]),
    (5, 30, "Time Expressions",
        ["vocabulary"],
        ["Use 今天, 明天, 昨天, 上午, 下午, 晚上, 现在, 以前, and 以后 in sentences",
         "Place time expressions correctly at the start of a sentence or before the verb"],
        ["Telling the Time"]),
    (5, 31, "Date Expressions",
        ["communication"],
        ["Express full dates using 年, 月, 号/日 in the correct order: year → month → day",
         "Ask and answer 今天几月几号? in natural conversation"],
        ["Days and Months", "Time Expressions"]),

    # ── Module 6: People & Family ─────────────────────────────────────────────
    (6, 32, "Family Members",
        ["vocabulary"],
        ["Name immediate family members: 爸爸, 妈妈, 哥哥, 姐姐, 弟弟, 妹妹, 儿子, 女儿",
         "Use family terms in sentences describing your family with correct pronouns and 是"],
        ["Personal Pronouns", "是 (shì) Sentences"]),
    (6, 33, "Measure Words (个, 位, 本, 张)",
        ["grammar"],
        ["Use the most common measure words: 个 (general), 位 (respectful for people), 本 (books), 张 (flat objects)",
         "Form correct noun phrases with number + measure word + noun"],
        ["Personal Pronouns", "Numbers 1–100"]),
    (6, 34, "Describing Nationality",
        ["communication"],
        ["Form nationality words by adding 人 to country names: 中国人, 美国人, 英国人, 法国人",
         "Ask and answer 你是哪国人? and 你来自哪里? in conversation"],
        ["是 (shì) Sentences", "Personal Pronouns"]),
    (6, 35, "Adjectives and 很",
        ["grammar"],
        ["Use stative verbs and adjectives with 很 as a linking element: 她很漂亮, 天气很好",
         "Understand that 很 is obligatory in simple adjective predicates even when not meaning 'very'"],
        ["是 (shì) Sentences"]),
    (6, 36, "Age Expressions",
        ["communication"],
        ["Ask and answer age questions: 你多大了? (adults), 你几岁? (children), 我…岁",
         "Use numbers correctly in age expressions for both children and adults"],
        ["Numbers 1–100", "Question Words"]),
    (6, 37, "Physical Descriptions",
        ["communication"],
        ["Use basic adjectives to describe appearance: 高, 矮, 胖, 瘦, 帅, 漂亮, 可爱",
         "Combine adjectives with 很 to describe people in natural sentences"],
        ["Adjectives and 很"]),

    # ── Module 7: Everyday Vocabulary ────────────────────────────────────────
    (7, 38, "Common Action Verbs",
        ["vocabulary"],
        ["Use 12 core action verbs: 吃, 喝, 看, 听, 说, 写, 读, 做, 去, 来, 买, 坐",
         "Combine action verbs with objects in correct SVO sentences"],
        ["Subject-Verb-Object Order", "Negation with 不 (bù)"]),
    (7, 39, "Food and Drink Basics",
        ["vocabulary"],
        ["Name and use HSK 1 food and drink vocabulary: 水, 茶, 咖啡, 饭, 面条, 苹果, 鸡蛋, 肉",
         "Order and discuss food using 我要…, 我想吃… in context"],
        ["Common Action Verbs"]),
    (7, 40, "Location Words",
        ["grammar"],
        ["Use 在 to express location: 我在家, 书在桌子上",
         "Use directional position words 上, 下, 里, 外, 前, 后 after a noun to specify location"],
        ["有 (yǒu) Sentences"]),
    (7, 41, "Common Objects",
        ["vocabulary"],
        ["Name everyday objects: 书, 本子, 电脑, 手机, 钱, 车, 桌子, 椅子, 水杯",
         "Use measure words correctly with common objects in quantity expressions"],
        ["Measure Words (个, 位, 本, 张)"]),
    (7, 42, "Colors",
        ["vocabulary"],
        ["Name the eight core colors: 红, 橙, 黄, 绿, 蓝, 紫, 白, 黑",
         "Use colors as adjectives before nouns (红色的苹果) and in predicate position (苹果是红色的)"],
        ["Adjectives and 很"]),
    (7, 43, "Weather Basics",
        ["communication"],
        ["Ask 今天天气怎么样? and describe weather using 晴天, 下雨, 下雪, 刮风, 热, and 冷",
         "Combine weather vocabulary with time expressions to describe conditions"],
        ["Adjectives and 很", "Question Words"]),

    # ── Module 8: Basic Communication ────────────────────────────────────────
    (8, 44, "Expressing Likes (喜欢)",
        ["communication"],
        ["Use 喜欢 to express likes and 不喜欢 for dislikes with nouns and verb phrases",
         "Ask 你喜欢…吗? and respond naturally with full and short-form answers"],
        ["Common Action Verbs", "Negation with 不 (bù)"]),
    (8, 45, "Expressing Wants (想 and 要)",
        ["communication"],
        ["Use 想 for wishes and hypothetical desire (我想去) and 要 for requests and firm intentions (我要一杯水)",
         "Distinguish 想 (softer, hypothetical) from 要 (more definite) in context"],
        ["Common Action Verbs"]),
    (8, 46, "Simple Requests",
        ["communication"],
        ["Make polite requests using 请, 请问, 麻烦你, 给我, and 帮我",
         "Soften requests appropriately for different social contexts"],
        ["Polite Expressions", "Expressing Wants (想 and 要)"]),
    (8, 47, "Asking for Clarification",
        ["communication"],
        ["Use 什么意思?, 你说什么?, 请再说一遍, and 请说慢一点 when you do not understand",
         "Handle communication breakdowns naturally without switching to English"],
        ["Basic Greetings", "Question Words"]),
    (8, 48, "Numbers in Context",
        ["communication"],
        ["Use numbers naturally in shopping (多少钱?), ordering food, and exchanging phone numbers",
         "Handle price questions and quantity requests in practical everyday contexts"],
        ["Money and Prices", "Food and Drink Basics"]),
    (8, 49, "Basic Dialogue Practice",
        ["communication"],
        ["Produce a complete HSK 1 level conversation covering greeting, self-introduction, and a simple transaction",
         "Combine all HSK 1 structures to hold a short, naturalistic Mandarin exchange"],
        ["Self-Introduction", "Expressing Likes (喜欢)", "Simple Requests"]),
]


# ─── Seed helpers ─────────────────────────────────────────────────────────────

def seed_languages(conn: psycopg2.extensions.connection) -> None:
    """
    Insert the canonical language list.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    conn.executemany(
        "INSERT INTO languages (code, name, native_name, framework) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
        _LANGUAGES,
    )
    # Ensure framework is correct on rows that pre-date the column (migration path)
    conn.executemany(
        "UPDATE languages SET framework = %s WHERE code = %s",
        [(framework, code) for code, _name, _native, framework in _LANGUAGES],
    )
    print(f"[db] Languages seeded ({len(_LANGUAGES)} rows)")


def seed_hobbies(conn: psycopg2.extensions.connection) -> None:
    """
    Insert the canonical hobby list.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT INTO hobbies (name) VALUES (%s) ON CONFLICT DO NOTHING"
    conn.executemany(sql, [(h,) for h in _HOBBIES])
    print(f"[db] Hobbies seeded ({len(_HOBBIES)} rows)")


def seed_motivations(conn: psycopg2.extensions.connection) -> None:
    """
    Insert the canonical motivation list.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT INTO motivations (label) VALUES (%s) ON CONFLICT DO NOTHING"
    conn.executemany(sql, [(m,) for m in _MOTIVATIONS])
    print(f"[db] Motivations seeded ({len(_MOTIVATIONS)} rows)")


def seed_xp_levels(conn: psycopg2.extensions.connection) -> None:
    """
    Insert XP level threshold bands.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT INTO xp_levels (level_no, label, xp_required, xp_to_next) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING"
    conn.executemany(sql, _XP_LEVELS)
    print(f"[db] XP levels seeded ({len(_XP_LEVELS)} rows)")


def seed_achievements(conn: psycopg2.extensions.connection) -> None:
    """
    Insert the canonical achievement catalog.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT INTO achievements (name, description, xp_reward) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
    conn.executemany(sql, _ACHIEVEMENTS)
    print(f"[db] Achievements seeded ({len(_ACHIEVEMENTS)} rows)")


def seed_french_curriculum(conn: psycopg2.extensions.connection) -> None:
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
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'A1', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _FRENCH_A1_MODULES],
    )

    # Build unit → module_id map (needed for nodes FK)
    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A1'",
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
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'CEFR', 'A1', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] French A1 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_french_a2_curriculum(conn: psycopg2.extensions.connection) -> None:
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
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'A2', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _FRENCH_A2_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ──────────────────────────
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _FRENCH_A2_NODES:
        conn.execute(
            """
            INSERT INTO curriculum_nodes
                (language_id, module_id, framework, level, lesson_order, topic,
                 skill_focus, prerequisites, learning_objectives)
            VALUES (%s, %s, 'CEFR', 'A2', %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
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
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2' ORDER BY lesson_order",
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
                "UPDATE curriculum_nodes SET prerequisites = %s WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2' AND lesson_order = %s",
                (json.dumps(prereq_ids), lang_id, lesson_order),
            )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] French A2 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_french_b1_curriculum(conn: psycopg2.extensions.connection) -> None:
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
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'B1', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _FRENCH_B1_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ──────────────────────────
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _FRENCH_B1_NODES:
        conn.execute(
            """
            INSERT INTO curriculum_nodes
                (language_id, module_id, framework, level, lesson_order, topic,
                 skill_focus, prerequisites, learning_objectives)
            VALUES (%s, %s, 'CEFR', 'B1', %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
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
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' ORDER BY id",
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
                "UPDATE curriculum_nodes SET prerequisites = %s WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1' AND lesson_order = %s",
                (json.dumps(prereq_ids), lang_id, lesson_order),
            )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] French B1 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_french_b2_curriculum(conn: psycopg2.extensions.connection) -> None:
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
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'B2', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _FRENCH_B2_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ──────────────────────────
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _FRENCH_B2_NODES:
        conn.execute(
            """
            INSERT INTO curriculum_nodes
                (language_id, module_id, framework, level, lesson_order, topic,
                 skill_focus, prerequisites, learning_objectives)
            VALUES (%s, %s, 'CEFR', 'B2', %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
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
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' ORDER BY id",
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
                "UPDATE curriculum_nodes SET prerequisites = %s WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2' AND lesson_order = %s",
                (json.dumps(prereq_ids), lang_id, lesson_order),
            )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] French B2 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_spanish_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for Spanish A1.
    Uses INSERT OR IGNORE — safe to re-run.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'es'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("Spanish language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'A1', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _SPANISH_A1_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Nodes ─────────────────────────────────────────────────────────────────
    rows = []
    for unit, lesson_order, topic, skill_focus, objectives in _SPANISH_A1_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'CEFR', 'A1', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] Spanish A1 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_spanish_a2_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for Spanish A2.
    Pass 2 queries ALL Spanish nodes (A1 + A2) ordered by id so that
    cross-level prereq resolution always picks the earlier-inserted node.
    Uses INSERT OR IGNORE — safe to re-run.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'es'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("Spanish language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'A2', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _SPANISH_A2_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ─────────────────────────
    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _SPANISH_A2_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'CEFR', 'A2', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    # ── Pass 2: resolve prereq topic names → node IDs (all Spanish nodes) ────
    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _SPANISH_A2_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'A2'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] Spanish A2 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_spanish_b1_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for Spanish B1.
    Pass 2 queries ALL Spanish nodes (A1 + A2 + B1) ordered by id so that
    cross-level prereq resolution always picks the earlier-inserted node.
    Uses INSERT OR IGNORE — safe to re-run.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'es'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("Spanish language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'B1', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _SPANISH_B1_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ─────────────────────────
    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _SPANISH_B1_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'CEFR', 'B1', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    # ── Pass 2: resolve prereq topic names → node IDs (all Spanish nodes) ────
    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _SPANISH_B1_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'B1'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] Spanish B1 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_spanish_b2_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for Spanish B2.
    Pass 2 queries ALL Spanish nodes (A1 + A2 + B1 + B2) ordered by id so that
    cross-level prereq resolution always picks the earlier-inserted node.
    Uses INSERT OR IGNORE — safe to re-run.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'es'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("Spanish language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'CEFR', 'B2', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _SPANISH_B2_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ─────────────────────────
    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _SPANISH_B2_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'CEFR', 'B2', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    # ── Pass 2: resolve prereq topic names → node IDs (all Spanish nodes) ────
    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _SPANISH_B2_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'CEFR' AND level = 'B2'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] Spanish B2 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


def seed_chinese_hsk1_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for Chinese HSK 1.
    Uses framework='HSK' and level='HSK1'.
    Two-pass approach: Pass 1 inserts nodes, Pass 2 resolves prereq topic names → IDs.
    Uses INSERT OR IGNORE — safe to re-run.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'zh'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("Chinese language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'HSK', 'HSK1', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _CHINESE_HSK1_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK1'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ─────────────────────────
    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _CHINESE_HSK1_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'HSK', 'HSK1', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    # ── Pass 2: resolve prereq topic names → node IDs (all HSK Chinese nodes) ─
    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _CHINESE_HSK1_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK1' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK1'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK1'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] Chinese HSK 1 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── Chinese HSK 2 curriculum ────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_CHINESE_HSK2_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "HSK1 Review & Pronunciation",        "Consolidate HSK1 vocabulary, master tone sandhi, and build pronunciation fluency",                         3),
    (2,  "Personal Information & Relationships","Describe yourself, your studies, work, hobbies, and family in natural Mandarin",                           6),
    (3,  "Time & Daily Routines",               "Express clock time, dates, schedules, frequency, and everyday habits",                                     5),
    (4,  "Locations & Directions",              "Use location words, position objects, and navigate using 来, 去, and direction-giving phrases",             5),
    (5,  "Grammar Expansion",                   "Master the core HSK2 grammar patterns: 在, 了, 过, 正在, frequency adverbs, and duration",                  6),
    (6,  "Comparisons",                         "Compare people and objects using 比, 更, and 最 in natural conversation",                                   5),
    (7,  "Modal Verbs",                         "Distinguish and correctly use 会, 能, 可以, 想, and 要 for ability, permission, and desire",                8),
    (8,  "Asking Questions",                    "Form and respond to questions using 为什么, 怎么, 哪, 哪儿/哪里, and follow-up strategies",                 6),
    (9,  "Measure Words",                       "Use the most common measure words correctly and build natural quantity expressions",                        7),
    (10, "Shopping & Food",                     "Navigate prices, menus, preferences, payment, and restaurant conversations",                               5),
    (11, "Travel & Transportation",             "Discuss transport, destinations, tickets, and travel questions confidently",                               5),
    (12, "Connected Communication",             "Link ideas and express opinions, reasons, sequences, and experiences using connectors",                    8),
    (13, "Chinese Sentence Patterns",           "Understand how Mandarin sentences are naturally organised: topic-comment, 是…的, verb-object, word order", 5),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_CHINESE_HSK2_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 1: HSK1 Review & Pronunciation ────────────────────────────────
    (1, 1, "HSK1 Review",
        ["concept"],
        ["Recall key HSK1 vocabulary across all topic areas",
         "Identify gaps in HSK1 knowledge before progressing to HSK2"],
        []),
    (1, 2, "Tone Sandhi",
        ["concept"],
        ["Understand and apply tone sandhi rules, especially 一, 不, and third-tone pairs",
         "Produce smooth, natural tone changes in connected speech"],
        ["Tones & Pronunciation"]),
    (1, 3, "Pronunciation Fluency",
        ["speaking"],
        ["Speak HSK1 sentences with correct tones and natural rhythm",
         "Identify and self-correct common pronunciation errors"],
        ["Tone Sandhi"]),

    # ── Module 2: Personal Information & Relationships ────────────────────────
    (2, 4, "Talking About Yourself",
        ["communication"],
        ["Introduce yourself with name, age, nationality, and profession",
         "Answer and ask personal questions naturally"],
        ["HSK1 Review"]),
    (2, 5, "Talking About Studies",
        ["communication"],
        ["Describe your school, subjects, and study habits in Mandarin",
         "Ask others about their education naturally"],
        ["Talking About Yourself"]),
    (2, 6, "Talking About Work",
        ["communication"],
        ["Describe your job, workplace, and daily work activities",
         "Ask and answer questions about professions"],
        ["Talking About Yourself"]),
    (2, 7, "Talking About Hobbies",
        ["communication"],
        ["Express what you like to do and how often using 喜欢 and frequency words",
         "Ask others about their interests and respond naturally"],
        ["Talking About Yourself"]),
    (2, 8, "Talking About Family",
        ["communication"],
        ["Describe family members and relationships using 家庭 vocabulary",
         "Discuss family size, members, and simple family situations"],
        ["Talking About Yourself"]),
    (2, 9, "Describing People",
        ["communication"],
        ["Describe physical appearance and personality traits",
         "Combine adjectives and measure words to describe people naturally"],
        ["Talking About Family"]),

    # ── Module 3: Time & Daily Routines ──────────────────────────────────────
    (3, 10, "Clock Time",
        ["concept"],
        ["Read and express clock times using 点, 分, 刻, and 半",
         "Ask and answer questions about the time naturally"],
        ["HSK1 Review"]),
    (3, 11, "Days and Dates",
        ["concept"],
        ["Express days of the week, months, and full calendar dates",
         "Use 今天, 明天, 昨天, and date expressions in sentences"],
        ["Clock Time"]),
    (3, 12, "Daily Schedule",
        ["communication"],
        ["Describe a typical day from morning to night using time expressions",
         "Sequence daily activities using time words and connectors"],
        ["Clock Time", "Days and Dates"]),
    (3, 13, "Frequency Expressions",
        ["concept"],
        ["Use 经常, 有时候, 很少, 每天, and 从来不 to express how often you do things",
         "Ask and answer questions about habits using frequency adverbs"],
        ["Daily Schedule"]),
    (3, 14, "Talking About Habits",
        ["communication"],
        ["Describe personal routines and habits using frequency expressions and time words",
         "Compare your habits with others naturally in conversation"],
        ["Frequency Expressions"]),

    # ── Module 4: Locations & Directions ─────────────────────────────────────
    (4, 15, "Location Words",
        ["concept"],
        ["Use 上, 下, 左, 右, 前, 后, 里, 外, 旁边, and 中间 to describe positions",
         "Place objects and people in relation to each other using location words"],
        ["HSK1 Review"]),
    (4, 16, "Positioning Objects",
        ["concept"],
        ["Use 在 + location word to state where things are",
         "Describe the position of objects in a room or environment"],
        ["Location Words"]),
    (4, 17, "来 vs 去",
        ["concept"],
        ["Distinguish and correctly use 来 (coming toward) and 去 (going away)",
         "Apply 来 and 去 with destinations and directions naturally"],
        ["Location Words"]),
    (4, 18, "Asking Directions",
        ["communication"],
        ["Ask for directions using 怎么走, 在哪儿, and polite question forms",
         "Understand and clarify direction responses"],
        ["Location Words", "来 vs 去"]),
    (4, 19, "Giving Directions",
        ["communication"],
        ["Give clear directions using 往, 左转, 右转, 直走, and landmarks",
         "Combine location words and direction verbs in fluent instructions"],
        ["Asking Directions"]),

    # ── Module 5: Grammar Expansion ──────────────────────────────────────────
    (5, 20, "在 + Verb",
        ["concept"],
        ["Use 在 before a verb to indicate an action is in progress at a location",
         "Distinguish 在 as location marker from 在 as progressive marker"],
        ["Positioning Objects"]),
    (5, 21, "了 (Completed Action)",
        ["concept"],
        ["Use sentence-final 了 to indicate a completed action or change of state",
         "Form affirmative, negative, and question sentences with 了"],
        ["HSK1 Review"]),
    (5, 22, "过 (Experience)",
        ["concept"],
        ["Use 过 after a verb to describe past experiences",
         "Distinguish 过 from 了 and use both correctly in context"],
        ["了 (Completed Action)"]),
    (5, 23, "正在 (Ongoing Action)",
        ["concept"],
        ["Use 正在 to express actions happening right now",
         "Combine 正在 with 呢 and contrast with 了 and 过"],
        ["在 + Verb"]),
    (5, 24, "Frequency Adverbs",
        ["concept"],
        ["Use 常常, 总是, 有时, 偶尔, and 从来 to modify verbs with frequency meaning",
         "Position frequency adverbs correctly before the verb in a sentence"],
        ["Talking About Habits"]),
    (5, 25, "Duration Expressions",
        ["concept"],
        ["Express how long an action lasts using time-duration phrases after the verb",
         "Form sentences like 学了两年 and ask 学了多长时间"],
        ["了 (Completed Action)"]),

    # ── Module 6: Comparisons ─────────────────────────────────────────────────
    (6, 26, "比 (Comparisons)",
        ["concept"],
        ["Form A 比 B + adjective sentences to compare two things",
         "Use 比 in affirmative, negative, and question forms"],
        ["HSK1 Review"]),
    (6, 27, "更 (Even More)",
        ["concept"],
        ["Use 更 to intensify comparisons — 'even more'",
         "Combine 更 with adjectives and 比 sentences naturally"],
        ["比 (Comparisons)"]),
    (6, 28, "最 (Superlative)",
        ["concept"],
        ["Use 最 before adjectives to form superlatives",
         "Apply 最 in sentences about preferences, rankings, and extremes"],
        ["更 (Even More)"]),
    (6, 29, "Comparing People",
        ["communication"],
        ["Compare two people's appearance, ability, or habits using 比, 更, and 最",
         "Sustain a natural comparison conversation about people"],
        ["比 (Comparisons)", "更 (Even More)", "最 (Superlative)"]),
    (6, 30, "Comparing Objects",
        ["communication"],
        ["Compare objects such as food, places, and prices using comparison structures",
         "Express preferences using comparisons and 觉得 / 认为"],
        ["Comparing People"]),

    # ── Module 7: Modal Verbs ─────────────────────────────────────────────────
    (7, 31, "会 (Learned Ability)",
        ["concept"],
        ["Use 会 to express a skill or learned ability",
         "Form questions and negatives with 不会 and 会…吗"],
        ["HSK1 Review"]),
    (7, 32, "能 (Physical Ability / Circumstantial Permission)",
        ["concept"],
        ["Use 能 to express physical ability or permission granted by circumstances",
         "Distinguish 能 from 会 in practical sentences"],
        ["会 (Learned Ability)"]),
    (7, 33, "可以 (Permission)",
        ["concept"],
        ["Use 可以 to ask for or grant permission",
         "Contrast 可以 with 能 in polite request contexts"],
        ["能 (Physical Ability / Circumstantial Permission)"]),
    (7, 34, "想 (Want / Would Like)",
        ["concept"],
        ["Use 想 to express wishes or desires",
         "Form sentences about what you want to do or have"],
        ["HSK1 Review"]),
    (7, 35, "要 (Need / Going To)",
        ["concept"],
        ["Use 要 for necessity, intention, or near-future plans",
         "Distinguish 要 from 想 in context"],
        ["想 (Want / Would Like)"]),
    (7, 36, "Expressing Ability",
        ["communication"],
        ["Use 会 and 能 naturally in conversation about skills and physical capacity",
         "Ask and answer ability questions fluently"],
        ["会 (Learned Ability)", "能 (Physical Ability / Circumstantial Permission)"]),
    (7, 37, "Expressing Permission",
        ["communication"],
        ["Ask for and grant permission using 能 and 可以 in real-life situations",
         "Respond politely to permission requests"],
        ["可以 (Permission)", "能 (Physical Ability / Circumstantial Permission)"]),
    (7, 38, "Expressing Desire",
        ["communication"],
        ["Express and discuss wants and intentions using 想 and 要 naturally",
         "Distinguish nuance between wanting and planning in Mandarin"],
        ["想 (Want / Would Like)", "要 (Need / Going To)"]),

    # ── Module 8: Asking Questions ────────────────────────────────────────────
    (8, 39, "为什么 (Why)",
        ["concept"],
        ["Form why-questions with 为什么 and answer using 因为",
         "Use 为什么 in both spoken and written question forms"],
        ["HSK1 Review"]),
    (8, 40, "怎么 (How)",
        ["concept"],
        ["Use 怎么 to ask how something is done or how to get somewhere",
         "Distinguish 怎么 from 怎么样 in context"],
        ["HSK1 Review"]),
    (8, 41, "哪 (Which)",
        ["concept"],
        ["Use 哪 with measure words to ask 'which' in choice questions",
         "Form 哪 + measure word + noun questions naturally"],
        ["HSK1 Review"]),
    (8, 42, "哪儿 / 哪里 (Where)",
        ["concept"],
        ["Use 哪儿 and 哪里 interchangeably to ask where",
         "Apply location question words in directions, addresses, and place queries"],
        ["Asking Directions"]),
    (8, 43, "Clarification Questions",
        ["communication"],
        ["Ask for clarification using 什么意思, 你说什么, 再说一遍, and similar phrases",
         "Handle misunderstandings naturally in conversation"],
        ["为什么 (Why)", "怎么 (How)"]),
    (8, 44, "Follow-up Questions",
        ["communication"],
        ["Keep a conversation going by asking relevant follow-up questions",
         "Use question words and rising intonation to probe for more detail"],
        ["Clarification Questions"]),

    # ── Module 9: Measure Words ───────────────────────────────────────────────
    (9, 45, "个 (General Measure Word)",
        ["concept"],
        ["Use 个 as the default measure word for people and general objects",
         "Form quantity phrases with 个 correctly in sentences"],
        ["HSK1 Review"]),
    (9, 46, "本 (Books)",
        ["concept"],
        ["Use 本 for books, notebooks, and bound volumes",
         "Form sentences about reading and purchasing books using 本"],
        ["个 (General Measure Word)"]),
    (9, 47, "张 (Flat Objects)",
        ["concept"],
        ["Use 张 for flat objects: paper, tickets, tables, photos, and beds",
         "Apply 张 in shopping and everyday description sentences"],
        ["个 (General Measure Word)"]),
    (9, 48, "杯 (Cups & Glasses)",
        ["concept"],
        ["Use 杯 for drinks measured by cup or glass",
         "Order drinks and describe quantities using 杯 naturally"],
        ["个 (General Measure Word)"]),
    (9, 49, "件 (Items of Clothing / Matters)",
        ["concept"],
        ["Use 件 for clothing items and abstract matters",
         "Distinguish 件 from 条 and apply correctly when shopping"],
        ["个 (General Measure Word)"]),
    (9, 50, "Common Measure Word Patterns",
        ["concept"],
        ["Review the most frequent measure words and the nouns they pair with",
         "Avoid the most common measure word errors made by HSK2 learners"],
        ["个 (General Measure Word)", "本 (Books)", "张 (Flat Objects)", "杯 (Cups & Glasses)", "件 (Items of Clothing / Matters)"]),
    (9, 51, "Quantity Expressions",
        ["communication"],
        ["Combine numbers, measure words, and nouns into fluent quantity phrases",
         "Use quantity expressions in shopping, ordering, and describing scenes"],
        ["Common Measure Word Patterns"]),

    # ── Module 10: Shopping & Food ────────────────────────────────────────────
    (10, 52, "Asking Prices",
        ["communication"],
        ["Ask how much something costs using 多少钱 and 怎么卖",
         "Understand and respond to price answers in a shopping context"],
        ["Quantity Expressions"]),
    (10, 53, "Ordering Food",
        ["communication"],
        ["Order food and drinks in a restaurant using 我要, 我想要, and 来一个",
         "Ask about the menu, specials, and recommendations"],
        ["Asking Prices"]),
    (10, 54, "Preferences",
        ["communication"],
        ["Express food and shopping preferences using 喜欢, 不喜欢, 更喜欢, and 最喜欢",
         "Discuss what you like and dislike about food or products"],
        ["Comparing Objects", "Ordering Food"]),
    (10, 55, "Paying for Items",
        ["communication"],
        ["Handle payment conversations: cash, card, change, and receipts",
         "Use 付钱, 找钱, 刷卡, and related vocabulary naturally"],
        ["Asking Prices"]),
    (10, 56, "Restaurant Conversations",
        ["communication"],
        ["Navigate a full restaurant experience from entry to payment",
         "Combine ordering, preferences, and payment language in a sustained conversation"],
        ["Ordering Food", "Paying for Items", "Preferences"]),

    # ── Module 11: Travel & Transportation ───────────────────────────────────
    (11, 57, "Transportation Vocabulary",
        ["concept"],
        ["Name common modes of transport: 公共汽车, 地铁, 出租车, 飞机, 火车, 自行车",
         "Use 坐 and 骑 correctly with different transport types"],
        ["HSK1 Review"]),
    (11, 58, "Destinations",
        ["communication"],
        ["Talk about places you want to go using 去 + destination",
         "Express travel plans and ask others about their destinations"],
        ["Transportation Vocabulary", "来 vs 去"]),
    (11, 59, "Buying Tickets",
        ["communication"],
        ["Buy transport tickets using quantity, destination, and time expressions",
         "Ask about schedules, platforms, and ticket types"],
        ["Destinations", "Asking Prices"]),
    (11, 60, "Asking Travel Questions",
        ["communication"],
        ["Ask about journey time, route options, and transport availability",
         "Use 多长时间, 怎么去, and 几号线 in travel contexts"],
        ["Buying Tickets", "怎么 (How)"]),
    (11, 61, "Giving Travel Information",
        ["communication"],
        ["Provide travel directions and information confidently",
         "Combine transport vocabulary, location words, and direction phrases"],
        ["Asking Travel Questions", "Giving Directions"]),

    # ── Module 12: Connected Communication ───────────────────────────────────
    (12, 62, "因为…所以… (Because…Therefore…)",
        ["concept"],
        ["Use 因为…所以… to express cause and effect",
         "Form complete cause-effect sentences and identify them in natural speech"],
        ["为什么 (Why)"]),
    (12, 63, "然后 (Then / After That)",
        ["concept"],
        ["Use 然后 to sequence events and actions",
         "Build multi-step narratives using 然后 naturally"],
        ["Daily Schedule"]),
    (12, 64, "以后 (After / In the Future)",
        ["concept"],
        ["Use 以后 to talk about what happens after an event or in the future",
         "Distinguish 以后 from 然后 in context"],
        ["然后 (Then / After That)"]),
    (12, 65, "以前 (Before / In the Past)",
        ["concept"],
        ["Use 以前 to talk about what happened before or in the past",
         "Contrast 以前 with 以后 and use both in narratives"],
        ["以后 (After / In the Future)"]),
    (12, 66, "Expressing Opinions",
        ["communication"],
        ["Share opinions using 我觉得, 我认为, 我想, and 在我看来",
         "Support opinions with brief reasons in natural conversation"],
        ["因为…所以… (Because…Therefore…)"]),
    (12, 67, "Giving Reasons",
        ["communication"],
        ["Explain reasons and justifications using 因为 and other causal connectors",
         "Respond naturally to 为什么 questions with full explanations"],
        ["Expressing Opinions", "因为…所以… (Because…Therefore…)"]),
    (12, 68, "Sequencing Events",
        ["communication"],
        ["Tell a story or describe a process in clear chronological order",
         "Use 先, 然后, 接着, 最后 to organise events fluently"],
        ["然后 (Then / After That)", "以后 (After / In the Future)", "以前 (Before / In the Past)"]),
    (12, 69, "Describing Experiences",
        ["communication"],
        ["Describe past experiences using 过, time expressions, and connectors",
         "Sustain a multi-sentence account of a personal experience"],
        ["过 (Experience)", "Sequencing Events"]),

    # ── Module 13: Chinese Sentence Patterns ─────────────────────────────────
    (13, 70, "Question Forms Review",
        ["concept"],
        ["Review all HSK1–2 question types: 吗, 呢, 吧, word-questions, and A-not-A",
         "Choose the appropriate question form for context and register"],
        ["Follow-up Questions"]),
    (13, 71, "Topic-Comment Structure",
        ["concept"],
        ["Understand how Mandarin places the topic first and comments after",
         "Recognise and produce topic-comment sentences naturally"],
        ["HSK1 Review"]),
    (13, 72, "是…的 (Introduction)",
        ["concept"],
        ["Use 是…的 to emphasise when, where, or how a past action happened",
         "Distinguish 是…的 from plain past sentences with 了"],
        ["了 (Completed Action)", "Topic-Comment Structure"]),
    (13, 73, "Verb-Object Patterns",
        ["concept"],
        ["Recognise how Mandarin separable verbs work and insert elements between verb and object",
         "Use common verb-object patterns like 说话, 唱歌, 游泳 correctly"],
        ["Topic-Comment Structure"]),
    (13, 74, "Common Word Order Rules",
        ["concept"],
        ["Internalise the core Mandarin word order: Subject–Time–Place–Manner–Verb–Object",
         "Self-correct word order errors and produce well-formed sentences confidently"],
        ["Topic-Comment Structure", "Verb-Object Patterns"]),
]


def seed_chinese_hsk2_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for Chinese HSK 2.
    Uses framework='HSK' and level='HSK2'.
    Two-pass: Pass 1 inserts nodes, Pass 2 resolves prereq topic names → IDs
    across ALL Chinese HSK nodes so HSK1 topics can be used as prereqs.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'zh'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("Chinese language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'HSK', 'HSK2', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _CHINESE_HSK2_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK2'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Pass 1: insert nodes with empty prerequisites ─────────────────────────
    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _CHINESE_HSK2_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'HSK', 'HSK2', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    # ── Pass 2: resolve prereq topic names → node IDs (all HSK Chinese nodes) ─
    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _CHINESE_HSK2_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK2' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK2'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK2'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] Chinese HSK 2 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── Chinese HSK 3 curriculum ────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_CHINESE_HSK3_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Consolidating Core Grammar",       "Increase fluency and improve natural spoken Mandarin by consolidating all HSK1–2 grammar",                   8),
    (2,  "Result Complements",               "Describe successful, failed, and completed actions using result complements",                                8),
    (3,  "Talking About the Past",           "Narrate events and describe experiences in sequence using advanced aspect markers and connectors",           10),
    (4,  "Future Plans & Intentions",        "Discuss plans, goals, and future activities using time markers and intention verbs",                        10),
    (5,  "Direction Complements",            "Describe movement and direction naturally using directional complement pairs",                              12),
    (6,  "Potential Complements",            "Express capability, possibility, and limitations using potential complement forms",                          6),
    (7,  "Modal & Auxiliary Verbs",          "Express desires, obligations, permissions, and possibilities with the full range of modal verbs",            9),
    (8,  "Cause & Effect",                   "Explain causes and outcomes clearly using 因为, 所以, 因此, and logical connectors",                           6),
    (9,  "Complex Comparisons",              "Make detailed comparisons and describe change over time using 比, 跟, 更, 最, and 越来越",                    8),
    (10, "Describing People, Feelings & Experiences", "Discuss emotions, personalities, and experiences in natural Mandarin",                             9),
    (11, "Work, School & Daily Life",        "Discuss work, studies, and responsibilities using practical everyday vocabulary",                           10),
    (12, "Travel & Social Life",             "Handle travel and social situations confidently",                                                            8),
    (13, "Communication Strategies",         "Participate actively in conversations and discussions using opinion and agreement language",                10),
    (14, "Sentence Pattern Expansion",       "Build more sophisticated and natural Mandarin sentences using advanced patterns",                            7),
    (15, "Connected Speech",                 "Produce connected speech rather than isolated sentences by linking ideas fluently",                          6),
    (16, "Writing Skills",                   "Write short connected texts on familiar topics across multiple genres",                                      6),
    (17, "着 and Continuous States",         "Describe continuing states and conditions accurately using 着",                                             6),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_CHINESE_HSK3_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 1: Consolidating Core Grammar ─────────────────────────────────
    (1, 1, "Review of 了 (Completed Actions)",
        ["concept"],
        ["Consolidate all uses of sentence-final 了 for completed actions",
         "Produce and correct 了 sentences fluently without hesitation"],
        ["了 (Completed Action)"]),
    (1, 2, "Review of 过 (Experiences)",
        ["concept"],
        ["Consolidate 过 for past experience and contrast with 了",
         "Narrate experience sentences naturally across tenses"],
        ["过 (Experience)"]),
    (1, 3, "Review of 在 (Ongoing Actions)",
        ["concept"],
        ["Consolidate 在, 正在, and 在…呢 for ongoing actions",
         "Distinguish progressive forms and use them correctly in context"],
        ["正在 (Ongoing Action)"]),
    (1, 4, "Review of 比 (Comparisons)",
        ["concept"],
        ["Consolidate all 比 comparison patterns from HSK2",
         "Produce comparison sentences quickly and accurately"],
        ["比 (Comparisons)"]),
    (1, 5, "Review of Measure Words",
        ["concept"],
        ["Consolidate the most common measure words and the nouns they pair with",
         "Use measure words automatically in quantity phrases"],
        ["Common Measure Word Patterns"]),
    (1, 6, "Natural Sentence Flow",
        ["speaking"],
        ["Produce multi-clause sentences without unnatural pauses",
         "Use fillers and connectors to keep speech flowing naturally"],
        ["Review of 了 (Completed Actions)", "Review of 过 (Experiences)"]),
    (1, 7, "Common Spoken Word Order Patterns",
        ["concept"],
        ["Internalise the most common word order patterns in spoken Mandarin",
         "Self-correct word order errors in real time"],
        ["Common Word Order Rules"]),
    (1, 8, "Reducing Direct Translation from English",
        ["skill"],
        ["Identify and eliminate direct English-to-Chinese translation errors",
         "Replace unnatural translated phrases with idiomatic Mandarin equivalents"],
        ["Natural Sentence Flow", "Common Spoken Word Order Patterns"]),

    # ── Module 2: Result Complements ─────────────────────────────────────────
    (2, 9, "Introduction to Result Complements",
        ["concept"],
        ["Understand the verb + result complement structure in Mandarin",
         "Recognise result complements in natural speech and text"],
        ["Review of 了 (Completed Actions)"]),
    (2, 10, "看懂 (Read and Understand)",
        ["concept"],
        ["Use 看懂 to express successful reading comprehension",
         "Form affirmative, negative, and question sentences with 看懂"],
        ["Introduction to Result Complements"]),
    (2, 11, "听懂 (Hear and Understand)",
        ["concept"],
        ["Use 听懂 to express successful listening comprehension",
         "Apply 听懂 in classroom, conversation, and media contexts"],
        ["Introduction to Result Complements"]),
    (2, 12, "做完 (Finish Doing)",
        ["concept"],
        ["Use 做完 to express completing a task",
         "Form sentences about finishing work, homework, and projects"],
        ["Introduction to Result Complements"]),
    (2, 13, "找到 (Successfully Find)",
        ["concept"],
        ["Use 找到 to express successfully locating something or someone",
         "Contrast 找到 with 没找到 in conversation"],
        ["Introduction to Result Complements"]),
    (2, 14, "买到 (Successfully Buy)",
        ["concept"],
        ["Use 买到 to express successfully purchasing an item",
         "Use 买到 and 没买到 in shopping and everyday situations"],
        ["Introduction to Result Complements"]),
    (2, 15, "学会 (Learn How To)",
        ["concept"],
        ["Use 学会 to express mastering a skill through learning",
         "Discuss skills you have and haven't mastered using 学会"],
        ["Introduction to Result Complements"]),
    (2, 16, "Using Result Complements in Conversation",
        ["communication"],
        ["Use multiple result complements naturally in conversation",
         "Describe outcomes, failures, and successes fluently"],
        ["看懂 (Read and Understand)", "听懂 (Hear and Understand)", "做完 (Finish Doing)", "找到 (Successfully Find)"]),

    # ── Module 3: Talking About the Past ─────────────────────────────────────
    (3, 17, "Advanced Usage of 了",
        ["concept"],
        ["Use 了 in complex sentences with time expressions, quantities, and clauses",
         "Handle advanced 了 placement in multi-verb sentences"],
        ["Review of 了 (Completed Actions)"]),
    (3, 18, "Change of State with 了",
        ["concept"],
        ["Use sentence-final 了 to signal a new situation or change of state",
         "Distinguish change-of-state 了 from completed-action 了 in context"],
        ["Advanced Usage of 了"]),
    (3, 19, "Mastering 过",
        ["concept"],
        ["Use 过 confidently for life experiences, including negation and questions",
         "Combine 过 with time expressions and result complements"],
        ["Review of 过 (Experiences)"]),
    (3, 20, "Talking About Life Experiences",
        ["communication"],
        ["Describe significant life experiences using 过, time expressions, and detail",
         "Ask and respond to experience questions naturally in conversation"],
        ["Mastering 过"]),
    (3, 21, "Sequencing Events",
        ["concept"],
        ["Order past events clearly using time words and sequencing connectors",
         "Build a coherent multi-event narrative in Mandarin"],
        ["Advanced Usage of 了", "Mastering 过"]),
    (3, 22, "先 (First)",
        ["concept"],
        ["Use 先 to indicate the first step in a sequence of actions",
         "Combine 先 with 然后 to narrate two-step processes"],
        ["Sequencing Events"]),
    (3, 23, "然后 (Then)",
        ["concept"],
        ["Use 然后 to continue a narrative sequence at HSK3 complexity",
         "Link three or more events naturally using 先…然后…"],
        ["先 (First)"]),
    (3, 24, "后来 (Afterwards)",
        ["concept"],
        ["Use 后来 to describe what happened later in a past narrative",
         "Distinguish 后来 from 然后 in temporal sequencing"],
        ["然后 (Then)"]),
    (3, 25, "最后 (Finally)",
        ["concept"],
        ["Use 最后 to close a narrative sequence or list",
         "Combine 先, 然后, 后来, and 最后 in a full story"],
        ["后来 (Afterwards)"]),
    (3, 26, "Storytelling in Mandarin",
        ["skill"],
        ["Tell a structured personal story using all past tense tools and sequence connectors",
         "Sustain a coherent multi-minute narrative in Mandarin"],
        ["最后 (Finally)", "Talking About Life Experiences"]),

    # ── Module 4: Future Plans & Intentions ──────────────────────────────────
    (4, 27, "Future Time Markers",
        ["concept"],
        ["Use 明天, 下周, 下个月, 明年, and 以后 to frame future statements",
         "Position time markers correctly at the start of a sentence"],
        ["Days and Dates"]),
    (4, 28, "明天 (Tomorrow)",
        ["communication"],
        ["Talk about tomorrow's plans using 明天 and future-oriented language",
         "Ask and answer questions about tomorrow's activities"],
        ["Future Time Markers"]),
    (4, 29, "下个月 (Next Month)",
        ["communication"],
        ["Discuss next month's plans and events",
         "Combine 下个月 with intention verbs in full sentences"],
        ["Future Time Markers"]),
    (4, 30, "明年 (Next Year)",
        ["communication"],
        ["Talk about long-term plans and goals using 明年",
         "Express hopes and intentions for the coming year"],
        ["Future Time Markers"]),
    (4, 31, "打算 (To Plan)",
        ["concept"],
        ["Use 打算 to express concrete plans and intentions",
         "Form 打算 sentences about near-future activities"],
        ["Future Time Markers"]),
    (4, 32, "准备 (To Prepare)",
        ["concept"],
        ["Use 准备 to express preparing to do something or making arrangements",
         "Distinguish 准备 from 打算 in context"],
        ["打算 (To Plan)"]),
    (4, 33, "希望 (To Hope)",
        ["concept"],
        ["Use 希望 to express wishes and hopes about the future",
         "Form sentences with 希望 + subject + verb phrase"],
        ["打算 (To Plan)"]),
    (4, 34, "计划 (To Plan)",
        ["concept"],
        ["Use 计划 to express organised plans, often more formal than 打算",
         "Distinguish 计划 from 打算 and 准备 in register"],
        ["打算 (To Plan)", "准备 (To Prepare)"]),
    (4, 35, "以后 (In the Future)",
        ["concept"],
        ["Use 以后 for future-oriented statements: after an event, or in general future",
         "Combine 以后 with 打算, 希望, and 计划 in forward-looking sentences"],
        ["Future Time Markers"]),
    (4, 36, "Discussing Goals and Intentions",
        ["communication"],
        ["Discuss personal goals and future intentions using all HSK3 intention vocabulary",
         "Sustain a conversation about plans, hopes, and ambitions naturally"],
        ["打算 (To Plan)", "希望 (To Hope)", "计划 (To Plan)", "以后 (In the Future)"]),

    # ── Module 5: Direction Complements ──────────────────────────────────────
    (5, 37, "Introduction to Direction Complements",
        ["concept"],
        ["Understand the verb + direction complement structure",
         "Recognise direction complements in listening and reading"],
        ["来 vs 去"]),
    (5, 38, "上来",
        ["concept"],
        ["Use 上来 to describe upward movement toward the speaker",
         "Apply 上来 with verbs of movement in sentences"],
        ["Introduction to Direction Complements"]),
    (5, 39, "上去",
        ["concept"],
        ["Use 上去 to describe upward movement away from the speaker",
         "Contrast 上来 and 上去 in context"],
        ["上来"]),
    (5, 40, "下来",
        ["concept"],
        ["Use 下来 to describe downward movement toward the speaker",
         "Apply 下来 in sentences about descending or coming down"],
        ["Introduction to Direction Complements"]),
    (5, 41, "下去",
        ["concept"],
        ["Use 下去 to describe downward movement away from the speaker",
         "Contrast 下来 and 下去 in context"],
        ["下来"]),
    (5, 42, "进来",
        ["concept"],
        ["Use 进来 for movement into a space toward the speaker",
         "Use 进来 in door, room, and space entry contexts"],
        ["Introduction to Direction Complements"]),
    (5, 43, "进去",
        ["concept"],
        ["Use 进去 for movement into a space away from the speaker",
         "Contrast 进来 and 进去 in entry scenarios"],
        ["进来"]),
    (5, 44, "出来",
        ["concept"],
        ["Use 出来 for movement out of a space toward the speaker",
         "Apply 出来 in exit and emergence contexts"],
        ["Introduction to Direction Complements"]),
    (5, 45, "出去",
        ["concept"],
        ["Use 出去 for movement out of a space away from the speaker",
         "Contrast 出来 and 出去 in everyday situations"],
        ["出来"]),
    (5, 46, "回来",
        ["concept"],
        ["Use 回来 for returning toward the speaker",
         "Use 回来 in contexts of returning home, to work, or to a place"],
        ["Introduction to Direction Complements"]),
    (5, 47, "回去",
        ["concept"],
        ["Use 回去 for returning away from the speaker",
         "Contrast 回来 and 回去 in return movement contexts"],
        ["回来"]),
    (5, 48, "Combining Verbs with Direction Complements",
        ["communication"],
        ["Combine action verbs with direction complements fluently in conversation",
         "Describe complex movement events using multi-complement sentences"],
        ["上来", "上去", "下来", "下去", "进来", "出来", "回来"]),

    # ── Module 6: Potential Complements ──────────────────────────────────────
    (6, 49, "Introduction to Potential Complements",
        ["concept"],
        ["Understand the verb + 得/不 + result/direction complement structure",
         "Distinguish potential complements from result complements"],
        ["Introduction to Result Complements"]),
    (6, 50, "看得懂 / 看不懂",
        ["concept"],
        ["Use 看得懂 and 看不懂 to express whether you can or cannot understand something by reading",
         "Apply in reading, studying, and media contexts"],
        ["Introduction to Potential Complements"]),
    (6, 51, "听得懂 / 听不懂",
        ["concept"],
        ["Use 听得懂 and 听不懂 to express listening comprehension ability",
         "Apply in conversation, lecture, and media listening contexts"],
        ["Introduction to Potential Complements"]),
    (6, 52, "做得到 / 做不到",
        ["concept"],
        ["Use 做得到 and 做不到 to express whether something is achievable",
         "Apply in discussions of tasks, goals, and challenges"],
        ["Introduction to Potential Complements"]),
    (6, 53, "找得到 / 找不到",
        ["concept"],
        ["Use 找得到 and 找不到 to express whether something can be found",
         "Apply in shopping, searching, and locating contexts"],
        ["Introduction to Potential Complements"]),
    (6, 54, "Potential Complements in Everyday Speech",
        ["communication"],
        ["Use potential complements naturally in conversation about ability and limitation",
         "Respond to ability questions using potential complement forms fluently"],
        ["看得懂 / 看不懂", "听得懂 / 听不懂", "做得到 / 做不到", "找得到 / 找不到"]),

    # ── Module 7: Modal & Auxiliary Verbs ────────────────────────────────────
    (7, 55, "会 (Ability and Learned Skills)",
        ["concept"],
        ["Use 会 for learned abilities and also for probable future events",
         "Distinguish ability 会 from future probability 会 in context"],
        ["会 (Learned Ability)"]),
    (7, 56, "能 (Ability and Possibility)",
        ["concept"],
        ["Use 能 for physical ability, circumstantial possibility, and requests",
         "Distinguish 能 from 会 and 可以 across registers"],
        ["能 (Physical Ability / Circumstantial Permission)"]),
    (7, 57, "可以 (Permission)",
        ["concept"],
        ["Use 可以 for permission in formal and informal contexts",
         "Form polite permission requests and responses"],
        ["可以 (Permission)"]),
    (7, 58, "想 (Want)",
        ["concept"],
        ["Use 想 for desires, wishes, and tentative intentions at HSK3 complexity",
         "Combine 想 with more complex verb phrases"],
        ["想 (Want / Would Like)"]),
    (7, 59, "要 (Need / Want)",
        ["concept"],
        ["Distinguish 要 for necessity, strong intention, and near-future plans",
         "Use 要 across formal and informal registers correctly"],
        ["要 (Need / Going To)"]),
    (7, 60, "应该 (Should)",
        ["concept"],
        ["Use 应该 to express moral or logical obligation",
         "Form advice and recommendation sentences with 应该"],
        ["Choosing the Correct Modal Verb" ]),
    (7, 61, "得 (Must)",
        ["concept"],
        ["Use 得 (děi) to express necessity and compulsion",
         "Distinguish 得 (děi) from 得 (de) as a structural particle"],
        ["应该 (Should)"]),
    (7, 62, "打算 (Intend To)",
        ["concept"],
        ["Use 打算 as a modal-like verb expressing intention",
         "Combine 打算 with time expressions and future plans"],
        ["打算 (To Plan)"]),
    (7, 63, "Choosing the Correct Modal Verb",
        ["skill"],
        ["Select the appropriate modal verb from 会, 能, 可以, 想, 要, 应该, 得, 打算 for a given context",
         "Avoid common modal verb substitution errors"],
        ["会 (Ability and Learned Skills)", "能 (Ability and Possibility)", "可以 (Permission)", "应该 (Should)", "得 (Must)"]),

    # ── Module 8: Cause & Effect ──────────────────────────────────────────────
    (8, 64, "因为…所以…",
        ["concept"],
        ["Use the full 因为…所以… structure to express cause and effect",
         "Form complete cause-effect sentences and identify them in speech"],
        ["因为…所以… (Because…Therefore…)"]),
    (8, 65, "所以",
        ["concept"],
        ["Use 所以 alone (without 因为) to signal a conclusion or consequence",
         "Understand when 所以 appears without an explicit 因为 clause"],
        ["因为…所以…"]),
    (8, 66, "因此 (Introduction)",
        ["concept"],
        ["Use 因此 as a formal written equivalent of 所以",
         "Recognise 因此 in written texts and produce it in formal contexts"],
        ["所以"]),
    (8, 67, "Giving Reasons",
        ["communication"],
        ["Give full, natural explanations for actions and decisions using causal connectors",
         "Respond to 为什么 questions with multi-clause answers"],
        ["因为…所以…", "所以"]),
    (8, 68, "Explaining Consequences",
        ["communication"],
        ["Explain the results and consequences of actions and situations",
         "Build logical consequence chains in conversation"],
        ["Giving Reasons", "因此 (Introduction)"]),
    (8, 69, "Building Logical Explanations",
        ["skill"],
        ["Combine cause, consequence, and opinion language into coherent logical arguments",
         "Sustain a reasoned explanation for two or more minutes"],
        ["Explaining Consequences"]),

    # ── Module 9: Complex Comparisons ────────────────────────────────────────
    (9, 70, "Review of 比",
        ["concept"],
        ["Consolidate all 比 comparison forms: degree, quantity, and frequency",
         "Use 比 in complex sentences without hesitation"],
        ["Comparing People", "Comparing Objects"]),
    (9, 71, "跟…一样…",
        ["concept"],
        ["Use 跟…一样… to express equality in comparisons",
         "Contrast 跟…一样… with 比 sentences in context"],
        ["Review of 比"]),
    (9, 72, "更… (Intensified Comparison)",
        ["concept"],
        ["Use 更 to intensify comparisons at HSK3 complexity with longer sentences",
         "Combine 更 with clauses and explanations"],
        ["Review of 比", "跟…一样…"]),
    (9, 73, "最… (Superlative)",
        ["concept"],
        ["Use 最 in extended sentences about rankings, preferences, and extremes",
         "Combine 最 with 的 nominalisations and relative clauses"],
        ["更… (Intensified Comparison)"]),
    (9, 74, "越来越… (Comparisons)",
        ["concept"],
        ["Use 越来越 to describe gradual change over time",
         "Form sentences about trends, progress, and deterioration"],
        ["最… (Superlative)"]),
    (9, 75, "Comparing People",
        ["communication"],
        ["Compare people's abilities, personalities, and habits using all HSK3 comparison tools",
         "Sustain a fluent comparison conversation about two or more people"],
        ["Review of 比", "更… (Intensified Comparison)", "最… (Superlative)"]),
    (9, 76, "Comparing Objects",
        ["communication"],
        ["Compare products, places, and options in practical situations",
         "Use comparisons to justify choices and express preferences"],
        ["跟…一样…", "Comparing People"]),
    (9, 77, "Comparing Situations and Trends",
        ["communication"],
        ["Describe changing situations and trends using 越来越 and comparison structures",
         "Discuss social, personal, and environmental changes naturally"],
        ["越来越… (Comparisons)", "Comparing Objects"]),

    # ── Module 10: Describing People, Feelings & Experiences ─────────────────
    (10, 78, "Personality Traits",
        ["concept"],
        ["Describe personality using adjectives: 开朗, 内向, 认真, 懒, 勤奋, 友好",
         "Use personality vocabulary in descriptions and comparisons"],
        ["Describing People"]),
    (10, 79, "Friendly and Outgoing Descriptions",
        ["communication"],
        ["Describe outgoing, friendly, and sociable personality types naturally",
         "Use 开朗, 外向, 热情, and 友好 in sentences about people"],
        ["Personality Traits"]),
    (10, 80, "Serious and Reserved Descriptions",
        ["communication"],
        ["Describe serious, reserved, and introverted personality types",
         "Use 内向, 严肃, 安静, and 认真 in context"],
        ["Personality Traits"]),
    (10, 81, "Feelings and Emotions",
        ["concept"],
        ["Name and express a range of emotions in Mandarin: happy, sad, angry, surprised, worried",
         "Use emotional vocabulary in conversation and narrative"],
        ["Talking About Yourself"]),
    (10, 82, "Excited",
        ["communication"],
        ["Express excitement using 兴奋, 激动, and 开心 in context",
         "Describe situations that cause excitement naturally"],
        ["Feelings and Emotions"]),
    (10, 83, "Nervous",
        ["communication"],
        ["Express nervousness using 紧张 in exam, performance, and social contexts",
         "Ask others if they are nervous and respond naturally"],
        ["Feelings and Emotions"]),
    (10, 84, "Disappointed",
        ["communication"],
        ["Express disappointment using 失望 and related vocabulary",
         "Describe disappointing situations and outcomes naturally"],
        ["Feelings and Emotions"]),
    (10, 85, "Health and Well-being",
        ["communication"],
        ["Discuss health, illness, and well-being using 身体, 生病, 感冒, 头疼, and 休息",
         "Ask about and describe health conditions in everyday situations"],
        ["Feelings and Emotions"]),
    (10, 86, "Describing Personal Experiences",
        ["communication"],
        ["Describe personal experiences combining emotion vocabulary, 过, and sequence connectors",
         "Sustain a vivid first-person experience narrative in Mandarin"],
        ["Storytelling in Mandarin", "Feelings and Emotions"]),

    # ── Module 11: Work, School & Daily Life ──────────────────────────────────
    (11, 87, "Jobs and Occupations",
        ["concept"],
        ["Name common jobs and professions and describe job responsibilities",
         "Ask and answer questions about work in natural conversation"],
        ["Talking About Work"]),
    (11, 88, "Workplace Vocabulary",
        ["concept"],
        ["Use workplace vocabulary: 办公室, 会议, 同事, 老板, 客户, 项目",
         "Describe the workplace environment and common work tasks"],
        ["Jobs and Occupations"]),
    (11, 89, "Education Vocabulary",
        ["concept"],
        ["Use education vocabulary: 学校, 班级, 作业, 成绩, 考试, 毕业",
         "Discuss academic life, subjects, and school experiences"],
        ["Talking About Studies"]),
    (11, 90, "Schedules and Timetables",
        ["communication"],
        ["Describe weekly schedules and timetables using time expressions",
         "Ask and respond to questions about regular commitments"],
        ["Daily Schedule"]),
    (11, 91, "Responsibilities",
        ["communication"],
        ["Discuss responsibilities at work, school, and home using 负责, 应该, and 得",
         "Express obligations and duties in natural conversation"],
        ["应该 (Should)", "得 (Must)"]),
    (11, 92, "上班",
        ["communication"],
        ["Use 上班 in sentences about going to work and work schedules",
         "Discuss commuting, start times, and work routines"],
        ["Workplace Vocabulary"]),
    (11, 93, "下班",
        ["communication"],
        ["Use 下班 in sentences about finishing work and after-work plans",
         "Discuss end-of-day routines and post-work activities"],
        ["上班"]),
    (11, 94, "上课",
        ["communication"],
        ["Use 上课 in sentences about attending class and study schedules",
         "Discuss class times, subjects, and attendance naturally"],
        ["Education Vocabulary"]),
    (11, 95, "考试",
        ["communication"],
        ["Discuss exams: preparation, performance, results, and feelings",
         "Use 考试, 复习, 通过, and 不及格 in context"],
        ["上课", "Nervous"]),
    (11, 96, "Daily Life Discussions",
        ["communication"],
        ["Discuss work, study, and home life in a connected, natural conversation",
         "Combine work, school, and responsibility vocabulary in sustained speech"],
        ["Workplace Vocabulary", "Education Vocabulary", "Responsibilities"]),

    # ── Module 12: Travel & Social Life ──────────────────────────────────────
    (12, 97, "Travel Situations",
        ["communication"],
        ["Handle common travel situations: lost, delayed, asking for help",
         "Use travel vocabulary and polite strategies to resolve problems"],
        ["Giving Travel Information"]),
    (12, 98, "Transportation",
        ["communication"],
        ["Discuss transport options, preferences, and routes at HSK3 complexity",
         "Compare transport methods and justify choices"],
        ["Transportation Vocabulary"]),
    (12, 99, "Hotels",
        ["communication"],
        ["Handle hotel check-in, check-out, requests, and complaints in Mandarin",
         "Use hotel vocabulary: 预订, 退房, 服务, 房间, 行李"],
        ["Travel Situations"]),
    (12, 100, "Invitations",
        ["communication"],
        ["Invite someone to an event, accept, and decline politely in Mandarin",
         "Use 邀请, 参加, 有空, and 不好意思 in social invitation contexts"],
        ["Social Plans"]),
    (12, 101, "Social Plans",
        ["communication"],
        ["Make and discuss social plans using intention verbs and time expressions",
         "Negotiate plans and suggest alternatives naturally"],
        ["打算 (To Plan)", "Discussing Goals and Intentions"]),
    (12, 102, "Visiting Friends",
        ["communication"],
        ["Handle a visit to a friend's home: arrival, conversation, and farewell",
         "Use appropriate social language for guest and host roles"],
        ["Invitations"]),
    (12, 103, "Making Arrangements",
        ["communication"],
        ["Arrange meetings, dates, and activities using time, place, and confirmation language",
         "Confirm, change, and cancel arrangements politely"],
        ["Social Plans", "Visiting Friends"]),
    (12, 104, "Common Social Interactions",
        ["communication"],
        ["Handle greetings, small talk, compliments, and farewells at a natural social level",
         "Sustain a short social conversation from opening to close"],
        ["Making Arrangements"]),

    # ── Module 13: Communication Strategies ──────────────────────────────────
    (13, 105, "我觉得…",
        ["communication"],
        ["Use 我觉得 to introduce personal opinions and feelings naturally",
         "Follow 我觉得 with full clauses in conversation"],
        ["Expressing Opinions"]),
    (13, 106, "我认为…",
        ["communication"],
        ["Use 我认为 for more considered or formal opinions",
         "Distinguish 我觉得 from 我认为 in register"],
        ["我觉得…"]),
    (13, 107, "同意",
        ["communication"],
        ["Express agreement using 同意, 对, 没错, and 我也觉得",
         "Agree with opinions naturally in spoken and written Mandarin"],
        ["我觉得…"]),
    (13, 108, "不同意",
        ["communication"],
        ["Disagree politely using 不同意, 但是, 我觉得不太对, and softening strategies",
         "Hold a respectful disagreement in conversation"],
        ["同意"]),
    (13, 109, "也许",
        ["concept"],
        ["Use 也许 to express uncertainty and possibility",
         "Combine 也许 with opinions and predictions naturally"],
        ["我认为…"]),
    (13, 110, "可能",
        ["concept"],
        ["Use 可能 to express probability at HSK3 complexity",
         "Distinguish 可能 from 也许 in formality and usage"],
        ["也许"]),
    (13, 111, "应该",
        ["concept"],
        ["Use 应该 in opinion and suggestion contexts",
         "Give advice and recommendations using 应该 naturally in discussion"],
        ["应该 (Should)"]),
    (13, 112, "Making Suggestions",
        ["communication"],
        ["Make suggestions using 我建议, 你可以, 不如, and 我们去吧",
         "Respond to suggestions positively, neutrally, and negatively"],
        ["我觉得…", "应该"]),
    (13, 113, "Giving Opinions",
        ["communication"],
        ["Give structured opinions using 我觉得, 我认为, 因为, and supporting evidence",
         "Sustain an opinion exchange for several turns"],
        ["我认为…", "Making Suggestions"]),
    (13, 114, "Agreeing and Disagreeing",
        ["skill"],
        ["Hold a full balanced discussion: agreeing, partly agreeing, and disagreeing respectfully",
         "Use all agreement and disagreement strategies in a sustained conversation"],
        ["同意", "不同意", "Giving Opinions"]),

    # ── Module 14: Sentence Pattern Expansion ────────────────────────────────
    (14, 115, "越来越… (Sentence Pattern)",
        ["concept"],
        ["Use 越来越 as a sentence-level pattern to describe progressive change",
         "Combine 越来越 with adjectives, verbs, and time contexts in complex sentences"],
        ["越来越… (Comparisons)"]),
    (14, 116, "一边…一边…",
        ["concept"],
        ["Use 一边…一边… to describe two actions happening simultaneously",
         "Form natural sentences about multitasking and parallel activities"],
        ["Natural Sentence Flow"]),
    (14, 117, "虽然…但是… (Pattern)",
        ["concept"],
        ["Use 虽然…但是… to concede a point while maintaining a contrasting argument",
         "Form concession sentences naturally in spoken and written Mandarin"],
        ["建立逻辑解释" if False else "Building Logical Explanations"]),
    (14, 118, "不但…而且…",
        ["concept"],
        ["Use 不但…而且… to express 'not only…but also…'",
         "Combine 不但…而且… with verbs and adjectives in natural sentences"],
        ["虽然…但是… (Pattern)"]),
    (14, 119, "除了…以外…",
        ["concept"],
        ["Use 除了…以外… to express 'except for' or 'in addition to'",
         "Apply 除了…以外… in both exclusive and inclusive meanings"],
        ["不但…而且…"]),
    (14, 120, "Combining Multiple Structures",
        ["skill"],
        ["Produce sentences that combine two or more advanced patterns naturally",
         "Avoid structural overload while increasing sentence complexity"],
        ["一边…一边…", "不但…而且…", "除了…以外…"]),
    (14, 121, "Producing Longer Sentences",
        ["skill"],
        ["Build multi-clause sentences of HSK3 length and complexity",
         "Self-edit for word order, aspect markers, and connectors in long sentences"],
        ["Combining Multiple Structures"]),

    # ── Module 15: Connected Speech ───────────────────────────────────────────
    (15, 122, "而且",
        ["concept"],
        ["Use 而且 to add a further point or intensify a statement",
         "Combine 而且 with 不但 and standalone in conversation"],
        ["不但…而且…"]),
    (15, 123, "但是",
        ["concept"],
        ["Use 但是 to introduce a contrast or reservation",
         "Distinguish 但是 from 可是 and 虽然…但是… in register"],
        ["虽然…但是… (Pattern)"]),
    (15, 124, "虽然…但是… (In Speech)",
        ["communication"],
        ["Use 虽然…但是… naturally in spoken responses and arguments",
         "Integrate 虽然…但是… into multi-turn conversational exchanges"],
        ["虽然…但是… (Pattern)", "但是"]),
    (15, 125, "Organizing Spoken Responses",
        ["skill"],
        ["Structure spoken answers with a clear opening, supporting points, and conclusion",
         "Use discourse markers to signal topic shifts and summaries"],
        ["而且", "但是"]),
    (15, 126, "Linking Multiple Ideas",
        ["skill"],
        ["Connect three or more ideas in a single spoken turn using connectors",
         "Avoid repetition and over-reliance on 然后 in connected speech"],
        ["Organizing Spoken Responses"]),
    (15, 127, "Speaking in Paragraphs",
        ["skill"],
        ["Produce spoken paragraphs of four or more sentences on a familiar topic",
         "Sustain coherent multi-sentence responses without prompting"],
        ["Linking Multiple Ideas"]),

    # ── Module 16: Writing Skills ─────────────────────────────────────────────
    (16, 128, "Writing Personal Messages",
        ["skill"],
        ["Write short informal messages in Mandarin using appropriate tone and vocabulary",
         "Apply greeting, body, and closing conventions for informal written Chinese"],
        ["Connected Speech" if False else "Storytelling in Mandarin"]),
    (16, 129, "Writing Emails",
        ["skill"],
        ["Structure and write a short formal or informal email in Mandarin",
         "Use 您好, 此致, and email conventions appropriately"],
        ["Writing Personal Messages"]),
    (16, 130, "Writing Descriptions",
        ["skill"],
        ["Write descriptive texts about people, places, and objects using rich vocabulary",
         "Combine adjectives, comparison structures, and 着 in written descriptions"],
        ["Writing Personal Messages"]),
    (16, 131, "Writing Narratives",
        ["skill"],
        ["Write a short personal narrative using past aspect markers and sequence connectors",
         "Organise a written account with a clear beginning, middle, and end"],
        ["Writing Personal Messages", "Storytelling in Mandarin"]),
    (16, 132, "Sequencing Events in Writing",
        ["skill"],
        ["Use 先, 然后, 后来, 最后 in written narratives to order events clearly",
         "Produce a well-sequenced written account of a past event"],
        ["Writing Narratives"]),
    (16, 133, "Expressing Opinions in Writing",
        ["skill"],
        ["Write a short opinion paragraph using 我觉得, 因为, and supporting reasons",
         "Structure a written argument with a claim, evidence, and conclusion"],
        ["Writing Narratives", "Giving Opinions"]),

    # ── Module 17: 着 and Continuous States ──────────────────────────────────
    (17, 134, "Introduction to 着",
        ["concept"],
        ["Understand 着 as a particle marking a continuing state or persistent condition",
         "Distinguish 着 from 在 and 了 in meaning and usage"],
        ["Review of 在 (Ongoing Actions)"]),
    (17, 135, "Describing Ongoing States",
        ["concept"],
        ["Use Verb + 着 to describe a state that continues as a backdrop to other actions",
         "Recognise 着 in reading and listening passages"],
        ["Introduction to 着"]),
    (17, 136, "门开着",
        ["concept"],
        ["Use 着 in object-state sentences like 门开着 and 灯开着",
         "Describe the state of objects in a room or environment"],
        ["Describing Ongoing States"]),
    (17, 137, "他站着",
        ["concept"],
        ["Use 着 with posture and position verbs: 站着, 坐着, 躺着, 穿着",
         "Describe how people are positioned or dressed using 着"],
        ["门开着"]),
    (17, 138, "Combining 着 with Everyday Verbs",
        ["communication"],
        ["Use 着 with a range of everyday verbs to describe ongoing background states",
         "Produce natural sentences where 着 frames the context for another action"],
        ["他站着"]),
    (17, 139, "着 vs 在 vs 了",
        ["skill"],
        ["Distinguish 着, 在, and 了 in sentences describing state, progress, and completion",
         "Self-correct aspect particle errors confidently in speech and writing"],
        ["Combining 着 with Everyday Verbs", "Review of 了 (Completed Actions)", "Review of 在 (Ongoing Actions)"]),
]


def seed_chinese_hsk3_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for Chinese HSK 3.
    Uses framework='HSK' and level='HSK3'.
    Two-pass: Pass 1 inserts nodes, Pass 2 resolves prereq topic names → IDs
    across ALL Chinese HSK nodes so HSK1/HSK2 topics can be used as prereqs.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'zh'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("Chinese language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'HSK', 'HSK3', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _CHINESE_HSK3_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK3'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _CHINESE_HSK3_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'HSK', 'HSK3', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _CHINESE_HSK3_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK3' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK3'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK3'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] Chinese HSK 3 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── Chinese HSK 4 curriculum ────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_CHINESE_HSK4_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Mastering Aspect Markers",          "Describe actions, experiences, and states accurately using 了, 着, and 过 at full HSK4 depth",              8),
    (2,  "Complex Time Relationships",         "Tell detailed stories and explanations with precise time sequencing",                                      11),
    (3,  "Complements Mastery",                "Express results, degree, and possibility using the full range of Mandarin complement types",              16),
    (4,  "Direction Complements",              "Describe movement and direction naturally using all directional complement pairs",                         12),
    (5,  "Advanced Comparisons",               "Compare ideas, people, and situations precisely using the full HSK4 comparison toolkit",                   9),
    (6,  "Expressing Opinions & Attitudes",    "Participate confidently in discussions by expressing, supporting, and softening opinions",                 9),
    (7,  "Cause, Effect & Logical Relationships","Explain reasoning and consequences clearly using advanced causal connectors",                            8),
    (8,  "Possibility, Probability & Necessity","Express confidence, obligation, and uncertainty with modal and adverbial markers",                        9),
    (9,  "Passive Voice (被)",                 "Describe events from multiple perspectives using 被 constructions",                                        7),
    (10, "Disposal Structure (把)",            "Describe how actions affect objects using 把 sentence patterns",                                           7),
    (11, "Advanced Sentence Patterns",         "Produce more natural and advanced sentence structures using complex patterns",                             8),
    (12, "Advanced Connectors",                "Produce connected and coherent speech using contrast, concession, and additive connectors",               7),
    (13, "Workplace & Academic Chinese",       "Handle work and study discussions confidently using professional and academic vocabulary",                 8),
    (14, "Society & Daily Life",               "Discuss broader social topics including health, technology, environment, and culture",                     8),
    (15, "Reading Development",                "Read authentic simplified Chinese materials including narratives, notices, and news",                     10),
    (16, "Functional Writing Skills",          "Write connected and purposeful texts across multiple registers and genres",                               10),
    (17, "Conversation & Discussion",          "Maintain comfortable conversations on a wide variety of topics including abstract subjects",               9),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_CHINESE_HSK4_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 1: Mastering Aspect Markers ───────────────────────────────────
    (1, 1, "Advanced Usage of 了",
        ["concept"],
        ["Use 了 in complex multi-clause sentences with time expressions and quantities",
         "Produce and correct advanced 了 usage without hesitation"],
        ["Advanced Usage of 了"]),
    (1, 2, "Change of State with 了",
        ["concept"],
        ["Distinguish change-of-state 了 from completed-action 了 in complex sentences",
         "Use sentence-final 了 to signal new situations in sustained speech"],
        ["Change of State with 了"]),
    (1, 3, "Sentence-Final 了",
        ["concept"],
        ["Master all functions of sentence-final 了 including change of state and new situation",
         "Eliminate common sentence-final 了 errors in both speech and writing"],
        ["Change of State with 了"]),
    (1, 4, "Introduction to 着",
        ["concept"],
        ["Consolidate all uses of 着 as a state-persistence marker",
         "Use 着 with posture, state, and backdrop action verbs automatically"],
        ["Introduction to 着"]),
    (1, 5, "Describing Ongoing States with 着",
        ["concept"],
        ["Use 着 fluently to describe ongoing background states in narratives",
         "Combine 着 with simultaneous action verbs naturally"],
        ["Describing Ongoing States with 着", "Introduction to 着"]),
    (1, 6, "Advanced Usage of 过",
        ["concept"],
        ["Use 过 in complex experience sentences with time frames and degree",
         "Combine 过 with result complements and quantifiers"],
        ["Mastering 过"]),
    (1, 7, "Combining Aspect Markers with Time Expressions",
        ["concept"],
        ["Combine 了, 着, and 过 with time expressions in multi-clause sentences",
         "Produce naturally sequenced narratives using all three aspect markers"],
        ["Advanced Usage of 了", "Describing Ongoing States with 着", "Advanced Usage of 过"]),
    (1, 8, "Choosing Between 了, 着, and 过",
        ["skill"],
        ["Select the correct aspect marker for any given context without hesitation",
         "Self-correct aspect marker errors in real-time speech and writing"],
        ["Combining Aspect Markers with Time Expressions"]),

    # ── Module 2: Complex Time Relationships ─────────────────────────────────
    (2, 9, "以前 (Before)",
        ["concept"],
        ["Use 以前 in complex time clauses to frame past contexts",
         "Combine 以前 with aspect markers and sequencing connectors"],
        ["以前 (Before / In the Past)"]),
    (2, 10, "以后 (After)",
        ["concept"],
        ["Use 以后 in complex future and post-event time clauses",
         "Combine 以后 with intention verbs and condition clauses"],
        ["以后 (After / In the Future)"]),
    (2, 11, "Simultaneous Actions",
        ["concept"],
        ["Describe two actions happening at the same time using time-overlap structures",
         "Distinguish simultaneous action patterns from sequential ones"],
        ["Describing Ongoing States with 着"]),
    (2, 12, "一边...一边... (Time)",
        ["concept"],
        ["Use 一边...一边... to describe two parallel simultaneous actions",
         "Produce natural 一边...一边... sentences about multitasking and parallel events"],
        ["Simultaneous Actions"]),
    (2, 13, "Sequencing Events (HSK4)",
        ["concept"],
        ["Sequence complex multi-event narratives with precise time markers",
         "Build chronological accounts using the full range of sequencing tools"],
        ["Storytelling in Mandarin"]),
    (2, 14, "首先",
        ["concept"],
        ["Use 首先 to mark the first step in formal spoken and written sequences",
         "Distinguish 首先 from 先 in register and context"],
        ["Sequencing Events (HSK4)"]),
    (2, 15, "然后 (HSK4)",
        ["concept"],
        ["Use 然后 in extended multi-step narratives and explanations",
         "Avoid over-reliance on 然后 by alternating with other sequencing connectors"],
        ["首先"]),
    (2, 16, "后来 (HSK4)",
        ["concept"],
        ["Use 后来 to mark unexpected or significant developments in past narratives",
         "Distinguish 后来 from 然后 in narrative register"],
        ["然后 (HSK4)"]),
    (2, 17, "最后 (HSK4)",
        ["concept"],
        ["Use 最后 to close narratives, arguments, and procedural explanations",
         "Combine 首先, 然后, 后来, and 最后 in a fluent extended account"],
        ["后来 (HSK4)"]),
    (2, 18, "Duration Patterns (...了多久)",
        ["concept"],
        ["Express how long an action lasted using 了 + duration phrase + 了",
         "Ask and answer duration questions using 多久 and 多长时间"],
        ["Combining Aspect Markers with Time Expressions"]),
    (2, 19, "Building Chronological Narratives",
        ["skill"],
        ["Tell a detailed chronological account using all time markers and sequence connectors",
         "Sustain a five-minute narrative with clear temporal structure"],
        ["最后 (HSK4)", "Duration Patterns (...了多久)"]),

    # ── Module 3: Complements Mastery ────────────────────────────────────────
    (3, 20, "Introduction to Complements",
        ["concept"],
        ["Understand all complement types in Mandarin: result, degree, potential, and direction",
         "Identify complement types in listening and reading passages"],
        ["Using Result Complements in Conversation"]),
    (3, 21, "Result Complement 完",
        ["concept"],
        ["Use 完 as a result complement meaning 'finish' across verbs and contexts",
         "Form affirmative, negative, and question sentences with Verb + 完"],
        ["Introduction to Complements"]),
    (3, 22, "Result Complement 好",
        ["concept"],
        ["Use 好 as a result complement meaning 'successfully done' or 'ready'",
         "Apply Verb + 好 in preparation, completion, and satisfactory-outcome sentences"],
        ["Introduction to Complements"]),
    (3, 23, "Result Complement 到",
        ["concept"],
        ["Use 到 as a result complement meaning 'reach' or 'achieve'",
         "Form 到 complement sentences about reaching goals, locations, and time points"],
        ["Introduction to Complements"]),
    (3, 24, "Result Complement 懂",
        ["concept"],
        ["Use 懂 as a result complement meaning 'come to understand'",
         "Apply Verb + 懂 in reading, listening, and learning contexts"],
        ["Introduction to Complements"]),
    (3, 25, "Result Complement 见",
        ["concept"],
        ["Use 见 as a result complement meaning 'perceive' or 'sense'",
         "Form 看见, 听见, 闻见 sentences about sensory perception"],
        ["Introduction to Complements"]),
    (3, 26, "Degree Complements",
        ["concept"],
        ["Use 得 + degree phrase to describe how an action is performed",
         "Form degree complement sentences with adjectival and verbal complements"],
        ["Introduction to Complements"]),
    (3, 27, "跑得很快",
        ["concept"],
        ["Use 跑得很快 as a model for speed and manner degree complements",
         "Produce degree complement sentences about physical actions and speeds"],
        ["Degree Complements"]),
    (3, 28, "说得很好",
        ["concept"],
        ["Use 说得很好 as a model for quality and proficiency degree complements",
         "Give and receive praise and criticism using degree complements naturally"],
        ["Degree Complements"]),
    (3, 29, "Potential Complements",
        ["concept"],
        ["Understand the full potential complement system: Verb + 得/不 + result or direction",
         "Distinguish potential complements from result and degree complements"],
        ["看得懂 / 看不懂", "听得懂 / 听不懂", "做得到 / 做不到"]),
    (3, 30, "看得懂 / 看不懂 (Mastery)",
        ["concept"],
        ["Use 看得懂 and 看不懂 with full fluency in complex reading and comprehension contexts",
         "Apply in academic, professional, and media reading situations"],
        ["Potential Complements"]),
    (3, 31, "听得懂 / 听不懂 (Mastery)",
        ["concept"],
        ["Use 听得懂 and 听不懂 with full fluency in complex listening contexts",
         "Apply in lectures, discussions, dialects, and rapid-speech situations"],
        ["Potential Complements"]),
    (3, 32, "做得到 / 做不到 (Mastery)",
        ["concept"],
        ["Use 做得到 and 做不到 fluently for complex tasks, goals, and challenges",
         "Discuss capability and limitation in professional and personal contexts"],
        ["Potential Complements"]),
    (3, 33, "Resultative Expressions",
        ["concept"],
        ["Understand expressive result complement patterns indicating emotional or physical extremes",
         "Recognise and produce high-affect resultative expressions in natural speech"],
        ["看得懂 / 看不懂 (Mastery)", "做得到 / 做不到 (Mastery)"]),
    (3, 34, "累坏了",
        ["communication"],
        ["Use 累坏了 and similar V + 坏 + 了 patterns to express extreme fatigue and damage",
         "Apply 坏 result complements in emotive everyday speech"],
        ["Resultative Expressions"]),
    (3, 35, "高兴极了",
        ["communication"],
        ["Use 高兴极了 and similar Adj + 极了 patterns to express extremes of feeling",
         "Produce 极了 expressions for joy, anger, surprise, and disappointment"],
        ["Resultative Expressions"]),

    # ── Module 4: Direction Complements ──────────────────────────────────────
    (4, 36, "上来",
        ["concept"],
        ["Use 上来 fluently in complex movement sentences toward the speaker",
         "Combine 上来 with objects and location phrases in extended sentences"],
        ["上来"]),
    (4, 37, "上去",
        ["concept"],
        ["Use 上去 fluently in complex movement sentences away from the speaker",
         "Alternate 上来 and 上去 correctly in directional narratives"],
        ["上去"]),
    (4, 38, "下来",
        ["concept"],
        ["Use 下来 fluently to describe downward movement toward speaker in context",
         "Apply 下来 metaphorically as well as literally"],
        ["下来"]),
    (4, 39, "下去",
        ["concept"],
        ["Use 下去 to describe downward movement away and continuing actions",
         "Apply 下去 in both spatial and 'keep doing' senses"],
        ["下去"]),
    (4, 40, "进来",
        ["concept"],
        ["Use 进来 fluently for entry movement toward the speaker",
         "Combine 进来 with objects in sentences like 拿进来"],
        ["进来"]),
    (4, 41, "进去",
        ["concept"],
        ["Use 进去 fluently for entry movement away from the speaker",
         "Contrast 进来 and 进去 in real-time directional communication"],
        ["进去"]),
    (4, 42, "出来",
        ["concept"],
        ["Use 出来 fluently for exit and emergence toward the speaker",
         "Apply 出来 in both physical and figurative senses"],
        ["出来"]),
    (4, 43, "出去",
        ["concept"],
        ["Use 出去 fluently for exit movement away from the speaker",
         "Combine 出去 with verbs of sending, taking, and moving in complex sentences"],
        ["出去"]),
    (4, 44, "回来",
        ["concept"],
        ["Use 回来 fluently in complex return sentences with objects and time frames",
         "Apply 回来 with verbs like 带, 拿, and 送 in natural speech"],
        ["回来"]),
    (4, 45, "回去",
        ["concept"],
        ["Use 回去 fluently for return movement away from speaker",
         "Contrast 回来 and 回去 and use both correctly in rapid speech"],
        ["回去"]),
    (4, 46, "Compound Direction Complements",
        ["concept"],
        ["Combine a primary direction verb with 来 or 去 in compound complements: 走上来, 跑进去",
         "Use compound direction complements in complex movement narratives"],
        ["上来", "上去", "进来", "出来", "回来"]),
    (4, 47, "Using Direction Complements in Daily Conversation",
        ["communication"],
        ["Use all direction complement types naturally in everyday conversation",
         "Sustain a directional movement description without hesitation"],
        ["Compound Direction Complements"]),

    # ── Module 5: Advanced Comparisons ───────────────────────────────────────
    (5, 48, "Review of 比",
        ["concept"],
        ["Consolidate all 比 patterns including degree, quantity, and frequency at HSK4 complexity",
         "Use 比 in multi-clause sentences and extended comparisons"],
        ["Comparing People (HSK4)" if False else "Comparing People", "Comparing Objects"]),
    (5, 49, "不如...",
        ["concept"],
        ["Use 不如 to express that A is not as good as B",
         "Compare options using 不如 in preference and recommendation contexts"],
        ["Review of 比"]),
    (5, 50, "没有...那么...",
        ["concept"],
        ["Use 没有...那么... to make negative equality comparisons",
         "Contrast 没有...那么... with 不如 and 比 in context"],
        ["不如..."]),
    (5, 51, "跟...一样... (HSK4)",
        ["concept"],
        ["Use 跟...一样... in complex equality comparisons at HSK4 level",
         "Combine 跟...一样... with degree adverbs and noun phrases"],
        ["没有...那么..."]),
    (5, 52, "越来越... (Advanced Comparisons)",
        ["concept"],
        ["Use 越来越 in extended sentences about trends, changes, and progression",
         "Combine 越来越 with complex verb and adjective phrases"],
        ["越来越… (Comparisons)"]),
    (5, 53, "Comparing People",
        ["communication"],
        ["Compare two or more people using all HSK4 comparison structures in extended discourse",
         "Sustain a nuanced people-comparison conversation naturally"],
        ["Review of 比", "跟...一样... (HSK4)"]),
    (5, 54, "Comparing Situations",
        ["communication"],
        ["Compare situations, conditions, and states using the full comparison toolkit",
         "Discuss changing situations using 越来越 and 比...更 structures"],
        ["越来越... (Advanced Comparisons)", "Comparing People"]),
    (5, 55, "Comparing Trends",
        ["communication"],
        ["Describe and compare trends over time using 越来越 and before/after structures",
         "Discuss social, environmental, and personal trends in extended speech"],
        ["Comparing Situations"]),
    (5, 56, "Expressing Nuance in Comparisons",
        ["skill"],
        ["Use hedging, intensifying, and conceding language to add nuance to comparisons",
         "Produce comparison statements that reflect subtle distinctions"],
        ["Comparing Trends", "没有...那么..."]),

    # ── Module 6: Expressing Opinions & Attitudes ─────────────────────────────
    (6, 57, "我觉得...",
        ["communication"],
        ["Use 我觉得 fluently to introduce opinions in extended academic and social discussion",
         "Follow 我觉得 with complex clauses and support structures"],
        ["我觉得…"]),
    (6, 58, "我认为...",
        ["communication"],
        ["Use 我认为 for considered and formal opinions in discussion and writing",
         "Alternate 我觉得 and 我认为 appropriately by register"],
        ["我认为…"]),
    (6, 59, "在我看来...",
        ["communication"],
        ["Use 在我看来 to signal a personal perspective in formal discussion",
         "Open opinion paragraphs with 在我看来 and follow with structured argument"],
        ["我认为..."]),
    (6, 60, "Expressing Agreement",
        ["communication"],
        ["Express agreement using 同意, 对, 没错, 确实, 你说得对, and 我也这么认为",
         "Agree with and build on others' points in multi-turn discussion"],
        ["同意"]),
    (6, 61, "Expressing Disagreement",
        ["communication"],
        ["Disagree politely and substantively using 不同意, 我觉得不太对, 但是, and 其实",
         "Maintain respectful disagreement across multiple turns"],
        ["不同意"]),
    (6, 62, "Supporting Opinions",
        ["skill"],
        ["Support opinions with evidence, examples, and reasons using 因为, 比如, 而且",
         "Build a three-part opinion: claim, support, conclusion"],
        ["我认为...", "在我看来..."]),
    (6, 63, "Giving Reasons",
        ["communication"],
        ["Give full multi-sentence explanations using causal and logical connectors",
         "Respond to 为什么 with structured, natural multi-clause answers"],
        ["Supporting Opinions", "因为…所以…"]),
    (6, 64, "Softening Opinions",
        ["communication"],
        ["Use hedging language — 也许, 可能, 不一定, 我不太确定 — to soften strong opinions",
         "Balance assertiveness with politeness in discussion"],
        ["也许", "可能 (HSK4)" if False else "可能"]),
    (6, 65, "Discussing Different Viewpoints",
        ["skill"],
        ["Present, compare, and evaluate multiple viewpoints in a structured discussion",
         "Sustain a balanced multi-perspective conversation for three or more minutes"],
        ["Expressing Agreement", "Expressing Disagreement", "Softening Opinions"]),

    # ── Module 7: Cause, Effect & Logical Relationships ──────────────────────
    (7, 66, "因为...所以... (HSK4)",
        ["concept"],
        ["Use 因为...所以... in complex multi-clause arguments and explanations",
         "Nest 因为...所以... within larger sentence structures naturally"],
        ["因为…所以…"]),
    (7, 67, "由于...",
        ["concept"],
        ["Use 由于 as a formal written equivalent of 因为",
         "Apply 由于 in reports, formal emails, and academic writing"],
        ["因为...所以... (HSK4)"]),
    (7, 68, "因此... (Advanced)",
        ["concept"],
        ["Use 因此 in complex written and spoken logical chains",
         "Combine 由于 and 因此 in formal cause-effect constructions"],
        ["由于..."]),
    (7, 69, "结果...",
        ["concept"],
        ["Use 结果 to introduce an unexpected or significant outcome",
         "Distinguish 结果 from 所以 in narrative versus logical contexts"],
        ["因此... (Advanced)"]),
    (7, 70, "Explaining Reasons",
        ["communication"],
        ["Give structured multi-sentence explanations for complex situations",
         "Use 由于, 因为, and 因此 appropriately in formal explanation contexts"],
        ["由于...", "因此... (Advanced)"]),
    (7, 71, "Explaining Consequences",
        ["communication"],
        ["Describe consequences and outcomes using 所以, 因此, and 结果 fluently",
         "Build logical consequence chains in formal and informal registers"],
        ["结果...", "Explaining Reasons"]),
    (7, 72, "Cause-and-Effect Narratives",
        ["skill"],
        ["Tell a cause-and-effect story using all causal connectors in a sustained narrative",
         "Alternate formal and informal causal language appropriately"],
        ["Explaining Consequences"]),
    (7, 73, "Building Logical Arguments",
        ["skill"],
        ["Construct a multi-step logical argument: premise, evidence, and conclusion",
         "Sustain a reasoned argument for three or more minutes in Mandarin"],
        ["Cause-and-Effect Narratives", "Discussing Different Viewpoints"]),

    # ── Module 8: Possibility, Probability & Necessity ───────────────────────
    (8, 74, "应该 (Probability)",
        ["concept"],
        ["Use 应该 to express probability and reasonable expectation",
         "Distinguish probability 应该 from obligation 应该 in context"],
        ["应该 (Should)"]),
    (8, 75, "必须",
        ["concept"],
        ["Use 必须 to express strong necessity and compulsion",
         "Distinguish 必须 from 应该 and 得 in degree of obligation"],
        ["应该 (Probability)"]),
    (8, 76, "可能 (HSK4)",
        ["concept"],
        ["Use 可能 in complex probability statements and conditional sentences",
         "Combine 可能 with 会, 是, and conditionals at HSK4 depth"],
        ["可能"]),
    (8, 77, "一定",
        ["concept"],
        ["Use 一定 to express certainty, determination, and strong probability",
         "Distinguish 一定 from 必须 and 肯定 in context"],
        ["可能 (HSK4)"]),
    (8, 78, "大概",
        ["concept"],
        ["Use 大概 to express rough estimation and approximation",
         "Combine 大概 with quantity expressions and time frames"],
        ["一定"]),
    (8, 79, "Degrees of Certainty",
        ["concept"],
        ["Rank and apply modal markers by certainty: 大概 → 可能 → 应该 → 一定 → 必须",
         "Choose the correct certainty marker for a given context"],
        ["大概", "一定", "必须"]),
    (8, 80, "Making Predictions",
        ["communication"],
        ["Make predictions about people, events, and trends using 会, 可能, 一定, and 大概",
         "Support predictions with reasons in natural conversation"],
        ["Degrees of Certainty"]),
    (8, 81, "Expressing Obligation",
        ["communication"],
        ["Express obligations and duties using 必须, 应该, 得, and 要 appropriately",
         "Give and respond to obligation statements in workplace and social contexts"],
        ["必须", "应该 (Probability)"]),
    (8, 82, "Expressing Probability",
        ["communication"],
        ["Express varying degrees of probability naturally in conversation and writing",
         "Use probability language to hedge, speculate, and predict fluently"],
        ["Making Predictions", "Expressing Obligation"]),

    # ── Module 9: Passive Voice (被) ──────────────────────────────────────────
    (9, 83, "Introduction to 被 Sentences",
        ["concept"],
        ["Understand when and why Mandarin uses 被 passive constructions",
         "Recognise 被 sentences in reading and listening passages"],
        ["Common Word Order Rules"]),
    (9, 84, "Basic Passive Constructions",
        ["concept"],
        ["Form basic Subject + 被 + Agent + Verb + Result sentences",
         "Identify the agent and patient roles in 被 sentences"],
        ["Introduction to 被 Sentences"]),
    (9, 85, "Extended Passive Structures",
        ["concept"],
        ["Form extended 被 sentences with complements, 了, and time expressions",
         "Produce complex passive sentences naturally in written and spoken Mandarin"],
        ["Basic Passive Constructions"]),
    (9, 86, "被 in Everyday Conversation",
        ["communication"],
        ["Use 被 naturally in conversation to describe things that happened to people",
         "Avoid over-using 被 by recognising when active voice is more natural"],
        ["Extended Passive Structures"]),
    (9, 87, "Passive vs Active Meaning",
        ["skill"],
        ["Choose between passive and active constructions to express the right focus",
         "Analyse sentences for information structure and topic prominence"],
        ["被 in Everyday Conversation"]),
    (9, 88, "Describing Unwanted Events",
        ["communication"],
        ["Use 被 to describe negative or unwanted events that happened to the subject",
         "Express misfortune, loss, and accidents using 被 naturally"],
        ["Passive vs Active Meaning"]),
    (9, 89, "Formal Passive Usage",
        ["skill"],
        ["Use 被 in formal written contexts: reports, news summaries, and official language",
         "Distinguish formal 被 usage from everyday conversational passive"],
        ["Describing Unwanted Events"]),

    # ── Module 10: Disposal Structure (把) ───────────────────────────────────
    (10, 90, "Introduction to 把 Sentences",
        ["concept"],
        ["Understand when 把 is used to bring the object before the verb",
         "Recognise 把 sentences in reading and listening passages"],
        ["Verb-Object Patterns"]),
    (10, 91, "Basic 把 Structure",
        ["concept"],
        ["Form Subject + 把 + Object + Verb + Result sentences correctly",
         "Identify which verbs and contexts require or allow 把"],
        ["Introduction to 把 Sentences"]),
    (10, 92, "Result-Oriented Actions",
        ["concept"],
        ["Use 把 with result complements to describe actions that change or affect the object",
         "Form 把 sentences with 完, 好, 到, and 坏 as result complements"],
        ["Basic 把 Structure"]),
    (10, 93, "把 with Complements",
        ["concept"],
        ["Combine 把 with degree, direction, and potential complements",
         "Produce 把 sentences with complex complement structures"],
        ["Result-Oriented Actions"]),
    (10, 94, "把 in Everyday Speech",
        ["communication"],
        ["Use 把 naturally in conversation about tidying, preparing, and affecting objects",
         "Recognise when native speakers use 把 versus SVO in natural speech"],
        ["把 with Complements"]),
    (10, 95, "Common 把 Patterns",
        ["concept"],
        ["Memorise and produce the most frequent 把 sentence patterns in Mandarin",
         "Avoid the most common 把 errors including missing result complements"],
        ["把 in Everyday Speech"]),
    (10, 96, "Choosing Between Normal and 把 Sentences",
        ["skill"],
        ["Select appropriately between SVO and 把 structure for a given communicative goal",
         "Explain why 把 is or is not appropriate in a given context"],
        ["Common 把 Patterns", "Introduction to 被 Sentences"]),

    # ── Module 11: Advanced Sentence Patterns ────────────────────────────────
    (11, 97, "一边...一边... (Advanced)",
        ["concept"],
        ["Use 一边...一边... in complex sentences describing parallel professional and abstract actions",
         "Combine 一边...一边... with complements and modal verbs"],
        ["一边...一边... (Time)"]),
    (11, 98, "越来越... (Advanced Pattern)",
        ["concept"],
        ["Use 越来越 in sophisticated sentences about trends, emotions, and abstract change",
         "Combine 越来越 with modal verbs, conditionals, and cause-effect structures"],
        ["越来越... (Advanced Comparisons)"]),
    (11, 99, "除了...以外... (Exclusion)",
        ["concept"],
        ["Use 除了...以外... to express 'except for' with exclusion meaning",
         "Apply the exclusion sense of 除了 in negative and contrasting contexts"],
        ["除了…以外…"]),
    (11, 100, "不管...都...",
        ["concept"],
        ["Use 不管...都... to express 'no matter what/who/how, still…'",
         "Form concessive conditional sentences using 不管 with question words"],
        ["虽然…但是… (Pattern)"]),
    (11, 101, "无论...都... (Introduction)",
        ["concept"],
        ["Use 无论...都... as a more formal equivalent of 不管...都...",
         "Distinguish 无论 and 不管 by register and written versus spoken use"],
        ["不管...都..."]),
    (11, 102, "即使...也... (Introduction)",
        ["concept"],
        ["Use 即使...也... to express 'even if' in concessive conditional sentences",
         "Contrast 即使 with 虽然 in hypothetical versus factual concession"],
        ["无论...都... (Introduction)"]),
    (11, 103, "Combining Multiple Patterns",
        ["skill"],
        ["Produce sentences that combine two or more advanced patterns fluently",
         "Edit for naturalness and avoid structural overload in complex sentences"],
        ["一边...一边... (Advanced)", "越来越... (Advanced Pattern)", "即使...也... (Introduction)"]),
    (11, 104, "Creating Sophisticated Sentences",
        ["skill"],
        ["Build multi-clause sentences demonstrating HSK4 grammatical range",
         "Self-edit complex sentences for accuracy, naturalness, and coherence"],
        ["Combining Multiple Patterns"]),

    # ── Module 12: Advanced Connectors ───────────────────────────────────────
    (12, 105, "虽然...但是... (HSK4)",
        ["concept"],
        ["Use 虽然...但是... in complex arguments, opinion pieces, and extended speech",
         "Combine with opinion language and cause-effect connectors in full paragraphs"],
        ["虽然…但是… (In Speech)"]),
    (12, 106, "不但...而且... (Advanced)",
        ["concept"],
        ["Use 不但...而且... in formal argumentation and extended written texts",
         "Combine 不但...而且... with 也, 还, and 更 for additive intensification"],
        ["不但…而且…"]),
    (12, 107, "除了...以外... (Addition)",
        ["concept"],
        ["Use 除了...以外... to express 'in addition to' with inclusive meaning",
         "Distinguish inclusive 除了 from exclusive 除了 with precision"],
        ["除了...以外... (Exclusion)"]),
    (12, 108, "不仅...还...",
        ["concept"],
        ["Use 不仅...还... to add a further intensifying point",
         "Compare 不仅...还... with 不但...而且... in register and usage"],
        ["不但...而且... (Advanced)"]),
    (12, 109, "Linking Multiple Ideas (HSK4)",
        ["skill"],
        ["Connect four or more ideas in sustained speech using varied connectors",
         "Avoid connector repetition and build naturally flowing multi-point arguments"],
        ["虽然...但是... (HSK4)", "不仅...还..."]),
    (12, 110, "Contrast and Concession",
        ["skill"],
        ["Use contrast and concession connectors fluently in discussion and debate",
         "Signal disagreement, qualification, and nuance naturally in conversation"],
        ["Linking Multiple Ideas (HSK4)"]),
    (12, 111, "Building Coherent Paragraphs",
        ["skill"],
        ["Produce spoken and written paragraphs with clear topic sentences and connected support",
         "Apply discourse markers to organise paragraphs for a listener or reader"],
        ["Contrast and Concession"]),

    # ── Module 13: Workplace & Academic Chinese ───────────────────────────────
    (13, 112, "Education Systems",
        ["concept"],
        ["Describe education systems: primary, secondary, university, and vocational in China and internationally",
         "Compare education systems using HSK4 comparison and opinion structures"],
        ["Education Vocabulary"]),
    (13, 113, "Exams and Assessment",
        ["communication"],
        ["Discuss exams, grades, assessments, and academic pressure",
         "Express opinions and experiences about exams using complex structures"],
        ["Education Systems", "考试"]),
    (13, 114, "University Life",
        ["communication"],
        ["Describe university courses, campus life, student activities, and academic challenges",
         "Sustain a conversation about university experience naturally"],
        ["Exams and Assessment"]),
    (13, 115, "Careers and Employment",
        ["communication"],
        ["Discuss career paths, job searching, interviews, and employment conditions",
         "Use 找工作, 面试, 薪水, and 发展 in context"],
        ["Jobs and Occupations"]),
    (13, 116, "Workplace Vocabulary (HSK4)",
        ["concept"],
        ["Use advanced workplace vocabulary: 项目, 汇报, 合同, 截止日期, 效率, 绩效",
         "Discuss work tasks and challenges using professional register"],
        ["Workplace Vocabulary"]),
    (13, 117, "Office Communication",
        ["communication"],
        ["Communicate in workplace situations: meetings, emails, requests, and updates",
         "Use formal and polite language appropriately in professional contexts"],
        ["Workplace Vocabulary (HSK4)"]),
    (13, 118, "Professional Situations",
        ["communication"],
        ["Handle professional scenarios: presentations, negotiations, and problem-solving",
         "Sustain a professional conversation in Mandarin naturally"],
        ["Office Communication"]),
    (13, 119, "Meetings and Discussions",
        ["communication"],
        ["Participate in meetings: agree, disagree, suggest, clarify, and summarise",
         "Use formal discussion language in structured meeting contexts"],
        ["Professional Situations", "Discussing Different Viewpoints"]),

    # ── Module 14: Society & Daily Life ──────────────────────────────────────
    (14, 120, "Health and Healthcare",
        ["communication"],
        ["Discuss health issues, medical appointments, treatments, and healthcare systems",
         "Use 症状, 医院, 治疗, 手术, and 保险 in medical conversations"],
        ["Health and Well-being"]),
    (14, 121, "Technology",
        ["communication"],
        ["Discuss technology trends, digital life, social media, and online behaviour",
         "Express opinions about technology using HSK4 opinion and comparison structures"],
        ["Discussing Different Viewpoints"]),
    (14, 122, "Environment",
        ["communication"],
        ["Discuss environmental issues: pollution, climate, recycling, and sustainability",
         "Use 环境, 污染, 保护, 节能 in context and argue for positions"],
        ["Building Logical Arguments"]),
    (14, 123, "Relationships",
        ["communication"],
        ["Discuss relationships: family dynamics, friendships, romantic relationships, and social bonds",
         "Use 关系, 感情, 矛盾, and 沟通 in extended relationship conversations"],
        ["Describing People"]),
    (14, 124, "Lifestyle Choices",
        ["communication"],
        ["Discuss and evaluate lifestyle choices: diet, exercise, work-life balance, and habits",
         "Express and justify lifestyle preferences using comparison and opinion structures"],
        ["Expressing Nuance in Comparisons"]),
    (14, 125, "Cultural Topics",
        ["communication"],
        ["Discuss Chinese and global cultural topics: festivals, traditions, food culture, and arts",
         "Compare cultural practices and express cultural opinions naturally"],
        ["Discussing Different Viewpoints"]),
    (14, 126, "Social Issues",
        ["communication"],
        ["Discuss social issues: education, inequality, urbanisation, and generational change",
         "Argue positions and evaluate solutions using logical argument structures"],
        ["Building Logical Arguments", "Environment"]),
    (14, 127, "Community Life",
        ["communication"],
        ["Discuss community, neighbourhood, civic participation, and social responsibility",
         "Sustain a conversation about community topics at HSK4 depth"],
        ["Social Issues"]),

    # ── Module 15: Reading Development ───────────────────────────────────────
    (15, 128, "Personal Narratives (Reading)",
        ["skill"],
        ["Read and fully comprehend personal narrative texts in simplified Chinese",
         "Identify narrative structure, voice, and key events in authentic texts"],
        ["Storytelling in Mandarin"]),
    (15, 129, "Informational Texts",
        ["skill"],
        ["Read informational and expository texts: articles, summaries, and encyclopaedia entries",
         "Extract main ideas, supporting details, and implied meaning from non-fiction"],
        ["Personal Narratives (Reading)"]),
    (15, 130, "Advertisements",
        ["skill"],
        ["Read and analyse advertisements, promotional materials, and product descriptions",
         "Identify persuasive language and implicit information in commercial texts"],
        ["Informational Texts"]),
    (15, 131, "Public Notices",
        ["skill"],
        ["Read public notices, announcements, and official signs in Chinese",
         "Extract key information from formal notice texts"],
        ["Informational Texts"]),
    (15, 132, "Instructions and Directions",
        ["skill"],
        ["Follow written instructions, recipes, manuals, and direction texts in Chinese",
         "Identify sequential and procedural structure in instructional texts"],
        ["Public Notices"]),
    (15, 133, "Online Posts",
        ["skill"],
        ["Read social media posts, forum entries, and online comments in simplified Chinese",
         "Understand informal register, abbreviations, and internet language in online text"],
        ["Advertisements"]),
    (15, 134, "News Summaries",
        ["skill"],
        ["Read news summaries and headlines and extract key information",
         "Understand news vocabulary and formal news register"],
        ["Informational Texts"]),
    (15, 135, "Short News Reports",
        ["skill"],
        ["Read short news reports and identify who, what, when, where, and why",
         "Build vocabulary for current affairs and social topics through news reading"],
        ["News Summaries"]),
    (15, 136, "Inferring Meaning from Context",
        ["skill"],
        ["Use context, grammar, and topic knowledge to infer the meaning of unfamiliar words",
         "Apply inference strategies to extend reading comprehension beyond known vocabulary"],
        ["Short News Reports"]),
    (15, 137, "Reading for Main Ideas",
        ["skill"],
        ["Identify the main idea, topic sentence, and key details of a paragraph or text",
         "Read efficiently by scanning and skimming rather than word-by-word processing"],
        ["Inferring Meaning from Context"]),

    # ── Module 16: Functional Writing Skills ─────────────────────────────────
    (16, 138, "Personal Narratives (Writing)",
        ["skill"],
        ["Write a structured personal narrative with clear events, feelings, and resolution",
         "Use aspect markers, sequence connectors, and descriptive language in narrative writing"],
        ["Writing Narratives"]),
    (16, 139, "Opinion Paragraphs",
        ["skill"],
        ["Write a structured opinion paragraph: topic sentence, reasons, examples, conclusion",
         "Apply HSK4 opinion and logical connectors in written argument"],
        ["Expressing Opinions in Writing"]),
    (16, 140, "Descriptive Writing",
        ["skill"],
        ["Write vivid descriptions of people, places, and events using rich vocabulary",
         "Combine 着, degree complements, and comparison structures in descriptive prose"],
        ["Personal Narratives (Writing)"]),
    (16, 141, "Event Reports",
        ["skill"],
        ["Write factual event reports using formal register and structured paragraphs",
         "Apply passive voice, 把, and formal connectors in event report writing"],
        ["Descriptive Writing"]),
    (16, 142, "Formal Messages",
        ["skill"],
        ["Write formal messages and letters using appropriate 您-register language",
         "Apply formal opening, body, and closing conventions in written Mandarin"],
        ["Opinion Paragraphs"]),
    (16, 143, "Complaint Messages",
        ["skill"],
        ["Write polite but firm complaint messages in formal Chinese",
         "Structure a complaint with context, issue, impact, and request for resolution"],
        ["Formal Messages"]),
    (16, 144, "Requests and Applications",
        ["skill"],
        ["Write formal request letters and simple job or programme applications in Chinese",
         "Use 申请, 请求, 希望, and formal closing phrases appropriately"],
        ["Complaint Messages"]),
    (16, 145, "Invitations (Written)",
        ["skill"],
        ["Write formal and informal written invitations in Chinese",
         "Include event details, tone, and RSVP conventions appropriately"],
        ["Formal Messages"]),
    (16, 146, "Organizing Multi-Paragraph Texts",
        ["skill"],
        ["Structure a multi-paragraph text with introduction, body, and conclusion",
         "Use discourse markers and topic sentences to guide the reader through a text"],
        ["Requests and Applications", "Invitations (Written)"]),
    (16, 147, "Cohesion and Flow in Writing",
        ["skill"],
        ["Use cohesive devices — pronouns, connectors, and lexical chains — to create flowing text",
         "Edit written texts for cohesion, coherence, and naturalness"],
        ["Organizing Multi-Paragraph Texts"]),

    # ── Module 17: Conversation & Discussion ─────────────────────────────────
    (17, 148, "Giving Advice",
        ["communication"],
        ["Give clear, polite advice using 你应该, 我建议, 最好, and 不妨",
         "Respond to requests for advice naturally in personal and professional contexts"],
        ["应该 (Probability)", "Making Suggestions (HSK4)" if False else "Making Suggestions (HSK4)"]),
    (17, 149, "Making Suggestions (HSK4)",
        ["communication"],
        ["Make suggestions in formal and informal contexts using 我建议, 不如, 要不然, 可以考虑",
         "Propose, negotiate, and refine suggestions in group discussion"],
        ["Giving Advice"]),
    (17, 150, "Explaining Decisions",
        ["communication"],
        ["Explain the reasoning behind decisions using cause-effect and opinion structures",
         "Justify choices clearly and naturally in conversation"],
        ["Building Logical Arguments", "Giving Advice"]),
    (17, 151, "Solving Problems",
        ["communication"],
        ["Discuss problems, propose solutions, evaluate options, and reach conclusions",
         "Use 问题, 解决, 方法, and 有效 in problem-solving discourse"],
        ["Making Suggestions (HSK4)", "Explaining Decisions"]),
    (17, 152, "Discussing Experiences",
        ["communication"],
        ["Describe and discuss personal experiences using aspect markers, emotions, and narrative structure",
         "Ask follow-up questions and respond with depth in experience sharing"],
        ["Describing Personal Experiences"]),
    (17, 153, "Negotiating Solutions",
        ["communication"],
        ["Negotiate outcomes using compromise language: 我们可以…, 如果…就…, 这样行吗",
         "Reach agreement through give-and-take in conversation"],
        ["Solving Problems"]),
    (17, 154, "Discussing Abstract Topics",
        ["communication"],
        ["Discuss abstract topics — happiness, success, fairness, freedom — in Mandarin",
         "Express and defend positions on abstract subjects using HSK4 grammar and vocabulary"],
        ["Discussing Different Viewpoints", "Social Issues"]),
    (17, 155, "Responding to Different Opinions",
        ["skill"],
        ["Respond thoughtfully to opinions you agree with, partially agree with, or disagree with",
         "Maintain a multi-turn discussion using agreement, qualification, and challenge strategies"],
        ["Discussing Abstract Topics", "Contrast and Concession"]),
    (17, 156, "Sustaining Extended Conversations",
        ["skill"],
        ["Maintain a natural conversation on any familiar or abstract topic for five or more minutes",
         "Use all HSK4 conversation strategies: opinions, reasons, comparisons, narratives, and responses"],
        ["Responding to Different Opinions", "Negotiating Solutions"]),
]


def seed_chinese_hsk4_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for Chinese HSK 4.
    Two-pass: Pass 1 inserts nodes, Pass 2 resolves prereq topic names → IDs
    across ALL Chinese HSK nodes so HSK1/2/3 topics can be used as prereqs.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'zh'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("Chinese language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'HSK', 'HSK4', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _CHINESE_HSK4_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK4'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _CHINESE_HSK4_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'HSK', 'HSK4', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _CHINESE_HSK4_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK4' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK4'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK4'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] Chinese HSK 4 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── Chinese HSK 5 curriculum ────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_CHINESE_HSK5_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Advanced Grammar System Mastery",       "Control time, state, and action fluidly in extended speech using all aspect marker combinations",          5),
    (2,  "把 & 被 Construction Mastery",           "Describe how actions affect objects and how events happen to people at full HSK5 depth",                   5),
    (3,  "Hypothetical & Conditional Reasoning",  "Express logic, imagination, and alternative realities using complex conditional structures",               5),
    (4,  "Discourse Engineering",                  "Structure speech like coherent arguments using advanced connectors and rhetorical organisation",            5),
    (5,  "Reported Speech Mastery",                "Accurately transmit what others said with nuance across statements, questions, and commands",              5),
    (6,  "Advanced Relative Clauses",              "Pack complex meaning into single natural sentences using chained modifiers and compressed structures",      5),
    (7,  "Formal & Written Chinese System",        "Write structured, professional, and academic Chinese with full register control",                          5),
    (8,  "Abstract & Societal Thinking",           "Talk about ideas, systems, and values — not just daily life",                                              5),
    (9,  "Argumentation & Debate System",          "Defend ideas clearly and persuasively using claim-reason-evidence-conclusion structure",                   5),
    (10, "Idioms & Fixed Expression Fluency",      "Sound culturally natural, not textbook-trained, through pragmatic idiomatic usage",                        4),
    (11, "Reading & Listening Integration",        "Understand real-world Chinese at natural speed through media, inference, and fast-speech decoding",        5),
    (12, "Pragmatics & Hidden Meaning",            "Understand what is meant, not just what is said, through politeness, implication, and face-saving",       5),
    (13, "Conversation Flow & Cohesion",           "Keep conversations stable and coherent across multiple turns and topic shifts",                            5),
    (14, "Interaction Survival Strategies",        "Stay fluent even when you don't know everything by paraphrasing, repairing, and negotiating meaning",     5),
    (15, "Writing Mastery System",                 "Write structured multi-paragraph texts including argumentative, comparative, and analytical essays",       5),
    (16, "Real-World Fluency Integration",         "Operate naturally in real-life environments: negotiations, conflict, professional settings, public speech", 5),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_CHINESE_HSK5_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 1: Advanced Grammar System Mastery ────────────────────────────
    (1, 1, "Aspect System Integration (了 / 着 / 过 combinations)",
        ["concept"],
        ["Combine 了, 着, and 过 in multi-clause sentences without hesitation",
         "Identify which aspect marker is required at each point in a narrative"],
        ["Choosing Between 了, 着, and 过"]),
    (1, 2, "Multi-aspect storytelling control",
        ["skill"],
        ["Alternate aspect markers strategically across a sustained narrative",
         "Control the foreground-background structure of a story using aspect"],
        ["Aspect System Integration (了 / 着 / 过 combinations)"]),
    (1, 3, "Temporal shifting in discourse",
        ["skill"],
        ["Shift between past, present, and future frames in extended discourse",
         "Use temporal anchors and aspect markers to orient the listener across time shifts"],
        ["Multi-aspect storytelling control"]),
    (1, 4, "Sentence-final 了 vs experiential 了",
        ["concept"],
        ["Distinguish sentence-final change-of-state 了 from verb-suffix experiential 了 with precision",
         "Produce and self-correct both types automatically in rapid speech"],
        ["Sentence-Final 了"]),
    (1, 5, "Aspect stacking in narrative flow",
        ["skill"],
        ["Produce fluent narratives where multiple aspect markers appear in a single paragraph",
         "Sustain temporal coherence across a five-minute spoken account"],
        ["Temporal shifting in discourse", "Sentence-final 了 vs experiential 了"]),

    # ── Module 2: 把 & 被 Construction Mastery ───────────────────────────────
    (2, 6, "把 sentence structure (result-driven actions)",
        ["concept"],
        ["Use 把 in complex result-oriented sentences with full complement chains",
         "Produce 把 sentences across registers: casual speech, written narrative, and formal report"],
        ["Choosing Between Normal and 把 Sentences"]),
    (2, 7, "把 with abstract objects",
        ["concept"],
        ["Extend 把 to abstract objects: 把问题解决, 把计划改变, 把关系处理好",
         "Use 把 with abstract nouns naturally in professional and academic discourse"],
        ["把 sentence structure (result-driven actions)"]),
    (2, 8, "被 passive structure (formal + informal)",
        ["concept"],
        ["Switch between formal written 被 and informal conversational passive naturally",
         "Produce extended 被 sentences with complements, time frames, and agents"],
        ["Formal Passive Usage"]),
    (2, 9, "Unexpected / negative outcomes",
        ["communication"],
        ["Use 被 to frame unexpected, unfortunate, or unwanted events with natural emphasis",
         "Convey speaker attitude through passive construction choice"],
        ["被 passive structure (formal + informal)"]),
    (2, 10, "Cause-explanation chaining in passive structures",
        ["skill"],
        ["Build cause-effect chains that include passive constructions as steps in an argument",
         "Integrate 把 and 被 into logical explanations and narratives fluidly"],
        ["Unexpected / negative outcomes", "把 with abstract objects"]),

    # ── Module 3: Hypothetical & Conditional Reasoning ───────────────────────
    (3, 11, "如果…就…",
        ["concept"],
        ["Use 如果…就… in complex real conditional sentences across formal and informal registers",
         "Embed 如果 clauses within longer arguments and explanations"],
        ["Building Logical Arguments"]),
    (3, 12, "要是…的话…",
        ["concept"],
        ["Use 要是…的话… as a more colloquial conditional form",
         "Alternate 如果 and 要是 by register appropriately in speech and writing"],
        ["如果…就…"]),
    (3, 13, "即使…也… (HSK5)",
        ["concept"],
        ["Use 即使…也… to build concessive conditional arguments at full HSK5 complexity",
         "Combine 即使 clauses with counter-arguments and rhetorical structures"],
        ["即使...也... (Introduction)"]),
    (3, 14, "Counterfactual thinking",
        ["skill"],
        ["Express counterfactual and contrary-to-fact scenarios using past-referenced conditionals",
         "Discuss what would have happened using 如果当时, 要是那时候, and related structures"],
        ["即使…也… (HSK5)"]),
    (3, 15, "Mixed real vs unreal condition chains",
        ["skill"],
        ["Combine real and hypothetical conditions in extended argumentative speech",
         "Sustain a three-minute conditional reasoning chain in Mandarin"],
        ["Counterfactual thinking"]),

    # ── Module 4: Discourse Engineering ──────────────────────────────────────
    (4, 16, "因此 / 由于 / 从而",
        ["concept"],
        ["Use 因此, 由于, and 从而 in formal argumentation and extended written discourse",
         "Distinguish the logical position of each connector in a causal chain"],
        ["因此... (Advanced)"]),
    (4, 17, "尽管如此 / 与此同时",
        ["concept"],
        ["Use 尽管如此 to concede and counter, and 与此同时 to add simultaneous points",
         "Deploy these connectors to create nuanced multi-part arguments"],
        ["因此 / 由于 / 从而"]),
    (4, 18, "Argument flow control (intro → body → conclusion)",
        ["skill"],
        ["Organise a spoken or written argument with a clear three-part structure",
         "Use discourse markers to signal transitions between introduction, body, and conclusion"],
        ["尽管如此 / 与此同时"]),
    (4, 19, "Contrast layering (multiple opposing ideas)",
        ["skill"],
        ["Layer multiple contrasting points using 虽然, 尽管, 但是, and 然而 in a single argument",
         "Produce nuanced positions that acknowledge opposing views while maintaining a stance"],
        ["Argument flow control (intro → body → conclusion)"]),
    (4, 20, "Emphasis and rhetorical balance",
        ["skill"],
        ["Use rhetorical emphasis structures — 正是…, 正因为…, 之所以… — to highlight key points",
         "Balance assertive and hedged language to create persuasive and credible discourse"],
        ["Contrast layering (multiple opposing ideas)"]),

    # ── Module 5: Reported Speech Mastery ────────────────────────────────────
    (5, 21, "Direct → indirect transformation",
        ["concept"],
        ["Transform direct speech into indirect reported speech in Mandarin",
         "Handle verb tense, pronoun shift, and time expression adjustment in reported speech"],
        ["Building Coherent Paragraphs"]),
    (5, 22, "Statements, questions, commands",
        ["concept"],
        ["Report statements, yes/no questions, content questions, and commands indirectly",
         "Use 说, 问, 叫, 让, and 告诉 with appropriate reported speech structures"],
        ["Direct → indirect transformation"]),
    (5, 23, "Embedded reporting structures",
        ["concept"],
        ["Embed reported speech within larger argument and narrative structures",
         "Use 据说, 据报道, 据我所知, and 他说他 in extended spoken and written contexts"],
        ["Statements, questions, commands"]),
    (5, 24, "Narrative consistency across paragraphs",
        ["skill"],
        ["Maintain consistent reference and reporting stance across a multi-paragraph text",
         "Avoid shifts in reported speech frame that confuse the reader or listener"],
        ["Embedded reporting structures"]),
    (5, 25, "Opinion and argument summarisation",
        ["skill"],
        ["Summarise others' opinions and arguments accurately and neutrally",
         "Use 总的来说, 换句话说, and summary structures to distil complex positions"],
        ["Narrative consistency across paragraphs"]),

    # ── Module 6: Advanced Relative Clauses ──────────────────────────────────
    (6, 26, "所 + noun + 的 structures",
        ["concept"],
        ["Use 所 + verb + 的 to create formal relative clause nominalisations",
         "Apply 所做的, 所说的, 所经历的 in formal written and spoken registers"],
        ["Nominalisation (verb → noun abstraction)"]),
    (6, 27, "Chained modifiers",
        ["concept"],
        ["Build noun phrases with multiple stacked 的-linked modifiers",
         "Produce and parse four-modifier noun phrases in natural Mandarin"],
        ["所 + noun + 的 structures"]),
    (6, 28, "Embedded descriptive clauses",
        ["concept"],
        ["Embed full clauses as pre-nominal modifiers using 的",
         "Parse and produce complex embedded clause structures in academic and literary Chinese"],
        ["Chained modifiers"]),
    (6, 29, "Sentence compression strategies",
        ["skill"],
        ["Compress multi-sentence ideas into single complex noun phrases using relative clause structures",
         "Apply compression strategies to increase writing density and sophistication"],
        ["Embedded descriptive clauses"]),
    (6, 30, "Multi-layer noun phrases",
        ["skill"],
        ["Produce and interpret multi-layer noun phrases in authentic formal Chinese",
         "Build reading fluency with complex nominal structures found in newspapers and reports"],
        ["Sentence compression strategies"]),

    # ── Module 7: Formal & Written Chinese System ─────────────────────────────
    (7, 31, "Spoken vs written register switching",
        ["skill"],
        ["Identify and switch between spoken and written Chinese registers automatically",
         "Produce the same content in both registers and explain the differences"],
        ["Formal tone control"]),
    (7, 32, "Academic vocabulary",
        ["concept"],
        ["Use academic vocabulary: 分析, 探讨, 阐述, 综合, 评估, 提出, 论述",
         "Apply academic vocabulary in essay introductions, arguments, and conclusions"],
        ["Spoken vs written register switching"]),
    (7, 33, "Report-style expression",
        ["skill"],
        ["Write report-style texts using formal connectors, nominalisation, and passive structures",
         "Produce a structured short report on a familiar topic in standard written Chinese"],
        ["Academic vocabulary"]),
    (7, 34, "Nominalisation (verb → noun abstraction)",
        ["concept"],
        ["Convert verb phrases into abstract nouns using 化, 性, 度, and 的 structures",
         "Use nominalisations to increase density and formality in written and spoken Chinese"],
        ["Report-style expression"]),
    (7, 35, "Formal tone control",
        ["skill"],
        ["Control tone across a text by adjusting vocabulary, sentence length, and connector choice",
         "Produce texts that are consistently formal, neutral, or informal as required"],
        ["Nominalisation (verb → noun abstraction)"]),

    # ── Module 8: Abstract & Societal Thinking ────────────────────────────────
    (8, 36, "Society systems (education, economy, governance)",
        ["communication"],
        ["Discuss societal systems: how they work, their strengths, weaknesses, and reform needs",
         "Use 制度, 体制, 政策, 改革, 经济 in extended analytical speech"],
        ["Discussing Abstract Topics"]),
    (8, 37, "Technology & AI discourse",
        ["communication"],
        ["Discuss technology trends, artificial intelligence, digital transformation, and their social impact",
         "Argue positions on technology ethics and opportunity using HSK5 structures"],
        ["Society systems (education, economy, governance)"]),
    (8, 38, "Ethics & values (light philosophy layer)",
        ["communication"],
        ["Discuss ethical dilemmas, values, and moral reasoning in Mandarin",
         "Use 道德, 价值观, 公平, 责任, 原则 in structured philosophical discussion"],
        ["Technology & AI discourse"]),
    (8, 39, "Environment & global issues",
        ["communication"],
        ["Discuss global environmental and development challenges at HSK5 depth",
         "Argue for positions on climate, sustainability, and international cooperation"],
        ["Ethics & values (light philosophy layer)"]),
    (8, 40, "Perspective-based reasoning",
        ["skill"],
        ["Present and evaluate issues from multiple stakeholder perspectives",
         "Sustain a multi-perspective analysis of a social or global issue for five minutes"],
        ["Environment & global issues", "Argumentation & Debate System" if False else "Opinion structuring (claim → reason → evidence → conclusion)"]),

    # ── Module 9: Argumentation & Debate System ───────────────────────────────
    (9, 41, "Opinion structuring (claim → reason → evidence → conclusion)",
        ["skill"],
        ["Build four-part opinion arguments consistently in both speech and writing",
         "Produce a two-minute structured spoken argument on any familiar topic"],
        ["Argument flow control (intro → body → conclusion)"]),
    (9, 42, "Counter-arguments and rebuttals",
        ["skill"],
        ["Anticipate, acknowledge, and refute counter-arguments naturally",
         "Use 尽管, 虽然, 然而, 但事实上 to frame and rebut opposing positions"],
        ["Opinion structuring (claim → reason → evidence → conclusion)"]),
    (9, 43, "Nuanced stance expressions",
        ["skill"],
        ["Express partial agreement, qualified positions, and conditional stances",
         "Use 在一定程度上, 总体而言, 不能一概而论 in nuanced argumentation"],
        ["Counter-arguments and rebuttals"]),
    (9, 44, "Persuasion techniques",
        ["skill"],
        ["Apply persuasion strategies: appeals to logic, emotion, authority, and shared values",
         "Adapt persuasion style to audience and context in Chinese"],
        ["Nuanced stance expressions"]),
    (9, 45, "Rhetorical balance and softening",
        ["skill"],
        ["Balance assertive and softening language to maintain credibility and rapport",
         "Use 当然, 不可否认, 不得不承认 to soften strong positions rhetorically"],
        ["Persuasion techniques"]),

    # ── Module 10: Idioms & Fixed Expression Fluency ─────────────────────────
    (10, 46, "High-frequency 成语 (functional usage)",
        ["concept"],
        ["Use the 30 most functional 成语 in natural conversation and writing",
         "Apply 成语 in context rather than as isolated memorised items"],
        ["Sustaining Extended Conversations"]),
    (10, 47, "Set phrases (总的来说, 换句话说, etc.)",
        ["concept"],
        ["Use high-frequency set phrases and discourse formulae naturally",
         "Deploy summary, paraphrase, and transition phrases to enhance fluency"],
        ["High-frequency 成语 (functional usage)"]),
    (10, 48, "Pragmatic idiomatic usage (not memorisation)",
        ["skill"],
        ["Understand how to use idioms for their communicative function, not as vocabulary items",
         "Recognise when an idiom adds value versus when plain language is clearer"],
        ["Set phrases (总的来说, 换句话说, etc.)"]),
    (10, 49, "Natural integration into speech",
        ["skill"],
        ["Integrate idioms and set phrases into sustained speech without stilted insertion",
         "Self-monitor idiom usage for naturalness and register appropriateness"],
        ["Pragmatic idiomatic usage (not memorisation)"]),

    # ── Module 11: Reading & Listening Integration ────────────────────────────
    (11, 50, "News and media comprehension",
        ["skill"],
        ["Comprehend authentic Chinese news broadcasts and articles with minimal unknown vocabulary",
         "Extract main points, supporting details, and implied stance from media texts"],
        ["Reading for Main Ideas"]),
    (11, 51, "Fast native speech decoding",
        ["skill"],
        ["Process native-speed speech without mental translation or word-by-word decoding",
         "Build automatic recognition of high-frequency spoken patterns at natural pace"],
        ["News and media comprehension"]),
    (11, 52, "Reduced pronunciation recognition",
        ["skill"],
        ["Recognise reduced, assimilated, and elided pronunciation in connected natural speech",
         "Decode contracted forms and unstressed syllables in fast colloquial Chinese"],
        ["Fast native speech decoding"]),
    (11, 53, "Implicit meaning inference",
        ["skill"],
        ["Infer unstated meaning from context, tone, and discourse structure",
         "Identify speaker intent and implied attitude in authentic spoken and written Chinese"],
        ["Reduced pronunciation recognition"]),
    (11, 54, "Context-based vocabulary guessing",
        ["skill"],
        ["Use grammatical structure, context, and topic knowledge to infer unknown word meanings",
         "Build strategies for sustaining comprehension despite vocabulary gaps"],
        ["Implicit meaning inference"]),

    # ── Module 12: Pragmatics & Hidden Meaning ────────────────────────────────
    (12, 55, "Indirect refusal / politeness strategies",
        ["communication"],
        ["Refuse requests, decline invitations, and say no politely using indirect language",
         "Recognise when a Chinese speaker is declining indirectly and respond appropriately"],
        ["Face-saving language strategies"]),
    (12, 56, "Implied meaning vs literal meaning",
        ["skill"],
        ["Interpret the gap between what is said and what is meant in Chinese communication",
         "Produce responses that address implied rather than only literal meaning"],
        ["Indirect refusal / politeness strategies"]),
    (12, 57, "Social tone adjustment",
        ["skill"],
        ["Calibrate tone — formal, neutral, warm, assertive — to match the social context",
         "Switch register mid-conversation when the social dynamic changes"],
        ["Implied meaning vs literal meaning"]),
    (12, 58, "Face-saving language strategies",
        ["skill"],
        ["Use face-saving language to avoid causing embarrassment or loss of face",
         "Apply 给面子, indirect framing, and positive framing in sensitive interactions"],
        ["Social tone adjustment"]),
    (12, 59, "Context-sensitive interpretation",
        ["skill"],
        ["Interpret meaning by combining linguistic content with situational and cultural context",
         "Avoid misreading Chinese communication through over-literal interpretation"],
        ["Face-saving language strategies", "Implicit meaning inference"]),

    # ── Module 13: Conversation Flow & Cohesion ───────────────────────────────
    (13, 60, "Topic maintenance across turns",
        ["skill"],
        ["Keep a conversation on topic across multiple turns without losing the thread",
         "Use topic-resuming and topic-holding strategies naturally"],
        ["Sustaining Extended Conversations"]),
    (13, 61, "Reference tracking (he/it/that issue ambiguity)",
        ["skill"],
        ["Track referents — people, objects, and ideas — across long conversations and texts",
         "Clarify and resolve reference ambiguity without disrupting conversation flow"],
        ["Topic maintenance across turns"]),
    (13, 62, "Multi-turn coherence",
        ["skill"],
        ["Maintain coherence across five or more conversation turns on a complex topic",
         "Connect each turn back to the shared topic and earlier contributions"],
        ["Reference tracking (he/it/that issue ambiguity)"]),
    (13, 63, "Conversation repair strategies",
        ["skill"],
        ["Repair communication breakdowns: misunderstandings, mishearing, and misspoken turns",
         "Use 我的意思是, 我想说的是, 让我换个说法 to repair and restate naturally"],
        ["Multi-turn coherence"]),
    (13, 64, "Clarification techniques",
        ["skill"],
        ["Request and provide clarification using targeted questions and paraphrase checks",
         "Distinguish genuine misunderstanding from implied meaning across contexts"],
        ["Conversation repair strategies"]),

    # ── Module 14: Interaction Survival Strategies ────────────────────────────
    (14, 65, "Asking for repetition naturally",
        ["communication"],
        ["Ask a speaker to repeat, slow down, or rephrase without breaking conversation flow",
         "Use 你能再说一遍吗, 请说慢一点, and 你的意思是… naturally"],
        ["Clarification techniques"]),
    (14, 66, "Paraphrasing when vocabulary fails",
        ["skill"],
        ["Describe a word or concept you don't know using simpler language and circumlocution",
         "Keep a conversation flowing when you lack a specific term"],
        ["Asking for repetition naturally"]),
    (14, 67, "Simplifying speech under pressure",
        ["skill"],
        ["Reduce sentence complexity under cognitive load while maintaining coherence",
         "Use backup communication strategies when complex structures fail"],
        ["Paraphrasing when vocabulary fails"]),
    (14, 68, "Negotiating meaning in real time",
        ["skill"],
        ["Collaboratively negotiate meaning with a conversation partner using check questions and confirmation",
         "Build shared understanding even when gaps in vocabulary or comprehension exist"],
        ["Simplifying speech under pressure"]),
    (14, 69, "Repairing misunderstandings",
        ["skill"],
        ["Identify when a misunderstanding has occurred and repair it efficiently",
         "Use both self-repair and other-repair strategies naturally in conversation"],
        ["Negotiating meaning in real time"]),

    # ── Module 15: Writing Mastery System ────────────────────────────────────
    (15, 70, "Essays (argumentative / comparative / analytical)",
        ["skill"],
        ["Write three essay types — argumentative, comparative, and analytical — in standard Chinese",
         "Apply appropriate structure, vocabulary register, and connector choice for each type"],
        ["Cohesion and Flow in Writing"]),
    (15, 71, "Structured paragraphing",
        ["skill"],
        ["Write focused paragraphs with topic sentences, support, and concluding links",
         "Ensure each paragraph advances the argument or analysis without digression"],
        ["Essays (argumentative / comparative / analytical)"]),
    (15, 72, "Thesis → support → conclusion",
        ["skill"],
        ["Produce a coherent multi-paragraph text with a clear thesis, three supporting points, and conclusion",
         "Apply this structure consistently in timed writing conditions"],
        ["Structured paragraphing"]),
    (15, 73, "Tone control (formal vs neutral)",
        ["skill"],
        ["Control writing tone by adjusting vocabulary density, sentence length, and connector formality",
         "Produce the same argument in formal and neutral registers and explain the difference"],
        ["Thesis → support → conclusion"]),
    (15, 74, "Cohesion and transition mastery",
        ["skill"],
        ["Apply a full range of cohesive devices — substitution, ellipsis, connectors, lexical chains — in extended writing",
         "Edit a text for cohesion and transition quality without losing content"],
        ["Tone control (formal vs neutral)"]),

    # ── Module 16: Real-World Fluency Integration ─────────────────────────────
    (16, 75, "Negotiation scenarios",
        ["communication"],
        ["Negotiate in Mandarin: prices, conditions, timelines, and outcomes",
         "Use strategy language — 我们可以考虑, 如果…那么…, 我的底线是 — naturally in negotiation"],
        ["Negotiating Solutions"]),
    (16, 76, "Conflict resolution",
        ["communication"],
        ["Handle conflict and disagreement constructively in Mandarin",
         "Use de-escalation, face-saving, and compromise language in tense situations"],
        ["Negotiation scenarios", "Face-saving language strategies"]),
    (16, 77, "Professional communication",
        ["communication"],
        ["Communicate effectively in professional Mandarin contexts: meetings, presentations, and client interactions",
         "Apply formal register, professional vocabulary, and appropriate tone in workplace Chinese"],
        ["Formal tone control", "Meetings and Discussions"]),
    (16, 78, "Public speaking basics",
        ["skill"],
        ["Deliver a short structured spoken presentation in Mandarin",
         "Use opening hooks, signposting, and closing summaries in public address"],
        ["Professional communication"]),
    (16, 79, "Complex idea explanation",
        ["skill"],
        ["Explain complex ideas clearly to a non-specialist audience in Mandarin",
         "Use analogies, examples, and step-by-step explanation to build understanding"],
        ["Public speaking basics", "Perspective-based reasoning"]),
]


def seed_chinese_hsk5_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for Chinese HSK 5.
    Two-pass: Pass 1 inserts nodes, Pass 2 resolves prereq topic names → IDs
    across ALL Chinese HSK nodes so HSK1–4 topics can be used as prereqs.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'zh'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("Chinese language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'HSK', 'HSK5', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _CHINESE_HSK5_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK5'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _CHINESE_HSK5_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'HSK', 'HSK5', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _CHINESE_HSK5_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK5' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK5'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK5'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] Chinese HSK 5 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── Chinese HSK 6 curriculum ────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_CHINESE_HSK6_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Near-Native Grammar Automation System",   "Grammar becomes unconscious — focus shifts to meaning and style control",                               7),
    (2,  "High-Speed Comprehension & Inference",    "Understand native speech without needing full clarity of input",                                        5),
    (3,  "Advanced Argumentation & Rhetoric",       "Produce structured, persuasive reasoning across extended discourse",                                    6),
    (4,  "Academic & Professional Fluency",         "Operate fluently in academic and professional environments",                                            8),
    (5,  "Advanced Reading Comprehension System",   "Extract meaning, bias, and structure from complex authentic texts",                                     6),
    (6,  "Advanced Writing Mastery System",         "Write structured, persuasive, and context-aware long-form text",                                        6),
    (7,  "Idiomatic & Cultural Fluency Layer",      "Sound culturally native and contextually natural",                                                      4),
    (8,  "Abstract & Philosophical Language Use",   "Discuss ideas beyond concrete reality with clarity and precision",                                      5),
    (9,  "Narrative Mastery System",                "Construct complex, natural narratives across time and perspective",                                      5),
    (10, "Real-Time Communication Under Pressure",  "Maintain fluency under unpredictable real-world conditions",                                            5),
    (11, "Stylistic Control System",                "Choose how you sound, not just what you say",                                                           5),
    (12, "Precision & Ambiguity Engineering",       "Control clarity vs ambiguity depending on communicative intent",                                        5),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives, prereq_topics)
_CHINESE_HSK6_NODES: list[tuple[int, int, str, list, list, list]] = [

    # ── Module 1: Near-Native Grammar Automation System ──────────────────────
    (1, 1, "Aspect system mastery (了 / 着 / 过 in all real-world contexts)",
        ["skill"],
        ["Deploy 了, 着, and 过 automatically across all real-world contexts without conscious selection",
         "Recover from aspect errors in real time without disrupting discourse flow"],
        ["Aspect stacking in narrative flow"]),
    (1, 2, "把 / 被 structures (formal, written, abstract usage)",
        ["skill"],
        ["Use 把 and 被 in abstract, formal, and literary registers automatically",
         "Switch between 把/被 constructions and standard SVO based on discourse needs"],
        ["Cause-explanation chaining in passive structures"]),
    (1, 3, "Sentence compression and expansion control",
        ["skill"],
        ["Compress complex ideas into dense single sentences and expand them into extended discourse",
         "Control information density to match register and audience"],
        ["Multi-layer noun phrases"]),
    (1, 4, "Embedded clause stacking (multi-layer syntax)",
        ["skill"],
        ["Produce and parse sentences with three or more levels of embedded clauses",
         "Maintain grammatical accuracy and semantic clarity in stacked clause structures"],
        ["Sentence compression and expansion control"]),
    (1, 5, "Stylistic transformation: spoken ↔ written ↔ academic",
        ["skill"],
        ["Transform the same content across spoken, written, and academic registers automatically",
         "Identify register markers and apply them consistently within a text"],
        ["Spoken vs written register switching"]),
    (1, 6, "Nominalisation and abstraction restructuring",
        ["skill"],
        ["Restructure verb-heavy sentences into nominally-dense academic prose",
         "Reverse-transform academic nominalisations back to spoken equivalents"],
        ["Nominalisation (verb → noun abstraction)", "Stylistic transformation: spoken ↔ written ↔ academic"]),
    (1, 7, "Sentence inversion and rhetorical rearrangement",
        ["skill"],
        ["Invert standard word order for rhetorical emphasis and stylistic effect",
         "Use fronting, topicalisation, and focus structures to control information prominence"],
        ["Nominalisation and abstraction restructuring"]),

    # ── Module 2: High-Speed Comprehension & Inference ───────────────────────
    (2, 8, "Natural-speed spoken Mandarin (native pacing)",
        ["skill"],
        ["Process native-speed Mandarin in real time without comprehension lag",
         "Sustain full comprehension during rapid, unscripted native speech"],
        ["Fast native speech decoding"]),
    (2, 9, "Slang, variation, and conversational reduction",
        ["skill"],
        ["Decode regional variation, slang, and heavily reduced colloquial speech",
         "Identify non-standard forms and map them to standard equivalents automatically"],
        ["Natural-speed spoken Mandarin (native pacing)"]),
    (2, 10, "Implicit meaning detection (what is NOT said)",
        ["skill"],
        ["Identify what a speaker intentionally omits and infer the communicative intent",
         "Respond appropriately to implied meaning, indirect speech acts, and strategic silence"],
        ["Context-sensitive interpretation"]),
    (2, 11, "Context reconstruction under missing information",
        ["skill"],
        ["Reconstruct meaning when significant input is missing — noise, gaps, partial hearing",
         "Use pragmatic and world knowledge to fill comprehension gaps under real-world conditions"],
        ["Implicit meaning detection (what is NOT said)"]),
    (2, 12, "Ambiguity resolution in real-time speech",
        ["skill"],
        ["Resolve lexical, structural, and pragmatic ambiguity instantly in conversation",
         "Choose the contextually appropriate interpretation of ambiguous utterances without backtracking"],
        ["Context reconstruction under missing information"]),

    # ── Module 3: Advanced Argumentation & Rhetoric ───────────────────────────
    (3, 13, "Multi-paragraph argument construction",
        ["skill"],
        ["Construct a five-paragraph or longer argument with coherent thesis development",
         "Sustain logical progression across paragraphs without repetition or digression"],
        ["Thesis → support → conclusion"]),
    (3, 14, "Thesis development and reinforcement",
        ["skill"],
        ["Develop a clear, arguable thesis and reinforce it through each paragraph",
         "Avoid thesis drift and return to the central claim after each supporting point"],
        ["Multi-paragraph argument construction"]),
    (3, 15, "Counterargument integration",
        ["skill"],
        ["Integrate and rebut counterarguments to strengthen the overall argument",
         "Use concession-refutation structures naturally in both speech and writing"],
        ["Thesis development and reinforcement"]),
    (3, 16, "Rhetorical balance and persuasion layering",
        ["skill"],
        ["Layer logical, emotional, and ethical appeals in a single sustained argument",
         "Balance assertive claims with acknowledgement of complexity"],
        ["Counterargument integration"]),
    (3, 17, "Tone modulation: formal / neutral / persuasive / critical",
        ["skill"],
        ["Switch between formal, neutral, persuasive, and critical tones within an argument",
         "Select tone deliberately based on audience, context, and communicative goal"],
        ["Rhetorical balance and persuasion layering"]),
    (3, 18, "Subtle rhetorical devices (soft irony, implication)",
        ["skill"],
        ["Use soft irony, understatement, and implication as rhetorical tools",
         "Produce rhetorical subtlety without ambiguity or misinterpretation"],
        ["Tone modulation: formal / neutral / persuasive / critical"]),

    # ── Module 4: Academic & Professional Fluency ─────────────────────────────
    (4, 19, "Meetings",
        ["communication"],
        ["Lead and participate in formal meetings in Mandarin",
         "Manage agenda, turn-taking, proposal, objection, and consensus in meeting discourse"],
        ["Meetings and Discussions"]),
    (4, 20, "Negotiations",
        ["communication"],
        ["Negotiate complex outcomes in Mandarin: multi-issue, multi-party scenarios",
         "Use advanced negotiation language including anchoring, concession, and closure"],
        ["Negotiation scenarios"]),
    (4, 21, "Presentations",
        ["communication"],
        ["Deliver a structured professional presentation in Mandarin with Q&A handling",
         "Use signposting, visual reference language, and audience engagement strategies"],
        ["Public speaking basics"]),
    (4, 22, "Reports",
        ["skill"],
        ["Write structured professional and academic reports in standard Chinese",
         "Apply report conventions: executive summary, findings, analysis, and recommendations"],
        ["Report-style expression"]),
    (4, 23, "Decision summaries",
        ["skill"],
        ["Write and deliver concise decision summaries that capture context, options, and rationale",
         "Use 综上所述, 鉴于以上, and summary structures in formal decision communication"],
        ["Reports"]),
    (4, 24, "Structured analysis",
        ["skill"],
        ["Produce structured analytical texts: problem framing, evidence, interpretation, conclusion",
         "Apply analytical frameworks in written and spoken academic Chinese"],
        ["Decision summaries"]),
    (4, 25, "Research summaries",
        ["skill"],
        ["Summarise research findings accurately and concisely in formal Chinese",
         "Attribute sources, report methods, and present conclusions in academic register"],
        ["Structured analysis"]),
    (4, 26, "Abstract explanation",
        ["skill"],
        ["Explain abstract academic concepts clearly to both specialist and non-specialist audiences",
         "Use analogy, example, and definition to make abstraction accessible"],
        ["Research summaries", "Complex idea explanation"]),

    # ── Module 5: Advanced Reading Comprehension System ──────────────────────
    (5, 27, "Newspapers and editorials",
        ["skill"],
        ["Read Chinese newspaper articles and editorials with full comprehension",
         "Distinguish factual reporting from editorial stance and implied bias"],
        ["Short News Reports"]),
    (5, 28, "Academic essays",
        ["skill"],
        ["Read and critically engage with academic essays in simplified Chinese",
         "Identify thesis, argument structure, evidence type, and rhetorical strategy"],
        ["Newspapers and editorials"]),
    (5, 29, "Modern and classical literary excerpts",
        ["skill"],
        ["Read modern Chinese literary prose and introductory classical text excerpts",
         "Identify literary devices, narrative voice, and cultural reference in Chinese literature"],
        ["Academic essays"]),
    (5, 30, "Author stance identification",
        ["skill"],
        ["Identify the author's stance, bias, and rhetorical purpose in a range of text types",
         "Distinguish explicit and implicit authorial positioning in Chinese texts"],
        ["Modern and classical literary excerpts"]),
    (5, 31, "Critical reading and interpretation",
        ["skill"],
        ["Evaluate argument quality, evidence strength, and logical consistency in Chinese texts",
         "Produce critical reading responses that identify strengths and weaknesses"],
        ["Author stance identification"]),
    (5, 32, "Summarisation under abstraction",
        ["skill"],
        ["Summarise abstract and complex texts accurately in concise Chinese prose",
         "Preserve the author's meaning and stance while reducing length and complexity"],
        ["Critical reading and interpretation"]),

    # ── Module 6: Advanced Writing Mastery System ─────────────────────────────
    (6, 33, "Argumentative essays (multi-layer structure)",
        ["skill"],
        ["Write extended argumentative essays with layered sub-arguments and integrated evidence",
         "Sustain argumentative coherence across six or more paragraphs"],
        ["Essays (argumentative / comparative / analytical)"]),
    (6, 34, "Analytical reports",
        ["skill"],
        ["Write analytical reports that frame a problem, examine evidence, and recommend action",
         "Apply professional and academic analytical report conventions in standard Chinese"],
        ["Argumentative essays (multi-layer structure)"]),
    (6, 35, "Opinion essays with nuance control",
        ["skill"],
        ["Write opinion essays that acknowledge complexity while maintaining a clear position",
         "Control hedging, concession, and assertion levels to create nuanced written argument"],
        ["Analytical reports"]),
    (6, 36, "Formal documentation writing",
        ["skill"],
        ["Write formal Chinese documentation: proposals, policy briefs, and official correspondence",
         "Apply formal documentation conventions, structure, and language register"],
        ["Opinion essays with nuance control"]),
    (6, 37, "Cohesion across long texts",
        ["skill"],
        ["Maintain lexical, grammatical, and thematic cohesion across a 600+ character text",
         "Use pronoun chains, lexical repetition, and connectors to unify extended texts"],
        ["Formal documentation writing"]),
    (6, 38, "Stylistic consistency control",
        ["skill"],
        ["Maintain a single consistent style — formal, academic, or persuasive — across an entire text",
         "Edit for stylistic inconsistency: vocabulary shifts, register breaks, and tone variation"],
        ["Cohesion across long texts"]),

    # ── Module 7: Idiomatic & Cultural Fluency Layer ──────────────────────────
    (7, 39, "成语 mastery (contextual, not memorised usage)",
        ["skill"],
        ["Use 成语 functionally in argument, narrative, and professional discourse",
         "Choose 成语 that add precision or cultural resonance rather than decorative effect"],
        ["Natural integration into speech"]),
    (7, 40, "Proverbs and cultural references",
        ["skill"],
        ["Use Chinese proverbs and cultural references naturally and accurately",
         "Understand the historical or literary origin of common proverbs and apply them in context"],
        ["成语 mastery (contextual, not memorised usage)"]),
    (7, 41, "Historical and metaphorical language integration",
        ["skill"],
        ["Integrate historical allusions and extended metaphors into speech and writing",
         "Use classical references without sounding forced or anachronistic"],
        ["Proverbs and cultural references"]),
    (7, 42, "Natural idiom embedding in speech/writing",
        ["skill"],
        ["Embed idioms and fixed expressions seamlessly into extended speech and written text",
         "Self-monitor for over-use, forced insertion, or register mismatch in idiomatic usage"],
        ["Historical and metaphorical language integration"]),

    # ── Module 8: Abstract & Philosophical Language Use ──────────────────────
    (8, 43, "Ethics, society, identity, human behaviour",
        ["communication"],
        ["Discuss ethics, social structures, identity formation, and human behaviour in Mandarin",
         "Use abstract vocabulary for values, norms, agency, and social dynamics"],
        ["Ethics & values (light philosophy layer)"]),
    (8, 44, "Political and societal discourse (non-technical)",
        ["communication"],
        ["Engage with political and societal topics in Mandarin without technical jargon",
         "Discuss governance, rights, inequality, and civic participation at a conceptual level"],
        ["Society systems (education, economy, governance)"]),
    (8, 45, "Multi-layer conceptual reasoning",
        ["skill"],
        ["Build multi-step conceptual arguments that connect abstract ideas across layers",
         "Produce and sustain philosophical reasoning chains in spoken and written Mandarin"],
        ["Ethics, society, identity, human behaviour"]),
    (8, 46, "Abstract idea stacking",
        ["skill"],
        ["Stack and relate multiple abstract concepts within a single coherent argument",
         "Maintain clarity and logical connection when combining high-level abstractions"],
        ["Multi-layer conceptual reasoning"]),
    (8, 47, "Perspective-based reasoning (HSK6)",
        ["skill"],
        ["Analyse complex issues from multiple ideological, cultural, and disciplinary perspectives",
         "Produce perspective-aware analysis that acknowledges the limits of each viewpoint"],
        ["Abstract idea stacking", "Perspective-based reasoning"]),

    # ── Module 9: Narrative Mastery System ───────────────────────────────────
    (9, 48, "Multi-perspective storytelling",
        ["skill"],
        ["Tell a story from multiple character perspectives with distinct voice and stance",
         "Switch narrative perspective cleanly while maintaining story coherence"],
        ["Storytelling in Mandarin"]),
    (9, 49, "Temporal manipulation: flashbacks / foreshadowing",
        ["skill"],
        ["Use flashback and foreshadowing techniques to control narrative time",
         "Signal temporal displacement clearly using discourse markers and aspect"],
        ["Temporal shifting in discourse"]),
    (9, 50, "Emotional vs neutral narration control",
        ["skill"],
        ["Switch between emotionally engaged and neutral reportorial narration deliberately",
         "Control emotional register in narrative to match genre and communicative purpose"],
        ["Temporal manipulation: flashbacks / foreshadowing"]),
    (9, 51, "Narrative cohesion across long sequences",
        ["skill"],
        ["Maintain character, theme, and temporal coherence across an extended narrative",
         "Use referential chains and discourse structure to hold a long narrative together"],
        ["Emotional vs neutral narration control"]),
    (9, 52, "Implication and indirect storytelling",
        ["skill"],
        ["Tell a story where key meaning is implied rather than stated",
         "Use omission, suggestion, and implication as deliberate narrative techniques"],
        ["Narrative cohesion across long sequences", "Subtle rhetorical devices (soft irony, implication)"]),

    # ── Module 10: Real-Time Communication Under Pressure ────────────────────
    (10, 53, "Fast conversational environments",
        ["skill"],
        ["Maintain comprehension and participation in fast-paced native conversational environments",
         "Process multiple speakers and rapid topic shifts without losing the thread"],
        ["Ambiguity resolution in real-time speech"]),
    (10, 54, "Group discussions",
        ["communication"],
        ["Participate fully in group discussions: contribute, respond, and build on others' points",
         "Manage turn-taking, overlapping speech, and topic transitions in group settings"],
        ["Fast conversational environments"]),
    (10, 55, "Interruptions and recovery strategies",
        ["skill"],
        ["Handle interruptions gracefully and recover your speaking turn without losing content",
         "Use interruption management strategies: holding, yielding, and reclaiming the floor"],
        ["Group discussions"]),
    (10, 56, "Debate participation in real time",
        ["skill"],
        ["Participate in real-time debate: make, defend, and rebut points under time pressure",
         "Maintain argument quality and language accuracy in competitive speaking situations"],
        ["Interruptions and recovery strategies", "Rhetorical balance and persuasion layering"]),
    (10, 57, "Informal spoken interaction mastery",
        ["skill"],
        ["Navigate unscripted informal conversation with full native-level interactional competence",
         "Use humour, sarcasm, small talk, and rapport-building language naturally"],
        ["Debate participation in real time"]),

    # ── Module 11: Stylistic Control System ──────────────────────────────────
    (11, 58, "Register switching: spoken / written / academic / formal",
        ["skill"],
        ["Switch between spoken, written, academic, and formal registers automatically and accurately",
         "Identify register mismatches in your own output and correct them in real time"],
        ["Stylistic transformation: spoken ↔ written ↔ academic"]),
    (11, 59, "Tone control: polite / neutral / persuasive / critical / diplomatic",
        ["skill"],
        ["Select and maintain appropriate tone — polite, neutral, persuasive, critical, or diplomatic — across extended discourse",
         "Modulate tone mid-text or mid-speech in response to context or audience"],
        ["Tone modulation: formal / neutral / persuasive / critical"]),
    (11, 60, "Style adaptation to audience and context",
        ["skill"],
        ["Adapt vocabulary, syntax, and discourse structure to match the specific audience and communicative context",
         "Analyse audience needs and adjust style preemptively rather than reactively"],
        ["Register switching: spoken / written / academic / formal", "Tone control: polite / neutral / persuasive / critical / diplomatic"]),
    (11, 61, "Producing spoken academic discourse",
        ["skill"],
        ["Deliver spoken academic-register content — lectures, seminars, oral defences — in fluent Mandarin",
         "Maintain academic vocabulary and argument structure in real-time oral academic contexts"],
        ["Style adaptation to audience and context"]),
    (11, 62, "Stylistic self-monitoring and editing",
        ["skill"],
        ["Monitor your own output for stylistic inconsistency and self-correct in real time",
         "Edit written texts for register, tone, and stylistic consistency across paragraphs"],
        ["Producing spoken academic discourse"]),

    # ── Module 12: Precision & Ambiguity Engineering ──────────────────────────
    (12, 63, "Expressing uncertainty without loss of clarity",
        ["skill"],
        ["Express degrees of uncertainty using modal language without reducing communicative clarity",
         "Calibrate hedging precisely so meaning remains unambiguous despite qualified claims"],
        ["Rhetorical balance and softening"]),
    (12, 64, "Layered meaning construction",
        ["skill"],
        ["Construct utterances that carry multiple simultaneous layers of meaning",
         "Produce layered meaning intentionally through lexical choice, syntax, and implication"],
        ["Expressing uncertainty without loss of clarity"]),
    (12, 65, "Controlled vagueness (intentional ambiguity)",
        ["skill"],
        ["Use intentional vagueness strategically to allow multiple interpretations",
         "Apply controlled ambiguity in diplomatic, face-saving, and negotiation contexts"],
        ["Layered meaning construction"]),
    (12, 66, "Indirect communication strategies",
        ["skill"],
        ["Communicate indirectly and implication-first in culturally appropriate Chinese contexts",
         "Produce and interpret indirect speech acts across formal, social, and professional situations"],
        ["Controlled vagueness (intentional ambiguity)", "Face-saving language strategies"]),
    (12, 67, "Meaning compression and expansion",
        ["skill"],
        ["Compress extended meaning into minimal language and expand minimal input into full meaning",
         "Master the full compression-expansion range as a deliberate communicative choice"],
        ["Indirect communication strategies", "Sentence compression and expansion control"]),
]


def seed_chinese_hsk6_curriculum(conn: psycopg2.extensions.connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for Chinese HSK 6.
    Two-pass: Pass 1 inserts nodes, Pass 2 resolves prereq topic names → IDs
    across ALL Chinese HSK nodes so HSK1–5 topics can be used as prereqs.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'zh'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("Chinese language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    conn.executemany(
        """
        INSERT INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (%s, 'HSK', 'HSK6', %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _CHINESE_HSK6_MODULES],
    )

    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK6'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    rows = []
    for unit, lesson_order, topic, skill_focus, objectives, _prereqs in _CHINESE_HSK6_NODES:
        rows.append((
            lang_id,
            unit_to_module_id[unit],
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (%s, %s, 'HSK', 'HSK6', %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    node_rows = conn.execute(
        "SELECT id, topic FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' ORDER BY id",
        (lang_id,),
    ).fetchall()
    topic_to_id: dict[str, int] = {}
    for r in node_rows:
        topic_to_id.setdefault(r["topic"], r["id"])

    for unit, lesson_order, topic, _skill, _obj, prereq_topics in _CHINESE_HSK6_NODES:
        if not prereq_topics:
            continue
        prereq_ids = [topic_to_id[t] for t in prereq_topics if t in topic_to_id]
        if not prereq_ids:
            continue
        conn.execute(
            """
            UPDATE curriculum_nodes
               SET prerequisites = %s
             WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK6' AND topic = %s
            """,
            (json.dumps(prereq_ids), lang_id, topic),
        )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK6'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = %s AND framework = 'HSK' AND level = 'HSK6'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] Chinese HSK 6 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── Initialization ───────────────────────────────────────────────────────────

def initialize_database() -> None:
    """
    Full first-run setup:

    1. Open connection to lingua_ai.db (creates file if absent)
    2. Create all tables + indexes, migrate any missing columns
    3. Seed reference data (languages, hobbies, motivations, xp_levels, achievements)
    4. Commit and close
    """
    # print(f"[db] Initializing database at {DB_PATH}")
    print(f"[db] Initializing database at {_DATABASE_URL}")
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
        seed_spanish_curriculum(conn)
        seed_spanish_a2_curriculum(conn)
        seed_spanish_b1_curriculum(conn)
        seed_spanish_b2_curriculum(conn)
        seed_german_a1_curriculum(conn)
        seed_german_a2_curriculum(conn)
        seed_german_b1_curriculum(conn)
        seed_german_b2_curriculum(conn)
        seed_chinese_hsk1_curriculum(conn)
        seed_chinese_hsk2_curriculum(conn)
        seed_chinese_hsk3_curriculum(conn)
        seed_chinese_hsk4_curriculum(conn)
        seed_chinese_hsk5_curriculum(conn)
        seed_chinese_hsk6_curriculum(conn)
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
