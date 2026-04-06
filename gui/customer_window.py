import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from models import User, Product, Cart
from gui.colors import COLORS
from gui.cart_window import CartWindow

class CustomerWindow:
    def __init__(self, user):
        self.user = user
        self.db = Database()
        self.session_id = self.db.create_session(user.id)
        self.cart = Cart(user.id, self.db)
        self.window = tk.Tk()
        self.window.title(f"Покупатель: {user.username} - Магазин")
        self.window.geometry("1100x600")
        self.window.configure(bg=COLORS['bg'])

        # Верхняя панель
        top_frame = tk.Frame(self.window, bg=COLORS['header_bg'], height=40)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text=f"Добро пожаловать, {user.username}!", bg=COLORS['header_bg'],
                 fg=COLORS['header_fg'], font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=20, pady=10)

        self.cart_btn = tk.Button(top_frame, text=f"Корзина ({self.cart.get_total_items()})",
                                   bg=COLORS['accent'], fg=COLORS['label_fg'],
                                   bd=0, padx=20, command=self.open_cart)
        self.cart_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        tk.Button(top_frame, text="Выход", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.logout).pack(side=tk.RIGHT, padx=10, pady=5)

        # Блокнот
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладки
        self.tab_home = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_home, text="О магазине")
        self.setup_home_tab()

        self.tab_products = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_products, text="Товары")
        self.setup_products_tab()

        self.tab_news = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_news, text="Новости")
        self.setup_news_tab()

        self.tab_reviews = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reviews, text="Отзывы")
        self.setup_reviews_tab()

        self.tab_profile = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_profile, text="Личный кабинет")
        self.setup_profile_tab()

        self.tab_wishlist = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_wishlist, text="Избранное")
        self.setup_wishlist_tab()

        self.tab_orders = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_orders, text="История заказов")
        self.setup_orders_tab()

        self.tab_chat = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_chat, text="Чат поддержки")
        self.setup_chat_tab()

        self.window.mainloop()

    def logout(self):
        self.window.destroy()
        from gui.login_window import LoginWindow
        LoginWindow()

    def update_cart_button(self):
        total = self.cart.get_total_items()
        self.cart_btn.config(text=f"Корзина ({total})")

    # ---------- О магазине ----------
    def setup_home_tab(self):
        frame = tk.Frame(self.tab_home, bg=COLORS['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        info = self.db.get_store_info()
        if info:
            address, hours, phone, email, description = info
        else:
            address = hours = phone = email = description = "Информация отсутствует"
        tk.Label(frame, text="О нашем магазине", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 16, 'bold')).pack(pady=10)
        for text in [f"Адрес: {address}", f"Часы работы: {hours}", f"Телефон: {phone}",
                     f"Email: {email}", f"Описание: {description}"]:
            tk.Label(frame, text=text, bg=COLORS['bg'], fg=COLORS['label_fg'],
                     font=('Arial', 12), justify=tk.LEFT, wraplength=800).pack(anchor=tk.W, pady=5)

    # ---------- Товары с фильтрацией, сортировкой, поиском и избранным ----------
    def setup_products_tab(self):
        filter_frame = tk.Frame(self.tab_products, bg=COLORS['bg'])
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(filter_frame, text="Поиск:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self.apply_filters())

        tk.Label(filter_frame, text="Цена от:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(side=tk.LEFT, padx=5)
        self.min_price_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.min_price_var, width=8).pack(side=tk.LEFT, padx=2)
        tk.Label(filter_frame, text="до:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(side=tk.LEFT)
        self.max_price_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.max_price_var, width=8).pack(side=tk.LEFT, padx=2)

        self.in_stock_var = tk.BooleanVar()
        tk.Checkbutton(filter_frame, text="Только в наличии", variable=self.in_stock_var,
                       bg=COLORS['bg'], fg=COLORS['label_fg'], selectcolor=COLORS['bg'],
                       command=self.apply_filters).pack(side=tk.LEFT, padx=10)

        tk.Button(filter_frame, text="Сбросить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=10, command=self.reset_filters).pack(side=tk.LEFT, padx=5)

        main_frame = tk.Frame(self.tab_products, bg=COLORS['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = tk.Frame(main_frame, bg=COLORS['bg'], width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Label(left_frame, text="Категории", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        self.cat_listbox = tk.Listbox(left_frame, bg=COLORS['tree_bg'], fg=COLORS['tree_fg'],
                                      selectbackground=COLORS['tree_selected'], bd=2, relief=tk.GROOVE,
                                      font=('Arial', 10), height=15)
        self.cat_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.cat_listbox.bind('<<ListboxSelect>>', self.on_category_select)

        right_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('ID', 'Название', 'Цена', 'В наличии', 'Описание', 'Категория')
        self.tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=20)
        self.sort_state = {col: None for col in columns}
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            if col == 'ID':
                self.tree.column(col, width=40, anchor='center')
            elif col == 'Название':
                self.tree.column(col, width=200)
            elif col == 'Цена':
                self.tree.column(col, width=70, anchor='e')
            elif col == 'В наличии':
                self.tree.column(col, width=70, anchor='e')
            elif col == 'Описание':
                self.tree.column(col, width=250)
            else:
                self.tree.column(col, width=120)

        self.tree.bind('<Button-3>', self.show_product_menu)
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(right_frame, bg=COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Добавить в корзину", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.add_to_cart).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="В избранное", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.add_to_wishlist).pack(side=tk.LEFT, padx=5)

        self.load_categories()
        self.current_category_id = None
        self.apply_filters()

    def load_categories(self):
        self.cat_listbox.delete(0, tk.END)
        self.categories = self.db.get_all_categories()
        self.cat_listbox.insert(0, "Все категории")
        for cat_id, name in self.categories:
            self.cat_listbox.insert(tk.END, name)
        self.cat_listbox.select_set(0)

    def on_category_select(self, event):
        selection = self.cat_listbox.curselection()
        if selection:
            idx = selection[0]
            self.current_category_id = None if idx == 0 else self.categories[idx-1][0]
            self.apply_filters()

    def apply_filters(self):
        min_price = self.min_price_var.get().strip()
        max_price = self.max_price_var.get().strip()
        products = self.db.get_products_by_category(
            category_id=self.current_category_id,
            min_price=float(min_price) if min_price else None,
            max_price=float(max_price) if max_price else None,
            in_stock_only=self.in_stock_var.get(),
            search_query=self.search_var.get().strip() or None
        )
        self.update_tree(products)

    def reset_filters(self):
        self.min_price_var.set('')
        self.max_price_var.set('')
        self.in_stock_var.set(False)
        self.search_var.set('')
        self.apply_filters()

    def sort_by_column(self, col):
        current = self.sort_state[col]
        order = 'ASC' if current in (None, 'desc') else 'DESC'
        self.sort_state[col] = 'asc' if order == 'ASC' else 'desc'
        for c in self.sort_state:
            if c != col:
                self.sort_state[c] = None
        min_price = self.min_price_var.get().strip()
        max_price = self.max_price_var.get().strip()
        products = self.db.get_products_sorted(
            category_id=self.current_category_id,
            sort_col=col,
            sort_order=order,
            min_price=float(min_price) if min_price else None,
            max_price=float(max_price) if max_price else None,
            in_stock_only=self.in_stock_var.get(),
            search_query=self.search_var.get().strip() or None
        )
        self.update_tree(products)

    def update_tree(self, products):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for prod in products:
            self.tree.insert('', tk.END, values=prod)

    def show_product_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self.window, tearoff=0)
            menu.add_command(label="В избранное", command=self.add_to_wishlist)
            menu.post(event.x_root, event.y_root)

    def add_to_wishlist(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Инфо", "Выберите товар")
            return
        prod_id = self.tree.item(selected[0])['values'][0]
        self.db.add_to_wishlist(self.user.id, prod_id)
        messagebox.showinfo("Избранное", "Товар добавлен в избранное")

    def add_to_cart(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Инфо", "Выберите товар для добавления в корзину")
            return
        prod_id, name, price, quantity, desc, cat = self.tree.item(selected[0])['values']
        if quantity <= 0:
            messagebox.showerror("Ошибка", "Товара нет в наличии")
            return
        dialog = tk.Toplevel(self.window)
        dialog.title("Количество")
        dialog.geometry("250x150")
        dialog.configure(bg=COLORS['bg'])
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(dialog, text=f"Товар: {name}", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 10, 'bold')).pack(pady=5)
        tk.Label(dialog, text="Количество:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack()
        var = tk.IntVar(value=1)
        spin = tk.Spinbox(dialog, from_=1, to=quantity, textvariable=var, width=10)
        spin.pack(pady=5)
        def add():
            product = Product(prod_id, name, float(price), quantity, desc, cat)
            self.cart.add_item(product, var.get())
            self.update_cart_button()
            dialog.destroy()
        tk.Button(dialog, text="Добавить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=20, command=add).pack(pady=5)

    def open_cart(self):
        CartWindow(self.window, self.cart, self.update_cart_button)

    # ---------- Новости ----------
    def setup_news_tab(self):
        canvas = tk.Canvas(self.tab_news, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_news, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg'])
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.news_container = scrollable_frame
        self.load_news()

    def load_news(self):
        for w in self.news_container.winfo_children():
            w.destroy()
        news_list = self.db.get_all_news()
        if not news_list:
            tk.Label(self.news_container, text="Скоро здесь появятся новости",
                     bg=COLORS['bg'], fg=COLORS['label_fg'], font=('Arial', 14)).pack(pady=50)
            return
        for news_id, message, created_at in news_list:
            self.create_news_item(news_id, message, created_at)

    def create_news_item(self, news_id, message, created_at):
        frame = tk.Frame(self.news_container, bg='white', relief=tk.GROOVE, bd=1)
        frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(frame, text=message, bg='white', fg='black',
                 font=('Arial', 11), wraplength=800, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=5)
        tk.Label(frame, text=created_at[:10], bg='white', fg='gray', font=('Arial', 9)).pack(anchor=tk.W, padx=10)
        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(anchor=tk.W, padx=10, pady=5)
        counts = self.db.get_news_vote_counts(news_id)
        like_btn = tk.Button(btn_frame, text=f"👍 {counts['like']}", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                             font=('Arial', 9), bd=0, padx=10)
        dislike_btn = tk.Button(btn_frame, text=f"👎 {counts['dislike']}", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                                font=('Arial', 9), bd=0, padx=10)
        def update():
            cnt = self.db.get_news_vote_counts(news_id)
            like_btn.config(text=f"👍 {cnt['like']}")
            dislike_btn.config(text=f"👎 {cnt['dislike']}")
        def like():
            current = self.db.get_user_vote_news(news_id, self.session_id)
            if current == 'like':
                self.db.delete_vote_news(news_id, self.session_id)
            else:
                self.db.vote_news(news_id, self.session_id, 'like')
            update()
        def dislike():
            current = self.db.get_user_vote_news(news_id, self.session_id)
            if current == 'dislike':
                self.db.delete_vote_news(news_id, self.session_id)
            else:
                self.db.vote_news(news_id, self.session_id, 'dislike')
            update()
        like_btn.config(command=like)
        dislike_btn.config(command=dislike)
        like_btn.pack(side=tk.LEFT, padx=2)
        dislike_btn.pack(side=tk.LEFT, padx=2)

    # ---------- Отзывы (выбор категории->товар, лайки, удаление) ----------
    def setup_reviews_tab(self):
        main_frame = tk.Frame(self.tab_reviews, bg=COLORS['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель: категории
        left_frame = tk.Frame(main_frame, bg=COLORS['bg'], width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Label(left_frame, text="Категории", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        self.rev_cat_listbox = tk.Listbox(left_frame, bg=COLORS['tree_bg'], fg=COLORS['tree_fg'],
                                          selectbackground=COLORS['tree_selected'], bd=2, relief=tk.GROOVE,
                                          font=('Arial', 10), height=10)
        self.rev_cat_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.rev_cat_listbox.bind('<<ListboxSelect>>', self.on_rev_category_select)

        # Средняя панель: товары
        mid_frame = tk.Frame(main_frame, bg=COLORS['bg'], width=250)
        mid_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Label(mid_frame, text="Товары", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        self.rev_product_listbox = tk.Listbox(mid_frame, bg=COLORS['tree_bg'], fg=COLORS['tree_fg'],
                                              selectbackground=COLORS['tree_selected'], bd=2, relief=tk.GROOVE,
                                              font=('Arial', 10), height=15)
        self.rev_product_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.rev_product_listbox.bind('<<ListboxSelect>>', self.on_rev_product_select)

        # Правая панель: форма и отзывы
        right_frame = tk.Frame(main_frame, bg=COLORS['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        form_frame = tk.LabelFrame(right_frame, text="Оставить отзыв", bg=COLORS['bg'], fg=COLORS['label_fg'],
                                   font=('Arial', 11, 'bold'))
        form_frame.pack(fill=tk.X, pady=5)
        tk.Label(form_frame, text="Оценка (1-5):", bg=COLORS['bg'], fg=COLORS['label_fg']).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.rating_var = tk.IntVar(value=5)
        tk.Spinbox(form_frame, from_=1, to=5, textvariable=self.rating_var, width=5).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        tk.Label(form_frame, text="Комментарий:", bg=COLORS['bg'], fg=COLORS['label_fg']).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.comment_text = tk.Text(form_frame, height=3, width=40)
        self.comment_text.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Фото:", bg=COLORS['bg'], fg=COLORS['label_fg']).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.image_path_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.image_path_var, width=30).grid(row=2, column=1, padx=5, pady=5, sticky='w')
        tk.Button(form_frame, text="Обзор...", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, command=self.select_image).grid(row=2, column=2, padx=5, pady=5)
        tk.Button(form_frame, text="Отправить отзыв", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.submit_review).grid(row=3, columnspan=3, pady=10)

        reviews_frame = tk.LabelFrame(right_frame, text="Отзывы", bg=COLORS['bg'], fg=COLORS['label_fg'],
                                      font=('Arial', 11, 'bold'))
        reviews_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        canvas = tk.Canvas(reviews_frame, bg=COLORS['bg'], highlightthickness=0)
        sbar = ttk.Scrollbar(reviews_frame, orient=tk.VERTICAL, command=canvas.yview)
        sc_frame = tk.Frame(canvas, bg=COLORS['bg'])
        sc_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sc_frame, anchor="nw")
        canvas.configure(yscrollcommand=sbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.reviews_container = sc_frame

        self.load_rev_categories()

    def load_rev_categories(self):
        self.rev_cat_listbox.delete(0, tk.END)
        self.rev_categories = self.db.get_all_categories()
        for cat_id, name in self.rev_categories:
            self.rev_cat_listbox.insert(tk.END, name)
        if self.rev_categories:
            self.rev_cat_listbox.select_set(0)
            self.current_rev_category_id = self.rev_categories[0][0]
            self.load_rev_products(self.current_rev_category_id)

    def on_rev_category_select(self, event):
        sel = self.rev_cat_listbox.curselection()
        if sel:
            idx = sel[0]
            self.current_rev_category_id = self.rev_categories[idx][0]
            self.load_rev_products(self.current_rev_category_id)

    def load_rev_products(self, category_id):
        self.rev_product_listbox.delete(0, tk.END)
        products = self.db.get_products_by_category(category_id)
        self.rev_products = []
        for prod in products:
            prod_id, name, price, qty, desc, cat_name = prod
            self.rev_products.append((prod_id, name))
            self.rev_product_listbox.insert(tk.END, name)
        if products:
            self.rev_product_listbox.select_set(0)
            self.current_rev_product_id = self.rev_products[0][0]
            self.load_reviews_for_product(self.current_rev_product_id)

    def on_rev_product_select(self, event):
        sel = self.rev_product_listbox.curselection()
        if sel:
            idx = sel[0]
            self.current_rev_product_id = self.rev_products[idx][0]
            self.load_reviews_for_product(self.current_rev_product_id)

    def load_reviews_for_product(self, product_id):
        for w in self.reviews_container.winfo_children():
            w.destroy()
        reviews = self.db.get_reviews_by_product(product_id)
        if not reviews:
            tk.Label(self.reviews_container, text="Отзывов пока нет. Будьте первым!",
                     bg=COLORS['bg'], fg=COLORS['label_fg'], font=('Arial', 11)).pack(pady=10)
            return
        for rev in reviews:
            rev_id, rating, comment, image_path, manager_response, created_at, author_id = rev
            self.create_review_item(rev_id, rating, comment, image_path, manager_response, created_at, author_id)

    def create_review_item(self, rev_id, rating, comment, image_path, manager_response, created_at, author_id):
        frame = tk.Frame(self.reviews_container, bg='white', relief=tk.GROOVE, bd=1)
        frame.pack(fill=tk.X, padx=5, pady=5)
        header = tk.Frame(frame, bg='white')
        header.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(header, text=f"Оценка: {rating}/5", bg='white', fg='blue', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        tk.Label(header, text=created_at[:10], bg='white', fg='gray', font=('Arial', 8)).pack(side=tk.RIGHT)
        tk.Label(frame, text=comment, bg='white', fg='black', font=('Arial', 10), wraplength=400, justify=tk.LEFT).pack(anchor=tk.W, padx=5, pady=2)
        if image_path:
            tk.Label(frame, text=f"Фото: {image_path}", bg='white', fg='purple', font=('Arial', 8)).pack(anchor=tk.W, padx=5)
        if manager_response:
            resp_frame = tk.Frame(frame, bg='#e6f7ff', relief=tk.SUNKEN, bd=1)
            resp_frame.pack(fill=tk.X, padx=10, pady=2)
            tk.Label(resp_frame, text=f"Ответ магазина: {manager_response}", bg='#e6f7ff', fg='green', font=('Arial', 9)).pack(anchor=tk.W, padx=5, pady=2)

        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(anchor=tk.W, padx=5, pady=2)
        counts = self.db.get_review_vote_counts(rev_id)
        like_btn = tk.Button(btn_frame, text=f"👍 {counts['like']}", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                             font=('Arial', 8), bd=0, padx=8)
        dislike_btn = tk.Button(btn_frame, text=f"👎 {counts['dislike']}", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                                font=('Arial', 8), bd=0, padx=8)

        def update_counts():
            cnt = self.db.get_review_vote_counts(rev_id)
            like_btn.config(text=f"👍 {cnt['like']}")
            dislike_btn.config(text=f"👎 {cnt['dislike']}")

        def like():
            cur = self.db.get_user_vote_review(rev_id, self.session_id)
            if cur == 'like':
                self.db.delete_vote_review(rev_id, self.session_id)
            else:
                self.db.vote_review(rev_id, self.session_id, 'like')
            update_counts()
        def dislike():
            cur = self.db.get_user_vote_review(rev_id, self.session_id)
            if cur == 'dislike':
                self.db.delete_vote_review(rev_id, self.session_id)
            else:
                self.db.vote_review(rev_id, self.session_id, 'dislike')
            update_counts()

        like_btn.config(command=like)
        dislike_btn.config(command=dislike)
        like_btn.pack(side=tk.LEFT, padx=2)
        dislike_btn.pack(side=tk.LEFT, padx=2)

        if author_id == self.user.id:
            tk.Button(btn_frame, text="Удалить", bg='red', fg='white',
                      font=('Arial', 8), bd=0, padx=8,
                      command=lambda rid=rev_id: self.delete_review(rid)).pack(side=tk.LEFT, padx=5)

    def delete_review(self, review_id):
        if messagebox.askyesno("Подтверждение", "Удалить ваш отзыв?"):
            self.db.delete_review(review_id, self.user.id)
            self.load_reviews_for_product(self.current_rev_product_id)

    def select_image(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if filename:
            self.image_path_var.set(filename)

    def submit_review(self):
        if not hasattr(self, 'current_rev_product_id'):
            messagebox.showwarning("Предупреждение", "Выберите товар")
            return
        comment = self.comment_text.get('1.0', tk.END).strip()
        if not comment:
            messagebox.showwarning("Предупреждение", "Введите комментарий")
            return
        self.db.add_review(self.current_rev_product_id, self.rating_var.get(), comment,
                           self.image_path_var.get().strip(), user_id=self.user.id)
        self.comment_text.delete('1.0', tk.END)
        self.image_path_var.set('')
        self.load_reviews_for_product(self.current_rev_product_id)
        messagebox.showinfo("Спасибо", "Отзыв добавлен!")

    # ---------- Личный кабинет ----------
    def setup_profile_tab(self):
        frame = tk.Frame(self.tab_profile, bg=COLORS['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        profile = self.db.get_customer_profile(self.user.id)
        if not profile:
            full_name = email = phone = ""
            bonus = 0
            currency = "RUB"
            lang = "ru"
            sub_email = sub_sms = 0
        else:
            full_name, email, phone, bonus, currency, lang, sub_email, sub_sms, _ = profile

        tk.Label(frame, text="Личный кабинет", bg=COLORS['bg'], fg=COLORS['label_fg'],
                 font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(frame, text=f"Бонусные баллы: {bonus}", bg=COLORS['bg'],
                 fg='green', font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)

        form_frame = tk.LabelFrame(frame, text="Редактировать профиль", bg=COLORS['bg'],
                                   fg=COLORS['label_fg'], font=('Arial', 12))
        form_frame.pack(fill=tk.X, pady=10)
        row=0
        tk.Label(form_frame, text="ФИО:", bg=COLORS['bg'], fg=COLORS['label_fg']).grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.full_name_var = tk.StringVar(value=full_name)
        tk.Entry(form_frame, textvariable=self.full_name_var, width=30).grid(row=row, column=1, padx=5, pady=5)
        row+=1
        tk.Label(form_frame, text="Email:", bg=COLORS['bg'], fg=COLORS['label_fg']).grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.email_var = tk.StringVar(value=email)
        tk.Entry(form_frame, textvariable=self.email_var, width=30).grid(row=row, column=1, padx=5, pady=5)
        row+=1
        tk.Label(form_frame, text="Телефон:", bg=COLORS['bg'], fg=COLORS['label_fg']).grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.phone_var = tk.StringVar(value=phone)
        tk.Entry(form_frame, textvariable=self.phone_var, width=30).grid(row=row, column=1, padx=5, pady=5)
        row+=1
        tk.Label(form_frame, text="Валюта:", bg=COLORS['bg'], fg=COLORS['label_fg']).grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.currency_var = tk.StringVar(value=currency)
        ttk.Combobox(form_frame, textvariable=self.currency_var, values=['RUB','USD','EUR'], state='readonly', width=10).grid(row=row, column=1, padx=5, pady=5, sticky='w')
        row+=1
        tk.Label(form_frame, text="Язык:", bg=COLORS['bg'], fg=COLORS['label_fg']).grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.lang_var = tk.StringVar(value=lang)
        ttk.Combobox(form_frame, textvariable=self.lang_var, values=['ru','en','de'], state='readonly', width=10).grid(row=row, column=1, padx=5, pady=5, sticky='w')
        row+=1
        self.sub_email_var = tk.BooleanVar(value=bool(sub_email))
        tk.Checkbutton(form_frame, text="Подписаться на email-рассылку", variable=self.sub_email_var,
                       bg=COLORS['bg'], fg=COLORS['label_fg'], selectcolor=COLORS['bg']).grid(row=row, columnspan=2, padx=5, pady=5, sticky='w')
        row+=1
        self.sub_sms_var = tk.BooleanVar(value=bool(sub_sms))
        tk.Checkbutton(form_frame, text="Подписаться на SMS-уведомления", variable=self.sub_sms_var,
                       bg=COLORS['bg'], fg=COLORS['label_fg'], selectcolor=COLORS['bg']).grid(row=row, columnspan=2, padx=5, pady=5, sticky='w')
        row+=1
        tk.Button(form_frame, text="Сохранить изменения", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=20, command=self.save_profile).grid(row=row, columnspan=2, pady=10)

    def save_profile(self):
        self.db.update_customer_profile(self.user.id, self.full_name_var.get().strip(),
                                        self.email_var.get().strip(), self.phone_var.get().strip(),
                                        self.currency_var.get(), self.lang_var.get(),
                                        1 if self.sub_email_var.get() else 0,
                                        1 if self.sub_sms_var.get() else 0)
        messagebox.showinfo("Успех", "Профиль обновлён")

    # ---------- Избранное ----------
    def setup_wishlist_tab(self):
        frame = tk.Frame(self.tab_wishlist, bg=COLORS['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('ID', 'Название', 'Цена', 'В наличии', 'Описание', 'Категория')
        self.wishlist_tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        for col in columns:
            self.wishlist_tree.heading(col, text=col)
            if col == 'ID':
                self.wishlist_tree.column(col, width=40, anchor='center')
            elif col == 'Название':
                self.wishlist_tree.column(col, width=200)
            elif col == 'Цена':
                self.wishlist_tree.column(col, width=70, anchor='e')
            elif col == 'В наличии':
                self.wishlist_tree.column(col, width=70, anchor='e')
            elif col == 'Описание':
                self.wishlist_tree.column(col, width=250)
            else:
                self.wishlist_tree.column(col, width=120)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.wishlist_tree.yview)
        self.wishlist_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.wishlist_tree.pack(fill=tk.BOTH, expand=True)
        btn_frame = tk.Frame(frame, bg=COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Удалить из избранного", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.remove_from_wishlist).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="В корзину", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.add_wishlist_to_cart).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.load_wishlist).pack(side=tk.LEFT, padx=5)
        self.load_wishlist()

    def load_wishlist(self):
        for row in self.wishlist_tree.get_children():
            self.wishlist_tree.delete(row)
        for item in self.db.get_wishlist(self.user.id):
            self.wishlist_tree.insert('', tk.END, values=item)

    def remove_from_wishlist(self):
        sel = self.wishlist_tree.selection()
        if not sel:
            return
        prod_id = self.wishlist_tree.item(sel[0])['values'][0]
        self.db.remove_from_wishlist(self.user.id, prod_id)
        self.load_wishlist()

    def add_wishlist_to_cart(self):
        sel = self.wishlist_tree.selection()
        if not sel:
            return
        prod_id, name, price, quantity, desc, cat = self.wishlist_tree.item(sel[0])['values']
        if quantity <= 0:
            messagebox.showerror("Ошибка", "Товара нет в наличии")
            return
        dialog = tk.Toplevel(self.window)
        dialog.title("Количество")
        dialog.geometry("250x120")
        dialog.configure(bg=COLORS['bg'])
        dialog.grab_set()
        tk.Label(dialog, text="Количество:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(pady=5)
        var = tk.IntVar(value=1)
        tk.Spinbox(dialog, from_=1, to=quantity, textvariable=var, width=10).pack(pady=5)
        def add():
            product = Product(prod_id, name, price, quantity, desc, cat)
            self.cart.add_item(product, var.get())
            self.update_cart_button()
            dialog.destroy()
        tk.Button(dialog, text="Добавить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, command=add).pack(pady=5)

    # ---------- История заказов ----------
    def setup_orders_tab(self):
        frame = tk.Frame(self.tab_orders, bg=COLORS['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('Номер', 'Дата', 'Сумма', 'Статус', 'Товары')
        self.orders_tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        for col in columns:
            self.orders_tree.heading(col, text=col)
        self.orders_tree.column('Номер', width=80)
        self.orders_tree.column('Дата', width=100)
        self.orders_tree.column('Сумма', width=80, anchor='e')
        self.orders_tree.column('Статус', width=100)
        self.orders_tree.column('Товары', width=400)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_tree.pack(fill=tk.BOTH, expand=True)
        tk.Button(frame, text="Обновить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.load_order_history).pack(pady=5)
        self.load_order_history()

    def load_order_history(self):
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)
        orders = self.db.get_order_history(self.user.id)
        for order_id, date, total, status, products in orders:
            self.orders_tree.insert('', tk.END, values=(order_id, date[:10], f"{total:.2f} руб.", status, products))

    # ---------- Чат поддержки ----------
    def setup_chat_tab(self):
        frame = tk.Frame(self.tab_chat, bg=COLORS['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        chat_frame = tk.Frame(frame, bg='white', relief=tk.SUNKEN, bd=1)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.chat_text = tk.Text(chat_frame, bg='white', fg='black', font=('Arial', 10),
                                 wrap=tk.WORD, state=tk.DISABLED)
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_chat = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=scroll_chat.set)
        scroll_chat.pack(side=tk.RIGHT, fill=tk.Y)
        input_frame = tk.Frame(frame, bg=COLORS['bg'])
        input_frame.pack(fill=tk.X, pady=5)
        self.message_var = tk.StringVar()
        entry = tk.Entry(input_frame, textvariable=self.message_var, width=80)
        entry.pack(side=tk.LEFT, padx=5)
        entry.bind('<Return>', lambda e: self.send_message())
        tk.Button(input_frame, text="Отправить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.send_message).pack(side=tk.LEFT, padx=5)
        self.load_chat_messages()

    def load_chat_messages(self):
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete('1.0', tk.END)
        for msg, is_from_manager, created_at in self.db.get_chat_messages(self.user.id):
            prefix = "Менеджер" if is_from_manager else "Вы"
            tag = 'manager' if is_from_manager else 'user'
            self.chat_text.insert(tk.END, f"{prefix} ({created_at[11:16]}): {msg}\n", tag)
        self.chat_text.tag_config('manager', foreground='blue')
        self.chat_text.tag_config('user', foreground='green')
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

    def send_message(self):
        msg = self.message_var.get().strip()
        if not msg:
            return
        self.db.add_chat_message(self.user.id, msg, is_from_manager=False)
        self.message_var.set('')
        self.load_chat_messages()