import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import database

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# مقداردهی اولیه دیتابیس Supabase
try:
    database.init_db()
    logging.info("Database initialized successfully.")
except Exception as e:
    logging.error(f"Error initializing database: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات مدیریت کارهای روزمره شما روی سرور آنلاین آماده است. 🚀\nراهنما: /add, /list, /done")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task_text = " ".join(context.args)
    if not task_text:
        await update.message.reply_text("لطفاً متن کار را وارد کنید. مثال:\n/add خرید نان")
        return
    database.add_task(user_id, task_text)
    await update.message.reply_text(f"✅ کار «{task_text}» با موفقیت ثبت شد.")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = database.get_tasks(user_id)
    if not tasks:
        await update.message.reply_text("هیچ کار معوقه‌ای نداری! 🎉")
        return
    msg = "📋 لیست کارهای شما:\n\n"
    for task in tasks:
        msg += f"🔹 کد {task[0]}: {task[1]}\n"
    await update.message.reply_text(msg)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("لطفاً شناسه (کد) کار را وارد کنید. مثال:\n/done 1")
        return
    try:
        task_id = int(context.args[0])
        success = database.mark_done(task_id, user_id)
        if success:
            await update.message.reply_text(f"🎉 کار شماره {task_id} انجام شد!")
        else:
            await update.message.reply_text("کار پیدا نشد یا قبلاً انجام شده.")
    except ValueError:
        await update.message.reply_text("کد کار باید عدد باشد.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("done", done))

    print("Bot is running online on Render...")
    app.run_polling()

if name == "main":
    main()

