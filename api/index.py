import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import database

# بارگذاری توکن
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ساخت اپلیکیشن تلگرام
app = Application.builder().token(BOT_TOKEN).build()

# تعریف هندلرهای ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات سرورلس مدیریت کارهای روزمره شما آماده است. 🚀\nراهنما: /add, /list, /done")

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

# ثبت هندلرها
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("list", list_tasks))
app.add_handler(CommandHandler("done", done))

# ساخت هندلر Vercel Serverless
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            update = Update.de_json(data, app.bot)
            
            # پردازش همگام update تلگرام
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(app.initialize())
            loop.run_until_complete(app.process_update(update))
            loop.close()

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is running successfully on Vercel Serverless!")