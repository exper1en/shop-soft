import tkinter as tk
from database import Database
from models import User
from gui.colors import COLORS
from gui.admin_auth_window import AdminAuthWindow

class LoginWindow:
    def __init__(self):
        self.db = Database()
        self.window = tk.Tk()
        self.window.title("Вход в систему - Магазин")
        self.window.geometry("350x300")
        self.window.configure(bg=COLORS['bg'])
        self.window.resizable(False, False)

        header = tk.Frame(self.window, bg=COLORS['header_bg'], height=40)
        header.pack(fill=tk.X)
        tk.Label(header, text="Добро пожаловать", bg=COLORS['header_bg'], fg=COLORS['header_fg'],
                 font=('Arial', 14, 'bold')).pack(pady=10)

        frame = tk.Frame(self.window, bg=COLORS['bg'], padx=20, pady=20)
        frame.pack(expand=True)

        btn_admin = tk.Button(frame, text="Войти как Администратор", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                              font=('Arial', 11, 'bold'), padx=20, pady=10, bd=0, cursor='hand2',
                              command=self.login_as_admin)
        btn_admin.pack(pady=10)

        # Кнопка для выбора покупателя
        btn_customer = tk.Button(frame, text="Войти как Покупатель", bg=COLORS['accent'], fg=COLORS['label_fg'],
                                 font=('Arial', 11, 'bold'), padx=20, pady=10, bd=0, cursor='hand2',
                                 command=self.show_customer_selection)
        btn_customer.pack(pady=10)

        self.window.mainloop()

    def login_as_admin(self):
        AdminAuthWindow(self.window)

    def show_customer_selection(self):
        # Получаем список всех покупателей
        conn = self.db._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE role='customer' ORDER BY username")
        customers = cursor.fetchall()
        conn.close()

        if not customers:
            messagebox.showerror("Ошибка", "Нет зарегистрированных покупателей")
            return

        # Окно выбора
        select_win = tk.Toplevel(self.window)
        select_win.title("Выбор покупателя")
        select_win.geometry("300x250")
        select_win.configure(bg=COLORS['bg'])
        select_win.grab_set()

        tk.Label(select_win, text="Выберите покупателя", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 12, 'bold')).pack(pady=10)

        listbox = tk.Listbox(select_win, bg=COLORS['tree_bg'], fg=COLORS['tree_fg'],
                             selectbackground=COLORS['tree_selected'])
        for cust_id, username in customers:
            listbox.insert(tk.END, username)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        def select():
            selection = listbox.curselection()
            if not selection:
                return
            idx = selection[0]
            cust_id, username = customers[idx]
            user = User(cust_id, username, 'customer')
            select_win.destroy()
            self.window.destroy()
            from gui.customer_window import CustomerWindow
            CustomerWindow(user)

        tk.Button(select_win, text="Войти", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=20, command=select).pack(pady=10)