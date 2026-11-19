import os
import json
import datetime
from .words_model import WordsModel
from config import WORDLISTS_DIR

class AchievementsModel():
    def __init__(self, filepath):
        self.filepath = filepath
        self.words_model = WordsModel(WORDLISTS_DIR)
        self.default_data = {
            "first_word": {"icon": "👶", "is_unlocked": False},
            "first_mistake": {"icon": "❗", "is_unlocked": False},
            "streak_10": {"icon": "🔥", "is_unlocked": False},
            "polyglot": {"icon": "🌍", "is_unlocked": False},
            "perfect_test": {"icon": "🎯", "is_unlocked": False},
            "living_dictionary": {"icon": "🌍", "is_unlocked": False},
            "streak_50": {"icon": "🔥", "is_unlocked": False},
            "night_owl": {"icon": "🦉", "is_unlocked": False},
            "early_bird": {"icon": "🌅", "is_unlocked": False},
            "the_end": {"icon": "🔄", "is_unlocked": False},
            "librarian": {"icon": "📚", "is_unlocked": False}
        }
        self.achievements = self.load_data_from_file()

    def load_data_from_file(self) -> dict:
        loaded_data = {}
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
            except Exception:
                pass

        merged_data = self.default_data.copy()
        for key, value in loaded_data.items():
            if key in merged_data:
                merged_data[key]["is_unlocked"] = value.get("is_unlocked", False)
        
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)

        return merged_data
    
    def save_data(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.achievements, f, ensure_ascii=False, indent=4)

    def check_new_achievements(self, current_stats: dict) -> list:
        newly_unlocked_ids = []

        # 1 правильне слово
        if not self.achievements["first_word"]["is_unlocked"] and current_stats.get("correct_answers", 0) >= 1:
            self.achievements["first_word"]["is_unlocked"] = True
            newly_unlocked_ids.append("first_word")

        # 1 неправильне слово
        if not self.achievements["first_mistake"]["is_unlocked"] and current_stats.get("wrong_answers", 0) >= 1:
            self.achievements["first_mistake"]["is_unlocked"] = True
            newly_unlocked_ids.append("first_mistake")

        # Стрік 10
        if not self.achievements["streak_10"]["is_unlocked"] and current_stats.get("current_streak", 0) >= 10:
            self.achievements["streak_10"]["is_unlocked"] = True
            newly_unlocked_ids.append("streak_10")

        # Стрік 50
        if not self.achievements["streak_50"]["is_unlocked"] and current_stats.get("current_streak", 0) >= 50:
            self.achievements["streak_50"]["is_unlocked"] = True
            newly_unlocked_ids.append("streak_50")

        # Поліглот 100 правильних відповідей загалом
        if not self.achievements["polyglot"]["is_unlocked"] and current_stats.get("correct_answers", 0) >= 100:
            self.achievements["polyglot"]["is_unlocked"] = True
            newly_unlocked_ids.append("polyglot")

        # Живий словник 500+ правильних слів
        if not self.achievements["living_dictionary"]["is_unlocked"] and current_stats.get("correct_answers", 0) >= 500:
            self.achievements["living_dictionary"]["is_unlocked"] = True
            newly_unlocked_ids.append("living_dictionary")
            
        # Ідеальний тест 
        if not self.achievements["perfect_test"]["is_unlocked"] and current_stats.get("perfect_sessions", 0) >= 1:
            self.achievements["perfect_test"]["is_unlocked"] = True
            newly_unlocked_ids.append("perfect_test")

        # Нічна сова (Виправлено логічну помилку: 'or' замість 'and')
        if not self.achievements["night_owl"]["is_unlocked"]:
            cur_hour = datetime.datetime.now().hour
            if cur_hour >= 23 or cur_hour <= 4:
                self.achievements["night_owl"]["is_unlocked"] = True
                newly_unlocked_ids.append("night_owl")

        # Жайворонок
        if not self.achievements["early_bird"]["is_unlocked"]:
            cur_hour = datetime.datetime.now().hour
            if cur_hour >= 5 and cur_hour <= 8:
                self.achievements["early_bird"]["is_unlocked"] = True
                newly_unlocked_ids.append("early_bird")

        # Кінець?
        if not self.achievements["the_end"]["is_unlocked"] and current_stats.get("reset_count", 0) >= 1:
            self.achievements["the_end"]["is_unlocked"] = True
            newly_unlocked_ids.append("the_end")

        # Бібліотекар
        if not self.achievements["librarian"]["is_unlocked"] and len(self.words_model.get_available_packs()) >= 10:
            self.achievements["librarian"]["is_unlocked"] = True
            newly_unlocked_ids.append("librarian")

        # Якщо щось відкрили - зберігаємо файл
        if newly_unlocked_ids:
            self.save_data()

        return newly_unlocked_ids
    
    def reset_all_achievements(self):
        for ach in self.achievements.values():
            ach["is_unlocked"] = False
        self.save_data()