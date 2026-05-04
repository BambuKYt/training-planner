"""
Training Planner - План тренировок
Автор: [Вставьте ваше имя и фамилию]
Дата: 2026
Описание: GUI-приложение для планирования тренировок с сохранением в JSON
"""

import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "trainings.json"


class TrainingPlanner:
    """Главный класс приложения Training Planner"""

    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("950x550")
        self.root.resizable(True, True)

        self.all_trainings = []
        self.filtered_trainings = []
        self.load_data()

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление тренировки", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.type_var, width=15)
        self.type_combo["values"] = ["Бег", "Плавание", "Велосипед", "Йога", "Силовая", "Футбол", "Лыжи", "Ходьба", "Танцы"]
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)
        self.type_combo.set("Бег")

        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.duration_entry = ttk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)

        self.add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_type_var = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, width=15)
        self.filter_type_combo["values"] = ["Все", "Бег", "Плавание", "Велосипед", "Йога", "Силовая", "Футбол", "Лыжи", "Ходьба", "Танцы"]
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type_combo.set("Все")

        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=3, padx=5, pady=5)

        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=4, padx=5, pady=5)

        self.reset_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_btn.grid(row=0, column=5, padx=5, pady=5)

        # Таблица с тренировками
        table_frame = ttk.LabelFrame(self.root, text="Список тренировок", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("type", width=150, anchor="center")
        self.tree.column("duration", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)

        self.delete_btn = ttk.Button(control_frame, text="Удалить выбранную", command=self.delete_training)
        self.delete_btn.pack(side="left", padx=5)

        self.edit_btn = ttk.Button(control_frame, text="Редактировать выбранную", command=self.edit_training)
        self.edit_btn.pack(side="left", padx=5)

        self.stats_label = ttk.Label(control_frame, text="", font=("Arial", 10))
        self.stats_label.pack(side="right", padx=10)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_duration(self, duration_str):
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False

    def add_training(self):
        date = self.date_entry.get().strip()
        training_type = self.type_var.get()
        duration = self.duration_entry.get().strip()

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте: ГГГГ-ММ-ДД")
            return

        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return

        new_id = max([t["id"] for t in self.all_trainings], default=0) + 1

        new_training = {
            "id": new_id,
            "date": date,
            "type": training_type,
            "duration": float(duration)
        }
        self.all_trainings.append(new_training)

        self.save_data()
        self.reset_filter()
        self.refresh_table()
        self.duration_entry.delete(0, tk.END)
        self.update_stats()

        messagebox.showinfo("Успех", f"Тренировка '{training_type}' на {date} добавлена!")

    def delete_training(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите тренировку для удаления!")
            return

        item = self.tree.item(selected[0])
        training_id = item['values'][0]

        if messagebox.askyesno("Подтверждение", f"Удалить тренировку ID {training_id}?"):
            self.all_trainings = [t for t in self.all_trainings if t["id"] != training_id]
            self.save_data()
            self.apply_filter()
            self.refresh_table()
            self.update_stats()
            messagebox.showinfo("Успех", "Тренировка удалена!")

    def edit_training(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите тренировку для редактирования!")
            return

        item = self.tree.item(selected[0])
        training_id = item['values'][0]

        training_to_edit = None
        for t in self.all_trainings:
            if t["id"] == training_id:
                training_to_edit = t
                break

        if not training_to_edit:
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование тренировки")
        edit_window.geometry("400x250")
        edit_window.resizable(False, False)
        edit_window.grab_set()

        ttk.Label(edit_window, text="Дата (ГГГГ-ММ-ДД):").pack(pady=(20, 5))
        date_edit = ttk.Entry(edit_window, width=20)
        date_edit.insert(0, training_to_edit["date"])
        date_edit.pack()

        ttk.Label(edit_window, text="Тип тренировки:").pack(pady=(10, 5))
        type_edit = ttk.Combobox(edit_window, values=["Бег", "Плавание", "Велосипед", "Йога", "Силовая", "Футбол", "Лыжи", "Ходьба", "Танцы"], width=17)
        type_edit.set(training_to_edit["type"])
        type_edit.pack()

        ttk.Label(edit_window, text="Длительность (мин):").pack(pady=(10, 5))
        duration_edit = ttk.Entry(edit_window, width=20)
        duration_edit.insert(0, str(training_to_edit["duration"]))
        duration_edit.pack()

        def save_edit():
            new_date = date_edit.get().strip()
            new_type = type_edit.get()
            new_duration = duration_edit.get().strip()

            if not self.validate_date(new_date):
                messagebox.showerror("Ошибка", "Неверный формат даты!")
                return

            if not self.validate_duration(new_duration):
                messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
                return

            training_to_edit["date"] = new_date
            training_to_edit["type"] = new_type
            training_to_edit["duration"] = float(new_duration)

            self.save_data()
            self.apply_filter()
            self.refresh_table()
            self.update_stats()

            messagebox.showinfo("Успех", "Тренировка обновлена!")
            edit_window.destroy()

        ttk.Button(edit_window, text="Сохранить изменения", command=save_edit).pack(pady=20)

    def apply_filter(self):
        filter_type = self.filter_type_var.get()
        filter_date = self.filter_date_entry.get().strip()

        self.filtered_trainings = self.all_trainings.copy()

        if filter_type != "Все":
            self.filtered_trainings = [t for t in self.filtered_trainings if t["type"] == filter_type]

        if filter_date:
            if self.validate_date(filter_date):
                self.filtered_trainings = [t for t in self.filtered_trainings if t["date"] == filter_date]
            else:
                messagebox.showwarning("Внимание", f"Дата '{filter_date}' имеет неверный формат!")

        self.refresh_table()
        self.update_stats()

    def reset_filter(self):
        self.filter_type_var.set("Все")
        self.filter_date_entry.delete(0, tk.END)
        self.filtered_trainings = self.all_trainings.copy()
        self.refresh_table()
        self.update_stats()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for training in self.filtered_trainings:
            self.tree.insert("", tk.END, values=(training["id"], training["date"], training["type"], f"{training['duration']}"))

    def update_stats(self):
        total_trainings = len(self.filtered_trainings)
        total_minutes = sum(t["duration"] for t in self.filtered_trainings)

        if total_trainings > 0:
            avg_duration = total_minutes / total_trainings
            self.stats_label.config(text=f"Всего: {total_trainings} тренировок | Суммарно: {total_minutes} мин | Средняя: {avg_duration:.1f} мин")
        else:
            self.stats_label.config(text="Нет тренировок для отображения")

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.all_trainings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные!\n{str(e)}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.all_trainings = json.load(f)
                self.filtered_trainings = self.all_trainings.copy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные!\n{str(e)}")
                self.all_trainings = []
                self.filtered_trainings = []
        else:
            self.all_trainings = [
                {"id": 1, "date": "2026-05-01", "type": "Бег", "duration": 30},
                {"id": 2, "date": "2026-05-02", "type": "Плавание", "duration": 45},
                {"id": 3, "date": "2026-05-03", "type": "Велосипед", "duration": 60},
                {"id": 4, "date": "2026-05-04", "type": "Силовая", "duration": 50},
                {"id": 5, "date": "2026-05-04", "type": "Йога", "duration": 40},
            ]
            self.filtered_trainings = self.all_trainings.copy()
            self.save_data()


def main():
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()


if __name__ == "__main__":
    main()