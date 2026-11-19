import random

class QuizModel:
    def __init__(self):
        self.words: dict[str, str] = {}
        self.keys: list[str] = []
        self.remaining_keys: list[str] = []


        self.current_word: str = ""
        self.current_translation: str = ""
        self.direction: int = 1 # 1: Eng->Ukr 2: Ukr->Eng

        self.asked_count: int = 0
        self.correct_count: int = 0
        self.wrong_words: list = []
        self.streak: int = 0
        self.max_questions: int = 0
        

        self.matching_pairs = {} 
        self.matched_count = 0   
        self.total_pairs = 0

    # --- ЛОГІКА ТЕСТУ  ---
    def get_progress_data(self):
        return {
            "asked": self.asked_count,
            "total": self.max_questions,
            "wrong_words": self.wrong_words,
            "correct": self.correct_count,
            "streak": self.streak,
            "percentage": (self.correct_count / self.asked_count * 100) if self.asked_count > 0 else 0
        }

    def is_test_finished(self):
        return self.asked_count >= self.max_questions
    
    def start_test(self, words_dict: dict[str, str], mode: str = "20"):
        if not words_dict:
            return
            
        self.words = words_dict
        self.keys = list(words_dict.keys())
        self.remaining_keys = self.keys.copy()
        random.shuffle(self.remaining_keys)

        self.asked_count = 0
        self.correct_count = 0
        self.wrong_words = []
        self.streak = 0


        if mode == "20":
            self.max_questions = min(20, len(self.keys))
        elif mode == "all":
            self.max_questions = len(self.keys)
        else: 
            self.max_questions = 999999
            
        return self.max_questions

    def get_next_question(self):
        if not self.remaining_keys:
            self.remaining_keys = self.keys.copy()
            random.shuffle(self.remaining_keys)

        self.current_word = self.remaining_keys.pop()
        self.current_translation = self.words[self.current_word]
        self.direction = random.choice([1, 2])
        
        return self.current_word, self.current_translation, self.direction
    
    def get_cur_word(self):
        return self.current_word
    
    def get_cur_translation(self):
        return self.current_translation
    
    def check_answer(self, user_input: str) -> bool:
        user_input = user_input.strip().lower()
        
        if self.direction == 1: # Eng -> Ukr
            # Перевіряємо через список (якщо перекладів кілька через кому)
            correct_variants = [t.strip().lower() for t in self.current_translation.split(",")]
            is_correct = user_input in correct_variants
        else: # Ukr -> Eng
            is_correct = user_input == self.current_word.lower()

        self.asked_count += 1
        if is_correct:
            self.correct_count += 1
            self.streak += 1
        else:
            if self.direction == 1:
                self.wrong_words.append(f"Слово: {self.current_word} | Правильно: {" або ".join(correct_variants)} | Ви ввели: {user_input}")
            else:
                self.wrong_words.append(f"Слово: {self.current_translation} | Правильно: {self.current_word} | Ви ввели: {user_input}")
            self.streak = 0
        return is_correct
    
    def get_hint(self):
        if self.direction == 2:
            return self.current_word[0] + "_." * (len(self.current_word) - 1)
        else:
            return self.words[self.current_word][0] + "_." * (len(self.words[self.current_word]) - 1)
        
    # --- ЛОГІКА ВІДПОВІДНОСТІ (MATCHING) ---
    def setup_matching(self, words_dict: dict, count=4):
        if len(words_dict) < 2:
            return None, None

        self.matched_count = 0
        self.total_pairs = min(count, len(words_dict))
        
        selected_keys = random.sample(list(words_dict.keys()), self.total_pairs)
        
        left_words = selected_keys.copy()
        right_translations = []
        self.matching_pairs.clear()
        
        for k in selected_keys:
            translation = words_dict[k].split(",")[0].strip()
            right_translations.append(translation)
            self.matching_pairs[k] = translation

        random.shuffle(left_words)
        random.shuffle(right_translations)
        
        return left_words, right_translations

    def check_match(self, word, translation) -> bool:
        is_correct = self.matching_pairs.get(word) == translation
        if is_correct:
            self.matched_count += 1
        return is_correct

    def is_matching_finished(self) -> bool:
        return self.matched_count >= self.total_pairs