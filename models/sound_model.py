import pygame
import os
import json
from config import SETTINGS_FILE
class SoundModel():
    def __init__(self, settings_path=SETTINGS_FILE):
        pygame.mixer.init()
        self.settings_path = settings_path
        self.sounds = {
            "correct": "assets/sounds/correct.mp3",
            "wrong": "assets/sounds/wrong.mp3"
        }
        self.enabled = self.load_sounds_state(default_state=True)

    def load_sounds_state(self, default_state: bool) -> bool:
        # Читає збережений стан звуків з файлу налаштувань.
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    # Шукаємо ключ "sounds", якщо його немає — повертаємо default_state
                    return settings.get("sounds", default_state)
            except Exception as e:
                print(f"Помилка читання файлу налаштувань {self.settings_path}: {e}")
        
        return default_state

    def play(self, event_type):
        if self.enabled and event_type in self.sounds:
            pygame.mixer.Sound(self.sounds[event_type]).play()

    def toggle_sounds(self):
        self.enabled = not self.enabled
        self.save_sounds_state()
    
    def save_sounds_state(self):
        # Зберігає поточну мову у файл налаштувань.
        settings = {"sounds": self.enabled}
        try:
            # Зберігаємо існуючі налаштування, якщо файл вже є 
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    try:
                        existing_settings = json.load(f)
                        existing_settings.update(settings)
                        settings = existing_settings
                    except json.JSONDecodeError:
                        pass 

            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Помилка збереження налаштувань у {self.settings_path}: {e}")

    def get_sounds_state(self):
        return self.enabled
