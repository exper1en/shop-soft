import sqlite3

class Database:
    def __init__(self, db_file='shop.db'):
        self.db_file = db_file

    def _connect(self):
        return sqlite3.connect(self.db_file)

    # ========== Пользователи и профили ==========
    def get_user(self, username, password):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        return user

    def get_admin_by_password(self, password):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE role='manager' AND password=?", (password,))
        user = cursor.fetchone()
        conn.close()
        return user

    def get_customer_user(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE role='customer' LIMIT 1")
        user = cursor.fetchone()
        conn.close()
        return user

    def get_customer_profile(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT full_name, email, phone, bonus_points, preferred_currency,
                   preferred_language, subscribe_email, subscribe_sms, created_at
            FROM customers WHERE user_id = ?
        ''', (user_id,))
        profile = cursor.fetchone()
        conn.close()
        return profile

    def update_customer_profile(self, user_id, full_name, email, phone,
                                preferred_currency, preferred_language,
                                subscribe_email, subscribe_sms):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE customers SET
                full_name = ?, email = ?, phone = ?,
                preferred_currency = ?, preferred_language = ?,
                subscribe_email = ?, subscribe_sms = ?
            WHERE user_id = ?
        ''', (full_name, email, phone, preferred_currency, preferred_language,
              subscribe_email, subscribe_sms, user_id))
        conn.commit()
        conn.close()

    # ========== Сессии ==========
    def create_session(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions (user_id) VALUES (?)", (user_id,))
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id

    # ========== Категории ==========
    def get_all_categories(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY name")
        cats = cursor.fetchall()
        conn.close()
        return cats

    def add_category(self, name):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def update_category(self, cat_id, new_name):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE categories SET name=? WHERE id=?", (new_name, cat_id))
        conn.commit()
        conn.close()

    def delete_category(self, cat_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE category_id=?", (cat_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            conn.close()
            return False
        cursor.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        conn.commit()
        conn.close()
        return True

    # ========== Товары ==========
    def get_products_by_category(self, category_id=None, min_price=None, max_price=None, in_stock_only=False, search_query=None):
        conn = self._connect()
        cursor = conn.cursor()
        query = '''
            SELECT p.id, p.name, p.price, p.quantity, p.description, c.name 
            FROM products p JOIN categories c ON p.category_id = c.id
            WHERE 1=1
        '''
        params = []
        if category_id is not None:
            query += " AND p.category_id = ?"
            params.append(category_id)
        if min_price is not None:
            query += " AND p.price >= ?"
            params.append(min_price)
        if max_price is not None:
            query += " AND p.price <= ?"
            params.append(max_price)
        if in_stock_only:
            query += " AND p.quantity > 0"
        if search_query:
            query += " AND p.name LIKE ?"
            params.append(f'%{search_query}%')
        query += " ORDER BY c.name, p.name"
        cursor.execute(query, params)
        products = cursor.fetchall()
        conn.close()
        return products

    def get_products_sorted(self, category_id, sort_col, sort_order='ASC', min_price=None, max_price=None, in_stock_only=False, search_query=None):
        col_map = {
            'id': 'p.id',
            'name': 'p.name',
            'price': 'p.price',
            'quantity': 'p.quantity',
            'category': 'c.name'
        }
        sql_col = col_map.get(sort_col, 'p.name')
        conn = self._connect()
        cursor = conn.cursor()
        query = '''
            SELECT p.id, p.name, p.price, p.quantity, p.description, c.name 
            FROM products p JOIN categories c ON p.category_id = c.id
            WHERE 1=1
        '''
        params = []
        if category_id is not None:
            query += " AND p.category_id = ?"
            params.append(category_id)
        if min_price is not None:
            query += " AND p.price >= ?"
            params.append(min_price)
        if max_price is not None:
            query += " AND p.price <= ?"
            params.append(max_price)
        if in_stock_only:
            query += " AND p.quantity > 0"
        if search_query:
            query += " AND p.name LIKE ?"
            params.append(f'%{search_query}%')
        query += f" ORDER BY {sql_col} {sort_order}"
        cursor.execute(query, params)
        products = cursor.fetchall()
        conn.close()
        return products

    def get_product_by_id(self, product_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, price, quantity, description, category_id 
            FROM products WHERE id=?
        ''', (product_id,))
        product = cursor.fetchone()
        conn.close()
        return product

    def add_product(self, name, price, quantity, category_id, description=''):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, price, quantity, category_id, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, price, quantity, category_id, description))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def update_product(self, product_id, name, price, quantity, category_id, description):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products 
            SET name=?, price=?, quantity=?, category_id=?, description=?
            WHERE id=?
        ''', (name, price, quantity, category_id, description, product_id))
        conn.commit()
        conn.close()

    def delete_product(self, product_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        conn.close()

    # ========== Новости и голосование ==========
    def add_news(self, message):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO news (message) VALUES (?)", (message,))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def get_all_news(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, message, created_at FROM news ORDER BY created_at DESC")
        news = cursor.fetchall()
        conn.close()
        return news

    def delete_news(self, news_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM news_votes WHERE news_id=?", (news_id,))
        cursor.execute("DELETE FROM news WHERE id=?", (news_id,))
        conn.commit()
        conn.close()

    def get_user_vote_news(self, news_id, session_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT vote_type FROM news_votes WHERE news_id=? AND session_id=?", (news_id, session_id))
        vote = cursor.fetchone()
        conn.close()
        return vote[0] if vote else None

    def vote_news(self, news_id, session_id, vote_type):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO news_votes (news_id, session_id, vote_type)
            VALUES (?, ?, ?)
        ''', (news_id, session_id, vote_type))
        conn.commit()
        conn.close()

    def delete_vote_news(self, news_id, session_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM news_votes WHERE news_id=? AND session_id=?", (news_id, session_id))
        conn.commit()
        conn.close()

    def get_news_vote_counts(self, news_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT vote_type, COUNT(*) FROM news_votes WHERE news_id=? GROUP BY vote_type", (news_id,))
        rows = cursor.fetchall()
        conn.close()
        counts = {'like': 0, 'dislike': 0}
        for vt, cnt in rows:
            counts[vt] = cnt
        return counts

    # ========== Отзывы и голосование ==========
    def add_review(self, product_id, rating, comment, image_path, user_id=None):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reviews (product_id, user_id, rating, comment, image_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, user_id, rating, comment, image_path))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def get_reviews_by_product(self, product_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, rating, comment, image_path, manager_response, created_at, user_id
            FROM reviews WHERE product_id = ?
            ORDER BY created_at DESC
        ''', (product_id,))
        reviews = cursor.fetchall()
        conn.close()
        return reviews

    def get_all_reviews(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, r.rating, r.comment, r.image_path, r.manager_response, 
                   r.created_at, p.name, u.username
            FROM reviews r
            JOIN products p ON r.product_id = p.id
            LEFT JOIN users u ON r.user_id = u.id
            ORDER BY r.created_at DESC
        ''')
        reviews = cursor.fetchall()
        conn.close()
        return reviews

    def add_manager_response(self, review_id, response):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE reviews SET manager_response = ? WHERE id = ?", (response, review_id))
        conn.commit()
        conn.close()

    def delete_review(self, review_id, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
        conn.commit()
        conn.close()

    def get_user_vote_review(self, review_id, session_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT vote_type FROM review_votes WHERE review_id=? AND session_id=?", (review_id, session_id))
        vote = cursor.fetchone()
        conn.close()
        return vote[0] if vote else None

    def vote_review(self, review_id, session_id, vote_type):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO review_votes (review_id, session_id, vote_type)
            VALUES (?, ?, ?)
        ''', (review_id, session_id, vote_type))
        conn.commit()
        conn.close()

    def delete_vote_review(self, review_id, session_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM review_votes WHERE review_id=? AND session_id=?", (review_id, session_id))
        conn.commit()
        conn.close()

    def get_review_vote_counts(self, review_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT vote_type, COUNT(*) FROM review_votes WHERE review_id=? GROUP BY vote_type", (review_id,))
        rows = cursor.fetchall()
        conn.close()
        counts = {'like': 0, 'dislike': 0}
        for vt, cnt in rows:
            counts[vt] = cnt
        return counts

    # ========== Корзина ==========
    def get_cart_items(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.product_id, c.quantity, p.name, p.price, p.description, cat.name
            FROM cart c
            JOIN products p ON c.product_id = p.id
            JOIN categories cat ON p.category_id = cat.id
            WHERE c.user_id = ?
        ''', (user_id,))
        items = cursor.fetchall()
        conn.close()
        return items

    def add_to_cart(self, user_id, product_id, quantity):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cart (user_id, product_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + excluded.quantity
        ''', (user_id, product_id, quantity))
        conn.commit()
        conn.close()

    def update_cart_item(self, user_id, product_id, quantity):
        if quantity <= 0:
            self.remove_from_cart(user_id, product_id)
        else:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?
            ''', (quantity, user_id, product_id))
            conn.commit()
            conn.close()

    def remove_from_cart(self, user_id, product_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        conn.commit()
        conn.close()

    def clear_cart(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    # ========== Заказы ==========
    def create_order(self, user_id, cart_items):
        conn = self._connect()
        cursor = conn.cursor()
        total = 0
        for item in cart_items:
            total += item['price'] * item['quantity']
        cursor.execute('''
            INSERT INTO orders (user_id, total_amount) VALUES (?, ?)
        ''', (user_id, total))
        order_id = cursor.lastrowid
        for item in cart_items:
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (order_id, item['product_id'], item['quantity'], item['price']))
        bonus = int(total * 0.01)
        cursor.execute('''
            UPDATE customers SET bonus_points = bonus_points + ? WHERE user_id = ?
        ''', (bonus, user_id))
        conn.commit()
        conn.close()
        return order_id

    def get_order_history(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, o.order_date, o.total_amount, o.status,
                   GROUP_CONCAT(p.name || ' (' || oi.quantity || ' шт.)', ', ')
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.user_id = ?
            GROUP BY o.id
            ORDER BY o.order_date DESC
        ''', (user_id,))
        orders = cursor.fetchall()
        conn.close()
        return orders

    def get_all_orders_with_details(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, u.username, o.order_date, o.total_amount, o.status,
                   GROUP_CONCAT(p.name || ' (' || oi.quantity || ' шт.)', ', ')
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            GROUP BY o.id
            ORDER BY o.order_date DESC
        ''')
        orders = cursor.fetchall()
        conn.close()
        return orders

    def update_order_status(self, order_id, new_status):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        conn.commit()
        conn.close()

    # ========== Wishlist ==========
    def add_to_wishlist(self, user_id, product_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO wishlist (user_id, product_id) VALUES (?, ?)
        ''', (user_id, product_id))
        conn.commit()
        conn.close()

    def remove_from_wishlist(self, user_id, product_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM wishlist WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id))
        conn.commit()
        conn.close()

    def get_wishlist(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, p.price, p.quantity, p.description, c.name
            FROM wishlist w
            JOIN products p ON w.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE w.user_id = ?
            ORDER BY w.added_at DESC
        ''', (user_id,))
        items = cursor.fetchall()
        conn.close()
        return items

    def is_in_wishlist(self, user_id, product_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM wishlist WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id))
        res = cursor.fetchone()
        conn.close()
        return res is not None

    # ========== Чат ==========
    def add_chat_message(self, user_id, message, is_from_manager=False):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (user_id, message, is_from_manager)
            VALUES (?, ?, ?)
        ''', (user_id, message, is_from_manager))
        conn.commit()
        conn.close()

    def get_chat_messages(self, user_id, limit=50):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message, is_from_manager, created_at
            FROM chat_messages
            WHERE user_id = ?
            ORDER BY created_at ASC
            LIMIT ?
        ''', (user_id, limit))
        messages = cursor.fetchall()
        conn.close()
        return messages

    # ========== Информация о магазине ==========
    def get_store_info(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT address, hours, phone, email, description FROM store_info LIMIT 1")
        info = cursor.fetchone()
        conn.close()
        return info
    def get_chat_users(self):
        """Возвращает список покупателей, которые писали в чат, с их последним сообщением"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT u.id, u.username, 
                   (SELECT message FROM chat_messages WHERE user_id = u.id ORDER BY created_at DESC LIMIT 1) as last_msg,
                   (SELECT created_at FROM chat_messages WHERE user_id = u.id ORDER BY created_at DESC LIMIT 1) as last_time
            FROM users u
            JOIN chat_messages c ON u.id = c.user_id
            WHERE u.role = 'customer'
            ORDER BY last_time DESC
        ''')
        users = cursor.fetchall()
        conn.close()
        return users

    def get_chat_messages_for_user(self, user_id):
        """Возвращает все сообщения конкретного пользователя (включая ответы менеджера)"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, message, is_from_manager, created_at
            FROM chat_messages
            WHERE user_id = ?
            ORDER BY created_at ASC
        ''', (user_id,))
        messages = cursor.fetchall()
        conn.close()
        return messages

    def send_manager_response(self, user_id, message):
        """Отправляет сообщение от менеджера конкретному пользователю"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (user_id, message, is_from_manager)
            VALUES (?, ?, ?)
        ''', (user_id, message, True))
        conn.commit()
        conn.close()