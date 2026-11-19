import tkinter as tk
from tkinter import scrolledtext
class StyledButton(tk.Button):
    def __init__(self, master, text, command=None, color="#4CAF50", **kwargs):
        # 1. Витягуємо 'fg' з kwargs, якщо він там є, інакше ставимо "white"
        text_color = kwargs.pop('fg', 'white') 
        super().__init__(
            master, 
            text=text, 
            command=command, 
            bg=color, 
            fg=text_color,
            font=("Arial", 12, "bold"),
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            **kwargs
        )
        self.default_bg = color
        self.hover_bg = self.adjust_color(color, -20) 
    
        # Прив'язуємо події анімації
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(bg=self.hover_bg)

    def on_leave(self, event):
        self.config(bg=self.default_bg)

    def adjust_color(self, hex_color, amount):
        # Прибираємо #, якщо він є
        hex_color = hex_color.lstrip('#')
        
        # Конвертуємо HEX в RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Змінюємо яскравість (amount < 0 для затемнення, > 0 для освітлення)
        # Використовуємо max(0, min(255, ...)) щоб не вийти за межі допустимих значень
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))

        # Повертаємо у форматі HEX рядок
        return f"#{r:02x}{g:02x}{b:02x}" 

class SessionSummaryPopup(tk.Toplevel):
    def __init__(self, parent, stats, mistakes, on_retry_callback, on_menu_callback, ui_texts: dict):
        super().__init__(parent)

        self.title(ui_texts.get("popup_session_title", "Результати тесту"))
        self.geometry("500x500")
        self.configure(bg="#f5f6fa", padx=20, pady=20)
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        self.on_retry_callback = on_retry_callback
        self.on_menu_callback = on_menu_callback
        correct = stats.get("correct_answers", 0)
        wrong = stats.get("wrong_answers", 0)
        total = correct + wrong
        accuracy = int((correct / total * 100)) if total > 0 else 0

        tk.Label(self, text=ui_texts.get("popup_test_completed", "Тестування завершено!"), 
                 font=("Arial", 16, "bold"), bg="#f5f6fa", fg="#236F15").pack(pady=(0, 15))

        stats_frame = tk.Frame(self, bg="#ecf0f1", padx=10, pady=10)
        stats_frame.pack(fill="x", pady=10)
        
        correct_text = ui_texts.get("popup_correct_format", "✅ Правильно: {correct}").format(correct=correct)
        wrong_text = ui_texts.get("popup_mistakes_format", "❌ Помилок: {wrong}").format(wrong=wrong)
        accuracy_text = ui_texts.get("popup_accuracy_format", "Точність: {accuracy}%").format(accuracy=accuracy)

        tk.Label(stats_frame, text=correct_text, font=("Arial", 12), bg="#ecf0f1", fg="#27ae60").pack(side="left", expand=True)
        tk.Label(stats_frame, text=wrong_text, font=("Arial", 12), bg="#ecf0f1", fg="#e74c3c").pack(side="left", expand=True)
        
        tk.Label(self, text=accuracy_text, font=("Arial", 14, "bold"), bg="#f5f6fa", fg="#2980b9").pack(pady=5)
        
        if mistakes:
            tk.Label(self, text=ui_texts.get("popup_words_to_repeat", "Слова для повторення:"), font=("Arial", 12, "bold"), 
                     bg="#f5f6fa", fg="black").pack(anchor="w", pady=(10, 5), padx=20)
            
            self.mistakes_text = scrolledtext.ScrolledText(
                self, height=6, font=("Arial", 11), bg="white", 
                relief="flat", wrap="word", padx=10, pady=5
            )
            self.mistakes_text.pack(fill="both", expand=True, padx=20)

            for item in mistakes:
                self.mistakes_text.insert(tk.END, f"{item}\n")

            self.mistakes_text.configure(state="disabled")
            
        else:
            tk.Label(self, text=ui_texts.get("popup_perfect_result", "🎉 Ідеальний результат!\nТи не зробив жодної помилки."), 
                     font=("Arial", 12), bg="#f5f6fa", fg="#f39c12", justify="center").pack(expand=True)

        btn_frame = tk.Frame(self, bg="#f5f6fa")
        btn_frame.pack(side="bottom", fill="x", pady=(20, 0))
        
        if mistakes:
            btn_retry = tk.Button(btn_frame, text=ui_texts.get("popup_btn_retry", "Повторити помилки"), font=("Arial", 10, "bold"), 
                                  bg="#3498db", activebackground="#1F88DE", fg="white", 
                                  relief="flat", cursor="hand2", command=self.handle_retry)
            btn_retry.pack(side="left", expand=True, fill="x", padx=5, ipady=5)
            
        btn_menu = tk.Button(btn_frame, text=ui_texts.get("popup_btn_menu", "Головне меню"), font=("Arial", 10, "bold"), 
                             bg="#2A821A",activebackground="#236F15",  fg="white", 
                             relief="flat", cursor="hand2", command=self.handle_menu)
        btn_menu.pack(side="left", expand=True, fill="x", padx=5, ipady=5)

    def handle_retry(self):
        self.destroy()
        if self.on_retry_callback:
            self.on_retry_callback()

    def handle_menu(self):
        self.destroy()
        if self.on_menu_callback:
            self.on_menu_callback()


class CardsSummaryPopup(tk.Toplevel):
    def __init__(self, parent, stats, on_close_callback, ui_texts: dict):
        super().__init__(parent)

        self.title(ui_texts.get("popup_cards_title", "Результати карток"))
        self.geometry("400x300")
        self.configure(bg="#f5f6fa", padx=20, pady=20)
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        self.on_close_callback = on_close_callback
        correct = stats.get("already_learned", 0)
        wrong = stats.get("still_learning", 0)
        total = correct + wrong
        accuracy = int((correct / total * 100)) if total > 0 else 0

        tk.Label(self, text=ui_texts.get("popup_session_completed", "Сесія завершена!"), 
                 font=("Arial", 16, "bold"), bg="#f5f6fa", fg="#236F15").pack(pady=(0, 15))

        stats_frame = tk.Frame(self, bg="#ecf0f1", padx=10, pady=10)
        stats_frame.pack(fill="x", pady=10)
        
        learned_text = ui_texts.get("popup_learned_format", "✅ Вивчено: {correct}").format(correct=correct)
        still_learning_text = ui_texts.get("popup_still_learning_format", "❌ Ще вивчаю: {wrong}").format(wrong=wrong)
        accuracy_text = ui_texts.get("popup_accuracy_format", "Точність: {accuracy}%").format(accuracy=accuracy)

        tk.Label(stats_frame, text=learned_text, font=("Arial", 12), bg="#ecf0f1", fg="#27ae60").pack(side="left", expand=True)
        tk.Label(stats_frame, text=still_learning_text, font=("Arial", 12), bg="#ecf0f1", fg="#e74c3c").pack(side="left", expand=True)
        
        tk.Label(self, text=accuracy_text, font=("Arial", 14, "bold"), bg="#f5f6fa", fg="#2980b9").pack(pady=5)

        btn_close = tk.Button(self, text=ui_texts.get("popup_btn_close", "Закрити"), font=("Arial", 10, "bold"), 
                              bg="#2A821A", activebackground="#236F15", fg="white", 
                              relief="flat", cursor="hand2", command=self.handle_close)
        btn_close.pack(side="bottom", fill="x", pady=(20, 0))

    def handle_close(self):
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()