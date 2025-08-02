import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
import psycopg2
from psycopg2 import pool

from dotenv import load_dotenv
load_dotenv()  # Загружает переменные из .env файла

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация бота
TOKEN = os.getenv("TELEGRAM_TOKEN", "7382727613:AAG7_S2GFaNIv6czqj6vJrS1EGVsSFS0WkM")
ADMIN_ID = os.getenv("ADMIN_ID", "@Soffya82") # Обязательно с @ в начале для username

# Проверка формата ADMIN_ID
if not ADMIN_ID:
    logger.error("ADMIN_ID не указан!")
    exit(1)
elif not (ADMIN_ID.startswith('@') or ADMIN_ID.lstrip('-').isdigit()):
    logger.error(f"Неверный формат ADMIN_ID: {ADMIN_ID}. Должен начинаться с @ или быть числовым ID")
    exit(1)

# Встроенный каталог товаров
CATALOG = {
    'winter': {
        'name': 'Зима',
        'items': [
            {
                'name': 'Женские зимние пуховики',
                'color': 'Черный',
                'link': 'https://www.wildberries.ru/catalog/175873915/detail.aspx'
            },
            {
                'name': 'Женские зимние пуховики',
                'color': 'Оливковый',
                'link': 'https://www.wildberries.ru/catalog/253587201/detail.aspx'
            },
            {
                'name': 'Женские зимние пуховики',
                'color': 'Голубой',
                'link': 'https://www.wildberries.ru/catalog/253587199/detail.aspx'
            },
            {
                'name': 'Женские зимние пуховики',
                'color': 'Фиолетовый',
                'link': 'https://www.wildberries.ru/catalog/253587202/detail.aspx'
            },
            {
                'name': 'Женские зимние пуховики',
                'color': 'Баклажан',
                'link': 'https://www.wildberries.ru/catalog/253587197/detail.aspx'
            },
            {
                'name': 'Женские зимние пуховики',
                'color': 'Бордо',
                'link': 'https://www.wildberries.ru/catalog/453814195/detail.aspx'
            },
            {
                'name': 'Женские зимние пуховики',
                'color': 'Фукси',
                'link': 'https://www.wildberries.ru/catalog/449566294/detail.aspx'
            },
            {
                'name': 'Женские зимние пуховики',
                'color': 'Бежевый',
                'link': 'https://www.wildberries.ru/catalog/253587198/detail.aspx'
            },
            {
                'name': 'Женские зимние пуховики с поясом',
                'color': 'Черный',
                'link': 'https://www.wildberries.ru/catalog/458138806/detail.aspx'
            },
            {
                'name': 'Женские зимние пуховики с поясом',
                'color': 'Бирюзовый',
                'link': 'https://www.wildberries.ru/catalog/458138809/detail.aspx'
            },
            {
                'name': 'Женские зимние пуховики с поясом',
                'color': 'Хаки',
                'link': 'https://www.wildberries.ru/catalog/458138808/detail.aspx'
            },
            {
                'name': 'Мужские парки',
                'color': 'Черный',
                'link': 'https://www.wildberries.ru/catalog/242081084/detail.aspx'
            },
            {
                'name': 'Мужские парки',
                'color': 'Белый',
                'link': 'https://www.wildberries.ru/catalog/242081085/detail.aspx'
            },
            {
                'name': 'Мужские парки',
                'color': 'Хаки',
                'link': 'https://www.wildberries.ru/catalog/451533759/detail.aspx'
            },
            {
                'name': 'Мужские парки',
                'color': 'Бежевый',
                'link': 'https://www.wildberries.ru/catalog/242081083/detail.aspx'
            },
            {
                'name': 'Мужские пуховики',
                'color': 'Черный',
                'link': 'https://www.wildberries.ru/catalog/175549540/detail.aspx'
            },
            {
                'name': 'Мужские пуховики',
                'color': 'Черный с коричневым',
                'link': 'https://www.wildberries.ru/catalog/175814955/detail.aspx'
            },
            {
                'name': 'Варежки зимние',
                'color': '',
                'link': 'https://seller.wildberries.ru/new-goods/all-goods'
            }
        ]
    },
    'spring': {
        'name': 'Весна/Осень',
        'items': [
            {
                'name': 'Куртка на осень короткая оверсайз',
                'color': 'Синяя',
                'link': 'https://www.wildberries.ru/catalog/314963480/detail.aspx'
            },
            {
                'name': 'Куртка на осень короткая оверсайз',
                'color': 'Графит',
                'link': 'https://www.wildberries.ru/catalog/325699105/detail.aspx'
            },
            {
                'name': 'Куртка на осень короткая оверсайз',
                'color': 'Мята',
                'link': 'https://www.wildberries.ru/catalog/314963481/detail.aspx'
            },
            {
                'name': 'Куртка на осень короткая оверсайз',
                'color': 'Жемчужный',
                'link': 'https://www.wildberries.ru/catalog/314963482/detail.aspx'
            },
            {
                'name': 'Куртка на осень короткая оверсайз',
                'color': 'Черный',
                'link': 'https://www.wildberries.ru/catalog/314963477/detail.aspx'
            },
            {
                'name': 'Куртка на осень короткая оверсайз',
                'color': 'Оливковый',
                'link': 'https://www.wildberries.ru/catalog/314963479/detail.aspx'
            },
            {
                'name': 'Куртка на осень с капюшоном',
                'color': 'Черная',
                'link': 'https://www.wildberries.ru/catalog/314958189/detail.aspx'
            },
            {
                'name': 'Куртка на осень с капюшоном',
                'color': 'Голубая',
                'link': 'https://www.wildberries.ru/catalog/314958190/detail.aspx'
            },
            {
                'name': 'Куртка на осень с капюшоном',
                'color': 'Серая',
                'link': 'https://www.wildberries.ru/catalog/314958188/detail.aspx'
            },
            {
                'name': 'Куртка на осень с капюшоном',
                'color': 'Бежевая',
                'link': 'https://www.wildberries.ru/catalog/314958191/detail.aspx'
            },
            {
                'name': 'Куртка на осень с капюшоном',
                'color': 'Красная',
                'link': 'https://www.wildberries.ru/catalog/320369447/detail.aspx'
            },
            {
                'name': 'Куртка на осень с капюшоном',
                'color': 'Темно-синяя',
                'link': 'https://www.wildberries.ru/catalog/320369449/detail.aspx'
            }
        ]
    },
    'summer': {
        'name': 'Лето',
        'items': [
            {
                'name': 'Платье летнее нарядное длинное',
                'color': 'Светлое',
                'link': 'https://www.wildberries.ru/catalog/370795701/detail.aspx'
            },
            {
                'name': 'Платье летнее нарядное длинное',
                'color': 'Темное',
                'link': 'https://www.wildberries.ru/catalog/370795702/detail.aspx'
            },
            {
                'name': 'Платье сарафан летнее крестьянка',
                'color': 'Мини',
                'link': 'https://www.wildberries.ru/catalog/370752622/detail.aspx'
            },
            {
                'name': 'Платье летнее короткое с воротником',
                'color': 'Светлое',
                'link': 'https://www.wildberries.ru/catalog/370747437/detail.aspx'
            },
            {
                'name': 'Платье летнее короткое с воротником',
                'color': 'Темное',
                'link': 'https://www.wildberries.ru/catalog/370747436/detail.aspx'
            },
            {
                'name': 'Платье летнее длинное льняное',
                'color': 'Черное',
                'link': 'https://www.wildberries.ru/catalog/368572748/detail.aspx'
            },
            {
                'name': 'Платье летнее длинное льняное',
                'color': 'Кремовое',
                'link': 'https://www.wildberries.ru/catalog/368572749/detail.aspx'
            },
            {
                'name': 'Платье летнее длинное льняное',
                'color': 'Хаки',
                'link': 'https://www.wildberries.ru/catalog/368572750/detail.aspx'
            }
        ]
    },
    'sweatshirts': {
        'name': 'Свитшоты',
        'items': [
            {
                'name': 'Свитшот базовый однотонный без начеса',
                'color': 'Белый',
                'link': 'https://www.wildberries.ru/catalog/208982848/detail.aspx'
            },
            {
                'name': 'Свитшот базовый однотонный без начеса',
                'color': 'Бежевый',
                'link': 'https://www.wildberries.ru/catalog/208982849/detail.aspx'
            },
            {
                'name': 'Свитшот базовый однотонный без начеса',
                'color': 'Черный',
                'link': 'https://www.wildberries.ru/catalog/208982851/detail.aspx'
            },
            {
                'name': 'Свитшот базовый однотонный без начеса',
                'color': 'Серый',
                'link': 'https://www.wildberries.ru/catalog/208982850/detail.aspx'
            }
        ]
    }
}

