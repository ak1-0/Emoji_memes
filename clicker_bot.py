import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('TELEGRAM_API_KEY')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Хранение прогресса
user_data = {}

# Пороговые значения для вывода картинок
milestones = [20, 50, 100, 200]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Инициализация данных пользователя
    if user_id not in user_data:
        user_data[user_id] = {'clicks': 0, 'multiplier': 1, 'last_image': 1}

    # Клавиатура с кнопкой
    keyboard = [[InlineKeyboardButton("Click me!", callback_data='click')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправка первой картинки по умолчанию
    image_path = "images/1.jpg"
    with open(image_path, 'rb') as image:
        await update.message.reply_photo(photo=image, caption='Clicks: 0. Start clicking the button below:', reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    # Инициализация данных пользователя, если еще нет
    if user_id not in user_data:
        user_data[user_id] = {'clicks': 0, 'multiplier': 1, 'last_image': 1}

    # Обновление кликов с учётом множителя
    user_data[user_id]['clicks'] += user_data[user_id]['multiplier']
    clicks = user_data[user_id]['clicks']

    # Логика изменения множителя
    new_milestone_reached = False
    if clicks >= 200 and user_data[user_id]['multiplier'] < 5:
        user_data[user_id]['multiplier'] = 5
        new_milestone_reached = True
        await query.message.reply_text('Congrats! Now each click counts as 5 clicks!')
    elif clicks >= 100 and user_data[user_id]['multiplier'] < 4:
        user_data[user_id]['multiplier'] = 4
        new_milestone_reached = True
        await query.message.reply_text('Congrats! Now each click counts as 4 clicks!')
    elif clicks >= 50 and user_data[user_id]['multiplier'] < 3:
        user_data[user_id]['multiplier'] = 3
        new_milestone_reached = True
        await query.message.reply_text('Congrats! Now each click counts as 3 clicks!')
    elif clicks >= 20 and user_data[user_id]['multiplier'] < 2:
        user_data[user_id]['multiplier'] = 2
        new_milestone_reached = True
        await query.message.reply_text('Congrats! Now each click counts as 2 clicks!')

    # Проверка на достижение порога для вывода новой картинки
    image_number = None
    if clicks >= 200 and user_data[user_id]['last_image'] < 5:
        image_number = 5
    elif clicks >= 100 and user_data[user_id]['last_image'] < 4:
        image_number = 4
    elif clicks >= 50 and user_data[user_id]['last_image'] < 3:
        image_number = 3
    elif clicks >= 20 and user_data[user_id]['last_image'] < 2:
        image_number = 2

    # Создание клавиатуры
    keyboard = [[InlineKeyboardButton("Click me!", callback_data='click')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Если достигнут новый порог, отправляем новую картинку с кнопкой
    if image_number:
        image_path = f"images/{image_number}.jpg"
        user_data[user_id]['last_image'] = image_number
        with open(image_path, 'rb') as image:
            await query.message.reply_photo(photo=image, caption=f'Clicks: {clicks} (Each click adds {user_data[user_id]["multiplier"]} clicks)', reply_markup=reply_markup)
    else:
        # Обновление сообщения с кликами и кнопкой
        await query.edit_message_caption(caption=f'Clicks: {clicks} (Each click adds {user_data[user_id]["multiplier"]} clicks)', reply_markup=reply_markup)

def main():
    # Создание и настройка приложения
    application = ApplicationBuilder().token(API_KEY).build()

    # Обработчики команд и событий
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_click))

    # Запуск приложения
    application.run_polling()

if __name__ == '__main__':
    main()