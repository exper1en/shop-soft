import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import Database
from models import User
from gui.colors import COLORS

class ManagerWindow:
    def __init__(self, user):
        self.user = user
        self.db = Database()
        self.window = tk.Tk()
        self.window.title(f"Администратор: {user.username} - Управление магазином")
        self.window.geometry("1100x600")
        self.window.configure(bg=COLORS['bg'])

        top_frame = tk.Frame(self.window, bg=COLORS['header_bg'], height=40)
        top_frame.pack(fill=tk.X)
        tk.Label(top_frame, text=f"Администратор: {user.username}", bg=COLORS['header_bg'],
                 fg=COLORS['header_fg'], font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(top_frame, text="Выход", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.logout).pack(side=tk.RIGHT, padx=20, pady=5)

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_products = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_products, text="Товары")
        self.setup_products_tab()

        self.tab_news = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_news, text="Новости")
        self.setup_news_tab()

        self.tab_reviews = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reviews, text="Отзывы")
        self.setup_reviews_tab()

        self.tab_orders = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_orders, text="Заказы")
        self.setup_orders_tab()

        # Новая вкладка "Чаты"
        self.tab_chats = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_chats, text="Чаты")
        self.setup_chats_tab()

        self.window.mainloop()

    def logout(self):
        self.window.destroy()
        from gui.login_window import LoginWindow
        LoginWindow()

    # ----- Вкладка "Товары" -----
    def setup_products_tab(self):
        left_frame = tk.Frame(self.tab_products, bg=COLORS['bg'], width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Label(left_frame, text="Категории", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)

        self.cat_listbox = tk.Listbox(left_frame, bg=COLORS['tree_bg'], fg=COLORS['tree_fg'],
                                      selectbackground=COLORS['tree_selected'], bd=2, relief=tk.GROOVE,
                                      font=('Arial', 10), height=15)
        self.cat_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.cat_listbox.bind('<<ListboxSelect>>', self.on_category_select)

        btn_frame_cat = tk.Frame(left_frame, bg=COLORS['bg'])
        btn_frame_cat.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame_cat, text="Добавить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=10, command=self.add_category).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame_cat, text="Изменить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=10, command=self.edit_category).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame_cat, text="Удалить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=10, command=self.delete_category).pack(side=tk.LEFT, padx=2)

        right_frame = tk.Frame(self.tab_products, bg=COLORS['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        header_frame = tk.Frame(right_frame, bg=COLORS['bg'])
        header_frame.pack(fill=tk.X, pady=5)

        tk.Label(header_frame, text="Список товаров", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT)

        btn_frame_prod = tk.Frame(header_frame, bg=COLORS['bg'])
        btn_frame_prod.pack(side=tk.RIGHT)

        tk.Button(btn_frame_prod, text="Добавить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.add_product).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame_prod, text="Изменить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.edit_product).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame_prod, text="Удалить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.delete_product).pack(side=tk.LEFT, padx=2)

        columns = ('ID', 'Название', 'Цена', 'Количество', 'Категория', 'Описание')
        self.tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=20)

        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=40, anchor='center')
            elif col == 'Название':
                self.tree.column(col, width=200)
            elif col == 'Цена':
                self.tree.column(col, width=70, anchor='e')
            elif col == 'Количество':
                self.tree.column(col, width=80, anchor='e')
            elif col == 'Категория':
                self.tree.column(col, width=120)
            else:
                self.tree.column(col, width=250)

        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.load_categories()
        self.load_products()

    def load_categories(self):
        self.cat_listbox.delete(0, tk.END)
        self.categories = self.db.get_all_categories()
        self.cat_listbox.insert(0, "Все категории")
        for cat_id, name in self.categories:
            self.cat_listbox.insert(tk.END, f"{name}")
        self.cat_listbox.select_set(0)

    def on_category_select(self, event):
        selection = self.cat_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx == 0:
                self.load_products()
            else:
                cat_id = self.categories[idx-1][0]
                self.load_products(cat_id)

    def load_products(self, category_id=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        products = self.db.get_products_by_category(category_id)
        for prod in products:
            self.tree.insert('', tk.END, values=prod)

    def add_category(self):
        name = simpledialog.askstring("Новая категория", "Введите название категории:", parent=self.window)
        if name and name.strip():
            self.db.add_category(name.strip())
            self.load_categories()

    def edit_category(self):
        selection = self.cat_listbox.curselection()
        if not selection or selection[0] == 0:
            messagebox.showinfo("Инфо", "Выберите категорию для редактирования")
            return
        idx = selection[0] - 1
        cat_id, old_name = self.categories[idx]
        new_name = simpledialog.askstring("Изменить категорию", "Новое название:", initialvalue=old_name, parent=self.window)
        if new_name and new_name.strip() and new_name != old_name:
            self.db.update_category(cat_id, new_name.strip())
            self.load_categories()

    def delete_category(self):
        selection = self.cat_listbox.curselection()
        if not selection or selection[0] == 0:
            messagebox.showinfo("Инфо", "Выберите категорию для удаления")
            return
        idx = selection[0] - 1
        cat_id, name = self.categories[idx]
        confirm = messagebox.askyesno("Подтверждение", f"Удалить категорию '{name}'? Это возможно только если в ней нет товаров.")
        if confirm:
            success = self.db.delete_category(cat_id)
            if success:
                self.load_categories()
            else:
                messagebox.showerror("Ошибка", "Нельзя удалить категорию, в которой есть товары. Сначала удалите или переместите товары.")

    def add_product(self):
        cats = self.db.get_all_categories()
        if not cats:
            messagebox.showwarning("Предупреждение", "Сначала создайте хотя бы одну категорию.")
            return
        self._edit_product_dialog(None, cats)

    def edit_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Инфо", "Выберите товар для редактирования")
            return
        item = self.tree.item(selected[0])
        prod_id = item['values'][0]
        product = self.db.get_product_by_id(prod_id)
        if product:
            cats = self.db.get_all_categories()
            self._edit_product_dialog(product, cats)

    def _edit_product_dialog(self, product, categories):
        dialog = tk.Toplevel(self.window)
        dialog.title("Редактирование товара" if product else "Новый товар")
        dialog.geometry("400x350")
        dialog.configure(bg=COLORS['bg'])
        dialog.resizable(False, False)
        dialog.grab_set()

        fields = {}
        tk.Label(dialog, text="Название:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(pady=5)
        fields['name'] = tk.Entry(dialog, width=40)
        fields['name'].pack(pady=5)

        tk.Label(dialog, text="Цена:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(pady=5)
        fields['price'] = tk.Entry(dialog, width=40)
        fields['price'].pack(pady=5)

        tk.Label(dialog, text="Количество:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(pady=5)
        fields['quantity'] = tk.Entry(dialog, width=40)
        fields['quantity'].pack(pady=5)

        tk.Label(dialog, text="Категория:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(pady=5)
        fields['category'] = ttk.Combobox(dialog, values=[c[1] for c in categories], state='readonly', width=37)
        fields['category'].pack(pady=5)

        tk.Label(dialog, text="Описание:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(pady=5)
        fields['description'] = tk.Entry(dialog, width=40)
        fields['description'].pack(pady=5)

        if product:
            fields['name'].insert(0, product[1])
            fields['price'].insert(0, product[2])
            fields['quantity'].insert(0, product[3])
            fields['description'].insert(0, product[4] if product[4] else '')
            for idx, (cid, cname) in enumerate(categories):
                if cid == product[5]:
                    fields['category'].current(idx)
                    break

        def save():
            name = fields['name'].get().strip()
            price_str = fields['price'].get().strip()
            qty_str = fields['quantity'].get().strip()
            cat_name = fields['category'].get()
            desc = fields['description'].get().strip()

            if not name or not price_str or not qty_str or not cat_name:
                messagebox.showwarning("Предупреждение", "Заполните все поля (кроме описания)")
                return

            try:
                price = float(price_str)
                qty = int(qty_str)
                if price <= 0 or qty < 0:
                    raise ValueError
            except:
                messagebox.showerror("Ошибка", "Цена должна быть положительным числом, количество — целым неотрицательным")
                return

            cat_id = None
            for cid, cname in categories:
                if cname == cat_name:
                    cat_id = cid
                    break

            if product:
                self.db.update_product(product[0], name, price, qty, cat_id, desc)
            else:
                self.db.add_product(name, price, qty, cat_id, desc)

            dialog.destroy()
            selection = self.cat_listbox.curselection()
            if selection and selection[0] == 0:
                self.load_products()
            elif selection:
                idx = selection[0] - 1
                cat_id_sel = self.categories[idx][0]
                self.load_products(cat_id_sel)

        tk.Button(dialog, text="Сохранить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=20, command=save).pack(pady=15)

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Инфо", "Выберите товар для удаления")
            return
        item = self.tree.item(selected[0])
        prod_id = item['values'][0]
        prod_name = item['values'][1]
        confirm = messagebox.askyesno("Подтверждение", f"Удалить товар '{prod_name}'?")
        if confirm:
            self.db.delete_product(prod_id)
            selection = self.cat_listbox.curselection()
            if selection and selection[0] == 0:
                self.load_products()
            elif selection:
                idx = selection[0] - 1
                cat_id = self.categories[idx][0]
                self.load_products(cat_id)

    # ----- Вкладка "Новости" -----
    def setup_news_tab(self):
        frame = tk.Frame(self.tab_news, bg=COLORS['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Новости магазина", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 14, 'bold')).pack(pady=10)

        self.news_text = tk.Text(frame, height=5, width=80, font=('Arial', 11))
        self.news_text.pack(pady=10)

        btn_publish = tk.Button(frame, text="Опубликовать новость", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                                font=('Arial', 11), padx=20, command=self.publish_news)
        btn_publish.pack(pady=5)

        list_frame = tk.Frame(frame, bg=COLORS['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Label(list_frame, text="Список новостей:", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 12)).pack(anchor=tk.W)

        columns = ('ID', 'Дата', 'Новость', 'Лайки', 'Дизлайки')
        self.news_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.news_tree.heading('ID', text='ID')
        self.news_tree.heading('Дата', text='Дата')
        self.news_tree.heading('Новость', text='Новость')
        self.news_tree.heading('Лайки', text='Лайки')
        self.news_tree.heading('Дизлайки', text='Дизлайки')

        self.news_tree.column('ID', width=40)
        self.news_tree.column('Дата', width=80)
        self.news_tree.column('Новость', width=400)
        self.news_tree.column('Лайки', width=60, anchor='center')
        self.news_tree.column('Дизлайки', width=60, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.news_tree.yview)
        self.news_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.news_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = tk.Frame(list_frame, bg=COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Удалить выбранную новость", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.delete_selected_news).pack(side=tk.LEFT, padx=5)

        self.load_news_list()

    def load_news_list(self):
        for row in self.news_tree.get_children():
            self.news_tree.delete(row)
        news_list = self.db.get_all_news()
        for news_id, message, created_at in news_list:
            counts = self.db.get_news_vote_counts(news_id)
            self.news_tree.insert('', tk.END, values=(news_id, created_at[:10], message[:50], counts['like'], counts['dislike']))

    def delete_selected_news(self):
        selected = self.news_tree.selection()
        if not selected:
            messagebox.showinfo("Инфо", "Выберите новость для удаления")
            return
        item = self.news_tree.item(selected[0])
        news_id = item['values'][0]
        confirm = messagebox.askyesno("Подтверждение", f"Удалить новость? Это действие нельзя отменить.")
        if confirm:
            self.db.delete_news(news_id)
            self.load_news_list()

    def publish_news(self):
        message = self.news_text.get('1.0', tk.END).strip()
        if not message:
            messagebox.showwarning("Предупреждение", "Введите текст новости")
            return
        self.db.add_news(message)
        self.news_text.delete('1.0', tk.END)
        self.load_news_list()
        messagebox.showinfo("Успех", "Новость опубликована")

    # ----- Вкладка "Отзывы" -----
    def setup_reviews_tab(self):
        frame = tk.Frame(self.tab_reviews, bg=COLORS['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID', 'Товар', 'Пользователь', 'Оценка', 'Комментарий', 'Лайки', 'Дизлайки', 'Ответ', 'Дата')
        self.reviews_tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)

        for col in columns:
            self.reviews_tree.heading(col, text=col)
            if col == 'ID':
                self.reviews_tree.column(col, width=40)
            elif col == 'Товар':
                self.reviews_tree.column(col, width=200)
            elif col == 'Пользователь':
                self.reviews_tree.column(col, width=100)
            elif col == 'Оценка':
                self.reviews_tree.column(col, width=60, anchor='center')
            elif col == 'Комментарий':
                self.reviews_tree.column(col, width=250)
            elif col == 'Лайки':
                self.reviews_tree.column(col, width=60, anchor='center')
            elif col == 'Дизлайки':
                self.reviews_tree.column(col, width=60, anchor='center')
            elif col == 'Ответ':
                self.reviews_tree.column(col, width=200)
            else:
                self.reviews_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.reviews_tree.yview)
        self.reviews_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.reviews_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = tk.Frame(frame, bg=COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Ответить на отзыв", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=20, command=self.respond_to_review).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=20, command=self.load_reviews).pack(side=tk.LEFT, padx=5)

        self.load_reviews()

    def load_reviews(self):
        for row in self.reviews_tree.get_children():
            self.reviews_tree.delete(row)
        reviews = self.db.get_all_reviews()
        if not reviews:
            self.reviews_tree.insert('', tk.END, values=('', 'Скоро здесь появятся отзывы', '', '', '', '', '', '', ''))
            return
        for rev in reviews:
            rev_id, rating, comment, img_path, manager_resp, created_at, product_name, username = rev
            username = username if username else "Аноним"
            manager_resp = manager_resp if manager_resp else ""
            counts = self.db.get_review_vote_counts(rev_id)
            self.reviews_tree.insert('', tk.END, values=(rev_id, product_name, username, rating, comment,
                                                          counts['like'], counts['dislike'], manager_resp, created_at[:10]))

    def respond_to_review(self):
        selected = self.reviews_tree.selection()
        if not selected:
            messagebox.showinfo("Инфо", "Выберите отзыв")
            return
        item = self.reviews_tree.item(selected[0])
        rev_id = item['values'][0]
        current_response = item['values'][7]

        dialog = tk.Toplevel(self.window)
        dialog.title("Ответ на отзыв")
        dialog.geometry("400x200")
        dialog.configure(bg=COLORS['bg'])
        dialog.grab_set()

        tk.Label(dialog, text="Ваш ответ:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(pady=5)
        text_widget = tk.Text(dialog, height=5, width=50)
        text_widget.pack(pady=5)
        if current_response:
            text_widget.insert('1.0', current_response)

        def save():
            response = text_widget.get('1.0', tk.END).strip()
            self.db.add_manager_response(rev_id, response)
            dialog.destroy()
            self.load_reviews()
            messagebox.showinfo("Успех", "Ответ сохранён")

        tk.Button(dialog, text="Сохранить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=20, command=save).pack(pady=5)

    # ----- Вкладка "Заказы" -----
    def setup_orders_tab(self):
        frame = tk.Frame(self.tab_orders, bg=COLORS['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID заказа', 'Покупатель', 'Дата', 'Сумма', 'Статус', 'Товары')
        self.orders_tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)

        self.orders_tree.heading('ID заказа', text='ID заказа')
        self.orders_tree.heading('Покупатель', text='Покупатель')
        self.orders_tree.heading('Дата', text='Дата')
        self.orders_tree.heading('Сумма', text='Сумма')
        self.orders_tree.heading('Статус', text='Статус')
        self.orders_tree.heading('Товары', text='Товары')

        self.orders_tree.column('ID заказа', width=80)
        self.orders_tree.column('Покупатель', width=150)
        self.orders_tree.column('Дата', width=100)
        self.orders_tree.column('Сумма', width=80, anchor='e')
        self.orders_tree.column('Статус', width=100)
        self.orders_tree.column('Товары', width=400)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(frame, bg=COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Изменить статус", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.change_order_status).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.load_orders).pack(side=tk.LEFT, padx=5)

        self.load_orders()

    def load_orders(self):
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)
        orders = self.db.get_all_orders_with_details()
        for order in orders:
            order_id, user_name, date, total, status, products = order
            self.orders_tree.insert('', tk.END, values=(order_id, user_name, date[:10], f"{total:.2f} руб.", status, products))

    def change_order_status(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showinfo("Инфо", "Выберите заказ")
            return
        item = self.orders_tree.item(selected[0])
        order_id = item['values'][0]
        current_status = item['values'][4]

        dialog = tk.Toplevel(self.window)
        dialog.title("Изменить статус")
        dialog.geometry("300x150")
        dialog.configure(bg=COLORS['bg'])
        dialog.grab_set()

        tk.Label(dialog, text="Выберите новый статус:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(pady=10)

        status_var = tk.StringVar(value=current_status)
        status_combo = ttk.Combobox(dialog, textvariable=status_var,
                                     values=['новый', 'сборка', 'доставка', 'выполнен', 'отменён'],
                                     state='readonly', width=20)
        status_combo.pack(pady=5)

        def save():
            new_status = status_var.get()
            if new_status != current_status:
                self.db.update_order_status(order_id, new_status)
                self.load_orders()
            dialog.destroy()

        tk.Button(dialog, text="Сохранить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=20, command=save).pack(pady=10)

    # ----- Новая вкладка "Чаты" -----
    def setup_chats_tab(self):
        main_frame = tk.Frame(self.tab_chats, bg=COLORS['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель: список покупателей
        left_frame = tk.Frame(main_frame, bg=COLORS['bg'], width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Label(left_frame, text="Покупатели", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)

        self.chat_users_listbox = tk.Listbox(left_frame, bg=COLORS['tree_bg'], fg=COLORS['tree_fg'],
                                             selectbackground=COLORS['tree_selected'], bd=2, relief=tk.GROOVE,
                                             font=('Arial', 10), height=20)
        self.chat_users_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.chat_users_listbox.bind('<<ListboxSelect>>', self.on_chat_user_select)

        # Правая панель: чат
        right_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.chat_title = tk.Label(right_frame, text="Выберите покупателя", bg=COLORS['bg'], fg=COLORS['label_fg'],
                                   font=('Arial', 12, 'bold'))
        self.chat_title.pack(anchor=tk.W, pady=5)

        chat_frame = tk.Frame(right_frame, bg='white', relief=tk.SUNKEN, bd=1)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.chat_display = tk.Text(chat_frame, bg='white', fg='black', font=('Arial', 10),
                                    wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_chat = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=scroll_chat.set)
        scroll_chat.pack(side=tk.RIGHT, fill=tk.Y)

        input_frame = tk.Frame(right_frame, bg=COLORS['bg'])
        input_frame.pack(fill=tk.X, pady=5)

        self.chat_entry = tk.Entry(input_frame, width=80)
        self.chat_entry.pack(side=tk.LEFT, padx=5)
        self.chat_entry.bind('<Return>', lambda e: self.send_manager_response())

        tk.Button(input_frame, text="Отправить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.send_manager_response).pack(side=tk.LEFT, padx=5)

        self.current_chat_user_id = None
        self.load_chat_users()

    def load_chat_users(self):
        self.chat_users_listbox.delete(0, tk.END)
        users = self.db.get_chat_users()
        self.chat_users = users
        for user_id, username, last_msg, last_time in users:
            display = f"{username} - {last_msg[:30]}..." if last_msg else username
            self.chat_users_listbox.insert(tk.END, display)
        if users:
            self.chat_users_listbox.select_set(0)
            self.on_chat_user_select()

    def on_chat_user_select(self, event=None):
        selection = self.chat_users_listbox.curselection()
        if not selection:
            self.current_chat_user_id = None
            self.chat_title.config(text="Выберите покупателя")
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete('1.0', tk.END)
            self.chat_display.config(state=tk.DISABLED)
            return
        idx = selection[0]
        self.current_chat_user_id = self.chat_users[idx][0]
        username = self.chat_users[idx][1]
        self.chat_title.config(text=f"Чат с {username}")
        self.load_chat_messages_for_user()

    def load_chat_messages_for_user(self):
        if not self.current_chat_user_id:
            return
        messages = self.db.get_chat_messages_for_user(self.current_chat_user_id)
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete('1.0', tk.END)
        for msg_id, msg, is_from_manager, created_at in messages:
            time_str = created_at[11:16] if len(created_at) > 10 else created_at
            if is_from_manager:
                self.chat_display.insert(tk.END, f"Менеджер [{time_str}]: {msg}\n", 'manager')
            else:
                self.chat_display.insert(tk.END, f"Покупатель [{time_str}]: {msg}\n", 'user')
        self.chat_display.tag_config('manager', foreground='blue')
        self.chat_display.tag_config('user', foreground='green')
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_manager_response(self):
        if not self.current_chat_user_id:
            messagebox.showinfo("Инфо", "Выберите покупателя")
            return
        msg = self.chat_entry.get().strip()
        if not msg:
            return
        self.db.send_manager_response(self.current_chat_user_id, msg)
        self.chat_entry.delete(0, tk.END)
        self.load_chat_messages_for_user()