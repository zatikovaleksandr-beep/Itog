import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

# Предопределённые цитаты
DEFAULT_QUOTES = [
    {"text": "Будь изменением, которое ты хочешь видеть в мире.", "author": "Махатма Ганди", "theme": "мотивация"},
    {"text": "Я мыслю, следовательно, существую.", "author": "Рене Декарт", "theme": "философия"},
    {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "theme": "жизнь"},
    {"text": "Не судите о каждом дне по собранному урожаю, а по посеянным семенам.", "author": "Роберт Льюис Стивенсон", "theme": "успех"},
    {"text": "Будущее зависит от того, что ты делаешь сегодня.", "author": "Махатма Ганди", "theme": "мотивация"},
]

QUOTES_FILE = "quotes.json"
HISTORY_FILE = "history.json"

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("700x650")

        # Основное хранилище всех цитат (НЕ меняется при фильтрации)
        self.all_quotes = self.load_quotes()
        
        # Текущий рабочий список (может быть отфильтрован)
        self.current_quotes = self.all_quotes.copy()
        
        self.history = self.load_history()

        self.create_widgets()
        self.update_author_filter()
        self.update_theme_filter()
        self.update_history_list()

    # ---------- Работа с файлами ----------
    def load_quotes(self):
        if os.path.exists(QUOTES_FILE):
            with open(QUOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            self.save_quotes(DEFAULT_QUOTES)
            return DEFAULT_QUOTES.copy()

    def save_quotes(self, quotes):
        with open(QUOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(quotes, f, indent=4, ensure_ascii=False)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    # ---------- GUI ----------
    def create_widgets(self):
        # Фрейм для отображения цитаты
        self.quote_frame = tk.LabelFrame(self.root, text="Случайная цитата", padx=10, pady=10)
        self.quote_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.quote_label = tk.Label(self.quote_frame, text="Нажмите 'Сгенерировать'", wraplength=650, font=("Arial", 12), justify="center")
        self.quote_label.pack()

        # Кнопка генерации
        self.generate_btn = tk.Button(self.root, text="Сгенерировать цитату", command=self.generate_quote, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.generate_btn.pack(pady=10)

        # Фрейм для фильтров
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Автор:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.author_filter = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.author_filter.grid(row=0, column=1, padx=5, pady=5)
        self.author_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        tk.Label(filter_frame, text="Тема:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.theme_filter = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.theme_filter.grid(row=1, column=1, padx=5, pady=5)
        self.theme_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Кнопка сброса фильтров
        self.reset_btn = tk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters, bg="#FF9800", fg="white")
        self.reset_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Статус фильтрации
        self.filter_status = tk.Label(filter_frame, text="", fg="blue", font=("Arial", 9))
        self.filter_status.grid(row=3, column=0, columnspan=2)

        # История
        history_frame = tk.LabelFrame(self.root, text="История цитат", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.history_listbox = tk.Listbox(history_frame, height=8)
        self.history_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_listbox.yview)

        # Кнопка для добавления новой цитаты
        add_frame = tk.Frame(self.root)
        add_frame.pack(pady=10)
        self.add_quote_btn = tk.Button(add_frame, text="➕ Добавить новую цитату", command=self.add_quote_dialog, bg="#2196F3", fg="white")
        self.add_quote_btn.pack()

    # ---------- Логика фильтрации (исправленная) ----------
    def update_author_filter(self):
        authors = sorted(set(q['author'] for q in self.all_quotes))
        self.author_filter['values'] = ["Все"] + authors
        self.author_filter.set("Все")

    def update_theme_filter(self):
        themes = sorted(set(q['theme'] for q in self.all_quotes))
        self.theme_filter['values'] = ["Все"] + themes
        self.theme_filter.set("Все")

    def apply_filters(self):
        """Применяет фильтры к all_quotes и сохраняет результат в current_quotes"""
        selected_author = self.author_filter.get()
        selected_theme = self.theme_filter.get()

        filtered = self.all_quotes.copy()
        
        if selected_author != "Все":
            filtered = [q for q in filtered if q['author'] == selected_author]
        if selected_theme != "Все":
            filtered = [q for q in filtered if q['theme'] == selected_theme]

        self.current_quotes = filtered
        
        # Обновляем статус фильтрации
        if len(filtered) == 0:
            self.filter_status.config(text="⚠️ Нет цитат, соответствующих фильтру! Измените фильтры.", fg="red")
            self.quote_label.config(text="Нет цитат для выбранных фильтров.\nСбросьте фильтры или выберите другие параметры.")
        else:
            self.filter_status.config(text=f"✓ Найдено цитат: {len(filtered)}", fg="green")
            self.quote_label.config(text=f"Фильтр активен: {len(filtered)} цитат доступно.\nНажмите 'Сгенерировать'.")

    def reset_filters(self):
        """Сбрасывает все фильтры"""
        self.author_filter.set("Все")
        self.theme_filter.set("Все")
        self.current_quotes = self.all_quotes.copy()
        self.filter_status.config(text="Фильтры сброшены", fg="blue")
        self.quote_label.config(text="Фильтры сброшены. Нажмите 'Сгенерировать' для получения цитаты.")

    # ---------- Генерация (исправленная) ----------
    def generate_quote(self):
        """Генерирует цитату из текущего отфильтрованного списка"""
        if not self.current_quotes:
            messagebox.showwarning(
                "Нет цитат", 
                "Нет цитат, соответствующих текущим фильтрам!\nСбросьте фильтры или добавьте новые цитаты."
            )
            return

        quote = random.choice(self.current_quotes)
        display_text = f"«{quote['text']}»\n\n— {quote['author']} (Тема: {quote['theme']})"
        self.quote_label.config(text=display_text)

        # Сохраняем в историю с датой
        history_entry = {
            "text": quote['text'],
            "author": quote['author'],
            "theme": quote['theme'],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(history_entry)
        self.save_history()
        self.update_history_list()

    def update_history_list(self):
        self.history_listbox.delete(0, tk.END)
        for entry in reversed(self.history[-20:]):  # Показываем последние 20
            self.history_listbox.insert(tk.END, f"{entry['date']} — {entry['author']}: {entry['text'][:50]}...")

    # ---------- Добавление новой цитаты с валидацией ----------
    def add_quote_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить новую цитату")
        dialog.geometry("400x300")

        tk.Label(dialog, text="Текст цитаты:").pack(pady=5)
        text_entry = tk.Text(dialog, height=5, width=50)
        text_entry.pack(pady=5)

        tk.Label(dialog, text="Автор:").pack(pady=5)
        author_entry = tk.Entry(dialog, width=50)
        author_entry.pack(pady=5)

        tk.Label(dialog, text="Тема:").pack(pady=5)
        theme_entry = tk.Entry(dialog, width=50)
        theme_entry.pack(pady=5)

        def save_new_quote():
            text = text_entry.get("1.0", tk.END).strip()
            author = author_entry.get().strip()
            theme = theme_entry.get().strip()

            # Проверка на пустые строки
            if not text or not author or not theme:
                messagebox.showerror("Ошибка", "Все поля обязательны для заполнения!")
                return

            new_quote = {"text": text, "author": author, "theme": theme}
            
            # Добавляем в общий список
            self.all_quotes.append(new_quote)
            self.save_quotes(self.all_quotes)
            
            # Обновляем текущий список с учётом фильтров
            self.current_quotes = self.all_quotes.copy()
            self.apply_filters()  # Переприменяем текущие фильтры
            
            # Обновляем выпадающие списки
            self.update_author_filter()
            self.update_theme_filter()
            
            dialog.destroy()
            messagebox.showinfo("Успех", "Цитата добавлена!")

        tk.Button(dialog, text="Сохранить", command=save_new_quote, bg="#4CAF50", fg="white").pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()