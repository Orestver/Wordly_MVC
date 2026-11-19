import os, json

class StatsModel():
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.default_stats = {
            "total_answers": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "sessions": 0,
            "perfect_sessions": 0,
            "current_mistakes_streak": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "reset_count": 0,
            "wrong_words": {}
        }
        self.stats = self.load_stats_from_file()

    def load_stats_from_file(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return self.default_stats
    
    def save_stats(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)


    def update_stats(self, word: str, translation: str, is_correct: bool,):
        self.stats["total_answers"] += 1

        if is_correct:
            self.stats["correct_answers"] += 1
            self.stats["current_streak"] += 1
            self.stats["current_mistakes_streak"] = 0

            if self.stats["current_streak"] > self.stats["longest_streak"]:
                self.stats["longest_streak"] = self.stats["current_streak"]
        else:
            self.stats["wrong_answers"] += 1
            self.stats["current_streak"] = 0
            self.stats["current_mistakes_streak"] += 1

            if word not in self.stats["wrong_words"]:
                self.stats["wrong_words"][word] = {
                    "translation": translation,
                    "count": 1
                }
            else:
                self.stats["wrong_words"][word]["count"] += 1

        self.save_stats()

    def get_wrong_words(self):
        return {
            word: data["translation"]
            for word, data in self.stats["wrong_words"].items()
        }
    
    def add_session(self):
        # Додає +1 до завершених тестувань
        self.stats["sessions"] += 1
        self.save_stats()

    def add_perfect_session(self):
        self.stats["perfect_sessions"] += 1
        self.save_stats()
        
    def add_reset_count(self):
        self.stats["reset_count"] += 1
        self.save_stats()
        
    def clear_wrong_words(self):
        self.stats["wrong_words"] = {}         
        self.save_stats()

    def reset_all_stats(self):
        # Повне очищення статистики з копіюванням
        self.stats = self.default_stats.copy() 
        self.stats["wrong_words"] = {}         
        self.save_stats()

