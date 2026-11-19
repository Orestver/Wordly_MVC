
from models.words_model import WordsModel
from models.quiz_model import QuizModel
from models.stats_model import StatsModel
from models.translator_model import TranslatorModel
from models.sound_model import SoundModel
from models.achievements_model import AchievementsModel
from models.cards_model import CardsModel
from models.localization_model import LocalizationModel
from views.main_view import MainView
from config import WORDLISTS_DIR, STATS_FILE, ACHIEVENTS_FILE, LOCATES_FILE

class MainController():
    def __init__(self, master):
        self.model = WordsModel(WORDLISTS_DIR)
        self.quiz_model = QuizModel()
        self.stats_model = StatsModel(STATS_FILE)
        self.translator_model = TranslatorModel()
        self.sound_model = SoundModel()
        self.achievements_model = AchievementsModel(ACHIEVENTS_FILE)
        self.cards_model = CardsModel()
        self.loc_model = LocalizationModel(filepath=LOCATES_FILE, default_lang="uk")
        self.view = MainView(master, 
                             # Editor
                             self.get_path_from_select, self.get_path_from_drop, self.save_current_dictionary, self.handle_change_language,
                             # Dictionaries
                             self.handle_dictionary_selection, self.save_dictionary_changes,self.delete_current_dictionary,
                             self.sort_by_word, self.sort_by_translation,
                             # Quiz
                             self.setup_test, self.setup_mistakes_repeat_test, self.process_answer, self.handle_hint,  self.start_matching_game,
                             self.handle_next_card, self.handle_card_click, self.start_cards_game, self.handle_mute,
                             # Translator
                             self.handle_translate, self.handle_say_text,
                             #Statistics
                             self.handle_clear_stats, self.handle_clear_wrong_words, self.update_wrong_words_ui, self.handle_clear_achievements)
        
        self.mode = ""
        self.view.config_root()
        self.load_word_packs()
        self.refresh_dictionary_list()
        self.handle_update_stats_ui()
        self.handle_set_languages()
        self.handle_update_achievements_ui()
        self.update_mute_text()
        self.update_all_texts()

        #self.update_cards_view()

        self.selected_left_word = None
        self.selected_right_word = None

    def update_all_texts(self):
        ui_texts = self.loc_model.get_text("ui")
        ach_texts = self.loc_model.get_text("achievements")
        
        lang_texts = self.loc_model.get_text("languages")

        self.translator_model.update_language_names(lang_texts)

        new_lang_list = self.translator_model.get_language_names()

        self.view.update_texts(ui_texts)
        ach_data = self.achievements_model.load_data_from_file()
        self.view.stats_tab.update_achievements_ui(ach_data, ach_texts)

        self.view.translator_tab.update_comboboxes(new_lang_list)

    def handle_change_language(self, new_lang: str):
        self.loc_model.set_language(new_lang)
        self.update_all_texts()

    # --- РЕДАКТОР (EditorTab) ---

    def get_path_from_select(self):
        path = self.view.editor_tab.select_file()
        self.handle_file_import(path)

    def get_path_from_drop(self, event):
        path = self.view.editor_tab.on_file_drop(event)
        self.handle_file_import(path)

    def handle_file_import(self, file_path):
        try:
            words = self.model.load_words_from_file(file_path)
            
            text_to_show = ""
            for w, t in words.items():
                text_to_show += f"{w} - {t}\n"
            
            self.view.editor_tab.set_editor_content(text_to_show)
            
        except Exception as e:
            self.view.show_error("Помилка", f"Не вдалося прочитати файл: {e}")

    def load_word_packs(self):
        packs = self.model.get_available_packs()
        self.view.quiz_tab.update_combobox(packs)

    def save_current_dictionary(self):
        data = self.view.editor_tab.get_data_for_save()
        name = data['name']
        if not name or name == "Введіть назву словника..." or name == "Enter dictionary name...":
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["enter_dict_name"]
            self.view.show_warning(title, message)
            return
        raw_text = data["content"]
        # strip() Для того щоб забрати всі пробіли і символи початку рядка
        if not raw_text.strip():
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["confirm_create_empty_dict"]
            confirm = self.view.ask_okcancel(title, message)
            if confirm:
                self.model.save_pack({}, filename=name)
                title = self.loc_model.get_text("ui")["success"]
                message = self.loc_model.get_text("ui")["dict_created"].format(name)
                self.view.show_info(title, message)
        else:
            new_words = {}
            for line in raw_text.strip().split('\n'):
                if " - " in line:
                    word, trans = line.split(" - ", 1)
                    new_words[word.strip()] = trans.strip()


            self.model.save_pack(new_words, filename=name)
            self.view.show_info("Успіх", f"Словник '{name}' збережено!")
        self.refresh_dictionary_list()
        self.handle_check_achievements()

    def refresh_dictionary_list(self):
        names = self.model.get_available_packs() 
        self.view.dict_tab.update_list(names)
        self.view.quiz_tab.update_combobox(names)

    # --- DictionariesTab ---
    def handle_dictionary_selection(self, event=None):
        pack_name = self.view.dict_tab.get_selected_pack_name()
        if pack_name and pack_name != "Виберіть словник для тестування":
            try:
                data = self.model.load_pack_data(pack_name) 
                self.view.dict_tab.set_words(data)
            except Exception as e:
                self.view.show_error("Помилка", f"Не вдалося завантажити словник: {e}")

    def save_dictionary_changes(self):
        name = self.view.dict_tab.get_selected_pack_name()
        if not name:
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["select_dict_to_update"]
            self.view.show_warning(title, message)
            return
        
        raw_text = self.view.dict_tab.get_editor_content()
        
        new_words = {}
        for line in raw_text.strip().split('\n'):
            if " - " in line:
                word, trans = line.split(" - ", 1)
                new_words[word.strip()] = trans.strip()


        self.model.save_pack(new_words, filename=name)
        title = self.loc_model.get_text("ui")["success"]
        message = self.loc_model.get_text("ui")["dict_updated"].format(name)
        self.view.show_info(title, message)

    def delete_current_dictionary(self):
        name = self.view.dict_tab.get_selected_pack_name()
        if not name:
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["select_dict_to_delete"]
            self.view.show_warning(title, message)
            return
        
        self.model.delete_pack(name)
        self.view.dict_tab.clear_editor_content()
        self.refresh_dictionary_list()
        title = self.loc_model.get_text("ui")["success"]
        message = self.loc_model.get_text("ui")["dict_deleted"].format(name)
        self.view.show_info(title, message)

    def sort_by_word(self):
        self.sort_text_editor(by_translation=False)

    def sort_by_translation(self):
        self.sort_text_editor(by_translation=True)

    def sort_text_editor(self, by_translation=False):
        content = self.view.dict_tab.get_editor_content()
        if not content:
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["select_dict_to_sort"]
            self.view.show_warning(title, message)
            return
        lines = [line for line in content.split("\n") if line.strip()]
        sortable_items = []
        for line in lines:
            parts = line.split("-", 1)
             
            if len(parts) == 2:
                if by_translation:
                    sort_val = parts[1].strip().lower()
                else:
                    sort_val = parts[0].strip().lower()
            else:
                sort_val = line.strip().lower()

            sortable_items.append((sort_val, line))
        sortable_items.sort()

        sorted_dict = {}
        for item in sortable_items:
            line = item[1]  
            parts = line.split("-", 1)
            
            if len(parts) == 2:
                eng = parts[0].strip()
                ukr = parts[1].strip()
                sorted_dict[eng] = ukr
            else:
                sorted_dict[line.strip()] = ""
        self.view.dict_tab.set_words(sorted_dict)
    
    # --- QuizTab ---

    def setup_test(self, mode: str):
        self.mode = mode
        pack_name = self.view.quiz_tab.get_selected_dict()
        if not pack_name or pack_name == "Виберіть словник для тестування" or pack_name == "Choose dictionary for testing":
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["select_dict_for_test"]
            self.view.show_warning(title, message)
            return
        
        words = self.model.load_pack_data(pack_name)
        if not words:
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["empty_dict_warning"]
            self.view.show_warning(title, message)
            return

        self.quiz_model.start_test(words, mode)
        self.view.quiz_tab.set_mode("typing")
        self.view.quiz_tab.set_test_state(True)
        stats = self.quiz_model.get_progress_data()
        self.view.quiz_tab.update_progress(stats['asked'], stats['total'])
        self.display_next_question()

    def setup_mistakes_repeat_test(self):
        words = self.stats_model.get_wrong_words()
        if not words:
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["no_words_to_repeat"]
            self.view.show_warning(title, message)
            return
        
        self.quiz_model.start_test(words, mode="all")
        
        self.view.quiz_tab.set_mode("typing")
        self.view.quiz_tab.set_test_state(True)
        stats = self.quiz_model.get_progress_data()
        self.view.quiz_tab.update_progress(stats['asked'], stats['total'])
        self.display_next_question()
    
    def display_next_question(self):
        self.view.quiz_tab.clear_feedback()
        if self.quiz_model.is_test_finished():
            self.handle_update_stats_ui()
            self.show_final_results()
            self.stats_model.add_session()
            return

        # Беремо нове питання з моделі
        word, trans, direction = self.quiz_model.get_next_question()
        stats = self.quiz_model.get_progress_data()

        # Формуємо текст питання
        if direction == 1:
            q_text = self.loc_model.get_text("ui")["how_to_translate"].format(stats['asked']+1, stats['total'], word)
        else:
            q_text = self.loc_model.get_text("ui")["how_to_say"].format(stats['asked']+1, stats['total'], trans)

        self.view.quiz_tab.set_question_label(q_text)

    def process_answer(self, event=None):
        user_input = self.view.quiz_tab.get_user_answer()
        if not user_input or user_input == "Ваша відповідь?": return


        is_correct = self.quiz_model.check_answer(user_input)
        stats = self.quiz_model.get_progress_data()
        word = self.quiz_model.get_cur_word()
        translation = self.quiz_model.get_cur_translation()
        self.stats_model.update_stats(word, translation, is_correct)

        self.handle_update_stats_ui()
        if is_correct:
            self.view.quiz_tab.show_feedback(self.loc_model.get_text("ui")["correct_answer"].format(stats['streak']), "green")

            self.sound_model.play("correct")
            self.view.after(1000, self.display_next_question)
            self.view.quiz_tab.clear_user_answer()
        else:

            correct = self.quiz_model.current_translation if self.quiz_model.direction == 1 else self.quiz_model.current_word

            self.view.quiz_tab.show_feedback(self.loc_model.get_text("ui")["wrong_answer"].format(correct), "red")
            self.sound_model.play("wrong")
            self.view.after(2000, self.display_next_question)
            self.view.quiz_tab.clear_user_answer()

        self.view.quiz_tab.update_progress(stats['asked'], stats['total'])

    def handle_hint(self):
        letter = self.quiz_model.get_hint()
        text = self.loc_model.get_text("ui")["hint_translation"].format(letter)
        self.view.quiz_tab.show_feedback(text, color="blue")

    def show_final_results(self):
        stats = self.quiz_model.get_progress_data()

        formatted_mistakes = []
        if stats["wrong_words"]:
            for word in stats["wrong_words"]:
                formatted_mistakes.append(word)
        

        elif not stats["wrong_words"] and self.mode == "20":
            self.stats_model.add_perfect_session()

        self.view.quiz_tab.set_question_label("Тест завершено")
        self.view.quiz_tab.set_test_state(False)


        popup_stats = {
            "correct_answers": stats['correct'],
            "wrong_answers": stats['total'] - stats['correct']
        }
        ui_texts = self.loc_model.get_text("ui")
        # Викликаємо попап і передаємо йому статистику та список помилок для відображення
        self.view.quiz_tab.show_session_summary(
            stats=popup_stats,
            mistakes=formatted_mistakes,      
            on_retry_cmd=self.handle_retry_test,   
            on_menu_cmd=None, 
            ui_texts=ui_texts
        )

        self.handle_check_achievements()

    def handle_retry_test(self):
        self.setup_mistakes_repeat_test()


    def show_achievements_summary(self, achievement_ids: list):
        if not achievement_ids:  
            return


        ui_texts = self.loc_model.get_text("ui")
        ach_texts = self.loc_model.get_text("achievements")
        
        # 2. Завантажуємо дані ачівок, щоб дістати звідти іконки
        ach_data = self.achievements_model.load_data_from_file()

        # 3. Вибираємо правильний текст для заголовка та повідомлення (однина/множина)
        is_multiple = len(achievement_ids) > 1
        
        if is_multiple:
            title = ui_texts.get("new_achievements_title", "🏆 Нові досягнення!")
            message = ui_texts.get("congrats_multiple", "Вітаємо! Ви здобули нові досягнення:\n\n")
        else:
            title = ui_texts.get("new_achievement_title", "🏆 Нове досягнення!")
            message = ui_texts.get("congrats_single", "Вітаємо! Ви здобули нове досягнення:\n\n")


        for ach_id in achievement_ids:
            text_info = ach_texts.get(ach_id, {"title": ach_id, "description": ""})
            ach_title = text_info["title"]
            ach_desc = text_info["description"]
            
            icon = ach_data.get(ach_id, {}).get("icon", "🏆")


            message += f"{icon} {ach_title} - {ach_desc}\n"


        self.view.show_info(title, message)

    # --- ВІДПОВІДНІСТЬ ---
    def start_matching_game(self):
        pack_name = self.view.quiz_tab.get_selected_dict()
        if not pack_name or pack_name == "Виберіть словник":
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["select_dict_for_matching"]
            self.view.show_warning(title, message)
            return


        words_dict = self.model.load_pack_data(pack_name)
        
        left_words, right_words = self.quiz_model.setup_matching(words_dict)

        if not left_words:
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["matching_mode_warning"]
            self.view.show_warning(title, message)
            return

        self.selected_left_word = None
        self.selected_right_word = None


        self.view.quiz_tab.set_mode("matching")
        self.view.quiz_tab.build_matching_ui(
            left_words, right_words, 
            on_left_click=self.handle_left_click, 
            on_right_click=self.handle_right_click
        )

    def handle_left_click(self, word):
        self.selected_left_word = word
        self.view.quiz_tab.reset_all_colors("left")
        self.view.quiz_tab.set_button_color("left", word, "lightblue")
        self.check_matching_pair()

    def handle_right_click(self, translation):
        self.selected_right_word = translation
        self.view.quiz_tab.reset_all_colors("right")
        self.view.quiz_tab.set_button_color("right", translation, "lightblue")
        self.check_matching_pair()

    def check_matching_pair(self):
        # Перевірка, чи вибрано слова з обох сторін
        if not self.selected_left_word or not self.selected_right_word:
            return

        word = self.selected_left_word
        translation = self.selected_right_word
        is_correct = self.quiz_model.check_match(word, translation)
        self.stats_model.update_stats(word, translation, is_correct)
        self.handle_update_stats_ui()

        if is_correct:
            self.view.quiz_tab.draw_connection_line(word, translation, "green")
            self.view.quiz_tab.set_button_color("left", word, "lightgreen", "disabled")
            self.view.quiz_tab.set_button_color("right", translation, "lightgreen", "disabled")
            self.sound_model.play("correct")
            

            if self.quiz_model.is_matching_finished():
                self.view.quiz_tab.set_question_label("Відповідність пройдено!")
                self.view.show_info("Готово", "Всі відповідності знайдені 🎉")

        else:

            self.view.quiz_tab.set_button_color("left", word, "red")
            self.view.quiz_tab.set_button_color("right", translation, "red")
            line_id = self.view.quiz_tab.draw_connection_line(word, translation, "red")
            self.sound_model.play("wrong")


            self.view.after(800, lambda: self.reset_failed_match(word, translation, line_id))

        self.selected_left_word = None
        self.selected_right_word = None

    def reset_failed_match(self, word, translation, line_id):
        """Скидає червоні кольори та видаляє лінію при помилці"""
        self.view.quiz_tab.set_button_color("left", word, "SystemButtonFace")
        self.view.quiz_tab.set_button_color("right", translation, "SystemButtonFace")
        self.view.quiz_tab.delete_line(line_id)

    # --------------------------- Картки ---------------------

    def update_cards_view(self):
        word, translation = self.cards_model.get_current_word()
        progress = self.cards_model.get_progress()
        self.view.quiz_tab.update_counter(word, translation, progress)

    def handle_card_click(self, event):
        if not self.view.quiz_tab.is_animating():
            self.view.quiz_tab.animate_flip()

    def handle_next_card(self, status="known"):
        if not self.view.quiz_tab.is_animating():
            self.cards_model.update_data(status)
            self.view.quiz_tab.animate_slide_out(on_complete_callback=self.on_slide_out_complete)
    
    def on_slide_out_complete(self):
        self.cards_model.next_word()
        if self.cards_model.is_cards_finished():
            self.view.quiz_tab.disable_next_button()
            ui_texts = self.loc_model.get_text("ui")
            self.view.quiz_tab.show_cards_summary(stats=self.cards_model.get_data(), on_menu_cmd=None, ui_texts=ui_texts)
            return
        self.update_cards_view()
        self.view.quiz_tab.animate_slide_in()

    def start_cards_game(self):
        pack_name = self.view.quiz_tab.get_selected_dict()
        if not pack_name or pack_name == "Виберіть словник для тестування" or pack_name == "Select dictionary for cards":
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["select_dict_for_cards"]
            self.view.show_warning(title, message)
            return
            
        words_dict = self.model.load_pack_data(pack_name)
        if not words_dict:
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["empty_dict_warning"]
            self.view.show_warning(title, message)
            return
        self.cards_model.set_words_list(words_dict)
        self.view.quiz_tab.set_mode("cards")
        self.view.quiz_tab.reset_card_position() 
        self.update_cards_view()
        self.view.quiz_tab.enable_next_button()


    def handle_mute(self):
        self.sound_model.toggle_sounds()
        self.update_mute_text()

    def update_mute_text(self):
        is_muted = self.sound_model.get_sounds_state()
        new_text = "🔊" if is_muted else "🔇"
        self.view.quiz_tab.set_mute_btn_text(new_text)

    # --- TranslatorTab ---
    
    def handle_set_languages(self):
        lang_names = self.translator_model.get_language_names()
        self.view.translator_tab.set_languages(lang_names)

    def handle_translate(self):
        text = self.view.translator_tab.get_input_text()
        if not text:
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["enter_word_to_translate"]
            self.view.show_warning(title, message)
            return
        
        s_language = self.view.translator_tab.get_selected_source_lang()
        t_language = self.view.translator_tab.get_selected_target_lang()
        if s_language == t_language:
            title = self.loc_model.get_text("ui")["warning"]
            message = self.loc_model.get_text("ui")["select_different_langs"]
            self.view.show_warning(title, message)
            return
        
        translation = self.translator_model.translate(s_language, t_language, text)
        self.view.translator_tab.set_output_text(translation)

    def handle_say_text(self, text, lang="en"):
        clean_text = text.strip()
        if not clean_text:
            return
        self.translator_model.speak(clean_text, lang)
    
    # --- StatisticsTab ---

    def handle_update_stats_ui(self):
        self.stats = self.stats_model.stats
        self.view.stats_tab.update_statistics_ui(self.stats)

    def handle_clear_stats(self):
        title = self.loc_model.get_text("ui")["warning"]
        message = self.loc_model.get_text("ui")["confirm_clear_stats"]
        confirm = self.view.ask_okcancel(title, message)
        if confirm:
            self.stats_model.add_reset_count()
            self.handle_check_achievements()
            self.stats_model.reset_all_stats()
            self.stats = self.stats_model.stats
            self.view.stats_tab.update_statistics_ui(self.stats)

    def handle_clear_wrong_words(self):
        title = self.loc_model.get_text("ui")["warning"]
        message = self.loc_model.get_text("ui")["confirm_clear_words"]
        confirm = self.view.ask_okcancel(title, message)
        if confirm:
            self.stats_model.clear_wrong_words()
            self.handle_update_stats_ui()

    def handle_clear_achievements(self):
        title = self.loc_model.get_text("ui")["warning"]
        message = self.loc_model.get_text("ui")["confirm_clear_achievements"]
        confirm = self.view.ask_okcancel(title, message)
        if confirm:
            self.achievements_model.reset_all_achievements()
            self.handle_update_achievements_ui()

    def handle_check_achievements(self):
        final_stats = self.stats_model.load_stats_from_file()
        
        new_achievements_ids = self.achievements_model.check_new_achievements(final_stats)
        
        if new_achievements_ids:
            self.handle_update_achievements_ui()
            self.show_achievements_summary(new_achievements_ids)

    def handle_update_achievements_ui(self):

        ach_data = self.achievements_model.load_data_from_file()
        
        current_texts = self.loc_model.get_text("achievements") 
        
        self.view.stats_tab.update_achievements_ui(ach_data, current_texts)

    def update_wrong_words_ui(self, stats):
        if not stats["wrong_words"]:
            self.view.stats_tab.set_wrong_words_var("")
            return

        text = ""
        for word, data in stats["wrong_words"].items():
            times = self.loc_model.get_text("ui")["times"]
            text += f"• {word} - {data['translation']} ({data['count']} {times})\n"
        self.view.stats_tab.set_wrong_words_var(text)