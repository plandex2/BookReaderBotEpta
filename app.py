from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from bs4 import BeautifulSoup
import json

# Функция для парсинга FB2
def parse_fb2(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')
        body = soup.find('body')
        if body:
            return body.get_text()
        return "Не удалось найти текст книги."

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот для чтения книг.')

# Обработка документов
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = f"books/{update.message.document.file_name}"
    await file.download_to_drive(file_path)
    await update.message.reply_text(f"Файл {update.message.document.file_name} сохранен!")

# Обработка данных из Mini App
async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.message.web_app_data.data)
    if data.get('type') == 'get_book':
        try:
            with open(f"books/{data.get('file_name')}", 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'lxml')
                body = soup.find('body')
                text = body.get_text() if body else "Не удалось загрузить книгу."
                await update.message.reply_text(text[:4000])  # Отправляем первые 4000 символов
        except Exception as e:
            await update.message.reply_text(f"Ошибка: {str(e)}")

# Создание и запуск бота
app = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

app.run_polling()
