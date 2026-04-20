> stip:
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from config import API_TOKEN, ADMIN_IDS
from database import add_user, set_wallet, create_deal, get_deal, conn, cur
from blockchain import check_nft, verify_payment
from forms import send_to_google

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

ADMIN_IDS = ADMIN_IDS

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить/изменить кошелёк")],
        [KeyboardButton(text="Создать сделку")],
        [KeyboardButton(text="Реферальная ссылка")],
        [KeyboardButton(text="Сменить язык")],
        [KeyboardButton(text="Поддержка")],
        [KeyboardButton(text="NFT Buyback")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(msg: types.Message):
    ref = None
    if msg.text and "ref=" in msg.text:
        ref = msg.text.split("ref=")[1]
    add_user(msg.from_user.id, ref)
    
    await msg.answer(
        "Добро пожаловать в ELF OTC – надёжный P2P-гарант\n\n"
        "Покупайте и продавайте всё, что угодно – безопасно!\n"
        "От Telegram-подарков и NFT до токенов и фиата – сделки проходят легко и без риска.\n\n"
        "Удобное управление кошельками\n"
        "Реферальная система\n\n"
        "Как пользоваться?\n"
        "https://telegra.ph/Podrobnyj-gajd-po-ispolzovaniyu-GiftElfRobot-04-25\n\n"
        "Выберите нужный раздел ниже:",
        reply_markup=main_kb
    )

@dp.message(F.text == "NFT Buyback")
async def nft_buyback(msg: types.Message):
    await msg.answer("Введите ID NFT или ссылку на коллекцию (TON/ETH/SOL):")
    
    @dp.message()
    async def nft_check(m: types.Message):
        data = check_nft("collection", m.text)
        await m.answer(
            f"✅ Оценка по Rarity Score: {data['rarity']}\n"
            f"💰 Сумма выкупа: {data['buyback']} ETH\n\n"
            f"Выплата на подключенный кошелёк"
        )
        # отвязываем handler
        dp.message.handlers.remove(nft_check)

@dp.message(F.text == "Создать сделку")
async def create_deal_handler(msg: types.Message):
    await msg.answer("Введите сумму и валюту (пример: 100 USDT):")
    
    @dp.message()
    async def get_amount(m: types.Message):
        parts = m.text.split()
        amount = float(parts[0])
        currency = parts[1] if len(parts) > 1 else "USDT"
        deal_id = create_deal(m.from_user.id, amount, currency)
        await m.answer(f"Сделка #{deal_id} создана. Ожидайте контрагента.")
        dp.message.handlers.remove(get_amount)

@dp.message(F.text == "Добавить/изменить кошелёк")
async def change_wallet(msg: types.Message):
    await msg.answer("Введите сеть и адрес (пример: TON EQD... или 0x...):")
    
    @dp.message()
    async def save_wallet(m: types.Message):
        parts = m.text.split()
        if len(parts) >= 2:
            network = "ETH" if "0x" in parts[1] else "TON" if "EQ" in parts[1] else "SOL"
            set_wallet(m.from_user.id, network, parts[1])
            await m.answer(f"✅ Кошелёк {network} сохранён")
        dp.message.handlers.remove(save_wallet)

@dp.message(F.text == "Реферальная ссылка")
async def referral_link(msg: types.Message):
    cur.execute("SELECT ref_count, earned FROM referrals WHERE user_id=?", (msg.from_user.id,))
    data = cur.fetchone()
    if not data:
        data = (0, 0.0)
    await msg.answer(
        f"Ваша реферальная ссылка:\n"
        f"https://t.me/{bot.username}?start=ref={msg.from_user.id}\n\n"
        f"Количество рефералов: {data[0]}\n"
        f"Заработано с рефералов: {data[1]} RUB\n"
        f"Вы получаете 20% от комиссии бота с рефералов."
    )

@dp.message(F.text == "Сменить язык")
async def change_lang(msg: types.Message):

> stip:
kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru")]
    ])
    await msg.answer("Choose your language / Выберите язык:", reply_markup=kb)

@dp.message(F.text == "Поддержка")
async def support(msg: types.Message):
    await msg.answer("dev: @seinarukiro\n\nt.me/otcgiftg")

@dp.callback_query()
async def handle_callbacks(call: types.CallbackQuery):
    if call.data.startswith("lang_"):
        lang = call.data.split("_")[1]
        await call.message.answer(f"Language set to {lang}" if lang == "en" else f"Язык установлен: Русский")
    await call.answer()

@dp.message(Command("admin"))
async def admin(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    cur.execute("SELECT * FROM deals WHERE status='pending'")
    deals = cur.fetchall()
    if not deals:
        await msg.answer("Нет активных сделок")
        return
    text = "📋 Сделки на модерации:\n"
    for d in deals:
        text += f"ID: {d[0]} | {d[1]} | {d[2]} {d[3]} | {d[4]}\n"
    await msg.answer(text)

async def main():
    print("✅ Бот запущен")
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
