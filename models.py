class User:
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Product:
    def __init__(self, id, name, price, quantity, description, category_name):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.description = description
        self.category_name = category_name

class CartItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

    def total_price(self):
        return self.product.price * self.quantity

class Cart:
    def __init__(self, user_id, db):
        self.user_id = user_id
        self.db = db
        self.items = []
        self.load_from_db()

    def load_from_db(self):
        self.items.clear()
        cart_data = self.db.get_cart_items(self.user_id)
        for prod_id, qty, name, price, desc, cat_name in cart_data:
            product = Product(prod_id, name, price, 0, desc, cat_name)
            self.items.append(CartItem(product, qty))

    def add_item(self, product, quantity=1):
        self.db.add_to_cart(self.user_id, product.id, quantity)
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                return
        self.items.append(CartItem(product, quantity))

    def remove_item(self, product_id):
        self.db.remove_from_cart(self.user_id, product_id)
        self.items = [item for item in self.items if item.product.id != product_id]

    def update_quantity(self, product_id, new_quantity):
        if new_quantity <= 0:
            self.remove_item(product_id)
        else:
            self.db.update_cart_item(self.user_id, product_id, new_quantity)
            for item in self.items:
                if item.product.id == product_id:
                    item.quantity = new_quantity
                    return

    def get_total_sum(self):
        return sum(item.total_price() for item in self.items)

    def get_total_items(self):
        return sum(item.quantity for item in self.items)

    def clear(self):
        self.db.clear_cart(self.user_id)
        self.items.clear()