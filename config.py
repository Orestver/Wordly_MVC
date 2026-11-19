import os

BASE_DIR = os.path.dirname(__file__)
STATS_FILE = os.path.join(BASE_DIR, "data", "statistics.json")
ACHIEVENTS_FILE = os.path.join(BASE_DIR, "data", "achievements.json")
LOCATES_FILE = os.path.join(BASE_DIR, "data", "locates.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "data", "settings.json")
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")
WORDLISTS_DIR = os.path.join(BASE_DIR, "wordlists")
LANGUAGES = {
    "Англійська": "en",
    "Українська": "uk",
    "Німецька": "de",
    "Польська": "pl",
    "Чеська": "cs"
}