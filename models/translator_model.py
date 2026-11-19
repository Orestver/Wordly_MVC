from translate import Translator
from gtts import gTTS
import pygame
from io import BytesIO
import threading

class TranslatorModel():
    def __init__(self):
        self.languages = {
            "Англійська": "en",
            "Українська": "uk",
            "Німецька": "de",
            "Польська": "pl",
            "Чеська": "cs"
        }
        
    def update_language_names(self, localized_langs: dict):
        """
        Приймає словник з локалізації: {"en": "English", "uk": "Ukrainian"}
        і "перевертає" його для внутрішнього використання: {"English": "en"}
        """
        if not localized_langs:
            return

        new_languages = {}
        for code, name in localized_langs.items():
            new_languages[name] = code
            
        self.languages = new_languages
    
    def get_language_names(self) -> list:
        return list(self.languages.keys())
    
    def translate(self, sourse_language: str, target_language: str, text: str):
        translator = Translator(
            from_lang=self.languages[sourse_language], 
            to_lang=self.languages[target_language]
        )
        try:
            result = translator.translate(text)
            return result
        except Exception as e:
            return e
        
    # Функція для озвучення тексту з перекладача
    def speak(self, text, lang):
        lang_code = self.languages.get(lang, "en")

        def speak_task():
            try:
                #голос через Google
                tts = gTTS(text=text, lang=lang_code)
                
                # Зберігаємо аудіо в оперативну пам'ять 
                fp = BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                
                # Відтворення звуку
                pygame.mixer.music.load(fp)
                pygame.mixer.music.play()
                

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
            except Exception as e:
                print(f"Помилка озвучки: {e}")

        threading.Thread(target=speak_task, daemon=True).start()
