import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import database

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"سلام {user_name} پرتلاش! 👋\n"
        f"این ربات با تقلب و کمک از هوش مصنوعی ساخته شده امیدوارم شما بهش مبتلا نشین.\n\n"
        f"📌 دستورات ربات:\n"
        f"➕ اگه میخوای کاری به لیستت اضافه کنی: /add متن کار\n"
        f"📋 لیست کارها با دستور: /list\n"
        f"✅ اگه کاری رو انجام دادی و میخوای تیک بزنی: /done شماره_کار\n"
        f"❓ راهنما: /help\n\n"
        f"راستی، اقای گنابادی خوشت اومد؟😎"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 راهنمای استفاده از ربات اینجاس:\n\n"
        "🔹 /start - شروع کار با ربات\n"
        "🔹 /add [متن کار] - اضافه کردن کار جدید\n"
        "🔹 /list - مشاهده لیست تمام کارها\n"
        "🔹 /done [شماره کار] - علامت‌زدن کار به‌عنوان انجام‌شده (مثال: /done 1)"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task_text = " ".join(context.args)
    
    if not task_text:
        await update.message.reply_text("❌ لطفا اول دستور رو بنویسید و بعد کار مد نظر رو .\nمثال: /add خرید نان")
        return

    database.add_task(user_id, task_text)
    await update.message.reply_text(f"✅ کار شما «{task_text}» با موفقیت اضافه شد هوراا!")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = database.get_tasks(user_id)
    
    if not tasks:
        await update.message.reply_text("📜 لیستت خالیه همین الان برنامه ریزی کن و ثبتش کن!")
        return

    message = "📋 لیست کارهای شما:\n\n"
    for task in tasks:
        task_id, task_text, status = task
        icon = "✅" if status == "done" else "⏳"
        message += f"{icon} کد {task_id}: {task_text}\n"

    await update.message.reply_text(message)

# دستور جدید برای انجام کار
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌لطفا اول دستور و بعد شماره کاری که به پایان رسیده رو وارد کنید.\nمثال: /done 1")
        return

    task_id = int(context.args[0])
    success = database.mark_done(task_id, user_id)

    if success:
        await update.message.reply_text(f"🎉 کار شماره {task_id} با موفقیت انجام شد ایول بهت! تا اخر روز همه رو زدی هااا! !")
    else:
        await update.message.reply_text("❌کار با این شماره نداری. دنبالش نگرد:}")

if __name__ == "__main__":
    database.init_db()
    
    print("ربات در حال روشن شدن است...")
    
    proxy_url = "http://127.0.0.1:3067"
    
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .proxy(proxy_url)
        .get_updates_proxy(proxy_url)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("done", done))
    
    print("ربات آنلاین شد!")
    app.run_polling()

