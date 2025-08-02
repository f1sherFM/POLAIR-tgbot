# db.py
import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            self.conn = psycopg2.connect(
                dbname="polair_bot",
                user="postgres",
                password="1234",
                host="localhost",
                port="5432"
            )
            print("Успешное подключение к базе данных")
            self.create_tables()
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")

    def create_tables(self):
        """Создает необходимые таблицы в базе данных"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reviews (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        username VARCHAR(100),
                        first_name VARCHAR(100),
                        review_text TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.conn.commit()
                print("Таблицы успешно созданы")
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")

    def add_review(self, user_id, username, first_name, review_text):
        """Добавляет отзыв в базу данных"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO reviews (user_id, username, first_name, review_text)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (user_id, username, first_name, review_text))
                review_id = cursor.fetchone()[0]
                self.conn.commit()
                return review_id
        except Exception as e:
            print(f"Ошибка при добавлении отзыва: {e}")
            self.conn.rollback()
            return None

    def get_recent_reviews(self, limit=5):
        """Получает последние отзывы из базы данных"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT username, first_name, review_text, created_at
                    FROM reviews
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении отзывов: {e}")
            return []

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()
            print("Соединение с базой данных закрыто")

# Создаем глобальный экземпляр базы данных
db = Database()