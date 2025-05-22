import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta

# Функция для проверки заполненности полей
def validate_fields(entries):
    for field, entry in entries.items():
        if not entry.get().strip():
            messagebox.showerror("Ошибка", f"Поле '{field}' должно быть заполнено!")
            return False
    return True

# Функция для проверки совпадения паролей
def validate_passwords(pass1, pass2):
    if pass1 != pass2:
        messagebox.showerror("Ошибка", "Пароли не совпадают!")
        return False
    return True

def registrations():
    global window_authoriz
    window_registrations = tk.Toplevel() 
    window_registrations.title("Регистрация")
    window_registrations.geometry('450x460')
    
    # Скрываем окно авторизации
    window_authoriz.withdraw()

    def on_closing():
        window_authoriz.deiconify()
        window_registrations.destroy()

    window_registrations.protocol("WM_DELETE_WINDOW", on_closing)

    content_frame = tk.Frame(window_registrations, padx=20, pady=20)
    content_frame.pack(expand=True, fill='both')

    tk.Label(content_frame, text="Регистрация", font=('Arial', 14)).pack(pady=(0, 20))
    
    # Создаем поля ввода
    fields = {
        "Фамилия": tk.Entry(content_frame),
        "Имя": tk.Entry(content_frame),
        "Отчество": tk.Entry(content_frame),
        "Телефон": tk.Entry(content_frame),
        "Логин": tk.Entry(content_frame),
        "Пароль": tk.Entry(content_frame),
        "Повторите пароль": tk.Entry(content_frame)
    }
    
    # Размещаем поля на форме
    entries = {}
    for label, entry in fields.items():
        tk.Label(content_frame, text=label, anchor='w').pack(fill='x')
        entry.pack(fill='x', pady=(0, 10))
        entries[label] = entry

    button_frame = tk.Frame(content_frame)
    button_frame.pack(fill='x')

    def register_user():
        # Проверяем заполненность полей
        if not validate_fields({
            "Фамилия": entries["Фамилия"],
            "Имя": entries["Имя"],
            "Логин": entries["Логин"],
            "Пароль": entries["Пароль"],
            "Повторите пароль": entries["Повторите пароль"]
        }):
            return
            
        # Проверяем совпадение паролей
        if not validate_passwords(
            entries["Пароль"].get(), 
            entries["Повторите пароль"].get()
        ):
            return
            
        try:
            # Добавляем пользователя в БД
            cursor.execute('''
                INSERT INTO user (fam, name, otch, number, login, password, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entries["Фамилия"].get(),
                entries["Имя"].get(),
                entries["Отчество"].get(),
                entries["Телефон"].get(),
                entries["Логин"].get(),
                entries["Пароль"].get(),
                "клиент",  
                "активен"
            ))
            connection.commit()
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            on_closing()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    register_button = tk.Button(button_frame, text="Зарегистрироваться", command=register_user)
    register_button.pack(side='left', expand=True, fill='x', padx=(5, 0))

    cancel_button = tk.Button(button_frame, text="Отмена", command=on_closing)
    cancel_button.pack(side='left', expand=True, fill='x', padx=(5, 0))

def show_client_panel(user_data):
    global window_authoriz
    
    # Скрываем окно авторизации
    window_authoriz.withdraw()
    
    client_window = tk.Toplevel()
    client_window.title("Панель клиента")
    client_window.geometry("800x600")
    
    def on_closing():
        window_authoriz.deiconify()
        client_window.destroy()
    
    client_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Основной контент
    content_frame = tk.Frame(client_window, padx=20, pady=20)
    content_frame.pack(expand=True, fill='both')
    
    # Приветствие
    welcome_label = tk.Label(content_frame, text=f"Добро пожаловать, {user_data[1]} {user_data[0]}!", font=('Arial', 14))
    welcome_label.pack(pady=(0, 20))
    
    # Фрейм для поиска
    search_frame = tk.Frame(content_frame)
    search_frame.pack(fill='x', pady=10)
    
    tk.Label(search_frame, text="Поиск сделки:").pack(side='left')
    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side='left', padx=5)
    
    def search_deals():
        search_term = search_entry.get().strip()
        if not search_term:
            refresh_deals()
            return
            
        query = """
        SELECT rowid, cabine, date, time, duration, price, status 
        FROM deals 
        WHERE user_id = ? AND (cabine LIKE ? OR date LIKE ? OR time LIKE ?)
        """
        cursor.execute(query, (user_data[0], f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        update_deals_table(cursor.fetchall())
    
    search_button = tk.Button(search_frame, text="Поиск", command=search_deals)
    search_button.pack(side='left', padx=5)
    
    # Таблица сделок
    columns = ("ID", "Кабинка", "Дата", "Время","Длительность", "Стоимость", "Статус")
    deals_table = ttk.Treeview(
        content_frame,
        columns=columns,
        show='headings'
    )
    
    for col in columns:
        deals_table.heading(col, text=col)
        deals_table.column(col, width=100, anchor='center')
    
    deals_table.pack(fill='both', expand=True, pady=10)
    
    # Фрейм для кнопок
    buttons_frame = tk.Frame(content_frame)
    buttons_frame.pack(fill='x', pady=10)
    
    def delete_deal():
        selected = deals_table.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите сделку для удаления")
            return
            
        deal_id = deals_table.item(selected[0])['values'][0]
        try:
            cursor.execute("DELETE FROM deals WHERE rowid = ? AND user_id = ?", (deal_id, user_data[0]))
            connection.commit()
            refresh_deals()
            messagebox.showinfo("Успех", "Сделка удалена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить сделку: {str(e)}")
    
    delete_button = tk.Button(buttons_frame, text="Удалить", command=delete_deal)
    delete_button.pack(side='left', padx=5)
    
    def create_deal():
        deal_window = tk.Toplevel(client_window)
        deal_window.title("Создание сделки")
        deal_window.geometry("400x350")
        
        tk.Label(deal_window, text="Кабинка:").pack(pady=5)
        cabine_var = tk.StringVar()
        cabine_combobox = ttk.Combobox(deal_window, textvariable=cabine_var, values=["1", "2", "3", "4", "5"])
        cabine_combobox.pack(pady=5)
        
        tk.Label(deal_window, text="Дата (ДД.ММ.ГГГГ):").pack(pady=5)
        date_entry = tk.Entry(deal_window)
        date_entry.pack(pady=5)
        
        tk.Label(deal_window, text="Время начала (ЧЧ:ММ):").pack(pady=5)
        time_entry = tk.Entry(deal_window)
        time_entry.pack(pady=5)
        
        tk.Label(deal_window, text="Длительность (часы):").pack(pady=5)
        duration_var = tk.StringVar()
        duration_combobox = ttk.Combobox(deal_window, textvariable=duration_var,values=["1 час (500 руб)", "2 часа (1000 руб)", "3 часа (1500 руб)"], state="readonly")
        duration_combobox.pack(pady=5)
        
        def save_deal():
            cabine = cabine_var.get()
            date = date_entry.get()
            time = time_entry.get()
            duration = duration_var.get()
            
            if not all([cabine, date, time, duration]):
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
                return
                
            # Проверка даты
            try:
                booking_date = datetime.strptime(date, "%d.%m.%Y").date()
                today = datetime.now().date()
                if booking_date < today:
                    messagebox.showerror("Ошибка", "Нельзя бронировать на прошедшую дату")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
                return
                
            # Проверка времени
            try:
                datetime.strptime(time, "%H:%M")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат времени. Используйте ЧЧ:ММ")
                return
                
            # Определяем продолжительность и стоимость
            if duration == "1 час (500 руб)":
                duration_hours = 1
                price = 500
            elif duration == "2 часа (1000 руб)":
                duration_hours = 2
                price = 1000
            else:
                duration_hours = 3
                price = 1500
                
            # Проверяем, свободна ли кабинка в это время
            start_time = datetime.strptime(time, "%H:%M")
            end_time = (start_time + timedelta(hours=duration_hours)).strftime("%H:%M")
            
            cursor.execute("""
                SELECT * FROM deals 
                WHERE cabine = ? AND date = ? AND (
                    (time <= ? AND time > ?) OR 
                    (time < ? AND time >= ?) OR 
                    (time >= ? AND time <= ?)
                )
            """, (cabine, date, time, end_time, time, end_time, time, end_time))
            
            if cursor.fetchone():
                messagebox.showerror("Ошибка", "Кабинка уже занята в это время")
                return
                
            try:
                # Добавляем сделку с полными данными клиента
                cursor.execute("""
                    INSERT INTO deals (
                        user_id, user_fam, user_name, user_otch, user_number,
                        cabine, date, time, duration, price, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data[0], user_data[1], user_data[2], user_data[3], user_data[4],
                    cabine, date, time, duration_hours, price, "в обработке"
                ))
                connection.commit()
                messagebox.showinfo("Успех", "Сделка создана")
                deal_window.destroy()
                refresh_deals()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать сделку: {str(e)}")
        
        button_frame = tk.Frame(deal_window)
        button_frame.pack(pady=10)
        
        save_button = tk.Button(button_frame, text="Создать", command=save_deal)
        save_button.pack(side='left', padx=5)
        
        cancel_button = tk.Button(button_frame, text="Отмена", command=deal_window.destroy)
        cancel_button.pack(side='left', padx=5)
    
    create_button = tk.Button(buttons_frame, text="Создать сделку", command=create_deal)
    create_button.pack(side='left', padx=5)
    
    exit_button = tk.Button(buttons_frame, text="Выход", command=on_closing)
    exit_button.pack(side='right')
    
    def refresh_deals():
        cursor.execute("""
            SELECT rowid, cabine, date, time, duration, price, status 
            FROM deals 
            WHERE user_id = ?
        """, (user_data[0],))
        update_deals_table(cursor.fetchall())
    
    def update_deals_table(deals):
        deals_table.delete(*deals_table.get_children())
        for deal in deals:
            deals_table.insert('', 'end', values=deal)
    
    # Первоначальная загрузка данных
    refresh_deals()

def show_manage_panel(user_data):
    global window_authoriz
    
    # Скрываем окно авторизации
    window_authoriz.withdraw()
    
    admin_window = tk.Toplevel()
    admin_window.title("Панель администратора")
    admin_window.geometry("370x220")
    
    def on_closing():
        window_authoriz.deiconify()
        admin_window.destroy()
    
    admin_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Основной контент
    content_frame = tk.Frame(admin_window, padx=20, pady=20)
    content_frame.pack(expand=True, fill='both')
    
    # Приветствие
    welcome_label = tk.Label(content_frame, text=f"Добро пожаловать, {user_data[1]} {user_data[0]}!", font=('Arial', 14))
    welcome_label.pack(pady=(0, 20))
    
    # Дата входа
    date_label = tk.Label(content_frame, text=f"Время входа: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    date_label.pack(pady=(0, 20))
    
    # Кнопки управления
    buttons_frame = tk.Frame(content_frame)
    buttons_frame.pack(fill='x', pady=2)
    
    # Кнопка отслеживания сделок
    deals_button = tk.Button(buttons_frame, text="Отслеживание сделок", width=25, height=2, command=lambda: show_admin_deals_panel(user_data))
    deals_button.pack(side='left', expand=True, padx=10)
    
    # Кнопка выхода
    bottom_frame = tk.Frame(content_frame)
    bottom_frame.pack(fill='x',side='bottom', pady=5)

    exit_button = tk.Button(bottom_frame, text="Выйти из учетной записи", command=on_closing)
    exit_button.pack(side='left')

def show_admin_deals_panel(user_data):
    deals_window = tk.Toplevel()
    deals_window.title("Управление сделками")
    deals_window.geometry("1200x600")
    
    def on_closing():
        deals_window.destroy()
    
    deals_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Основной контент
    content_frame = tk.Frame(deals_window, padx=20, pady=20)
    content_frame.pack(expand=True, fill='both')
    
    # Фрейм для поиска и фильтрации
    filter_frame = tk.Frame(content_frame)
    filter_frame.pack(fill='x', pady=10)
    
    tk.Label(filter_frame, text="Поиск сделки:").pack(side='left')
    search_entry = tk.Entry(filter_frame, width=30)
    search_entry.pack(side='left', padx=5)

    def search_deals():
        search_term = search_entry.get().strip()
        status_filter = status_var.get()
        
        query = """
        SELECT rowid, 
               user_id, 
               user_fam,
               user_name,
               user_otch,
               cabine, 
               date, 
               time, 
               duration,
               price, 
               status 
        FROM deals
        WHERE (user_id LIKE ? OR user_fam LIKE ? OR user_name LIKE ? OR user_otch LIKE ? 
               OR cabine LIKE ? OR date LIKE ? OR time LIKE ?)
        """
        
        params = [f"%{search_term}%"] * 7
        
        if status_filter != "все":
            query += " AND status = ?"
            params.append(status_filter)
            
        cursor.execute(query, params)
        deals = cursor.fetchall()
        update_deals_table(deals)
        
    search_button = tk.Button(filter_frame, text="Поиск", command=search_deals)
    search_button.pack(side='left', padx=5)

    tk.Label(filter_frame, text="Статус:").pack(side='left', padx=(10, 5))
    status_var = tk.StringVar(value="все")
    status_combobox = ttk.Combobox(filter_frame, textvariable=status_var,values=["все", "в обработке", "подтверждено", "отменено"], state="readonly")
    status_combobox.bind("<<ComboboxSelected>>", lambda e: search_deals())
    status_combobox.pack(side='left', padx=5)
    
    # Таблица сделок
    columns = ("ID", "Фамилия", "Имя", "Отчество", "Телефон", "Кабинка", "Дата", "Время", "Длительность", "Стоимость", "Статус")
    deals_table = ttk.Treeview(content_frame, columns=columns, show='headings')
    
    # Настройка ширины колонок
    deals_table.column("ID", width=50, anchor='center')
    deals_table.column("Фамилия", width=100, anchor='w')
    deals_table.column("Имя", width=100, anchor='w')
    deals_table.column("Отчество", width=100, anchor='w')
    deals_table.column("Телефон", width=120, anchor='w')
    deals_table.column("Кабинка", width=80, anchor='center')
    deals_table.column("Дата", width=100, anchor='center')
    deals_table.column("Время", width=80, anchor='center')
    deals_table.column("Длительность", width=80, anchor='center')
    deals_table.column("Стоимость", width=100, anchor='center')
    deals_table.column("Статус", width=120, anchor='center')
    
    for col in columns:
        deals_table.heading(col, text=col)
    
    scroll_y = ttk.Scrollbar(content_frame, orient='vertical', command=deals_table.yview)
    scroll_y.pack(side='right', fill='y')
    deals_table.configure(yscrollcommand=scroll_y.set)
    
    scroll_x = ttk.Scrollbar(content_frame, orient='horizontal', command=deals_table.xview)
    scroll_x.pack(side='bottom', fill='x')
    deals_table.configure(xscrollcommand=scroll_x.set)
    
    deals_table.pack(fill='both', expand=True, pady=10)
    
    # Фрейм для кнопок
    buttons_frame = tk.Frame(content_frame)
    buttons_frame.pack(fill='x', pady=10)
    
    def update_status():
        selected = deals_table.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите сделку")
            return
            
        deal_id = deals_table.item(selected[0])['values'][0]
        current_status = deals_table.item(selected[0])['values'][10]  
        
        status_window = tk.Toplevel(deals_window)
        status_window.title("Изменение статуса")
        status_window.geometry("300x150")
        
        tk.Label(status_window, text="Новый статус:").pack(pady=10)
        
        status_var = tk.StringVar(value=current_status)
        status_combobox = ttk.Combobox(status_window, textvariable=status_var, values=["в обработке", "подтверждено", "отменено"], state="readonly")
        status_combobox.pack(pady=5)
        
        def apply_status():
            new_status = status_var.get()
            try:
                cursor.execute("UPDATE deals SET status = ? WHERE rowid = ?", (new_status, deal_id))
                connection.commit()
                refresh_deals()
                messagebox.showinfo("Успех", "Статус обновлен")
                status_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить статус: {str(e)}")
        
        tk.Button(status_window, text="Применить", command=apply_status).pack(pady=10)
    
    def delete_deal():
        selected = deals_table.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите сделку для удаления")
            return
            
        deal_id = deals_table.item(selected[0])['values'][0]
        try:
            cursor.execute("DELETE FROM deals WHERE rowid = ?", (deal_id,))
            connection.commit()
            refresh_deals()
            messagebox.showinfo("Успех", "Сделка удалена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить сделку: {str(e)}")
    
    def create_report():
        items = deals_table.get_children()
        if not items:
            messagebox.showwarning("Ошибка", "Нет данных для отчета")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Сохранить отчет как"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as txtfile:
                # Получаем все данные из таблицы
                cursor.execute("""
                    SELECT user_id, user_name, user_fam, user_otch, 
                            cabine, date, time, duration, price, status
                    FROM deals
                    ORDER BY user_fam, user_name, user_otch
                """)
                deals = cursor.fetchall()
                
                current_client = None
                for deal in deals:
                    # Если сменился клиент, добавляем заголовок
                    client_key = (deal[0], deal[1], deal[2])
                    if client_key != current_client:
                        current_client = client_key
                        txtfile.write(f"\nКлиент: {deal[0]} {deal[1]} {deal[2]}\n")
                        txtfile.write(f"Телефон: {deal[3]}\n")
                        txtfile.write("-" * 50 + "\n")
                    
                    # Записываем данные о сделке
                    txtfile.write(
                        f"Кабинка: {deal[4]}, Дата: {deal[5]}, Время: {deal[6]}, "
                        f"Длительность: {deal[7]} час(а), Стоимость: {deal[8]} руб., "
                        f"Статус: {deal[9]}\n"
                    )
                
            messagebox.showinfo("Успех", f"Отчет сохранен в {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчет: {str(e)}")
    
    status_button = tk.Button(buttons_frame, text="Изменить статус", command=update_status)
    status_button.pack(side='left', padx=5)
    
    delete_button = tk.Button(buttons_frame, text="Удалить сделку", command=delete_deal)
    delete_button.pack(side='left', padx=5)
    
    report_button = tk.Button(buttons_frame, text="Создать отчет", command=create_report)
    report_button.pack(side='left', padx=5)
    
    exit_button = tk.Button(buttons_frame, text="Закрыть", command=on_closing)
    exit_button.pack(side='right')
    
    def refresh_deals():
        cursor.execute("""
            SELECT rowid, 
                   user_id, 
                   user_fam,
                   user_name,
                   user_otch,
                   cabine,                        
                   date, 
                   time, 
                   duration,
                   price, 
                   status 
            FROM deals
        """)
        deals = cursor.fetchall()
        update_deals_table(deals)
    
    def update_deals_table(deals):
        deals_table.delete(*deals_table.get_children())
        for deal in deals:
            # Форматируем длительность для отображения
            duration = f"{deal[8]} час." if deal[8] == 1 else f"{deal[8]} час."
            formatted_deal = deal[:8] + (duration,) + deal[9:]
            deals_table.insert('', 'end', values=formatted_deal)

    refresh_deals()

def show_admin_panel(user_data):
    global window_authoriz
    
    # Скрываем окно авторизации
    window_authoriz.withdraw()
    
    admin_window = tk.Toplevel()
    admin_window.title("Панель администратора")
    admin_window.geometry("370x220")
    
    def on_closing():
        window_authoriz.deiconify()
        admin_window.destroy()
    
    admin_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Основной контент
    content_frame = tk.Frame(admin_window, padx=20, pady=20)
    content_frame.pack(expand=True, fill='both')
    
    # Приветствие
    welcome_label = tk.Label(content_frame, text=f"Добро пожаловать, {user_data[1]} {user_data[0]}!", font=('Arial', 14))
    welcome_label.pack(pady=(0, 20))
    
    # Дата входа
    date_label = tk.Label(content_frame, text=f"Время входа: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    date_label.pack(pady=(0, 20))
    
    # Кнопки управления
    buttons_frame = tk.Frame(content_frame)
    buttons_frame.pack(fill='x', pady=2)
    
    # Кнопка управления пользователями
    users_button = tk.Button(buttons_frame,text="Управление пользователями", width=25,height=2,command=lambda: manage_users(admin_window))
    users_button.pack(side='left', expand=True)
    
    # Кнопка отслеживания сделок
    deals_button = tk.Button(buttons_frame, text="Отслеживание сделок", width=25, height=2, command=lambda: show_admin_deals_panel(user_data))
    deals_button.pack(side='left', expand=True, padx=10)
    
    # Кнопка выхода
    bottom_frame = tk.Frame(content_frame)
    bottom_frame.pack(fill='x',side='bottom', pady=5)

    exit_button = tk.Button(bottom_frame, text="Выйти из учетной записи", command=on_closing)
    exit_button.pack(side='left')

def manage_users(parent_window):
    """Форма управления пользователями"""
    users_window = tk.Toplevel(parent_window)
    users_window.title("Управление пользователями")
    users_window.geometry("900x500")
    
    # Фрейм для поиска
    search_frame = tk.Frame(users_window, padx=10, pady=10)
    search_frame.pack(fill='x')
    
    tk.Label(search_frame, text="Поиск пользователя:").pack(side='left')
    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side='left', padx=5)
    
    # Вертикальный скроллбар
    scroll_y = ttk.Scrollbar(users_window, orient='vertical')
    scroll_y.pack(side='right', fill='y')
    
    # Горизонтальный скроллбар
    scroll_x = ttk.Scrollbar(users_window, orient='horizontal')
    scroll_x.pack(side='bottom', fill='x')
    
    # Таблица пользователей
    columns = ("ID", "Фамилия", "Имя", "Отчество", "Телефон", "Логин","Пароль", "Роль", "Статус")
    users_table = ttk.Treeview(users_window, columns=columns, show='headings', yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    
    # Настройка столбцов
    users_table.column("ID", width=50, anchor='center')
    users_table.column("Фамилия", width=120, anchor='w')
    users_table.column("Имя", width=120, anchor='w')
    users_table.column("Отчество", width=120, anchor='w')
    users_table.column("Телефон", width=120, anchor='w')
    users_table.column("Логин", width=120, anchor='w')
    users_table.column("Пароль", width=120, anchor='w')
    users_table.column("Роль", width=100, anchor='center')
    users_table.column("Статус", width=100, anchor='center')
    
    for col in columns:
        users_table.heading(col, text=col)
    
    users_table.pack(fill='both', expand=True, padx=10, pady=5)
    
    scroll_y.config(command=users_table.yview)
    scroll_x.config(command=users_table.xview)
    
    def refresh_users():
        cursor.execute("""
            SELECT rowid, fam, name, otch, number, login, password, role, 
                   COALESCE(status, 'активен') as status 
            FROM user
        """)
        update_users_table(cursor.fetchall())
    
    def update_users_table(users):
        users_table.delete(*users_table.get_children())
        for user in users:
            users_table.insert('', 'end', values=user)
    
    def search_users():
        search_term = search_entry.get().strip()
        if not search_term:
            refresh_users()
            return
            
        query = """
        SELECT rowid, fam, name, otch, number, login, password, role, 
               COALESCE(status, 'активен') as status 
        FROM user 
        WHERE fam LIKE ? OR name LIKE ? OR login LIKE ? OR number LIKE ?
        """
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        users = cursor.fetchall()
        
        update_users_table(users)
        
        if len(users) == 1:
            users_table.selection_set(users_table.get_children()[0])
            users_table.focus(users_table.get_children()[0])
    
    search_button = tk.Button(search_frame, text="Найти", command=search_users)
    search_button.pack(side='left', padx=5)
    
    # Фрейм для кнопок управления
    control_frame = tk.Frame(users_window, padx=10, pady=10)
    control_frame.pack(fill='x')
    
    def update_role():
        selected = users_table.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пользователя")
            return
            
        user_id = users_table.item(selected[0])['values'][0]
        current_role = users_table.item(selected[0])['values'][7]

        login = username_entry.get()
        if login == users_table.item(selected[0])['values'][5]:
            messagebox.showwarning("Ошибка", "Вы не можете изменить свою роль!")
            return
        
        # Создаем окно для выбора роли
        role_window = tk.Toplevel(users_window)
        role_window.title("Изменение роли")
        role_window.geometry("300x150")
        
        tk.Label(role_window, text="Выберите новую роль:").pack(pady=10)
        
        # Выпадающий список с ролями
        role_var = tk.StringVar(value=current_role)
        roles = ["администратор", "бухгалтер", "клиент"]
        role_combobox = ttk.Combobox(role_window, textvariable=role_var, values=roles, state="readonly")
        role_combobox.pack(pady=5)
        
        def apply_role():
            new_role = role_var.get()
            try:
                cursor.execute("UPDATE user SET role = ? WHERE rowid = ?", (new_role, user_id))
                connection.commit()
                refresh_users()
                messagebox.showinfo("Успех", "Роль пользователя изменена")
                role_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить роль: {str(e)}")
        
        tk.Button(role_window, text="Применить", command=apply_role).pack(pady=10)
    
    role_button = tk.Button(control_frame, text="Изменить роль", command=update_role)
    role_button.pack(side='left', padx=5)
    
    def toggle_block():
        selected = users_table.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пользователя")
            return
            
        user_id = users_table.item(selected[0])['values'][0]
        current_status = users_table.item(selected[0])['values'][8]  # Индекс статуса был неверным (было 7, должно быть 8)
        
        # Получаем логин текущего пользователя (не из поля ввода, а из глобальной переменной)
        current_login = current_user[5] if current_user else None
        selected_login = users_table.item(selected[0])['values'][5]
        
        if current_login == selected_login:
            messagebox.showwarning("Ошибка", "Вы не можете заблокировать себя!")
            return
        
        new_status = "заблокирован" if current_status == "активен" else "активен"
        
        try:
            cursor.execute("UPDATE user SET status = ? WHERE rowid = ?", (new_status, user_id))
            connection.commit()
            refresh_users()
            status_msg = "заблокирован" if new_status == "заблокирован" else "разблокирован"
            messagebox.showinfo("Успех", f"Пользователь {status_msg}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить статус: {str(e)}")
    
    block_button = tk.Button(control_frame, text="Блокировка", command=toggle_block)
    block_button.pack(side='left', padx=5)

    def on_closing():
        users_window.destroy()

    exit_button = tk.Button(control_frame, text="Закрыть", command=on_closing)
    exit_button.pack(side='right')
    
    # Первоначальная загрузка данных
    refresh_users()

def entrance():
    global current_user
    
    login = username_entry.get()
    password = password_entry.get()
    
    if not login or not password:
        messagebox.showerror("Ошибка", "Введите логин и пароль")
        return
    
    cursor.execute('''
        SELECT * FROM user WHERE login = ? AND password = ? AND status != 'заблокирован'
    ''', (login, password))
    
    user_data = cursor.fetchone()
    
    if user_data:
        current_user = user_data
        if user_data[6] == "администратор":
            show_admin_panel(user_data)
        elif user_data[6] == "бухгалтер":
            show_manage_panel(user_data)
        else:
            show_client_panel(user_data)
    else:
        # Проверяем, был ли пользователь заблокирован
        cursor.execute('''
            SELECT * FROM user WHERE login = ? AND password = ? AND status = 'заблокирован'
        ''', (login, password))
        if cursor.fetchone():
            messagebox.showerror("Ошибка", "Ваш аккаунт заблокирован!")
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

# Основное окно авторизации
connection = sqlite3.connect('studio.db')
cursor = connection.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        fam TEXT NOT NULL,
        name TEXT NOT NULL,
        otch TEXT NOT NULL,
        number TEXT NOT NULL,
        login TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        status TEXT NOT NULL
    )
''')
connection.commit()

