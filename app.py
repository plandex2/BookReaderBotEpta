from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from bs4 import BeautifulSoup
import json
import os

# Функция для парсинга FB2
def parse_fb2(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'lxml')
            body = soup.find('body')
            if body:
                return body.get_text()
            return "Не удалось найти текст книги."
    except Exception as e:
        return f"Ошибка при чтении файла: {str(e)}"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received /start command")  # Отладочное сообщение
    await update.message.reply_text('Привет! Я бот для чтения книг.')

# Обработка документов
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received a document")  # Отладочное сообщение
    file = await update.message.document.get_file()
    file_path = f"books/{update.message.document.file_name}"
    
    # Создаем папку books, если её нет
    if not os.path.exists("books"):
        os.makedirs("books")
    
    await file.download_to_drive(file_path)
    print(f"File saved: {file_path}")  # Отладочное сообщение
    await update.message.reply_text(f"Файл {update.message.document.file_name} сохранен!")

# Обработка данных из Mini App
async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received data from Mini App")  # Отладочное сообщение
    try:
        data = json.loads(update.message.web_app_data.data)
        print("Parsed data:", data)  # Отладочное сообщение
        
        if data.get('type') == 'get_book':
            file_name = data.get('file_name')
            file_path = f"books/{file_name}"
            
            if not os.path.exists(file_path):
                print("File not found:", file_path)  # Отладочное сообщение
                await update.message.reply_text("Файл не найден.")
                return
            
            text = parse_fb2(file_path)
            print("Parsed book text:", text[:100])  # Отладочное сообщение (первые 100 символов)
            await update.message.reply_text(text[:4000])  # Отправляем первые 4000 символов
        else:
            print("Unknown request type:", data.get('type'))  # Отладочное сообщение
            await update.message.reply_text("Неизвестный тип запроса.")
    except Exception as e:
        print("Error handling web app data:", str(e))  # Отладочное сообщение
        await update.message.reply_text(f"Ошибка: {str(e)}")

# Создание и запуск бота
def main():
    print("Starting bot...")  # Отладочное сообщение
    app = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

    print("Bot is running...")  # Отладочное сообщение
    app.run_polling()

if __name__ == "__main__":
    main()