class Database:
    def __init__(self):
        self.conn_pool = None
        self.connect()

    def connect(self):
    # Устанавливает соединение с базой данных через пул соединений
        try:
            # Получаем параметры подключения из переменных окружения
            db_host = os.getenv('DB_HOST', 'localhost')
            db_name = os.getenv('DB_NAME', 'polair_bot')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', '1234')
            db_port = os.getenv('DB_PORT', '5432')
            
            # Формируем строку подключения
            dsn = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            self.conn_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                dsn=dsn
            )
            logger.info("Успешное подключение к базе данных")
            self.create_tables()
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    def create_tables(self):
        """Создает необходимые таблицы в базе данных"""
        conn = None
        try:
            conn = self.conn_pool.getconn()
            with conn.cursor() as cursor:
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
                conn.commit()
                logger.info("Таблица отзывов создана или уже существует")
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                self.conn_pool.putconn(conn)

    def add_review(self, user_id, username, first_name, review_text):
        """Добавляет отзыв в базу данных"""
        conn = None
        try:
            conn = self.conn_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO reviews (user_id, username, first_name, review_text)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (user_id, username, first_name, review_text))
                review_id = cursor.fetchone()[0]
                conn.commit()
                return review_id
        except Exception as e:
            logger.error(f"Ошибка при добавлении отзыва: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                self.conn_pool.putconn(conn)

    def get_recent_reviews(self, limit=5):
        """Получает последние отзывы из базы данных"""
        conn = None
        try:
            conn = self.conn_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT username, first_name, review_text, created_at
                    FROM reviews
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении отзывов: {e}")
            return []
        finally:
            if conn:
                self.conn_pool.putconn(conn)

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.conn_pool:
            self.conn_pool.closeall()
            logger.info("Соединение с базой данных закрыто")

# Создаем глобальный экземпляр базы данных
db = Database()

async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение"""
    if update.message and update.message.text not in ["👋 Добро пожаловать в официальный бот POLAIR!", "/start"]:
        keyboard = [[InlineKeyboardButton("Начать ➡️", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "👋 Добро пожаловать в официальный бот POLAIR!\n\n"
            "✨ Одежда для каждого сезона с заботой о вашем комфорте\n\n"
            "Для начала работы нажмите кнопку ниже:"
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start и главного меню"""
    message = update.message or update.callback_query.message
    
    keyboard = [
        [InlineKeyboardButton("Каталог", callback_data='catalog')],
        [InlineKeyboardButton("Техподдержка", callback_data='support')],
        [InlineKeyboardButton("Оставить отзыв", callback_data='leave_review')],
        [InlineKeyboardButton("Посмотреть отзывы", callback_data='show_reviews')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "Сияй в каждом сезоне вместе с POLAIR\n\nВыберите действие:",
                reply_markup=reply_markup
            )
        else:
            welcome_text = (
                "👋 Добро пожаловать в официальный бот POLAIR!\n\n"
                "✨ Одежда для каждого сезона с заботой о вашем комфорте\n\n"
                "Для продолжения выберите действие:"
            )
            await message.reply_text(
                welcome_text,
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline-кнопки"""
    query = update.callback_query
    await query.answer()

    try:
        if query.data == 'start':
            await start(update, context)
        elif query.data == 'catalog':
            seasons = [
                [InlineKeyboardButton("Зима", callback_data='winter')],
                [InlineKeyboardButton("Весна/Осень", callback_data='spring')],
                [InlineKeyboardButton("Лето", callback_data='summer')],
                [InlineKeyboardButton("Назад", callback_data='back')]
            ]
            reply_markup = InlineKeyboardMarkup(seasons)
            await query.edit_message_text(
                text="Выберите сезон:",
                reply_markup=reply_markup
            )
                
        elif query.data in ['winter', 'spring', 'summer']:
            season = CATALOG.get(query.data, {'name': query.data.capitalize(), 'items': []})
            
            if season['items']:
                keyboard = []
                for item in season['items']:
                    if item.get('link'):
                        button_text = item['name']
                        if item.get('color'):
                            button_text += f" ({item['color']})"
                        keyboard.append([InlineKeyboardButton(button_text, url=item['link'])])
                
                if keyboard:
                    keyboard.append([InlineKeyboardButton("Назад", callback_data='catalog')])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(
                        text=f"Выберите товар из сезона {season['name']}:",
                        reply_markup=reply_markup
                    )
                else:
                    await query.edit_message_text(
                        text=f"В сезоне {season['name']} нет доступных товаров.",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='catalog')]])
                    )
            else:
                await query.edit_message_text(
                    text=f"Товары для сезона {season['name']} временно отсутствуют.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='catalog')]])
                )
                
        elif query.data == 'back':
            await start(update, context)
        
        elif query.data == 'support':
            context.user_data['awaiting_support'] = True
            await query.edit_message_text(
                text="✉️ Опишите вашу проблему, и мы обязательно вам поможем!\n\n"
                     "Просто напишите сообщение с описанием проблемы, и оно будет переправлено администратору.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]])
            )
        
        elif query.data == 'leave_review':
            context.user_data['awaiting_review'] = True
            await query.edit_message_text(
                text="📝 Пожалуйста, напишите ваш отзыв о нашем магазине и продукции.\n\n"
                     "Мы ценим ваше мнение!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]])
            )
        
        elif query.data == 'show_reviews':
            reviews = db.get_recent_reviews()
            if reviews:
                reviews_text = "📜 Последние отзывы:\n\n" + "\n\n".join(
                    [f"👤 {review[0] or review[1]}:\n{review[2]}\n⏱ {review[3].strftime('%d.%m.%Y %H:%M')}" 
                     for review in reviews]
                )
            else:
                reviews_text = "Пока нет отзывов. Будьте первым!"
            
            await query.edit_message_text(
                text=reviews_text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]])
            )
    
    except Exception as e:
        logger.error(f"Ошибка при обработке callback: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user = update.message.from_user
    
    if context.user_data.get('awaiting_review'):
        review_text = update.message.text
        review_id = db.add_review(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            review_text=review_text
        )
        
        if review_id:
            await update.message.reply_text("🌟 Спасибо за ваш отзыв! Мы очень ценим ваше мнение.")
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"📢 Новый отзыв от @{user.username or user.first_name} (ID: {review_id}):\n\n{review_text}"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке отзыва администратору: {e}")
        else:
            await update.message.reply_text("⚠️ Произошла ошибка при сохранении отзыва. Пожалуйста, попробуйте позже.")
        
        context.user_data['awaiting_review'] = False
    
    elif context.user_data.get('awaiting_support'):
        problem_text = update.message.text
        user_info = f"@{user.username}" if user.username else f"{user.first_name} (ID: {user.id})"
        
        try:
            admin_message = (
                f"🆘 Новый запрос в поддержку\n"
                f"От: {user_info}\n"
                f"Текст:\n{problem_text}"
            )
            
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_message,
                parse_mode='Markdown'
            )
            
            await update.message.reply_text(
                "✅ Ваше сообщение успешно отправлено в поддержку. "
                "Мы ответим вам в ближайшее время."
            )
            
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения администратору {ADMIN_ID}: {e}")
            
            await update.message.reply_text(
                "⚠️ Если у вас возникли вопросы, "
                "Пожалуйста, свяжитесь с администратором "
                f"напрямую: {ADMIN_ID}"
            )
            
            logger.info(f"Сообщение от {user_info} не было доставлено администратору: {problem_text}")
        
        finally:
            context.user_data['awaiting_support'] = False
    
    else:
        await send_welcome(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке сообщения: {context.error}")

def main():
    """Запуск бота"""
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, send_welcome))
    application.add_error_handler(error_handler)
    
    application.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    finally:
        db.close()