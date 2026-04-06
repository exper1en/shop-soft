import sqlite3

def create_tables():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    # Таблица категорий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('manager', 'customer'))
        )
    ''')

    # Таблица дополнительной информации о покупателях
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            bonus_points INTEGER DEFAULT 0,
            preferred_currency TEXT DEFAULT 'RUB',
            preferred_language TEXT DEFAULT 'ru',
            subscribe_email BOOLEAN DEFAULT 0,
            subscribe_sms BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Таблица сессий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Таблица товаров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # Таблица новостей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица голосов за новости
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            vote_type TEXT NOT NULL CHECK(vote_type IN ('like', 'dislike')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(news_id, session_id),
            FOREIGN KEY (news_id) REFERENCES news (id),
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')

    # Таблица отзывов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comment TEXT,
            image_path TEXT,
            manager_response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # Таблица голосов за отзывы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS review_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            vote_type TEXT NOT NULL CHECK(vote_type IN ('like', 'dislike')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(review_id, session_id),
            FOREIGN KEY (review_id) REFERENCES reviews (id),
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')

    # Таблица корзины
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            UNIQUE(user_id, product_id)
        )
    ''')

    # Таблица заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'новый',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Таблица позиций заказа
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # Таблица списка желаемого
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wishlist (
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, product_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # Таблица сообщений чата
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_from_manager BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Таблица информации о магазине
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS store_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT,
            hours TEXT,
            phone TEXT,
            email TEXT,
            description TEXT
        )
    ''')

    # Добавляем категории
    categories = [
        ('Молочные продукты',),
        ('Напитки',),
        ('Бакалея',),
        ('Овощи и фрукты',),
        ('Мясо и рыба',),
        ('Хлебобулочные изделия',),
        ('Кондитерские изделия',),
        ('Замороженные продукты',)
    ]
    cursor.executemany('INSERT OR IGNORE INTO categories (name) VALUES (?)', categories)

    # Добавляем пользователей
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', '123', 'manager'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('customer', '', 'customer'))

    # Добавляем информацию о магазине
    cursor.execute("SELECT * FROM store_info")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO store_info (address, hours, phone, email, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'г. Москва, ул. Ленина, д. 10',
            'Пн-Пт: 9:00 - 21:00, Сб-Вс: 10:00 - 20:00',
            '+7 (495) 123-45-67',
            'info@magazin.ru',
            'Добро пожаловать в наш магазин! Широкий ассортимент продуктов, свежие товары, приятные цены.'
        ))

    # Добавляем начальную запись для покупателя в таблицу customers
    cursor.execute("SELECT user_id FROM customers WHERE user_id = (SELECT id FROM users WHERE role='customer' LIMIT 1)")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO customers (user_id, full_name, email, phone)
            VALUES ((SELECT id FROM users WHERE role='customer' LIMIT 1), 'Иван Иванов', 'ivan@example.com', '+7 (999) 123-45-67')
        ''')

    # Полный список товаров (80+)
    products = [
        # Молочные продукты (category_id = 1)
        ('Молоко "Домик в деревне" 3.2%', 89.90, 25, 1, 'Пастеризованное, 1 л'),
        ('Кефир 2.5%', 65.50, 30, 1, 'Стакан 500 мл'),
        ('Сметана 20%', 120.00, 15, 1, 'Вес 300 г'),
        ('Творог 9%', 150.00, 12, 1, 'Мягкая упаковка 200 г'),
        ('Йогурт питьевой "Фругурт"', 45.00, 40, 1, 'Клубника, 300 мл'),
        ('Сыр "Российский"', 450.00, 8, 1, 'Кусок 300 г'),
        ('Масло сливочное 82.5%', 210.00, 10, 1, 'Пачка 180 г'),
        ('Ряженка 4%', 70.00, 18, 1, 'Бутылка 500 мл'),
        ('Снежок', 55.00, 20, 1, 'Стакан 300 мл'),
        ('Мороженое пломбир', 80.00, 30, 1, 'Вафельный стаканчик'),

        # Напитки (category_id = 2)
        ('Вода минеральная "Боржоми"', 95.00, 50, 2, 'Стекло 0.5 л'),
        ('Сок апельсиновый "Добрый"', 120.00, 22, 2, 'Пакет 1 л'),
        ('Лимонад "Дюшес"', 65.00, 35, 2, 'Бутылка 1.5 л'),
        ('Чай "Гринфилд"', 180.00, 14, 2, 'Упаковка 25 пакетиков'),
        ('Кофе растворимый "Nescafe"', 350.00, 9, 2, 'Стеклянная банка 100 г'),
        ('Пиво светлое "Балтика 7"', 75.00, 40, 2, 'Банка 0.5 л'),
        ('Квас "Очаковский"', 85.00, 25, 2, 'Пластик 1 л'),
        ('Энергетик "Burn"', 110.00, 20, 2, 'Банка 0.5 л'),
        ('Морс клюквенный', 130.00, 12, 2, 'Бутылка 1 л'),
        ('Компот из сухофруктов', 90.00, 10, 2, 'Пакет 1 л'),

        # Бакалея (category_id = 3)
        ('Макароны "Barilla"', 95.00, 40, 3, 'Пачка 500 г'),
        ('Рис "Кубань"', 70.00, 55, 3, 'Пакет 900 г'),
        ('Гречка "Ярмарка"', 85.00, 60, 3, 'Пакет 900 г'),
        ('Сахар песок', 60.00, 100, 3, 'Килограмм'),
        ('Соль "Экстра"', 25.00, 80, 3, 'Пачка 1 кг'),
        ('Масло подсолнечное "Злато"', 110.00, 30, 3, 'Бутылка 1 л'),
        ('Мука пшеничная', 50.00, 45, 3, 'Пакет 2 кг'),
        ('Овсяные хлопья "Геркулес"', 45.00, 35, 3, 'Пачка 500 г'),
        ('Консервы "Говядина тушеная"', 150.00, 20, 3, 'Банка 325 г'),
        ('Паштет печеночный', 80.00, 25, 3, 'Банка 150 г'),

        # Овощи и фрукты (category_id = 4)
        ('Картофель', 45.00, 200, 4, 'Килограмм'),
        ('Морковь', 35.00, 150, 4, 'Килограмм'),
        ('Лук репчатый', 30.00, 180, 4, 'Килограмм'),
        ('Яблоки "Голден"', 120.00, 80, 4, 'Килограмм'),
        ('Бананы', 95.00, 70, 4, 'Килограмм'),
        ('Апельсины', 110.00, 60, 4, 'Килограмм'),
        ('Помидоры', 150.00, 40, 4, 'Килограмм'),
        ('Огурцы', 130.00, 45, 4, 'Килограмм'),
        ('Капуста белокочанная', 25.00, 90, 4, 'Килограмм'),
        ('Чеснок', 180.00, 15, 4, 'Килограмм'),

        # Мясо и рыба (category_id = 5)
        ('Куриное филе', 280.00, 30, 5, 'Килограмм'),
        ('Свинина (шея)', 350.00, 20, 5, 'Килограмм'),
        ('Говядина (вырезка)', 500.00, 15, 5, 'Килограмм'),
        ('Фарш домашний', 320.00, 18, 5, 'Килограмм'),
        ('Колбаса "Докторская"', 450.00, 12, 5, 'Килограмм'),
        ('Сосиски "Молочные"', 280.00, 25, 5, 'Упаковка 400 г'),
        ('Филе семги', 850.00, 8, 5, 'Килограмм'),
        ('Минтай', 210.00, 20, 5, 'Килограмм'),
        ('Креветки', 600.00, 10, 5, 'Упаковка 400 г'),
        ('Икра красная', 1500.00, 5, 5, 'Банка 100 г'),

        # Хлебобулочные изделия (category_id = 6)
        ('Хлеб "Бородинский"', 55.00, 30, 6, 'Буханка'),
        ('Батон нарезной', 45.00, 40, 6, 'Штука'),
        ('Булочка с маком', 25.00, 50, 6, 'Штука'),
        ('Пирожок с капустой', 35.00, 25, 6, 'Штука'),
        ('Лаваш тонкий', 40.00, 35, 6, 'Упаковка'),
        ('Сухари ванильные', 30.00, 20, 6, 'Пачка 200 г'),
        ('Торт "Наполеон"', 350.00, 5, 6, 'Килограмм'),
        ('Печенье "Юбилейное"', 80.00, 30, 6, 'Пачка 300 г'),
        ('Пряники', 70.00, 25, 6, 'Пачка 250 г'),
        ('Кекс столичный', 90.00, 15, 6, 'Штука'),

        # Кондитерские изделия (category_id = 7)
        ('Шоколад "Аленка"', 85.00, 50, 7, 'Плитка 100 г'),
        ('Конфеты "Коровка"', 120.00, 40, 7, 'Коробка 200 г'),
        ('Зефир', 95.00, 30, 7, 'Упаковка 250 г'),
        ('Мармелад', 70.00, 35, 7, 'Пачка 200 г'),
        ('Вафли', 60.00, 45, 7, 'Пачка 200 г'),
        ('Халва', 110.00, 20, 7, 'Пачка 250 г'),
        ('Пастила', 130.00, 15, 7, 'Упаковка 200 г'),
        ('Козинаки', 90.00, 25, 7, 'Пачка 100 г'),
        ('Шоколадные конфеты "Рафаэлло"', 300.00, 10, 7, 'Коробка 150 г'),
        ('Чупа-чупс', 15.00, 100, 7, 'Штука'),

        # Замороженные продукты (category_id = 8)
        ('Пельмени "Русские"', 220.00, 30, 8, 'Пачка 500 г'),
        ('Вареники с картошкой', 180.00, 25, 8, 'Пачка 500 г'),
        ('Блинчики с мясом', 200.00, 20, 8, 'Пачка 400 г'),
        ('Овощная смесь', 130.00, 18, 8, 'Пачка 400 г'),
        ('Мороженое "Пломбир"', 100.00, 40, 8, 'Стаканчик'),
        ('Креветки замороженные', 450.00, 12, 8, 'Пачка 400 г'),
        ('Кальмары', 320.00, 10, 8, 'Пачка 400 г'),
        ('Ягоды замороженные', 180.00, 15, 8, 'Пачка 300 г'),
        ('Пицца замороженная', 250.00, 8, 8, 'Штука'),
        ('Ледяная рыба', 200.00, 14, 8, 'Килограмм')
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO products 
        (name, price, quantity, category_id, description) 
        VALUES (?, ?, ?, ?, ?)
    ''', products)

    conn.commit()
    conn.close()
    print("База данных успешно создана со всеми таблицами и полным ассортиментом!")

if __name__ == '__main__':
    create_tables()