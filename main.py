import logging
import json
import os
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
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

WEBHOOK_URL = "https://polair-tgbot.onrender.com"  # Замените на ваш URL
PORT = int(os.environ.get('PORT', 8443))

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация бота
TOKEN = "7382727613:AAG7_S2GFaNIv6czqj6vJrS1EGVsSFS0WkM"
ADMIN_ID = "@f1sherFM"  # Обязательно с @ в начале для username
CATALOG_FILE = "catalog.json"  # Файл для хранения каталога

# Проверка формата ADMIN_ID
if not ADMIN_ID:
    logger.error("ADMIN_ID не указан!")
    exit(1)
elif not (ADMIN_ID.startswith('@') or ADMIN_ID.lstrip('-').isdigit()):
    logger.error(f"Неверный формат ADMIN_ID: {ADMIN_ID}. Должен начинаться с @ или быть числовым ID")
    exit(1)

# Загрузка каталога из файла или создание стандартного
def load_catalog():
    if os.path.exists(CATALOG_FILE):
        try:
            with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки каталога: {e}")
    
    # Стандартный каталог, если файл не найден или ошибка
    return {
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

# Сохранение каталога в файл
def save_catalog():
    try:
        with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(CATALOG, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения каталога: {e}")

# Загружаем каталог при старте
CATALOG = load_catalog()

class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            self.conn = psycopg2.connect(
                dbname="polair_bot",
                user="polair_bot_user",
                password="XLPCNXclJyZsOYUdgWVOAoNHDINgPqmN",
                host="dpg-d27ic015pdvs73flabq0-a.oregon-postgres.render.com",
                port="5432"
            )
            logger.info("Успешное подключение к базе данных")
            self.create_tables()
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")

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
                logger.info("Таблица отзывов создана")
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")

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
            logger.error(f"Ошибка при добавлении отзыва: {e}")
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
            logger.error(f"Ошибка при получении отзывов: {e}")
            return []

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()
            logger.info("Соединение с базой данных закрыто")

# Создаем глобальный экземпляр базы данных
db = Database()

def is_admin(user_id: int, username: str) -> bool:
    """Проверяет, является ли пользователь администратором"""
    if ADMIN_ID.startswith('@'):
        return username == ADMIN_ID[1:]  # Сравниваем username без @
    else:
        return str(user_id) == ADMIN_ID.lstrip('-')  # Сравниваем ID

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
    
    # Добавляем кнопку админа только для администратора
    if update.message and is_admin(update.message.from_user.id, update.message.from_user.username):
        keyboard.append([InlineKeyboardButton("Добавить товар (админ)", callback_data='admin_add_item')])
    
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
                [InlineKeyboardButton("Свитшоты", callback_data='sweatshirts')],
                [InlineKeyboardButton("Назад", callback_data='back')]
            ]
            reply_markup = InlineKeyboardMarkup(seasons)
            await query.edit_message_text(
                text="Выберите сезон:",
                reply_markup=reply_markup
            )
                
        elif query.data in ['winter', 'spring', 'summer', 'sweatshirts']:
            season = CATALOG.get(query.data, {'name': query.data.capitalize(), 'items': []})
            
            if season['items']:
                keyboard = []
                for item in season['items']:
                    button_text = item['name']
                    if item.get('color'):
                        button_text += f" ({item['color']})"
                    
                    # Если есть ссылка и она не '-', делаем URL кнопку
                    if item.get('link') and item['link'] != '-':
                        keyboard.append([InlineKeyboardButton(button_text, url=item['link'])])
                    else:
                        # Иначе делаем обычную кнопку с текстом
                        keyboard.append([InlineKeyboardButton(button_text, callback_data='no_link')])
                
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

        elif query.data == 'no_link':
            await query.answer("ℹ️ Ссылка на этот товар не указана", show_alert=True)
                
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
        
        elif query.data == 'admin_add_item':
            user = query.from_user
            if not is_admin(user.id, user.username):
                await query.edit_message_text("⛔ У вас нет прав для выполнения этой команды.")
                return
            
            keyboard = [
                [InlineKeyboardButton(season['name'], callback_data=f'add_item_season_{season_id}')]
                for season_id, season in CATALOG.items()
            ]
            keyboard.append([InlineKeyboardButton("Отмена", callback_data='cancel_add_item')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text="Выберите сезон для нового товара:",
                reply_markup=reply_markup
            )
        
        elif query.data.startswith('add_item_season_'):
            season_id = query.data.split('_')[-1]
            context.user_data['add_item_season'] = season_id
            
            await query.edit_message_text(
                text="Введите название товара:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data='cancel_add_item')]])
            )
            context.user_data['awaiting_item_name'] = True
        
        elif query.data == 'cancel_add_item':
            # Очищаем контекст
            for key in ['add_item_season', 'add_item_name', 'add_item_color', 
                        'awaiting_item_name', 'awaiting_item_color', 'awaiting_item_link']:
                context.user_data.pop(key, None)
            
            await query.edit_message_text(
                text="❌ Добавление товара отменено.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("В меню", callback_data='back')]])
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
                "пожалуйста, свяжитесь с администратором "
                f"напрямую: {ADMIN_ID}"
            )
            
            logger.info(f"Сообщение от {user_info} не было доставлено администратору: {problem_text}")
        
        finally:
            context.user_data['awaiting_support'] = False
    
    elif context.user_data.get('awaiting_item_name'):
        item_name = update.message.text
        context.user_data['add_item_name'] = item_name
        context.user_data['awaiting_item_name'] = False
        context.user_data['awaiting_item_color'] = True
        
        await update.message.reply_text(
            "Введите цвет товара (или '-' если цвета нет):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data='cancel_add_item')]])
        )
    
    elif context.user_data.get('awaiting_item_color'):
        item_color = update.message.text
        if item_color == '-':
            item_color = ''
        context.user_data['add_item_color'] = item_color
        context.user_data['awaiting_item_color'] = False
        context.user_data['awaiting_item_link'] = True
        
        await update.message.reply_text(
            "Введите ссылку на товар:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data='cancel_add_item')]])
        )
    
    elif context.user_data.get('awaiting_item_link'):
        item_link = update.message.text
        season_id = context.user_data['add_item_season']
        item_name = context.user_data['add_item_name']
        item_color = context.user_data.get('add_item_color', '')
        
        new_item = {
            'name': item_name,
            'color': item_color,
            'link': item_link
        }
        
        # Добавляем товар в каталог
        CATALOG[season_id]['items'].append(new_item)
        
        # Сохраняем каталог в файл
        save_catalog()
        
        # Очищаем контекст
        for key in ['add_item_season', 'add_item_name', 'add_item_color', 
                    'awaiting_item_link']:
            context.user_data.pop(key, None)
        
        await update.message.reply_text(
            f"✅ Товар успешно добавлен в раздел {CATALOG[season_id]['name']}!\n\n"
            f"Название: {item_name}\n"
            f"Цвет: {item_color if item_color else 'не указан'}\n"
            f"Ссылка: {item_link}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("В меню", callback_data='back')]])
        )
    
    else:
        await send_welcome(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке сообщения: {context.error}")
    
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check():
    server = HTTPServer(('0.0.0.0', 8443), HealthCheckHandler)
    server.serve_forever()

def main():
    """Запуск бота"""
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, send_welcome))
    application.add_error_handler(error_handler)
    
    # Запускаем health check в отдельном потоке
    threading.Thread(target=run_health_check, daemon=True).start()
    
    # Запускаем бота с обработкой KeyboardInterrupt
    try:
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    finally:
        db.close()

if __name__ == "__main__":
    main()