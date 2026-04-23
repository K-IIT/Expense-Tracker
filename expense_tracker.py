import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

# --- Конфигурация ---
DATA_FILE = 'expenses.json'
DATE_FORMAT = "%Y-%m-%d"

# --- Работа с данными ---
def load_expenses():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, OSError) as e:
        messagebox.showerror("Ошибка файла", f"Не удалось загрузить данные: {e}")
        return []

def save_expenses(expenses):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(expenses, f, ensure_ascii=False, indent=2)
    except OSError as e:
        messagebox.showerror("Ошибка файла", f"Не удалось сохранить данные: {e}")

# --- Логика приложения ---
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("900x600")
        self.expenses = load_expenses()
        self.create_widgets()
        self.update_treeview()

    def create_widgets(self):
        # --- Поля ввода ---
        frame_input = tk.LabelFrame(self.root, text="Добавить расход", padx=10, pady=10)
        frame_input.pack(pady=10, fill='x')

        tk.Label(frame_input, text="Сумма:").grid(row=0, column=0, sticky='e')
        self.entry_amount = tk.Entry(frame_input, width=15)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="Категория:").grid(row=1, column=0, sticky='e')
        self.entry_category = tk.Entry(frame_input, width=30)
        self.entry_category.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="Дата:").grid(row=2, column=0, sticky='e')
        # Используем DateEntry из tkcalendar для удобного выбора даты
        self.entry_date = DateEntry(frame_input, width=15, date_pattern='yyyy-mm-dd')
        self.entry_date.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(frame_input, text="Добавить расход", command=self.add_expense).grid(
            row=3, column=0, columnspan=2, pady=10)

        # --- Фильтрация и подсчёт ---
        frame_filter = tk.LabelFrame(self.root, text="Фильтр и статистика", padx=10, pady=10)
        frame_filter.pack(pady=10, fill='x')

        tk.Label(frame_filter, text="Категория:").grid(row=0, column=0, sticky='e')
        self.filter_category = tk.Entry(frame_filter, width=30)
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_filter, text="Дата с:").grid(row=1, column=0, sticky='e')
        self.filter_date_from = DateEntry(frame_filter, width=12, date_pattern='yyyy-mm-dd')
        self.filter_date_from.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        tk.Label(frame_filter, text="Дата по:").grid(row=2, column=0, sticky='e')
        self.filter_date_to = DateEntry(frame_filter, width=12, date_pattern='yyyy-mm-dd')
        self.filter_date_to.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        tk.Button(frame_filter, text="Применить фильтр", command=self.apply_filter).grid(
            row=3, column=0, columnspan=2, pady=10)
        
        self.label_total = tk.Label(frame_filter, text="Сумма за период: 0.00 ₽", font=('Arial', 12))
        self.label_total.grid(row=4, column=0, columnspan=2, pady=10)

        # --- Таблица расходов ---
        columns = ("date", "category", "amount")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        
        for col in columns:
            header_text = {"date": "Дата", "category": "Категория", "amount": "Сумма"}[col]
            self.tree.heading(col, text=header_text)
            self.tree.column(col, minwidth=0, width=200)
            
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

    def add_expense(self):
         amount_str = self.entry_amount.get().strip()
         category = self.entry_category.get().strip()
         date_str = self.entry_date.get_date().strftime(DATE_FORMAT)
         
         # Валидация полей
         if not (amount_str and category):
             messagebox.showerror("Ошибка", "Сумма и категория должны быть заполнены!")
             return

         try:
             amount = float(amount_str.replace(',', '.'))
             if amount <= 0:
                 raise ValueError("Сумма должна быть положительной")
         except ValueError as e:
             messagebox.showerror("Ошибка", f"Неверный формат суммы: {e}")
             return

         expense = {
             "date": date_str,
             "category": category,
             "amount": amount
         }

         self.expenses.append(expense)
         save_expenses(self.expenses)
         self.update_treeview()
         
    def apply_filter(self):
         category = self.filter_category.get().strip().lower()
         
         date_from_str = None
         if self.filter_date_from.get_date():
             date_from_str = self.filter_date_from.get_date().strftime(DATE_FORMAT)
             
         date_to_str = None
         if self.filter_date_to.get_date():
             date_to_str = self.filter_date_to.get_date().strftime(DATE_FORMAT)
         
         filtered_expenses = []
         for expense in self.expenses:
             if category and expense["category"].lower() != category:
                 continue
             
             if date_from_str and expense["date"] < date_from_str:
                 continue
                 
             if date_to_str and expense["date"] > date_to_str:
                 continue
                 
             filtered_expenses.append(expense)
         
         total_sum = sum(expense["amount"] for expense in filtered_expenses)
         
         self.display_expenses(filtered_expenses)
         self.label_total.config(text=f"Сумма за период: {total_sum:.2f} ₽")
    
    def display_expenses(self, expenses_to_show):
         for i in self.tree.get_children():
             self.tree.delete(i)
             
         for expense in expenses_to_show:
             formatted_amount = f"{expense['amount']:.2f} ₽"
             self.tree.insert("", "end", values=(expense["date"], expense["category"], formatted_amount))
    
    def update_treeview(self):
         # Отображает все расходы из self.expenses в таблице при старте или после добавления.
         # Сбрасывает фильтр и сумму.
         self.display_expenses(self.expenses)
         self.label_total.config(text="Сумма за период: 0.00 ₽")


# --- Точка входа ---
if __name__ == '__main__':
     root = tk.Tk()
     app = ExpenseTrackerApp(root)
     root.mainloop()
