from aiogram import types
from database import cur, conn

async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    cur.execute("SELECT * FROM deals WHERE status='pending'")
    deals = cur.fetchall()
    text = "Сделки на модерации:\n"
    for d in deals:
        text += f"ID:{d[0]} | {d[1]} | {d[2]} {d[3]}\n"
    await message.answer(text)