connection = sqlite3.connect('studio.db')
cursor = connection.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS deals (
        user_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        user_fam TEXT NOT NULL,
        user_otch TEXT NOT NULL,
        user_number TEXT NOT NULL,
        cabine TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        duration INTEGER NOT NULL,
        price REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES user(rowid)
    )
''')
connection.commit()

window_authoriz = tk.Tk()
window_authoriz.title("Вход в учетную запись")
window_authoriz.geometry("450x250")

content_frame = tk.Frame(window_authoriz, padx=20, pady=20)
content_frame.pack(expand=True, fill='both')

tk.Label(content_frame, text="Вход в учетную запись", font=('Arial', 14)).pack(pady=(0, 20))

tk.Label(content_frame, text="Логин", anchor='w').pack(fill='x')
username_entry = tk.Entry(content_frame)
username_entry.pack(fill='x', pady=(0, 10))

tk.Label(content_frame, text="Пароль", anchor='w').pack(fill='x')
password_entry = tk.Entry(content_frame)
password_entry.pack(fill='x', pady=(0, 20))

button_frame = tk.Frame(content_frame)
button_frame.pack(fill='x')

login_button = tk.Button(button_frame, text="Войти",command=entrance)
login_button.pack(side='left', expand=True, fill='x', padx=(0, 5))

register_button = tk.Button(button_frame, text="Зарегистрироваться", command=registrations)
register_button.pack(side='left', expand=True, fill='x', padx=(5, 0))

window_authoriz.mainloop()
connection.close()