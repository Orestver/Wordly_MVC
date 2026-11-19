import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from tkinterdnd2 import DND_FILES

from views.components import CardsSummaryPopup, SessionSummaryPopup, StyledButton


class MainView(tk.Frame):
    def __init__(self, master, 
                 # Editor
                 get_path_from_select, get_path_from_drop, save_current_dictionary,handle_change_language,
                 # Dictionaries
                 handle_dictionary_selection, save_dictionary_changes, delete_current_dictionary,
                 sort_by_word, sort_by_translation,
                 # Quiz
                 setup_test, setup_mistakes_repeat_test, process_answer, get_hint, start_matching_game,
                 handle_next_card, handle_card_click, start_cards_game, handle_mute, 
                 # Translator
                 handle_translate, handle_say_text,
                 # Statistics
                 handle_clear_stats, handle_clear_wrong_words, update_wrong_words_ui, handle_clear_achievements
                 ):
        super().__init__(master)
        self.pack(expand=True, fill="both")
        self._setup_styles()

        # Створюємо меню з вкладками
        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)

        self.current_lang_var = tk.StringVar()

        # 3. Випадаюче меню для мов
        self.lang_menu = tk.Menu(self.menu_bar, tearoff=0)


        def on_lang_change():
            selected_lang = self.current_lang_var.get()
            handle_change_language(selected_lang)


        self.lang_menu.add_radiobutton(label="Українська", variable=self.current_lang_var, value="uk", command=on_lang_change)
        self.lang_menu.add_radiobutton(label="English", variable=self.current_lang_var, value="en", command=on_lang_change)

        self.menu_bar.add_cascade(label="Language", menu=self.lang_menu)


        # Створюємо Notebook для вкладок
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.editor_tab = EditorTab(self.notebook, get_path_from_select, get_path_from_drop, save_current_dictionary, handle_change_language)

        self.dict_tab = DictionariesTab(self.notebook, handle_dictionary_selection, save_dictionary_changes, 
                                        delete_current_dictionary, sort_by_word, sort_by_translation, self.go_to_editor)

        self.quiz_tab = QuizTab(self.notebook, setup_test, setup_mistakes_repeat_test, process_answer, get_hint,  
                                start_matching_game, handle_next_card, handle_card_click, start_cards_game, handle_mute)
        
        self.translator_tab = TranslatorTab(self.notebook, handle_translate, handle_say_text)

        self.stats_tab = StatsTab(self.notebook, handle_clear_stats, handle_clear_wrong_words, update_wrong_words_ui,
                                  handle_clear_achievements)

        self.notebook.add(self.editor_tab, text=" Редактор ")
        self.notebook.add(self.dict_tab, text=" Мої словники ")
        self.notebook.add(self.quiz_tab, text=" Тестування ")
        self.notebook.add(self.translator_tab, text=" Перекладач ")
        self.notebook.add(self.stats_tab, text=" Статистика ")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
    
    def update_texts(self, ui_texts: dict):
        # 1. Оновлюємо назви самих вкладок у Notebook
        # (Використовуємо індекси 0, 1, 2, 3, 4 у тому порядку, в якому ви їх додавали)
        self.notebook.tab(0, text=f' {ui_texts.get("editor_tab", "Редактор")} ')
        self.notebook.tab(1, text=f' {ui_texts.get("dictionaries_tab", "Мої словники")} ')
        self.notebook.tab(2, text=f' {ui_texts.get("quiz_tab", "Тестування")} ')
        self.notebook.tab(3, text=f' {ui_texts.get("translator_tab", "Перекладач")} ')
        self.notebook.tab(4, text=f' {ui_texts.get("stats_tab", "Статистика")} ')
        
        self.menu_bar.entryconfig(1, label=ui_texts.get("menu_language", "Мова"))  
        
        if hasattr(self.editor_tab, 'update_texts'):
            self.editor_tab.update_texts(ui_texts)
            
        if hasattr(self.dict_tab, 'update_texts'):
            self.dict_tab.update_texts(ui_texts)
            
        if hasattr(self.quiz_tab, 'update_texts'):
            self.quiz_tab.update_texts(ui_texts)
            
        if hasattr(self.translator_tab, 'update_texts'):
            self.translator_tab.update_texts(ui_texts)
            
        if hasattr(self.stats_tab, 'update_texts'):
            self.stats_tab.update_texts(ui_texts)

    # Функція щоб пробіл працював тільки в тестуванні, а не в інших вкладках
    def on_tab_change(self, event):
        selected_tab_id = self.notebook.select()
        current_tab_index = self.notebook.index(selected_tab_id)
        main_window = self.notebook.winfo_toplevel()

        if current_tab_index == 2:
            main_window.bind("<space>", self.quiz_tab.handle_card_click)
            main_window.focus_set() 
        else:
            main_window.unbind("<space>")
            

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') 
        style.configure("TNotebook", 
                        background="#f0f0f0", 
                        borderwidth=0)
        
        style.configure("TNotebook.Tab", 
                        font=("Arial", 12, "bold"),
                        padding=[0, 5],
                        width=25,
                        cursor="hand2",           
                        anchor="center",       
                        background="#d9d9d9",  
                        foreground="#333333",  
                        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", "#2A821A"), ("active", "#4caf50")], 
                  foreground=[("selected", "white")])
        
    def config_root(self):
        self.master.update_idletasks()
        w = self.master.winfo_width()
        h = self.master.winfo_height()
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        self.master.geometry(f"{w}x{h}+{sw//2-w//2}+{sh//2-h//2}")
        #self.master.maxsize(1023, 768)
        #self.master.minsize(600, 800)

    def go_to_editor(self):
        self.notebook.select(0)
        self.editor_tab.dict_name_entry.delete(0, tk.END)
        self.editor_tab.dict_name_entry.insert(0, "Введіть назву словника...")
        self.editor_tab.set_editor_content("")

    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message)

    def show_warning(self, title: str, message: str):
        messagebox.showwarning(title, message)

    def show_info(self, title: str, message: str):
        messagebox.showinfo(title, message)

    def ask_okcancel(self, title: str, message: str):
        return messagebox.askokcancel(title, message)


    
