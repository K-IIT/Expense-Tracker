import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.data = []
        self.load_data()

        # --- Поля ввода ---
        tk.Label(root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Категория:").grid(row=1, column=0, padx=5, pady=5)
        self.category_entry = tk.Entry(root)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        # --- Кнопка добавления ---
        tk.Button(root, text="Добавить расход", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=10)

        # --- Таблица расходов ---
        self.tree = ttk.Treeview(root, columns=("amount", "category", "date"), show='headings')
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # --- Фильтры ---
        tk.Label(root, text="Фильтр по категории:").grid(row=5, column=0, padx=5, pady=5)
        self.filter_category = tk.Entry(root)
        self.filter_category.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(root, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=6, column=0, padx=5, pady=5)
        self.filter_date = tk.Entry(root)
        self.filter_date.grid(row=6, column=1, padx=5, pady=5)

        tk.Button(root, text="Применить фильтры", command=self.apply_filters).grid(row=7, column=0, columnspan=2, pady=5)

        # --- Период для суммы ---
        tk.Label(root, text="Период для суммы (с):").grid(row=8, column=0, padx=5, pady=5)
        self.sum_start = tk.Entry(root)
        self.sum_start.grid(row=8, column=1, padx=5, pady=5)

        tk.Label(root, text="Период для суммы (по):").grid(row=9, column=0, padx=5, pady=5)
        self.sum_end = tk.Entry(root)
        self.sum_end.grid(row=9, column=1, padx=5, pady=5)

        tk.Button(root, text="Сумма за период", command=self.calculate_sum).grid(row=10, column=0, columnspan=2, pady=5)

        self.sum_result_label = tk.Label(root, text="")
        self.sum_result_label.grid(row=11, column=0, columnspan=2)

        # --- Сохранение/загрузка ---
        tk.Button(root, text="Сохранить в JSON", command=self.save_data).grid(row=12, column=0, pady=5)
        tk.Button(root, text="Загрузить из JSON", command=self.load_data_gui).grid(row=12, column=1, pady=5)

        self.update_table()

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        date = self.date_entry.get()

        if not amount.replace('.', '', 1).isdigit() or float(amount) <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
            return

        self.data.append({
            "amount": float(amount),
            "category": category,
            "date": date
        })

        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

        self.update_table()

    def update_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for item in self.data:
            self.tree.insert("", "end", values=(item["amount"], item["category"], item["date"]))

    def apply_filters(self):
        cat_filter = self.filter_category.get().lower()
        date_filter = self.filter_date.get()

        filtered = self.data

        if cat_filter:
            filtered = [x for x in filtered if cat_filter in x["category"].lower()]

        if date_filter:
            try:
                datetime.strptime(date_filter, "%Y-%m-%d")
                filtered = [x for x in filtered if x["date"] == date_filter]
            except ValueError:
                messagebox.showerror("Ошибка", "Дата фильтра в неверном формате!")
                return

        for i in self.tree.get_children():
            self.tree.delete(i)

        for item in filtered:
            self.tree.insert("", "end", values=(item["amount"], item["category"], item["date"]))

    def calculate_sum(self):
        start_date = self.sum_start.get()
        end_date = self.sum_end.get()

        try:
            if start_date:
                datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты!")
            return

        total = 0.0
        for item in self.data:
            date_ok = True
            if start_date and item["date"] < start_date:
                date_ok = False
            if end_date and item["date"] > end_date:
                date_ok = False
            if date_ok:
                total += item["amount"]

        self.sum_result_label.config(text=f"Сумма за период: {total:.2f} ₽")

    def save_data(self):
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
                self.update_table()
                return True
        except FileNotFoundError:
            return False

    def load_data_gui(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
                self.update_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
