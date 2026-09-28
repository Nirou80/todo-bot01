import sqlite3

DB_NAME = "todo_bot.db"

def init_db():
    """ساخت جدول کارها در صورت عدم وجود"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    conn.commit()
    conn.close()
def add_task(user_id, task_text):
    """افزودن یک کار جدید به دیتابیس"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, task) VALUES (?, ?)",
        (user_id, task_text)
    )
    conn.commit()
    conn.close()

def get_tasks(user_id):
    """دریافت لیست کارهای یک کاربر مشخص"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, task, status FROM tasks WHERE user_id = ?",
        (user_id,)
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def mark_done(task_id, user_id):
    """علامت‌زدن کار به عنوان انجام‌شده"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = 'done' WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

if __name__ == "__main__":
    init_db()
    print("دیتابیس با موفقیت ساخته شد!")
    