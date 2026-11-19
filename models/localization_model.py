import json
import os
from config import SETTINGS_FILE

class LocalizationModel:
    def __init__(self, filepath="locales.json", settings_path=SETTINGS_FILE, default_lang="uk"):
        self.filepath = filepath
        self.settings_path = settings_path
        
        # Одразу при створенні моделі завантажуємо всі переклади в пам'ять
        self.translations = self.load_translations()
        
        # Завантажуємо збережену мову (або використовуємо default_lang, якщо файлу ще немає)
        self.current_lang = self.load_saved_language(default_lang)

    def load_translations(self) -> dict:
        # Завантажує всі тексти з JSON-файлу.
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Помилка читання файлу перекладів {self.filepath}: {e}")
                
        # Резервний словник на випадок відсутності файлу
        return {"uk": {"ui": {}, "achievements": {}}, "en": {"ui": {}, "achievements": {}}}

    def load_saved_language(self, default_lang: str) -> str:
        # Читає збережену мову з файлу налаштувань.
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    # Повертаємо збережену мову, якщо вона є в перекладах
                    saved_lang = settings.get("language", default_lang)
                    if saved_lang in self.translations:
                        return saved_lang
            except Exception as e:
                print(f"Помилка читання файлу налаштувань {self.settings_path}: {e}")
        
        return default_lang

    def save_language(self):
        # Зберігає поточну мову у файл налаштувань.
        settings = {"language": self.current_lang}
        try:
            # Зберігаємо існуючі налаштування, якщо файл вже є (щоб не затерти інші параметри в майбутньому)
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    try:
                        existing_settings = json.load(f)
                        existing_settings.update(settings)
                        settings = existing_settings
                    except json.JSONDecodeError:
                        pass # Файл був порожній або пошкоджений

            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Помилка збереження налаштувань у {self.settings_path}: {e}")

    def set_language(self, lang_code: str):
        # Змінює активну мову та зберігає її у файл.
        if lang_code in self.translations:
            self.current_lang = lang_code
            # Зберігаємо вибір користувача
            self.save_language()
        else:
            print(f"Помилка: Мову '{lang_code}' не знайдено у файлі перекладів.")

    def get_text(self, category: str, key: str = None):
        # Універсальний метод отримання перекладів.
        lang_data = self.translations.get(self.current_lang, {})
        category_data = lang_data.get(category, {})
        
        if key:
            return category_data.get(key, f"_{key}_") 
        
        return category_data