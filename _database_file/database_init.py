import sqlite3
from datetime import datetime

class BusinessDatabaseInitializer:
    def __init__(self, db_path="business_empire.db"):
        self.db_path = db_path
    
    def init_database(self):
        """Инициализация структуры базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица бизнесов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                icon TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                income_per_hour INTEGER DEFAULT 0,
                workers INTEGER DEFAULT 0,
                workload INTEGER DEFAULT 0,
                primary_action TEXT,
                type TEXT CHECK(type IN ('light', 'dark')),
                risk INTEGER DEFAULT 0,
                price INTEGER DEFAULT 0,
                can_go_dark BOOLEAN DEFAULT 0,
                ev_production BOOLEAN DEFAULT 0,
                bio_prosthetics BOOLEAN DEFAULT 0,
                neuro_chips BOOLEAN DEFAULT 0,
                servers INTEGER DEFAULT 0,
                data_center BOOLEAN DEFAULT 0,
                heat_recovery BOOLEAN DEFAULT 0,
                botnet_active BOOLEAN DEFAULT 0,
                trust_level INTEGER DEFAULT 1,
                max_launder_amount INTEGER DEFAULT 50000,
                crypto_reserve_usage REAL DEFAULT 0.1,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица ролей для бизнесов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER,
                name TEXT NOT NULL,
                cost INTEGER DEFAULT 0,
                effect TEXT,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # Таблица специальных режимов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS special_modes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER,
                name TEXT NOT NULL,
                cooldown TEXT,
                cost INTEGER DEFAULT 0,
                effect TEXT,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # Таблица синергий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_synergies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER,
                synergy_name TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # Таблица темных действий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dark_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER,
                name TEXT NOT NULL,
                income_multiplier REAL DEFAULT 1.0,
                risk_increase INTEGER DEFAULT 0,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # Таблица улучшений бизнесов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_upgrades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER,
                upgrade_type INTEGER,
                level INTEGER DEFAULT 1,
                FOREIGN KEY (business_id) REFERENCES businesses (id),
                UNIQUE(business_id, upgrade_type)
            )
        ''')
        
        # Таблица купленных бизнесов игрока
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER,
                level INTEGER DEFAULT 1,
                income_per_hour INTEGER,
                workers INTEGER,
                workload INTEGER,
                is_active BOOLEAN DEFAULT 1,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        ''')
        
        # Создаем индексы для производительности
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_businesses_type ON businesses(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_businesses_price ON businesses(price)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_businesses_active ON player_businesses(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_roles_business_id ON business_roles(business_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_special_modes_business_id ON special_modes(business_id)')
        
        conn.commit()
        conn.close()
        print("✅ Структура базы данных создана успешно!")
    
    def populate_businesses(self):
        """Заполнение таблицы бизнесов начальными данными"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Очищаем существующие данные
        tables = ['business_roles', 'special_modes', 'business_synergies', 'dark_actions', 'business_upgrades', 'player_businesses', 'businesses']
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
            except sqlite3.Error as e:
                print(f"⚠️ Ошибка при очистке таблицы {table}: {e}")
        
        print("🗑️ Существующие данные очищены")
        
        # Данные для светлых бизнесов
        light_businesses = [
            # (id, name, icon, level, income_per_hour, workers, workload, primary_action, type, risk, price, can_go_dark, 
            #  ev_production, bio_prosthetics, neuro_chips, servers, data_center, heat_recovery, botnet_active, trust_level, max_launder_amount, crypto_reserve_usage, description)
            
            # 1. Продажа (Retail)
            (1, 'Продажа (Retail)', '🏪', 1, 5000, 5, 75, 'Открыть ассортимент', 'light', 0, 50000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Розничная торговля товарами широкого потребления'),
            
            # 2. Строительство
            (2, 'Строительство', '🏗️', 1, 12000, 12, 80, 'Запустить проект', 'light', 0, 150000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Строительство жилых и коммерческих объектов'),
            
            # 3. IT-стартап
            (3, 'IT-стартап', '💻', 1, 8000, 3, 60, 'Разработать фичу', 'light', 0, 75000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Разработка инновационных IT-решений'),
            
            # 4. Электросетевая компания
            (4, 'Электросетевая компания', '⚡', 1, 18000, 8, 70, 'План генерации', 'light', 0, 200000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Энергоснабжение и распределение электроэнергии'),
            
            # 5. Сеть кофеен
            (5, 'Сеть кофеен', '☕', 1, 6000, 6, 65, 'Открыть новую точку', 'light', 0, 60000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Сеть кофеен премиум-класса'),
            
            # 6. Биотех Лаборатория
            (6, 'Биотех Лаборатория', '🧬', 1, 12000, 8, 45, 'Запустить исследование', 'light', 0, 150000, 1, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Исследования в области биотехнологий'),
            
            # 7. Образовательная платформа
            (7, 'Образовательная платформа', '🎓', 1, 9000, 5, 55, 'Создать курс', 'light', 0, 100000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Онлайн-образование и курсы'),
            
            # 8. Технопарк
            (8, 'Технопарк', '🏭', 1, 15000, 7, 60, 'Принять стартап', 'light', 0, 180000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Инфраструктура для технологических компаний'),
            
            # 9. Автопром
            (9, 'Автопром', '🚗', 1, 20000, 15, 80, 'Запустить производство модели', 'light', 0, 300000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Производство автомобилей'),
            
            # 10. Кибербезопасность
            (10, 'Кибербезопасность', '🛡️', 1, 16000, 6, 70, 'Предложить контракт', 'light', 0, 140000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Защита от киберугроз'),
            
            # 11. Медицинский центр
            (11, 'Медицинский центр', '🏥', 1, 14000, 10, 75, 'Открыть отдел', 'light', 0, 160000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Медицинские услуги премиум-класса'),
            
            # 12. Робототехника
            (12, 'Робототехника', '🤖', 1, 18000, 10, 70, 'Запустить проект робота', 'light', 0, 250000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Разработка робототехнических систем'),
            
            # 13. Космический туризм
            (13, 'Космический туризм', '🚀', 1, 35000, 5, 40, 'Строить корабль', 'light', 0, 500000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Космические путешествия для туристов'),
            
            # 14. AI разработки
            (14, 'AI разработки', '🧠', 1, 15000, 6, 65, 'Запустить обучение модели', 'light', 0, 200000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Искусственный интеллект и машинное обучение'),
            
            # 15. Банк
            (15, 'Банк', '🏦', 1, 22000, 8, 85, 'Открыть продукт', 'light', 0, 280000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Финансовые услуги и банковские операции'),
            
            # 16. Нефтегазовая компания
            (16, 'Нефтегазовая компания', '🛢️', 1, 25000, 12, 80, 'Начать бурение', 'light', 0, 350000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Добыча и переработка нефти и газа'),
            
            # 17. Трейдинг
            (17, 'Трейдинг', '📊', 1, 25000, 4, 90, 'Запустить стратегию', 'light', 0, 180000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Торговля на финансовых рынках'),
            
            # 18. Оборонное предприятие
            (18, 'Оборонное предприятие', '🪖', 1, 30000, 10, 70, 'Подать на тендер', 'light', 0, 400000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Производство оборонной продукции'),
            
            # 19. УГМК
            (19, 'УГМК', '⛏️', 1, 30000, 25, 85, 'Открыть рудник', 'light', 0, 400000, 1, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Горнодобывающая и металлургическая компания'),
        ]
        
        # Данные для темных бизнесов
        dark_businesses = [
            # 101. Кибер-мошенничество
            (101, 'Кибер-мошенничество', '🌐', 1, 15000, 4, 85, 'Запустить кампанию', 'dark', 25, 100000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Незаконные операции в киберпространстве'),
            
            # 102. Теневой банкинг
            (102, 'Теневой банкинг', '💳', 1, 18000, 5, 75, 'Открыть пул', 'dark', 30, 150000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Нелегальные финансовые операции'),
            
            # 103. Контрабанда
            (103, 'Контрабанда', '📦', 1, 14000, 6, 80, 'Отправить партию', 'dark', 35, 120000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Незаконная транспортировка товаров'),
            
            # 104. Пиратское ПО
            (104, 'Пиратское ПО', '🏴‍☠️', 1, 11000, 3, 70, 'Выпустить релиз', 'dark', 20, 90000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Распространение нелицензионного ПО'),
            
            # 105. Нелегальные ставки
            (105, 'Нелегальные ставки', '🎲', 1, 16000, 4, 85, 'Открыть ставку', 'dark', 28, 130000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Подпольные азартные игры'),
            
            # 106. Фальшивые документы
            (106, 'Фальшивые документы', '📄', 1, 9000, 4, 65, 'Сделать партию', 'dark', 22, 80000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Изготовление поддельных документов'),
            
            # 107. Нелегальный импорт/экспорт
            (107, 'Нелегальный импорт/экспорт', '🚢', 1, 17000, 7, 75, 'Запустить рейс', 'dark', 32, 160000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Незаконная международная торговля'),
            
            # 108. Теневой майнинг
            (108, 'Теневой майнинг', '⛏️', 1, 12000, 3, 75, 'Построить ферму', 'dark', 20, 80000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Незаконный майнинг криптовалют'),
            
            # 109. Наркокартель
            (109, 'Наркокартель', '💊', 1, 25000, 8, 90, 'Запустить производство', 'dark', 45, 200000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Незаконный оборот наркотиков'),
            
            # 110. Отмывание денег
            (110, 'Отмывание денег', '💸', 1, 20000, 5, 60, 'Отмыть сумму', 'dark', 35, 150000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Легализация незаконных доходов'),
            
            # 111. Подпольный хостинг
            (111, 'Подпольный хостинг', '🖥️', 1, 13000, 4, 70, 'Запустить ноду', 'dark', 18, 110000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Незаконные хостинг-услуги'),
            
            # 112. Нелегальный аутсорсинг
            (112, 'Нелегальный аутсорсинг', '👥', 1, 10000, 6, 80, 'Взять заказ', 'dark', 15, 70000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Незаконные услуги аутсорсинга'),
            
            # 113. Тёмный арбитраж
            (113, 'Тёмный арбитраж', '🔄', 1, 19000, 3, 85, 'Запустить арбитраж', 'dark', 25, 170000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Незаконные арбитражные операции'),
            
            # 114. Частная военная компания
            (114, 'Частная военная компания', '⚔️', 1, 28000, 12, 90, 'Взять контракт', 'dark', 40, 300000, 0, 0, 0, 0, 0, 0, 0, 0, 1, 50000, 0.1, 'Нелегальные военные операции'),
        ]
        
        # Вставляем светлые бизнесы
        cursor.executemany('''
            INSERT INTO businesses (id, name, icon, level, income_per_hour, workers, workload, 
                                  primary_action, type, risk, price, can_go_dark, ev_production,
                                  bio_prosthetics, neuro_chips, servers, data_center, heat_recovery,
                                  botnet_active, trust_level, max_launder_amount, crypto_reserve_usage, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', light_businesses + dark_businesses)
        
        print(f"✅ Добавлено {len(light_businesses)} светлых и {len(dark_businesses)} темных бизнесов")
        
        # Заполняем связанные таблицы
        self._populate_roles(cursor)
        self._populate_special_modes(cursor)
        self._populate_synergies(cursor)
        self._populate_dark_actions(cursor)
        self._populate_upgrades(cursor)
        
        conn.commit()
        conn.close()
        print("🎉 База данных успешно заполнена начальными данными!")
    
    def _populate_roles(self, cursor):
        """Заполнение таблицы ролей"""
        roles_data = [
            # Продажа (Retail)
            (1, 'Продавец', 1000, '+10% доход'),
            (1, 'Менеджер', 3000, '+25% эффективность'),
            (1, 'Merchandiser', 2000, '+15% оборачиваемость'),
            
            # Строительство
            (2, 'Бригадир', 8000, '+20% скорость строительства'),
            (2, 'Инженер', 12000, '+25% качество'),
            (2, 'Менеджер проектов', 15000, '+30% эффективность'),
            
            # IT-стартап
            (3, 'Junior Dev', 2000, '+5% скорость разработки'),
            (3, 'Senior Dev', 5000, '+20% качество кода'),
            (3, 'PM', 4000, '+15% эффективность команды'),
            (3, 'Growth Hacker', 4500, '+25% прирост пользователей'),
            
            # Добавьте остальные роли по аналогии...
        ]
        
        cursor.executemany('''
            INSERT INTO business_roles (business_id, name, cost, effect)
            VALUES (?, ?, ?, ?)
        ''', roles_data)
        print(f"✅ Добавлено {len(roles_data)} ролей для бизнесов")
    
    def _populate_special_modes(self, cursor):
        """Заполнение таблицы специальных режимов"""
        special_modes_data = [
            # Продажа (Retail)
            (1, 'Маркет-кампания', '6ч', 15000, '+200% спрос на 1ч'),
            (1, 'Сезонные коллаборации', '24ч', 25000, '+10% маржа'),
            
            # Строительство
            (2, 'Экспресс-лаг', '24ч', 40000, 'Ускорение проекта 50%'),
            (2, 'Лоббирование', '48ч', 30000, 'Ускорение разрешений'),
            
            # IT-стартап
            (3, 'Инвест-раунд', '12ч', 30000, '+50000 капитала'),
            (3, 'Бета-тест', '8ч', 10000, 'Шанс вирусного роста'),
            
            # Добавьте остальные специальные режимы по аналогии...
        ]
        
        cursor.executemany('''
            INSERT INTO special_modes (business_id, name, cooldown, cost, effect)
            VALUES (?, ?, ?, ?, ?)
        ''', special_modes_data)
        print(f"✅ Добавлено {len(special_modes_data)} специальных режимов")
    
    def _populate_synergies(self, cursor):
        """Заполнение таблицы синергий"""
        synergies_data = [
            (1, 'IT-стартап'),
            (1, 'Логистика'),
            (2, 'УГМК'),
            (2, 'Электросетевая компания'),
            (3, 'AI разработки'),
            (3, 'Кибербезопасность'),
            # Добавьте остальные синергии по аналогии...
        ]
        
        cursor.executemany('''
            INSERT INTO business_synergies (business_id, synergy_name)
            VALUES (?, ?)
        ''', synergies_data)
        print(f"✅ Добавлено {len(synergies_data)} синергий")
    
    def _populate_dark_actions(self, cursor):
        """Заполнение таблицы темных действий"""
        dark_actions_data = [
            (6, 'Несанкционированные испытания', 2.0, 25),
            (6, 'Продажа запрещенных имплантов', 3.0, 40),
            (19, 'Нелегальный экспорт', 2.5, 30),
            (19, 'Схемы уклонения', 1.8, 20),
        ]
        
        cursor.executemany('''
            INSERT INTO dark_actions (business_id, name, income_multiplier, risk_increase)
            VALUES (?, ?, ?, ?)
        ''', dark_actions_data)
        print(f"✅ Добавлено {len(dark_actions_data)} темных действий")
    
    def _populate_upgrades(self, cursor):
        """Заполнение таблицы улучшений"""
        upgrades_data = []
        business_ids = list(range(1, 20)) + list(range(101, 115))  # Все ID бизнесов
        
        for business_id in business_ids:
            for upgrade_type in range(1, 6):  # 5 типов улучшений
                upgrades_data.append((business_id, upgrade_type, 1))
        
        cursor.executemany('''
            INSERT INTO business_upgrades (business_id, upgrade_type, level)
            VALUES (?, ?, ?)
        ''', upgrades_data)
        print(f"✅ Добавлено {len(upgrades_data)} записей улучшений")
    
    def verify_data(self):
        """Проверка целостности данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tables = ['businesses', 'business_roles', 'special_modes', 'business_synergies', 'dark_actions', 'business_upgrades']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"📊 Таблица {table}: {count} записей")
        
        conn.close()

def main():
    """Основная функция для инициализации базы данных"""
    print("🚀 Начало инициализации базы данных бизнесов...")
    
    initializer = BusinessDatabaseInitializer()
    
    try:
        # Создаем структуру БД
        initializer.init_database()
        
        # Заполняем данными
        initializer.populate_businesses()
        
        # Проверяем целостность
        initializer.verify_data()
        
        print("\n🎊 Инициализация базы данных завершена успешно!")
        print("📁 Файл базы данных: business_empire.db")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")

if __name__ == "__main__":
    main()