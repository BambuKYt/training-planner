"""
Weather Diary - Дневник погоды
Автор: Uraltsev Aleksej
Дата: 2026
Описание: GUI-приложение для ведения дневника погоды с сохранением в JSON
"""

import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "weather_data.json"


class WeatherDiary:
    """Главный класс приложения Weather Diary"""

    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)

        self.all_records = []
        self.filtered_records = []
        self.load_data()

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление записи о погоде", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Температура
        ttk.Label(input_frame, text="Температура (C):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        # Описание погоды
        ttk.Label(input_frame, text="Описание погоды:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.desc_entry = ttk.Entry(input_frame, width=20)
        self.desc_entry.grid(row=0, column=5, padx=5, pady=5)

        # Осадки (да/нет)
        ttk.Label(input_frame, text="Осадки:").grid(row=0, column=6, padx=5, pady=5, sticky="e")
        self.precipitation_var = tk.StringVar()
        self.precipitation_combo = ttk.Combobox(input_frame, textvariable=self.precipitation_var, width=8)
        self.precipitation_combo["values"] = ["Нет", "Да"]
        self.precipitation_combo.grid(row=0, column=7, padx=5, pady=5)
        self.precipitation_combo.set("Нет")

        # Кнопка добавления
        self.add_btn = ttk.Button(input_frame, text="Добавить запись", command=self.add_record)
        self.add_btn.grid(row=0, column=8, padx=10, pady=5)

        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Фильтр по температуре
        ttk.Label(filter_frame, text="Температура выше (C):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)

        # Кнопки фильтрации
        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=4, padx=5, pady=5)

        self.reset_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_btn.grid(row=0, column=5, padx=5, pady=5)

        # Таблица с записями
        table_frame = ttk.LabelFrame(self.root, text="Список записей о погоде", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("temperature", width=120, anchor="center")
        self.tree.column("description", width=300, anchor="w")
        self.tree.column("precipitation", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)

        self.delete_btn = ttk.Button(control_frame, text="Удалить выбранную", command=self.delete_record)
        self.delete_btn.pack(side="left", padx=5)

        self.edit_btn = ttk.Button(control_frame, text="Редактировать выбранную", command=self.edit_record)
        self.edit_btn.pack(side="left", padx=5)

        # Статистика
        self.stats_label = ttk.Label(control_frame, text="", font=("Arial", 10))
        self.stats_label.pack(side="right", padx=10)

    def validate_date(self, date_str):
        """Проверка корректности формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_temperature(self, temp_str):
        """Проверка, что температура - число"""
        try:
            float(temp_str)
            return True
        except ValueError:
            return False

    def validate_description(self, desc_str):
        """Проверка, что описание не пустое"""
        return desc_str.strip() != ""

    def add_record(self):
        """Добавление новой записи"""
        date = self.date_entry.get().strip()
        temperature = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precipitation_var.get()

        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте: ГГГГ-ММ-ДД")
            return

        if not self.validate_temperature(temperature):
            messagebox.showerror("Ошибка", "Температура должна быть числом!\nПример: 25.5, -10, 0")
            return

        if not self.validate_description(description):
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым!")
            return

        # Создание ID
        if self.all_records:
            new_id = max(r["id"] for r in self.all_records) + 1
        else:
            new_id = 1

        # Добавление
        new_record = {
            "id": new_id,
            "date": date,
            "temperature": float(temperature),
            "description": description,
            "precipitation": precipitation
        }
        self.all_records.append(new_record)

        # Сохранение и обновление
        self.save_data()
        self.reset_filter()
        self.refresh_table()

        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

        self.update_stats()

        messagebox.showinfo("Успех", f"Запись добавлена!\nДата: {date}\nТемпература: {temperature} C")

    def delete_record(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления!")
            return

        item = self.tree.item(selected[0])
        record_id = item['values'][0]

        if messagebox.askyesno("Подтверждение", f"Удалить запись ID {record_id}?"):
            self.all_records = [r for r in self.all_records if r["id"] != record_id]
            self.save_data()
            self.apply_filter()
            self.refresh_table()
            self.update_stats()
            messagebox.showinfo("Успех", "Запись удалена!")

    def edit_record(self):
        """Редактирование выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования!")
            return

        item = self.tree.item(selected[0])
        record_id = item['values'][0]

        record_to_edit = None
        for r in self.all_records:
            if r["id"] == record_id:
                record_to_edit = r
                break

        if not record_to_edit:
            return

        # Окно редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование записи")
        edit_window.geometry("400x300")
        edit_window.resizable(False, False)
        edit_window.grab_set()

        ttk.Label(edit_window, text="Дата (ГГГГ-ММ-ДД):").pack(pady=(20, 5))
        date_edit = ttk.Entry(edit_window, width=20)
        date_edit.insert(0, record_to_edit["date"])
        date_edit.pack()

        ttk.Label(edit_window, text="Температура (C):").pack(pady=(10, 5))
        temp_edit = ttk.Entry(edit_window, width=20)
        temp_edit.insert(0, str(record_to_edit["temperature"]))
        temp_edit.pack()

        ttk.Label(edit_window, text="Описание погоды:").pack(pady=(10, 5))
        desc_edit = ttk.Entry(edit_window, width=30)
        desc_edit.insert(0, record_to_edit["description"])
        desc_edit.pack()

        ttk.Label(edit_window, text="Осадки:").pack(pady=(10, 5))
        precip_edit = ttk.Combobox(edit_window, values=["Нет", "Да"], width=17)
        precip_edit.set(record_to_edit["precipitation"])
        precip_edit.pack()

        def save_edit():
            new_date = date_edit.get().strip()
            new_temp = temp_edit.get().strip()
            new_desc = desc_edit.get().strip()
            new_precip = precip_edit.get()

            if not self.validate_date(new_date):
                messagebox.showerror("Ошибка", "Неверный формат даты!")
                return

            if not self.validate_temperature(new_temp):
                messagebox.showerror("Ошибка", "Температура должна быть числом!")
                return

            if not self.validate_description(new_desc):
                messagebox.showerror("Ошибка", "Описание не может быть пустым!")
                return

            record_to_edit["date"] = new_date
            record_to_edit["temperature"] = float(new_temp)
            record_to_edit["description"] = new_desc
            record_to_edit["precipitation"] = new_precip

            self.save_data()
            self.apply_filter()
            self.refresh_table()
            self.update_stats()

            messagebox.showinfo("Успех", "Запись обновлена!")
            edit_window.destroy()

        ttk.Button(edit_window, text="Сохранить изменения", command=save_edit).pack(pady=20)

    def apply_filter(self):
        """Применение фильтрации"""
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        self.filtered_records = self.all_records.copy()

        # Фильтр по дате
        if filter_date:
            if self.validate_date(filter_date):
                self.filtered_records = [r for r in self.filtered_records if r["date"] == filter_date]
            else:
                messagebox.showwarning("Внимание", f"Дата '{filter_date}' имеет неверный формат!")

        # Фильтр по температуре (выше указанного значения)
        if filter_temp_str:
            if self.validate_temperature(filter_temp_str):
                temp_threshold = float(filter_temp_str)
                self.filtered_records = [r for r in self.filtered_records if r["temperature"] > temp_threshold]
            else:
                messagebox.showwarning("Внимание", f"Температура '{filter_temp_str}' должна быть числом!")

        self.refresh_table()
        self.update_stats()

    def reset_filter(self):
        """Сброс всех фильтров"""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.filtered_records = self.all_records.copy()
        self.refresh_table()
        self.update_stats()

    def refresh_table(self):
        """Обновление таблицы с данными"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for record in self.filtered_records:
            self.tree.insert("", tk.END, values=(
                record["id"],
                record["date"],
                f"{record['temperature']}",
                record["description"],
                record["precipitation"]
            ))

    def update_stats(self):
        """Обновление статистики"""
        total_records = len(self.filtered_records)
        if total_records > 0:
            avg_temp = sum(r["temperature"] for r in self.filtered_records) / total_records
            self.stats_label.config(text=f"Всего записей: {total_records} | Средняя температура: {avg_temp:.1f} C")
        else:
            self.stats_label.config(text="Нет записей для отображения")

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.all_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные!\n{str(e)}")

    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.all_records = json.load(f)
                self.filtered_records = self.all_records.copy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные!\n{str(e)}")
                self.all_records = []
                self.filtered_records = []
        else:
            # Примеры записей для демонстрации
            self.all_records = [
                {"id": 1, "date": "2026-05-01", "temperature": 18.5, "description": "Солнечно, легкий ветер", "precipitation": "Нет"},
                {"id": 2, "date": "2026-05-02", "temperature": 12.0, "description": "Пасмурно, моросит дождь", "precipitation": "Да"},
                {"id": 3, "date": "2026-05-03", "temperature": 22.0, "description": "Ясно, тепло", "precipitation": "Нет"},
                {"id": 4, "date": "2026-05-04", "temperature": 15.5, "description": "Облачно, без осадков", "precipitation": "Нет"},
                {"id": 5, "date": "2026-05-04", "temperature": 8.0, "description": "Дождливо, холодно", "precipitation": "Да"},
            ]
            self.filtered_records = self.all_records.copy()
            self.save_data()


def main():
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()


if __name__ == "__main__":
    main()
