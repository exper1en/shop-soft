import tkinter as tk
from tkinter import messagebox
from database import Database
from models import User
from gui.colors import COLORS

class AdminAuthWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.window = tk.Toplevel(parent)
        self.window.title("Авторизация администратора")
        self.window.geometry("350x180")
        self.window.configure(bg=COLORS['bg'])
        self.window.resizable(False, False)
        self.window.grab_set()

        tk.Label(self.window, text="Введите пароль администратора", bg=COLORS['bg'],
                 fg=COLORS['label_fg'], font=('Arial', 11)).pack(pady=10)

        self.entry_password = tk.Entry(self.window, show="*", font=('Arial', 10), bd=2, relief=tk.GROOVE)
        self.entry_password.pack(pady=5)
        self.entry_password.focus()

        hint = tk.Label(self.window, text="Подсказка: 123", bg=COLORS['bg'],
                        fg='gray', font=('Arial', 9))
        hint.pack()

        btn_login = tk.Button(self.window, text="Войти", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                              font=('Arial', 10, 'bold'), padx=20, pady=5, bd=0, cursor='hand2',
                              command=self.login)
        btn_login.pack(pady=10)

        self.entry_password.bind('<Return>', lambda e: self.login())

    def login(self):
        password = self.entry_password.get()
        if not password:
            messagebox.showwarning("Предупреждение", "Введите пароль")
            return
        user_data = self.db.get_admin_by_password(password)
        if user_data:
            user = User(*user_data)
            self.window.destroy()
            self.parent.destroy()
            from gui.manager_window import ManagerWindow
            ManagerWindow(user)
        else:
            messagebox.showerror("Ошибка", "Неверный пароль")