class EditorTab(tk.Frame):
    def __init__(self, master, handle_select_file, get_path_from_drop, save_current_dictionary, handle_change_language):
        super().__init__(master)
        self.controller = None
        self.get_path_from_drop = get_path_from_drop
        self.handle_change_language = handle_change_language
        # --- ЛІВА ПАНЕЛЬ ---
        self.left_frame = tk.Frame(self, width=250)
        self.left_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        self.left_frame.pack_propagate(False)

        # 1. Поле для шляху файлу
        self.entry_file_label = tk.Label(self.left_frame, text="Шлях до файлу:", font=("Times New Roman", 10))
        self.entry_file_label.pack(fill="x", padx=5, pady=5)
        
        self.entry_file = tk.Entry(self.left_frame, font=("Times New Roman", 10))
        self.entry_file.pack(fill="x", padx=5, pady=5)


        self.current_lang = "ua" 
        
        # # Кнопка тепер викликає наш новий метод перемикання (без lambda і "en")
        # self.change_lang_btn = StyledButton(
        #     self.left_frame, 
        #     text="🇺🇦 UA", # Можна одразу показати, яка мова зараз
        #     color="#2196F3", 
        #     activebackground="#1F88DE", 
        #     width=5,
        #     command=self.toggle_lang_action
        # )
        # self.change_lang_btn.pack(fill="x", padx=5, pady=5)
        # 2. Кнопка огляду
        self.load_btn = StyledButton(self.left_frame, text="Огляд...", color="#2196F3", activebackground="#1F88DE", width=3, command=handle_select_file)
        self.load_btn.pack(fill="x", padx=5, pady=5)

        self.description_label = tk.Label(
            self.left_frame, 
            text="Виберіть файл через кнопку 'огляд' або перетягніть його сюди ⬇️", 
            fg="grey", wraplength=230, font=("Arial", 10)
        )
        self.description_label.pack(fill="x", padx=5, pady=5)

        # 3. Зона Drop
        self.drop_frame = tk.Frame(self.left_frame, bg="#dddddd", bd=2, relief="groove")
        self.drop_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.drop_frame.pack_propagate(False)

        self.drop_label = tk.Label(
            self.drop_frame, 
            text="Перетягніть PDF, DOCX, JSON, TXT файл зі словами сюди",
            font=("Arial", 12), bg="#dddddd", wraplength=200
        )
        self.drop_label.pack(fill="both", expand=True, padx=5, pady=5)

        self.dict_name_label = tk.Label(self.left_frame, text="Назва словника:", font=("Arial", 14))
        self.dict_name_label.pack(fill="x", pady=(10, 0))

        # ------------------
        self.current_placeholder = "Введіть назву словника..."

        self.dict_name_entry = tk.Entry(self.left_frame, font=("Arial", 10))
        self.dict_name_entry.pack(fill="x", padx=5, pady=5)
        self.dict_name_entry.insert(0, self.current_placeholder)
        # Тепер бінди перевіряють не жорсткий текст, а нашу змінну!
        self.dict_name_entry.bind("<FocusIn>", lambda e: self.dict_name_entry.delete(0, 'end') if self.dict_name_entry.get() == self.current_placeholder else None)
        self.dict_name_entry.bind("<FocusOut>", lambda e: self.dict_name_entry.insert(0, self.current_placeholder) if not self.dict_name_entry.get() else None)
        self.dict_name_entry.bind("<Return>", save_current_dictionary)
        # --------------------
        self.save_btn = StyledButton(
            self.left_frame, text="Зберегти словник", 
            color="#2A821A", activebackground="#236F15",
            command=save_current_dictionary
        )
        self.save_btn.pack(pady=10, padx=5, fill="x")
        # --- ПРАВА ПАНЕЛЬ ---
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side="right", expand=True, fill="both", padx=5, pady=5)

        self.text_editor_label = tk.Label(
            self.right_frame, 
            text="Формат: слово - переклад (кожне з нового рядка)", 
            fg="grey", font=("Arial", 12)
        )
        self.text_editor_label.pack(fill="x", padx=5, pady=5)
        
        # Текстовий редактор
        
        self.text_editor = tk.Text(self.right_frame, font=("Times New Roman", 12), undo=True)
        self.text_editor.bind("<KeyPress>", self.block_digits_in_text)
        self.text_editor.pack(expand=True, fill="both")
        
        # Активую Drag-and-Drop
        self.setup_dnd()
        
    def toggle_lang_action(self):
        if self.current_lang == "uk":
            self.current_lang = "en"
        else:
            self.current_lang = "uk"
            
        # А ТЕПЕР передаємо нову мову у ваш контролер/функцію
        self.handle_change_language(self.current_lang)
        
    def update_texts(self, ui_texts: dict):
        """Оновлює всі тексти на вкладці редактора"""
        
        # 1. Оновлюємо звичайні текстові мітки та кнопки
        self.entry_file_label.config(text=ui_texts.get("path_to_file", "Шлях до файлу:"))
        self.load_btn.config(text=ui_texts.get("browse", "Огляд..."))
        self.description_label.config(text=ui_texts.get("drop_zone_label", "Виберіть файл..."))
        self.drop_label.config(text=ui_texts.get("drop_zone", "Перетягніть PDF..."))
        self.dict_name_label.config(text=ui_texts.get("dict_name_label", "Назва словника:"))
        self.save_btn.config(text=ui_texts.get("save_dict", "Зберегти словник"))
        self.text_editor_label.config(text=ui_texts.get("format", "Формат: слово - переклад..."))

        # 2. Оновлюємо плейсхолдер для поля вводу
        new_placeholder = ui_texts.get("dict_name_entry", "Введіть назву словника...")
        
        # Перевіряємо: якщо користувач ще нічого не ввів і там висить стара підказка,
        # міняємо її на підказку новою мовою
        if self.dict_name_entry.get() == getattr(self, "current_placeholder", ""):
            self.dict_name_entry.delete(0, 'end')
            self.dict_name_entry.insert(0, new_placeholder)
            
        # Зберігаємо нову підказку в пам'ять, щоб FocusIn/FocusOut працювали правильно
        self.current_placeholder = new_placeholder

    def get_editor_content(self):
        return self.text_editor.get("1.0", tk.END)

    def set_editor_content(self, text: str):
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", text)

    def get_data_for_save(self):
        return {
            "name": self.dict_name_entry.get(),
            "content": self.text_editor.get("1.0", "end")
        }
    
    def setup_dnd(self):
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.get_path_from_drop)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.get_path_from_drop)

    def on_file_drop(self, event=None):
        path = event.data.strip('{}') 
        if path:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, path)
        return path


    def select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Documents", "*.pdf *.docx *.txt *.json"), ("All Files", "*.*")],
            initialdir="."
        )
        if path:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, path)
        return path
    
    
    def block_digits_in_text(self, event):
        # event.char - це конкретний символ, який щойно натиснули 
        char = event.char
        
        if char.isdigit():
            # Скасовує вивід у текст якщо це цифра
            return "break"

