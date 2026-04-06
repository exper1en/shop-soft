import tkinter as tk
from tkinter import ttk, messagebox
from gui.colors import COLORS

class CartWindow:
    def __init__(self, parent, cart, update_callback=None):
        self.cart = cart
        self.update_callback = update_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Корзина")
        self.window.geometry("600x400")
        self.window.configure(bg=COLORS['bg'])
        self.window.grab_set()

        tk.Label(self.window, text="Ваша корзина", bg=COLORS['header_bg'], fg=COLORS['header_fg'],
                 font=('Arial', 14, 'bold')).pack(fill=tk.X, pady=5)

        columns = ('Название', 'Цена', 'Количество', 'Сумма')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings', height=15)

        self.tree.heading('Название', text='Название')
        self.tree.heading('Цена', text='Цена')
        self.tree.heading('Количество', text='Количество')
        self.tree.heading('Сумма', text='Сумма')

        self.tree.column('Название', width=250)
        self.tree.column('Цена', width=80, anchor='e')
        self.tree.column('Количество', width=80, anchor='e')
        self.tree.column('Сумма', width=100, anchor='e')

        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self.window, bg=COLORS['bg'])
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(btn_frame, text="Удалить выбранное", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.remove_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Изменить количество", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.edit_quantity).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Очистить корзину", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.clear_cart).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Оформить заказ", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, padx=15, command=self.checkout).pack(side=tk.LEFT, padx=5)

        self.total_label = tk.Label(btn_frame, text="Итого: 0.00 руб.", bg=COLORS['bg'],
                                     fg=COLORS['label_fg'], font=('Arial', 12, 'bold'))
        self.total_label.pack(side=tk.RIGHT, padx=10)

        self.refresh()
        self.window.mainloop()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        total = 0.0
        for item in self.cart.items:
            product = item.product
            qty = item.quantity
            sum_price = product.price * qty
            total += sum_price
            self.tree.insert('', tk.END, values=(product.name, f"{product.price:.2f}", qty, f"{sum_price:.2f}"),
                             tags=(product.id,))
        self.total_label.config(text=f"Итого: {total:.2f} руб.")

    def remove_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        product_id = item['tags'][0]
        self.cart.remove_item(product_id)
        self.refresh()
        if self.update_callback:
            self.update_callback()

    def edit_quantity(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Инфо", "Выберите товар")
            return
        item = self.tree.item(selected[0])
        product_id = item['tags'][0]
        current_qty = None
        for it in self.cart.items:
            if it.product.id == product_id:
                current_qty = it.quantity
                break
        if current_qty is None:
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("Изменить количество")
        dialog.geometry("250x120")
        dialog.configure(bg=COLORS['bg'])
        dialog.grab_set()

        tk.Label(dialog, text="Новое количество:", bg=COLORS['bg'], fg=COLORS['label_fg']).pack(pady=5)
        var = tk.IntVar(value=current_qty)
        spin = tk.Spinbox(dialog, from_=1, to=1000, textvariable=var, width=10)
        spin.pack(pady=5)

        def save():
            new_qty = var.get()
            self.cart.update_quantity(product_id, new_qty)
            self.refresh()
            if self.update_callback:
                self.update_callback()
            dialog.destroy()

        tk.Button(dialog, text="Сохранить", bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                  bd=0, command=save).pack(pady=5)

    def clear_cart(self):
        if messagebox.askyesno("Подтверждение", "Очистить корзину?"):
            self.cart.clear()
            self.refresh()
            if self.update_callback:
                self.update_callback()

    def checkout(self):
        if not self.cart.items:
            messagebox.showinfo("Корзина", "Корзина пуста")
            return
        if not messagebox.askyesno("Подтверждение", "Оформить заказ?"):
            return
        cart_items = []
        for item in self.cart.items:
            cart_items.append({
                'product_id': item.product.id,
                'quantity': item.quantity,
                'price': item.product.price
            })
        order_id = self.cart.db.create_order(self.cart.user_id, cart_items)
        if order_id:
            self.cart.clear()
            if self.update_callback:
                self.update_callback()
            messagebox.showinfo("Заказ оформлен", f"Ваш заказ №{order_id} принят!")
            self.window.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось оформить заказ")