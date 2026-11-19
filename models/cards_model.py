class CardsModel():
    def __init__(self):
        self.words_list = []
        self.current_index = 0

        self.still_learning_words = []
        self.already_learned_words = []
        self.known_count = 0
        self.unknown_count = 0

    def set_words_list(self, words_dict):
        self.words_list = list(words_dict.items())
        self.current_index = 0
        self.still_learning_words = []
        self.already_learned_words = []
        self.known_count = 0
        self.unknown_count = 0

    def get_current_word(self):
        
        if self.is_cards_finished():
            return None, None
        return self.words_list[self.current_index]
    
    def update_data(self, status: str):
        word, _ = self.get_current_word()
        if status == "known":
            self.known_count += 1
            self.already_learned_words.append(word)
        else:
            self.unknown_count += 1
            self.still_learning_words.append(word)

    def get_data(self):
        return {
            "total": len(self.words_list),
            "still_learning": len(self.still_learning_words),
            "already_learned": len(self.already_learned_words),
            "still_learning_words": self.still_learning_words,
            "already_learned_words": self.already_learned_words
        }
    
    def next_word(self):
        self.current_index += 1 

    def get_progress(self):
        if self.is_cards_finished():
             return f"{len(self.words_list)} / {len(self.words_list)}"
        return f"{self.current_index + 1} / {len(self.words_list)}"
    
    def is_cards_finished(self):
        return self.current_index >= len(self.words_list)