class DictionariesTab(tk.Frame):
    def __init__(self, master, handle_dictionary_selection, save_dictionary_changes, delete_current_dictionary,
                 sort_by_word, sort_by_translation, go_to_editor): 
        super().__init__(master)
        # --- ЛІВА ПАНЕЛЬ ---
        self.dicts_frame = tk.Frame(self, width=250)
        self.dicts_frame.pack(side="left", fill="y", padx=5, pady=5)
        self.dicts_frame.pack_propagate(False)

        self.dicts_label = tk.Label(self.dicts_frame, text="Мої словники:", font=("Times New Roman", 12))
        self.dicts_label.pack(fill="x", padx=5, pady=5)


        self.dicts_list = tk.Listbox(self.dicts_frame, 
                                    width=25,
                                    font=("Arial", 12, "bold"),
                                    bg="#ffffff",       
                                    fg="#333333",       
                                    selectbackground="#4CAF50",  
                                    selectforeground="black",
                                    # Щоб виділення з лістбокса не скидувалося при виділенні тексту в text area
                                    exportselection=False,         
                                    highlightthickness=0,
                                    activestyle="none" )
        self.dicts_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.dicts_list.bind("<Motion>", self._on_mouse_move)
        self.dicts_list.bind("<Leave>", self._on_mouse_leave)
        self.dicts_list.bind("<<ListboxSelect>>", handle_dictionary_selection)
        self._last_hover_index = -1


        # self.save_btn = StyledButton(self.dicts_frame, text="Додати словник", 
        #                              color="#2A821A", activebackground="#236F15",
        #                              command=go_to_editor)
        # self.save_btn.pack(fill="x", padx=5, pady=5)


        self.save_btn = StyledButton(self.dicts_frame, text="Зберегти словник", 
                                     color="#2A821A", activebackground="#236F15",
                                     command=save_dictionary_changes)
        self.save_btn.pack(fill="x", padx=5, pady=5)

        self.delete_btn = StyledButton(self.dicts_frame, text="Видалити словник", 
                                       color="#e11111", activebackground="#b40f0f",
                                       command=delete_current_dictionary)
        self.delete_btn.pack(fill="x", padx=5, pady=5)

        # --- ПРАВА ПАНЕЛЬ --- 
        self.text_frame =tk.Frame(self)
        self.text_frame.pack(side="right", expand=True, fill="both", padx=5, pady=5)

        self.text_label = tk.Label(
            self.text_frame, 
            text="Формат: слово - переклад (кожне з нового рядка)", 
            fg="grey", font=("Arial", 12)
        )
        self.text_label.pack(fill="x", padx=5, pady=5)

        self.text_editor = tk.Text(self.text_frame, font=("Times New Roman", 12), undo=True)
        self.text_editor.pack(expand=True, fill="both")
        self.text_editor.bind("<KeyPress>", self.block_digits_in_text)
        self.tools_frame = tk.Frame(self.text_frame)
        self.tools_frame.pack(fill="x", pady=(10, 0))

        self.tools_frame.columnconfigure(0, weight=1)
        self.tools_frame.columnconfigure(1, weight=1)


        # Поле пошуку 
        self.search_vcmd = (self.register(self.validate_no_digits), "%S")
        self.search_entry = tk.Entry(self.tools_frame, font=("Arial", 11), 
                                     bd=1, relief="solid",
                                     validate="key", validatecommand=self.search_vcmd)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=(0, 5), ipady=4) 
        
        # Створюємо змінну для підказки
        self.current_search_placeholder = "Введіть слово для пошуку..."
        
        self.search_entry.insert(0, self.current_search_placeholder)
        
        # Прив'язуємо події до змінної
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, 'end') if self.search_entry.get() == self.current_search_placeholder else None)
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.insert(0, self.current_search_placeholder) if not self.search_entry.get() else None)
        self.search_entry.bind("<Return>", lambda e: self.search_in_text()) # Обгорнув у lambda, щоб уникнути помилки передачі аргументів

        # 2. Кнопка "Сортувати за словом"
        self.sort_word_btn = StyledButton(self.tools_frame, text="Сортувати за словом", 
                                          color="#2A821A", activebackground="#236F15", 
                                          command=sort_by_word)
        self.sort_word_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=(0, 5))

        # 3. Кнопка "Знайти" 
        self.search_btn = StyledButton(self.tools_frame, text="Знайти", 
                                       color="#2A821A", activebackground="#236F15", 
                                       command=self.search_in_text)
        self.search_btn.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        # 4. Кнопка "Сортувати за перекладом" 
        self.sort_trans_btn = StyledButton(self.tools_frame, text="Сортувати за перекладом", 
                                           color="#2A821A", activebackground="#236F15", 
                                           command=sort_by_translation)
        self.sort_trans_btn.grid(row=1, column=1, sticky="ew", padx=(5, 0))

    def update_texts(self, ui_texts: dict):
        """Оновлює всі тексти на вкладці словників"""
        
        # 1. Оновлюємо звичайні лейбли та кнопки
        self.dicts_label.config(text=ui_texts.get("my_dictionaries", "Мої словники:"))
        self.save_btn.config(text=ui_texts.get("save_changes", "Зберегти словник"))
        self.delete_btn.config(text=ui_texts.get("delete_dict", "Видалити словник"))
        self.text_label.config(text=ui_texts.get("format", "Формат: слово - переклад (кожне з нового рядка)"))
        
        self.sort_word_btn.config(text=ui_texts.get("sort_by_word", "Сортувати за словом"))
        self.search_btn.config(text=ui_texts.get("find", "Знайти"))
        self.sort_trans_btn.config(text=ui_texts.get("sort_by_translation", "Сортувати за перекладом"))

        # 2. Оновлюємо плейсхолдер для поля пошуку
        new_placeholder = ui_texts.get("find_placeholder", "Введіть слово для пошуку...")
        
        # Якщо в полі зараз висить стара підказка, замінюємо її на нову
        if self.search_entry.get() == getattr(self, "current_search_placeholder", ""):
            self.search_entry.delete(0, 'end')
            self.search_entry.insert(0, new_placeholder)
            
        # Зберігаємо нову підказку
        self.current_search_placeholder = new_placeholder

    def validate_no_digits(self, char_inserted):
        for char in char_inserted:
            if char.isdigit():
                return False
        return True
    
    def block_digits_in_text(self, event):
        # event.char - це конкретний символ, який щойно натиснули 
        char = event.char
        
        if char.isdigit():
            # Скасовує вивід у текст якщо це цифра
            return "break"
    
    def _on_mouse_move(self, event):
        # Визначаємо, над яким рядком зараз курсор
        index = self.dicts_list.nearest(event.y)
        
        # Якщо курсор все ще над тим самим рядком — нічого не робимо (економимо ресурси)
        if index == self._last_hover_index:
            return

        # Повертаємо попередньому рядку стандартний колір
        if self._last_hover_index != -1:
            self.dicts_list.itemconfig(self._last_hover_index, bg="#ffffff")

        # Підсвічуємо новий рядок
        self.dicts_list.itemconfig(index, bg="#e8f5e9") # Світло-зелений
        self._last_hover_index = index

    def _on_mouse_leave(self, event):
        # Коли миша взагалі пішла зі списку — скидаємо все
        if self._last_hover_index != -1:
            self.dicts_list.itemconfig(self._last_hover_index, bg="#ffffff")
        self._last_hover_index = -1

    # Отримання тексту з Text
    def get_editor_content(self):
        return self.text_editor.get("1.0", tk.END)
    
    def get_search_text(self):
        return self.search_entry.get()
    
    def clear_editor_content(self):
        self.text_editor.delete("1.0", tk.END)  
    # Вставлення словника в Text
    def set_words(self, words_dict: dict):
        """Приймає словник {слово: переклад} і вставляє в редактор"""
        self.text_editor.delete("1.0", tk.END)
        text_to_display = ""
        for eng, ukr in words_dict.items():
            text_to_display += f"{eng} - {ukr}\n"
        self.text_editor.insert("1.0", text_to_display)

    # Отримання імені вибраного словника
    def get_selected_pack_name(self):
        selection = self.dicts_list.curselection()
        if selection:
            return self.dicts_list.get(selection[0])
        return None
    
    # Очищує Listbox і вставляє нові назви словників після додавання нових або видалення
    def update_list(self, names_list: list):
        self.dicts_list.delete(0, tk.END)
        for name in names_list:
            self.dicts_list.insert(tk.END, name)

    def search_in_text(self, event=None):
        query = self.search_entry.get().strip()
        
        # 2. Очищення старих підсвічень
        self.text_editor.tag_remove("found", "1.0", tk.END)

        if not query or query == "Введіть слово для пошуку...":
            return
        
        self.text_editor.tag_config("found", background="yellow", foreground="black")
        
        start_pos = "1.0"
        while True:
            start_pos = self.text_editor.search(query, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos:
                break
                
            end_pos = f"{start_pos}+{len(query)}c"
            
            self.text_editor.tag_add("found", start_pos, end_pos)

            start_pos = end_pos

class QuizTab(tk.Frame):
    def __init__(self, master, setup_test, setup_mistakes_repeat_test, process_answer, get_hint,  
                 start_matching_game, handle_next_card, handle_card_click, start_cards_game, handle_mute): 
        # Задаємо загальний світлий фон
        super().__init__(master, bg="#f5f6fa")
        self.header_frame = tk.Frame(self, bg="#f5f6fa")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.label = tk.Label(self.header_frame, text="Оберіть словник для тестування:", font=("Arial", 12, "bold"), bg="#f5f6fa", fg="#333333")
        self.label.pack(pady=(0, 5))

        self.dict_combo_box = ttk.Combobox(self.header_frame, font=("Arial", 12), state="readonly", width=40)
        self.dict_combo_box.pack()

        self.mute_btn = tk.Button(
            self.header_frame, 
            text="🔊", 
            command=handle_mute,
            width=3,
            font=("Segoe UI Symbol", 18),
            relief="flat",
            bg="#f5f6fa",
            activebackground="#f5f6fa"
        )
        self.mute_btn.place(relx=1.0, rely=0.0, x=-10, y=0, anchor="ne")

        self.modes_frame = tk.Frame(self, bg="#f5f6fa")
        self.modes_frame.pack(fill="x", padx=20, pady=5)
        
        # Створюємо внутрішній фрейм, щоб відцентрувати кнопки всі разом
        self.modes_inner_frame = tk.Frame(self.modes_frame, bg="#f5f6fa")
        self.modes_inner_frame.pack(anchor="center")

        # колір для всіх кнопок режимі
        btn_color = "#2A821A" 


        self.top_modes = tk.Frame(self.modes_inner_frame, bg="#f5f6fa")
        self.top_modes.pack(pady=5)

        self.mode_20_btn = StyledButton(self.top_modes, text="20 Слів", 
                                        color=btn_color, width=15, activebackground="#236F15",
                                        command=lambda: setup_test("20"))
        self.mode_20_btn.pack(side="left", padx=5)

        self.mode_inf_btn = StyledButton(self.top_modes, text="Нескінченно", 
                                         color=btn_color, width=15, activebackground="#236F15",
                                         command=lambda: setup_test("inf"))
        self.mode_inf_btn.pack(side="left", padx=5)

        self.mode_all_btn = StyledButton(self.top_modes, text="Всі слова", 
                                         color=btn_color, width=15, activebackground="#236F15",
                                         command=lambda: setup_test("all"))
        self.mode_all_btn.pack(side="left", padx=5)


        self.bottom_modes = tk.Frame(self.modes_inner_frame, bg="#f5f6fa")
        self.bottom_modes.pack(pady=5)

        self.mode_repeat_mistakes_btn = StyledButton(self.bottom_modes, text="Повторити помилки", 
                                                     color=btn_color, width=15, activebackground="#236F15",
                                                     command=setup_mistakes_repeat_test)
        self.mode_repeat_mistakes_btn.pack(side="left", padx=5)

        self.mode_match_btn = StyledButton(self.bottom_modes, text="Відповідність", 
                                           color=btn_color, width=15, activebackground="#236F15",
                                           command=start_matching_game)
        self.mode_match_btn.pack(side="left", padx=5)

        # Змінено назву змінної на mode_cards_btn
        self.mode_cards_btn = StyledButton(self.bottom_modes, text="Картки", 
                                           color=btn_color, width=15, activebackground="#236F15",
                                           command=start_cards_game)
        self.mode_cards_btn.pack(side="left", padx=5)

        self.question_text_var = tk.StringVar()
        self.question_text_var.set("Оберіть режим тесту вище")
        self.hint_text_var = tk.StringVar()

        self.testing_frame = tk.Frame(self, bg="white", bd=1, relief="ridge")
        self.testing_frame.pack(padx=20, pady=15)

        self.question_label = tk.Label(self.testing_frame, textvariable=self.question_text_var, wraplength=400, font=("Arial", 16, "bold"), bg="white", fg="#222222")
        self.question_label.pack(padx=20, pady=(30, 15))

        self.answer_vcmd = (self.register(self.validate_no_digits), "%S")
        self.answer_entry = tk.Entry(self.testing_frame, font=("Arial", 14), state="disabled", 
                                     width=30, bd=1, relief="solid", justify="left",
                                     validate="key", validatecommand=self.answer_vcmd)
        self.answer_entry.pack(pady=10, ipady=5) 

        # Створюємо змінну для підказки
        self.current_answer_placeholder = "Ваша відповідь?"
        self.answer_entry.insert(0, self.current_answer_placeholder)
        
        self.answer_entry.bind("<FocusIn>", lambda e: self.answer_entry.delete(0, 'end') if self.answer_entry.get() == self.current_answer_placeholder else None)
        self.answer_entry.bind("<FocusOut>", lambda e: self.answer_entry.insert(0, self.current_answer_placeholder) if not self.answer_entry.get() else None)
        self.answer_entry.bind('<Return>', process_answer)

        self.additional_btns_frame = tk.Frame(self.testing_frame, bg="white")
        self.additional_btns_frame.pack(pady=15)

        self.answer_btn = StyledButton(self.additional_btns_frame, text="Відповісти", 
                                       color="#2A821A", width=15, activebackground="#236F15",
                                       command=process_answer)
        self.answer_btn.pack(side="left", padx=10)

        self.hint_btn = StyledButton(self.additional_btns_frame, text="Підказка", 
                                     color="#3498db", width=15, activebackground="#1F88DE",
                                     command=get_hint)
        self.hint_btn.pack(side="left", padx=10)

        self.hint_label = tk.Label(self.testing_frame, textvariable=self.hint_text_var, font=("Arial", 11, "italic"), fg="#3498db", bg="white")
        self.hint_label.pack(pady=(0, 20))

        # -------------------- (Відповідність) ----------------------------
        self.matching_frame = tk.Frame(self, bg="#f5f6fa")
        self.matching_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.bottom_bar = tk.Frame(self, bg="#f5f6fa")
        self.bottom_bar.pack(side="bottom", fill="x", padx=20, pady=(0, 20))

        style = ttk.Style()
        style.configure("TProgressbar", thickness=15, background="#2A821A", troughcolor="#d9d9d9", bordercolor="#d9d9d9", lightcolor="#2A821A", darkcolor="#2A821A")

        self.progress_bar = ttk.Progressbar(self.bottom_bar, orient="horizontal", mode="determinate", style="TProgressbar")
        self.progress_bar.pack(fill="x")

        # -------------------- (Картки) ----------------------------
        self.front_text = ""
        self.back_text = ""
        self.is_front = True
        
        self.animating = False
        self.show_text = True
        self.canvas_width, self.canvas_height = 600, 350
        self.card_width, self.card_height = 350, 200
        
        self.default_center_x = self.canvas_width / 2
        self.center_y = self.canvas_height / 2
        self.current_center_x = self.default_center_x
        self.current_card_width = self.card_width

        self.cards_frame = tk.Frame(self, bg="#f5f6fa", bd=1, relief="ridge")
        #self.cards_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(self.cards_frame, width=self.canvas_width, height=self.canvas_height, 
                                bg="#f5f6fa", highlightthickness=0)
        self.canvas.pack()


        self.button_frame = tk.Frame(self.cards_frame, bg="#f5f6fa",)
        self.button_frame.pack(fill="x", pady=10)


        self.know_btn = StyledButton(self.button_frame, text="Знаю", 
                                       color="#2A821A", width=15, activebackground="#236F15",
                                       command=lambda: handle_next_card("known"))
        self.know_btn.pack(side="right", padx=10)
        
        self.unknown_btn = StyledButton(self.button_frame, text="Не знаю", 
                                       color="#e11111", width=15, activebackground="#b40f0f",
                                       command=lambda: handle_next_card("unknown"))
        self.unknown_btn.pack(side="right", padx=10)

        self.label_counter = tk.Label(self.button_frame, text="", font=("Arial", 14), bg="#f5f6fa", fg="black")
        self.label_counter.pack(side="left", padx=50)

        self.handle_card_click = handle_card_click
        self.canvas.bind("<Button-1>", self.handle_card_click)
        # ------------------------------------
        self.buttons_left = {}
        self.buttons_right = {}
        self.current_line = None

    def update_texts(self, ui_texts: dict):
        """Оновлює всі тексти на вкладці тестування"""
        
        # 1. Заголовки та випадаючий список
        self.label.config(text=ui_texts.get("choose_dict", "Оберіть словник для тестування:"))
        

        if self.dict_combo_box.get() in ["Виберіть словник для тестування", "Choose dictionary for testing", ""]:
            self.dict_combo_box.set(ui_texts.get("choose_dict", "Виберіть словник для тестування:"))

        # 2. Кнопки режимів (Top)
        self.mode_20_btn.config(text=ui_texts.get("mode_20_words", "20 Слів"))
        self.mode_inf_btn.config(text=ui_texts.get("mode_inf_words", "Безкінечно"))
        self.mode_all_btn.config(text=ui_texts.get("mode_all_words", "Усі слова"))

        # 3. Кнопки режимів (Bottom)
        self.mode_repeat_mistakes_btn.config(text=ui_texts.get("mode_mistakes", "Повторення помилок"))
        self.mode_match_btn.config(text=ui_texts.get("mode_matching", "Відповідність"))
        self.mode_cards_btn.config(text=ui_texts.get("mode_cards", "Картки"))


        current_text = self.question_text_var.get()
        

        if current_text in ["Оберіть режим тесту вище", "Choose test mode above"]:
            self.question_text_var.set(ui_texts.get("select_test_mode", "Оберіть режим тесту вище"))

        # 4. Кнопки під час тесту
        self.answer_btn.config(text=ui_texts.get("answer_btn", "Відповісти"))
        self.hint_btn.config(text=ui_texts.get("hint_btn", "Підказка"))

        # 5. Кнопки режиму "Картки"
        self.know_btn.config(text=ui_texts.get("know_btn", "Знаю"))
        self.unknown_btn.config(text=ui_texts.get("dont_know_btn", "Не знаю"))


        new_placeholder = ui_texts.get("answer_placeholder", "Ваша відповідь?")
        
        entry_state = self.answer_entry.cget('state')
        if entry_state == 'disabled':
            self.answer_entry.config(state='normal')
            
        if self.answer_entry.get() == getattr(self, "current_answer_placeholder", ""):
            self.answer_entry.delete(0, 'end')
            self.answer_entry.insert(0, new_placeholder)
            

        if entry_state == 'disabled':
            self.answer_entry.config(state='disabled')
            
        self.current_answer_placeholder = new_placeholder

    def clear_dict_box(self):
        self.dict_combo_box.delete(0, tk.END)

    def get_user_answer(self):
        return self.answer_entry.get()
    
    def clear_user_answer(self):
        self.answer_entry.delete(0, tk.END)

    def get_selected_dict(self):
        return self.dict_combo_box.get()
    
    def set_question_label(self, question: str):
        self.question_text_var.set(question)

    def set_mute_btn_text(self, text):
        self.mute_btn.config(text=text)

    def set_hint_label(self, hint: str):
        self.hint_text_var.set(hint)

    def clear_frame(self, frame: tk.Frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def validate_no_digits(self, char_inserted):
        for char in char_inserted:
            if char.isdigit():
                return False
        return True
    
    def update_combobox(self, dict_names: dict):
        self.clear_dict_box()
        self.dict_combo_box.config(values=dict_names)

    def set_mode(self, mode: str):
        self.testing_frame.pack_forget()
        self.matching_frame.pack_forget()
        self.cards_frame.pack_forget()
        
        if mode == "typing":
            self.testing_frame.pack(pady=10)
            self.additional_btns_frame.pack(padx=5, pady=5)
            self.bottom_bar.pack(side="bottom", fill="x", padx=20, pady=(0, 20))

        elif mode == "matching":
            self.matching_frame.pack(pady=10)
            self.bottom_bar.pack_forget()
            self.testing_frame.pack_forget()
            self.additional_btns_frame.pack_forget()

        elif mode == "cards":
            self.cards_frame.pack(pady=10)
            self.bottom_bar.pack_forget()
            self.testing_frame.pack_forget()
            self.additional_btns_frame.pack_forget()



    def set_test_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.answer_entry.config(state=state)
        self.answer_btn.config(state=state)
        self.hint_btn.config(state=state)  

    def show_feedback(self, message: str, color: str):
        self.hint_text_var.set(message)
        self.hint_label.config(fg=color, font=("Arial", 16, "bold"))

    def clear_feedback(self):
        self.hint_text_var.set("")

    def update_progress(self, asked: int, total: int):
        self.progress_bar["maximum"] = total
        self.progress_bar["value"] = asked

    def show_session_summary(self, stats, mistakes, on_retry_cmd, on_menu_cmd, ui_texts):
        SessionSummaryPopup(
            parent=self, 
            stats=stats, 
            mistakes=mistakes, 
            on_retry_callback=on_retry_cmd, 
            on_menu_callback=on_menu_cmd, 
            ui_texts=ui_texts
        )
    # ---------------------------------------
    def build_matching_ui(self, left_words: list, right_words: list, on_left_click, on_right_click):
        self.clear_frame(self.matching_frame)
        self.buttons_left.clear()
        self.buttons_right.clear()


        container = tk.Frame(self.matching_frame, bg="white", bd=1, relief="ridge")
        container.pack(fill="both", expand=True, padx=20, pady=10)


        left_frame = tk.Frame(container, bg="white")
        self.canvas_lines = tk.Canvas(container, width=150, bg="white", highlightthickness=0) 
        right_frame = tk.Frame(container, bg="white")

        left_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="n")
        self.canvas_lines.grid(row=0, column=1, pady=20, sticky="ns")
        right_frame.grid(row=0, column=2, padx=(10, 20), pady=20, sticky="n")
        

        tk.Label(left_frame, text="Оригінал", font=("Arial", 14, "bold"), bg="white", fg="#555555").pack(pady=(0, 15))
        tk.Label(right_frame, text="Переклад", font=("Arial", 14, "bold"), bg="white", fg="#555555").pack(pady=(0, 15))

        BTN_BG = "#f0f0f0"
        BTN_FG = "#333333"
        for word in left_words:
            btn = tk.Button(
                left_frame, text=word, width=22, font=("Arial", 11, "bold"), 
                wraplength=180, 
                bg=BTN_BG, fg=BTN_FG, 
                activebackground="#dcdcdc", 
                bd=0, relief="flat", 
                cursor="hand2",      
                pady=10,             
                command=lambda w=word: on_left_click(w)
            )
            btn.pack(pady=6) 
            self.buttons_left[word] = btn


        for tr in right_words:
            btn = tk.Button(
                right_frame, text=tr, width=22, font=("Arial", 11, "bold"), 
                wraplength=180, 
                bg=BTN_BG, fg=BTN_FG, 
                activebackground="#dcdcdc", 
                bd=0, relief="flat", 
                cursor="hand2",
                pady=10, 
                command=lambda t=tr: on_right_click(t)
            )
            btn.pack(pady=6)
            self.buttons_right[tr] = btn

        self.update_idletasks()

    def set_button_color(self, side, item, color, state: str = "normal"):
        btns = self.buttons_left if side == "left" else self.buttons_right
        if item in btns:
            btn = btns[item]

            if state == "disabled":
                fg_color = "#a0a0a0" 
                cursor = "arrow"
            else:
                fg_color = "white" if color != "#f0f0f0" else "#333333" 
                cursor = "hand2"

            btn.config(bg=color, fg=fg_color, state=state, cursor=cursor)

    def reset_all_colors(self, side):
        btns = self.buttons_left if side == "left" else self.buttons_right
        for btn in btns.values():
            if btn['state'] == 'normal':
                btn.config(bg="#f0f0f0", fg="#333333") 

    def draw_connection_line(self, word: str, translation: str, color="#2A821A"):
        btn_left = self.buttons_left.get(word)
        btn_right = self.buttons_right.get(translation)
        
        if not btn_left or not btn_right: return None


        self.update_idletasks()


        x1 = btn_left.winfo_rootx() + btn_left.winfo_width()
        y1 = btn_left.winfo_rooty() + btn_left.winfo_height() // 2
        

        x2 = btn_right.winfo_rootx()
        y2 = btn_right.winfo_rooty() + btn_right.winfo_height() // 2


        cx = self.canvas_lines.winfo_rootx()
        cy = self.canvas_lines.winfo_rooty()


        line_id = self.canvas_lines.create_line(
            x1 - cx, y1 - cy, x2 - cx, y2 - cy,
            width=4, fill=color, 
            capstyle="round", 
            smooth=True       
        )
        return line_id

    def delete_line(self, line_id: int):
        if line_id:
            self.canvas_lines.delete(line_id)

    # --------------- (Картки) -------------------------

    def is_animating(self):
        return self.animating
    
    def disable_next_button(self):
        self.know_btn.config(state="disabled")
        self.unknown_btn.config(state="disabled")

    def enable_next_button(self):
        self.know_btn.config(state="normal")
        self.unknown_btn.config(state="normal")
    # Малює картку
    def draw_card(self):
        
        self.canvas.delete("all")

        x1 = self.current_center_x - self.current_card_width / 2
        y1 = self.center_y - self.card_height / 2
        x2 = self.current_center_x + self.current_card_width / 2
        y2 = self.center_y + self.card_height / 2

        color = "#E8F8F5"
        text_color = "black"
        text = self.front_text if self.is_front else self.back_text

        if self.current_card_width > 10:
            self.canvas.create_rectangle(x1+3, y1+3, x2+3, y2+3, fill="#D5DBDB", outline="")

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#BDC3C7", width=2)

        if self.show_text and self.current_card_width > 50:
            self.canvas.create_text(self.current_center_x, self.center_y, text=text, font=("Arial", 20, "bold"), fill=text_color)

    def update_counter(self, front, back, progress):
        self.front_text = front
        self.back_text = back
        self.label_counter.config(text=progress)
        self.draw_card()

    def animate_flip(self):
        self.animating = True
        self._shrink()

    def _shrink(self):
        if self.current_card_width > 0:
            self.current_card_width -= 40
            self.current_card_width = max(self.current_card_width, 0)
            if self.current_card_width < 60: self.show_text = False
            self.draw_card()
            self.after(15, self._shrink)
        else:
            self.is_front = not self.is_front
            self._expand()

    def _expand(self):
        if self.current_card_width < self.card_width:
            self.current_card_width += 40
            self.current_card_width = min(self.current_card_width, self.card_width)
            self.draw_card()
            self.after(15, self._expand)
        else:
            self.after(50, self._reveal_text)

    def _reveal_text(self):
        self.show_text = True
        self.draw_card()
        self.animating = False

    # --- АНІМАЦІЇ ЗСУВУ ---
    def animate_slide_out(self, on_complete_callback):
        self.animating = True
        self.disable_next_button()
        self._slide_out_step(on_complete_callback)

    def _slide_out_step(self, callback):
        if self.current_center_x > -(self.card_width / 2):
            self.current_center_x -= 40
            self.draw_card()
            self.after(15, lambda: self._slide_out_step(callback))
        else:
            # Картка вилетіла. Викликаємо контролер, щоб він дав нові дані
            callback() 

    def animate_slide_in(self):
        self.is_front = True
        self.show_text = True
        self.current_center_x = self.canvas_width + (self.card_width / 2)
        self._slide_in_step()

    def _slide_in_step(self):
        if self.current_center_x > self.default_center_x:
            self.current_center_x -= 40
            self.current_center_x = max(self.current_center_x, self.default_center_x)
            self.draw_card()
            self.after(15, self._slide_in_step)
        else:
            self.animating = False
            self.enable_next_button()

    def reset_card_position(self):
        self.current_center_x = self.canvas_width / 2 
        self.is_front = True
        self.animating = False
        self.canvas.delete("all")
        self.draw_card()

    def show_cards_summary(self, stats,on_menu_cmd, ui_texts):
        CardsSummaryPopup(
            parent=self, 
            stats=stats, 
            on_close_callback=on_menu_cmd,
            ui_texts=ui_texts
        )

class TranslatorTab(tk.Frame):
    def __init__(self, master, handle_translate, handle_say_text): 
        super().__init__(master, bg="#f5f6fa") 
        

        self.languages_frame = tk.Frame(self, bg="#f5f6fa")
        self.languages_frame.pack(padx=20, pady=(20, 10))


        self.sourse_lang_combo = ttk.Combobox(self.languages_frame, state="readonly", font=("Arial", 12), width=15)
        self.sourse_lang_combo.grid(row=0, column=0, padx=10)

        self.swap_btn = tk.Button(
            self.languages_frame, 
            text=" ⇄ ",                  
            font=("Arial", 18, "bold"), 
            fg="#2A821A",              
            bg="#f5f6fa",            
            bd=0,                      
            activebackground="#f5f6fa",
            activeforeground="#1e5c12",
            cursor="hand2",            
            command=self.swap_languages 
        )
        self.swap_btn.grid(row=0, column=1, padx=10)

        self.target_lang_combo = ttk.Combobox(self.languages_frame, state="readonly", font=("Arial", 12), width=15)
        self.target_lang_combo.grid(row=0, column=2, padx=10)


        # --- СЕРЕДНІЙ БЛОК: Текстові поля ---
        self.translation_frame = tk.Frame(self, bg="#f5f6fa")
        self.translation_frame.pack(padx=20, pady=10, expand=True, fill="both")
        
        self.translation_frame.columnconfigure(0, weight=1)
        self.translation_frame.columnconfigure(1, weight=1)

        self.input_label = tk.Label(self.translation_frame, text="Оригінал", font=("Arial", 11, "bold"), bg="#f5f6fa", fg="#555555")
        self.input_label.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="w")

        self.output_label = tk.Label(self.translation_frame, text="Переклад", font=("Arial", 11, "bold"), bg="#f5f6fa", fg="#555555")
        self.output_label.grid(row=0, column=1, padx=5, pady=(0, 5), sticky="w")
        
        self.input_text = tk.Text(self.translation_frame, font=("Arial", 12), height=15, width=35,  wrap="word", padx=10, pady=10)
        self.input_text.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="nsew")

        self.current_input_placeholder = "Введіть текст"
        
        self.input_text.insert("1.0", self.current_input_placeholder)
        self.input_text.bind("<FocusIn>", lambda e: self.input_text.delete("1.0", tk.END) if self.input_text.get("1.0", "end-1c") == self.current_input_placeholder else None)
        self.input_text.bind("<FocusOut>", lambda e: self.input_text.insert("1.0", self.current_input_placeholder) if not self.input_text.get("1.0", "end-1c") else None)
        self.output_text = tk.Text(self.translation_frame, font=("Arial", 12), height=15, width=35,  wrap="word", padx=10, pady=10, bg="#fdfdfd")
        self.output_text.grid(row=1, column=1, padx=(10, 0), pady=5, sticky="nsew")

        self.say_input_text_btn = tk.Button(self.translation_frame,
                                            text="🔊",
                                            fg="#2A821A",              
                                            bg="#f5f6fa",
                                            font=("Arial", 14, "bold"),            
                                            bd=0,                      
                                            activebackground="#f5f6fa",
                                            activeforeground="#1e5c12",
                                            cursor="hand2",
                                            command=lambda: handle_say_text(self.input_text.get("1.0", "end-1c"), 
                                                                            lang=self.get_selected_source_lang()))
        self.say_input_text_btn.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="w") 

        self.say_output_text_btn = tk.Button(self.translation_frame,
                                            text="🔊",
                                            fg="#2A821A",              
                                            bg="#f5f6fa",
                                            font=("Arial", 14, "bold"),                 
                                            bd=0,                      
                                            activebackground="#f5f6fa",
                                            activeforeground="#1e5c12",
                                            cursor="hand2",
                                            command=lambda: handle_say_text(self.output_text.get("1.0", "end-1c"), 
                                                                            lang=self.get_selected_target_lang()))
        self.say_output_text_btn.grid(row=2, column=1, padx=5, pady=(0, 5), sticky="w")
        # --- НИЖНІЙ БЛОК: Кнопка ---
        self.translate_btn = StyledButton(self, text="Перекласти", color="#2A821A",
                                          activebackground="#236F15", 
                                          width=40, command=handle_translate)
        self.translate_btn.pack(padx=20, pady=(10, 20))
    def update_texts(self, ui_texts: dict):
        """Оновлює всі тексти на вкладці перекладача"""
        
        # 1. Оновлюємо лейбли та кнопки
        self.input_label.config(text=ui_texts.get("original_label", "Оригінал"))
        self.output_label.config(text=ui_texts.get("translation_label", "Переклад"))
        self.translate_btn.config(text=ui_texts.get("translate_btn", "Перекласти"))

        # 2. Оновлюємо плейсхолдер для поля вводу
        new_placeholder = ui_texts.get("translator_placeholder", "Введіть текст")
        
        current_text = self.input_text.get("1.0", "end-1c")
        
        if current_text == getattr(self, "current_input_placeholder", ""):
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", new_placeholder)
            
        self.current_input_placeholder = new_placeholder

    def set_languages(self, lang_names: list[str]):
        self.sourse_lang_combo["values"] = lang_names
        self.target_lang_combo["values"] = lang_names
        
        if len(lang_names) >= 2:
            self.sourse_lang_combo.current(0)
            self.target_lang_combo.current(1)

    def update_comboboxes(self, new_languages_list: list):
        """Оновлює значення у випадаючих списках"""
        self.sourse_lang_combo.config(values=new_languages_list)
        self.target_lang_combo.config(values=new_languages_list)
        
        if new_languages_list:
            if self.sourse_lang_combo.get() not in new_languages_list:
                self.sourse_lang_combo.set(new_languages_list[0])
            if self.target_lang_combo.get() not in new_languages_list:
                self.target_lang_combo.set(new_languages_list[1])

    def swap_languages(self):
        sl = self.sourse_lang_combo.get()
        tl = self.target_lang_combo.get()
        self.sourse_lang_combo.set(tl)
        self.target_lang_combo.set(sl)

    def get_selected_source_lang(self) -> str:
        return self.sourse_lang_combo.get()

    def get_selected_target_lang(self) -> str:
        return self.target_lang_combo.get()

    def get_input_text(self) -> str:
        return self.input_text.get("1.0", tk.END).strip()

    def set_output_text(self, text: str):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)

class StatsTab(tk.Frame):
    def __init__(self, master, handle_clear_stats, handle_clear_wrong_words, update_wrong_words_ui, handle_clear_achievements): 
        super().__init__(master, bg="#f5f6fa")
        self.update_wrong_words_ui = update_wrong_words_ui

        self.buttons_frame = tk.Frame(self, bg="#f5f6fa")
        self.buttons_frame.pack(padx=20, pady=10, side="bottom", fill="x")

        self.clear_words_btn = StyledButton(self.buttons_frame, text="Очистити слова", 
                                            color="#e11111", activebackground="#b40f0f",
                                            width=25, command=handle_clear_wrong_words)
        self.clear_words_btn.pack(side="left", padx=10)

        self.clear_stats_btn = StyledButton(self.buttons_frame, text="Очистити статистику", 
                                            color="#e11111", activebackground="#b40f0f",
                                            width=25, command=handle_clear_stats)
        self.clear_stats_btn.pack(side="left", padx=10)

        self.clear_achvm_btn = StyledButton(self.buttons_frame, text="Очистити досягнення", 
                                            color="#e11111", activebackground="#b40f0f",
                                            width=25, command=handle_clear_achievements)
        self.clear_achvm_btn.pack(side="left", padx=10)

        style = ttk.Style()
        style.configure(
            "Inner.TNotebook.Tab", font=("Arial", 11, "bold"), width=60,
            padding=[15, 5], background="#f5f6fa", foreground="#555555", borderwidth=0
        )
        self.inner_notebook = ttk.Notebook(self, style="Inner.TNotebook")
        self.inner_notebook.pack(fill="both", expand=True, padx=20, pady=(20, 0))

        # ------ Підвкладка 1 статистика -----
        self.total_answers_var = tk.StringVar(value="0")
        self.correct_answers_var = tk.StringVar(value="0")
        self.wrong_answers_var = tk.StringVar(value="0")
        self.sessions_var = tk.StringVar(value="0")
        self.current_streak_var = tk.StringVar(value="0")
        self.longest_streak_var = tk.StringVar(value="0")


        # --- ГОЛОВНИЙ ФРЕЙМ ДЛЯ КАРТОК ---
        self.stats_frame = tk.Frame(self.inner_notebook, bg="#f5f6fa")
        self.inner_notebook.add(self.stats_frame, text="📊 Загальна статистика")
        
        self.cards_frame = tk.Frame(self.stats_frame, bg="#f5f6fa")
        self.cards_frame.pack(padx=20, pady=10, fill="x")

        self.cards_frame.columnconfigure(0, weight=1)
        self.cards_frame.columnconfigure(1, weight=1)
        self.stat_card_labels = {}

        self.stat_card_labels["total"] = self.create_stat_card(self.cards_frame, "📊 Загалом відповідей", self.total_answers_var, 0, 0)
        self.stat_card_labels["sessions"] = self.create_stat_card(self.cards_frame, "📚 Тестувань пройдено", self.sessions_var, 0, 1)
        self.stat_card_labels["correct"] = self.create_stat_card(self.cards_frame, "✅ Правильних відповідей", self.correct_answers_var, 1, 0, color="#2A821A")
        self.stat_card_labels["wrong"] = self.create_stat_card(self.cards_frame, "❌ Неправильних відповідей", self.wrong_answers_var, 1, 1, color="#e11111")
        self.stat_card_labels["streak"] = self.create_stat_card(self.cards_frame, "🔥 Поточний стрік", self.current_streak_var, 2, 0, color="#ff9800")
        self.stat_card_labels["max_streak"] = self.create_stat_card(self.cards_frame, "🏆 Найдовший стрік", self.longest_streak_var, 2, 1, color="#f5b041")

        self.words_frame = tk.Frame(self.stats_frame, bg="white", bd=1, relief="solid")
        self.words_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.words_label = tk.Label(self.words_frame, text="Слова для повторення:", font=("Arial", 12, "bold"), bg="white")
        self.words_label.pack(pady=(10, 0))
        
        self.wrong_words_text = scrolledtext.ScrolledText(
            self.words_frame, 
            font=("Arial", 12), 
            bg="white", 
            wrap="word", 
            height=4     
        )
        self.wrong_words_text.pack(padx=10, pady=10, fill="both", expand=True)
        self.wrong_words_text.config(state="disabled")


        self.achievements_frame = tk.Frame(self.inner_notebook, bg="#f5f6fa")
        self.inner_notebook.add(self.achievements_frame, text="🏆 Досягнення")

        # 1. Створюємо лейбл тут і зберігаємо його в self
        self.achievements_header_label = tk.Label(
            self.achievements_frame, 
            text="Ваші досягнення 🏆", 
            font=("Arial", 16, "bold"), 
            bg="#f5f6fa", fg="#333333"
        )
        self.achievements_header_label.pack(pady=(15, 15), anchor="center", padx=10)

        # 2. Створюємо окремий фрейм суто для карток
        self.achievements_grid_frame = tk.Frame(self.achievements_frame, bg="#f5f6fa")
        self.achievements_grid_frame.pack(fill="both", expand=True, padx=20)

    def update_texts(self, ui_texts: dict):
        """Оновлює всі тексти на вкладці статистики"""
        
        # 1. Оновлюємо нижні кнопки
        self.clear_words_btn.config(text=ui_texts.get("clear_words", "Очистити слова"))
        self.clear_stats_btn.config(text=ui_texts.get("clear_stats", "Очистити статистику"))
        self.clear_achvm_btn.config(text=ui_texts.get("clear_achievements", "Очистити досягнення"))

        # 2. Оновлюємо вкладки внутрішнього Notebook (індекси 0 і 1)
        self.inner_notebook.tab(0, text=ui_texts.get("general_stats_tab", "📊 Загальна статистика"))
        self.inner_notebook.tab(1, text=ui_texts.get("achievements_tab", "🏆 Досягнення"))

        # 3. Оновлюємо лейбл над полем зі словами
        self.words_label.config(text=ui_texts.get("words_to_repeat", "Слова для повторення:"))
        
        self.achievements_header_label.config(text=ui_texts.get("your_achievements", "Ваші досягнення 🏆"))

        if hasattr(self, 'stat_card_labels'):
            if "total" in self.stat_card_labels:
                self.stat_card_labels["total"].config(text=ui_texts.get("total_answers", "📊 Загалом відповідей"))
            if "sessions" in self.stat_card_labels:
                self.stat_card_labels["sessions"].config(text=ui_texts.get("total_quizzes", "📚 Тестувань пройдено"))
            if "correct" in self.stat_card_labels:
                self.stat_card_labels["correct"].config(text=ui_texts.get("correct_answers", "✅ Правильних відповідей"))
            if "wrong" in self.stat_card_labels:
                self.stat_card_labels["wrong"].config(text=ui_texts.get("wrong_answers", "❌ Неправильних відповідей"))
            if "streak" in self.stat_card_labels:
                self.stat_card_labels["streak"].config(text=ui_texts.get("current_streak", "🔥 Поточний стрік"))
            if "max_streak" in self.stat_card_labels:
                self.stat_card_labels["max_streak"].config(text=ui_texts.get("longest_streak", "🏆 Найдовший стрік"))

    def create_stat_card(self, parent, title, variable, row, col, color="#333333"):
        card = tk.Frame(parent, bg="white", bd=1, relief="ridge", padx=10, pady=10)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        label_title = tk.Label(card, text=title, font=("Arial", 11), bg="white", fg="#555555")
        label_title.pack()
        
        label_value = tk.Label(card, textvariable=variable, font=("Arial", 20, "bold"), bg="white", fg=color)
        label_value.pack()

        return label_title

    def set_wrong_words_var(self, text: str):
        if not text:
            text = "Немає помилок! 🎉"
        self.wrong_words_text.config(state="normal")
        self.wrong_words_text.delete("1.0", tk.END)
        self.wrong_words_text.insert(tk.END, text)
        self.wrong_words_text.config(state="disabled")

    def update_statistics_ui(self, stats: dict):
        self.total_answers_var.set(stats.get('total_answers', 0))
        self.correct_answers_var.set(stats.get('correct_answers', 0))
        self.wrong_answers_var.set(stats.get('wrong_answers', 0))
        self.sessions_var.set(stats.get('sessions', 0))
        self.current_streak_var.set(stats.get('current_streak', 0))
        self.longest_streak_var.set(stats.get('longest_streak', 0))

        self.update_wrong_words_ui(stats)

    def update_achievements_ui(self, achievements_data: dict, current_texts: dict):
        for widget in self.achievements_grid_frame.winfo_children():
            widget.destroy()

        self.achievements_grid_frame.columnconfigure(0, weight=1, uniform="equal")
        self.achievements_grid_frame.columnconfigure(1, weight=1, uniform="equal")
        self.achievements_grid_frame.columnconfigure(2, weight=1, uniform="equal")

        row = 0
        col = 0

        for ach_id, ach_info in achievements_data.items():
            is_unlocked = ach_info["is_unlocked"]
            
            ach_texts = current_texts.get(ach_id, {"title": "Unknown", "description": "Unknown"})
            title_text = ach_texts["title"]
            desc_text = ach_texts["description"]
            
            # Налаштовуємо кольори та іконку залежно від статусу (відкрито/закрито)
            bg_color = "white" if is_unlocked else "#e8e8e8"
            title_color = "#2A821A" if is_unlocked else "#888888" 
            desc_color = "#555555" if is_unlocked else "#999999"
            icon = ach_info["icon"] if is_unlocked else "🔒" 
            hbg = "#2A821A" if is_unlocked else "#888888"
            
            card = tk.Frame(self.achievements_grid_frame, bg=bg_color, 
                            bd=1, relief="solid", 
                            padx=10, pady=10,
                            highlightbackground=hbg,  
                            highlightcolor=hbg,       
                            highlightthickness=5
                            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Іконка
            icon_label = tk.Label(card, text=icon, font=("Arial", 24), bg=bg_color, fg=title_color)
            icon_label.pack(side="left", padx=(0, 10))

            text_frame = tk.Frame(card, bg=bg_color)
            text_frame.pack(side="left", fill="both", expand=True)

            # Заголовок та опис ачівки
            tk.Label(text_frame, text=title_text, font=("Arial", 11, "bold"), bg=bg_color, fg=title_color, anchor="w").pack(fill="x")
            tk.Label(text_frame, text=desc_text, font=("Arial", 9), bg=bg_color, fg=desc_color, wraplength=180, justify="left", anchor="w").pack(fill="x")

            # Логіка переходу на наступний рядок
            col += 1
            if col > 2:
                col = 0
                row += 1