#!/usr/bin/env python3
"""
🌾 TON Farming Bot - Production Version with REAL Crypto Payments
Оплата обязательна! Баланс начисляется только после реальной оплаты в CryptoBot.                                        """
import asyncio
import json
import os                                                                                                               import uuid
import time
import threading
import random                                                                                                           import shutil
from datetime import datetime
from typing import Dict, List
                                                                                                                        import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton               from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
                                                                                                                        # ========== 🔧 КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8571257166:AAHIgqGOjTj3X4sXb0YHc13hVjaZd9dHtBY"
CRYPTO_TOKEN = "421672:AAqhefoXaViidRXzHvI3g5DYnfgeWLcbXBI"
ADMIN_ID = 1124116259
ADMIN_USERNAME = "@soqudik"
REQUIRED_CHANNEL = "TonFarmingChannel"
REQUIRED_CHANNEL_URL = "https://t.me/TonFarmingChannel"

CRYPTO_API = "https://pay.crypt.bot/api"
HEADERS = {"Crypto-Pay-API-Token": CRYPTO_TOKEN}
                                                                                                                        SAVE_DIR = "/storage/emulated/0/TonFarmingBot_v2"
SAVE_DIR = "/app/data"
SAVE_FILE = os.path.join(SAVE_DIR, "farm_data.json")
BACKUP_FILE = os.path.join(SAVE_DIR, "farm_data_backup.json")

                                                                                                                        # ========== 💰 КОМИССИИ ==========
COMMISSION_FARM = 0.22
COMMISSION_PET_CLAIM = 0.08
COMMISSION_MARKET = 0.10                                                                                                MIN_WITHDRAW = 5.0
MIN_DEPOSIT = 0.5
WITHDRAW_FEE = 0.05
                                                                                                                        # ========== 🌱 ДАННЫЕ ==========
SEEDS = {
    "tulip": {
        "name": "🌷 Тюльпан",
        "price": 0.0,
        "time": 10800,
        "reward": 0.0005,                                                                                                       "xp": 15,
        "level": 1,
        "desc": "Бесплатное семя, доступно каждые 4 часа",
        "free_cooldown": 14400                                                                                              },
    "weed": {
        "name": "🌿 Сорняк",
        "price": 0.05,                                                                                                          "time": 1500,
        "reward": 0.07,
        "xp": 20,
        "level": 1,                                                                                                             "desc": "Базовое растение для начинающих фермеров"
    },
    "wheat": {
        "name": "🌾 Пшеница",                                                                                                   "price": 0.15,
        "time": 2700,
        "reward": 0.20,
        "xp": 32,                                                                                                               "level": 1,
        "desc": "Надежный выбор для стабильного дохода"
    },
    "corn": {                                                                                                                   "name": "🌽 Кукуруза",
        "price": 0.40,
        "time": 5400,
        "reward": 0.55,                                                                                                         "xp": 55,
        "level": 2,
        "desc": "Сладкая и прибыльная культура"
    },
    "carrot": {
        "name": "🥕 Морковь",
        "price": 1.00,
        "time": 9000,
        "reward": 1.35,
        "xp": 70,
        "level": 3,                                                                                                             "desc": "Сладкая прибыль для опытных фермеров"
    },
    "tomato": {
        "name": "🍅 Помидор",                                                                                                   "price": 2.50,
        "time": 14400,
        "reward": 3.20,
        "xp": 130,                                                                                                              "level": 4,
        "desc": "Сочный урожай с отличной прибылью"
    },
    "potato": {                                                                                                                 "name": "🥔 Картофель",
        "price": 6.00,
        "time": 21600,
        "reward": 7.50,
        "xp": 270,
        "level": 5,
        "desc": "Много не бывает - много картошки!"                                                                         },
    "sunflower": {
        "name": "🌻 Подсолнух",
        "price": 15.00,                                                                                                         "time": 36000,
        "reward": 18.00,
        "xp": 490,
        "level": 7,                                                                                                             "desc": "Следит за солнцем и приносит золото"
    },
    "strawberry": {
        "name": "🍓 Клубника",                                                                                                  "price": 40.00,
        "time": 57600,
        "reward": 48.00,
        "xp": 950,                                                                                                              "level": 9,
        "desc": "Королева ягод - роскошный урожай"
    },
    "rose": {                                                                                                                   "name": "🌹 Роза",
        "price": 100.00,
        "time": 86400,
        "reward": 120.00,                                                                                                       "xp": 1900,
        "level": 12,
        "desc": "Премиум цветок для элитных фермеров"
    },                                                                                                                      "cannabis": {
        "name": "☘️ Калифорния",
        "price": 250.00,
        "time": 129600,
        "reward": 300.00,
        "xp": 4300,
        "level": 15,
        "desc": "Элитный сорт с максимальной прибылью"
    },
    "truffle": {
        "name": "🍄 Трюфель",                                                                                                   "price": 600.00,
        "time": 172800,
        "reward": 720.00,
        "xp": 8100,                                                                                                             "level": 18,
        "desc": "Черное золото - редкий деликатес"
    },
    "crystal": {                                                                                                                "name": "💎 Кристалл",
        "price": 1500.00,
        "time": 259200,
        "reward": 1800.00,                                                                                                      "xp": 17000,
        "level": 22,
        "desc": "Редкий минерал с космической прибылью"
    },
    "golden": {
        "name": "👑 Золотое яблоко",
        "price": 5000.00,                                                                                                       "time": 432000,
        "reward": 6000.00,
        "xp": 70000,
        "level": 30,                                                                                                            "desc": "Легендарный плод богов"
    }
}
                                                                                                                        PETS = {
    "chicken": {
        "name": "🐔 Курица",
        "price": 2.0,                                                                                                           "income": 0.001,
        "level": 1,
        "feed_time": 43200,
        "desc": "Простая курочка - начни с малого!"                                                                         },
    "rabbit": {
        "name": "🐰 Кролик",
        "price": 5.0,                                                                                                           "income": 0.003,
        "level": 3,
        "feed_time": 43200,
        "desc": "Быстрый и пушистый друг"                                                                                   },
    "sheep": {
        "name": "🐑 Овечка",
        "price": 15.0,                                                                                                          "income": 0.008,
        "level": 5,
        "feed_time": 43200,
        "desc": "Дает шерсть и стабильный доход"
    },
    "cow": {
        "name": "🐄 Корова",
        "price": 50.0,
        "income": 0.025,
        "level": 8,
        "feed_time": 43200,                                                                                                     "desc": "Много молока - много денег!"
    },
    "pig": {
        "name": "🐷 Свинья",                                                                                                    "price": 120.0,
        "income": 0.060,
        "level": 12,
        "feed_time": 43200,                                                                                                     "desc": "Сохраняет трюфели и приносит золото"
    },
    "horse": {
        "name": "🐴 Лошадь",                                                                                                    "price": 300.0,
        "income": 0.150,
        "level": 16,
        "feed_time": 43200,
        "desc": "Быстрый заработок без границ"
    },
    "dragon": {                                                                                                                 "name": "🐉 Дракон",
        "price": 1000.0,
        "income": 0.500,
        "level": 25,                                                                                                            "feed_time": 43200,
        "desc": "Легендарный питомец для избранных"
    }
}                                                                                                                       
UPGRADES = {
    "autowater": {
        "name": "💧 Авто-полив",                                                                                                "price": 10.00,
        "desc": "Скорость роста растений +15%",
        "effect": "speed",
        "value": 0.85,                                                                                                          "max": 3
    },
    "fertilizer": {
        "name": "🧪 Удобрения",                                                                                                 "price": 35.00,
        "desc": "Прибыль с урожая +20%",
        "effect": "profit",
        "value": 1.20,                                                                                                          "max": 3
    },
    "greenhouse": {
        "name": "🏠 Теплица",                                                                                                   "price": 45.00,
        "desc": "+1 дополнительная грядка",
        "effect": "slot",
        "value": 1,
        "max": 5
    },
    "robot": {
        "name": "🤖 Робот-сборщик",
        "price": 100.00,
        "desc": "Автоматический сбор урожая",
        "effect": "auto",
        "value": 1,
        "max": 1
    },
    "genetics": {
        "name": "🧬 ГМО-семена",
        "price": 250.00,
        "desc": "Прибыль с урожая +35%",
        "effect": "profit2",
        "value": 1.35,
        "max": 2
    },
    "warehouse": {
        "name": "🏭 Склад",
        "price": 300.00,
        "desc": "Питомцы копят доход x2 дольше",
        "effect": "storage",
        "value": 2,
        "max": 1
    },
    "megafarm": {
        "name": "🌐 МегаФерма",
        "price": 700.00,
        "desc": "+3 грядки, все бонусы x1.3",
        "effect": "mega",
        "value": 3,
        "max": 1
    }
}

BOOSTERS = {
    "speed": {
        "name": "⚡ Ускоритель роста",
        "price": 3.00,
        "desc": "Скорость роста растений x2 на 2 часа",
        "duration": 7200,
        "emoji": "⚡"
    },
    "profit": {                                                                                                                 "name": "💰 Богатство",
        "price": 40.00,
        "desc": "Прибыль с урожая x2 на 3 часа",                                                                                "duration": 10800,
        "emoji": "💰"
    },
    "instant": {                                                                                                                "name": "⏰ Мгновенный сбор",
        "price": 10.00,
        "desc": "Все растения созреют мгновенно",
        "duration": 0,                                                                                                          "emoji": "⏰"
    },
    "lucky": {
        "name": "🍀 Удача",                                                                                                     "price": 30.00,
        "desc": "Шанс двойного урожая 50% на 1 час",
        "duration": 3600,
        "emoji": "🍀"
    }
}
                                                                                                                        DEFAULT_TASKS = [
    {
        "id": 1,
        "name": "Birds Empire",                                                                                                 "url": "https://t.me/BirdsEmpireBot?start=90446",
        "description": "Перейдите по ссылке, нажмите /start",
        "reward_type": "seed_tulip",
        "reward_amount": 1                                                                                                  },
    {
        "id": 2,
        "name": "Land Bot",                                                                                                     "url": "https://t.me/land_ibot?startapp=47d35749f2",
        "description": "Запустите бота и выполните задания",
        "reward_type": "seed_tulip",
        "reward_amount": 1                                                                                                  },
    {
        "id": 3,
        "name": "Crypto Farm",                                                                                                  "url": "https://t.me/CryptoFarmBot",
        "description": "Запустите бота и соберите первый урожай",
        "reward_type": "seed_tulip",
        "reward_amount": 1                                                                                                  }
]

# ========== 📊 ХРАНИЛИЩЕ ==========                                                                                    users_data: Dict[int, dict] = {}
pending_invoices: Dict[str, dict] = {}
pending_withdraws: Dict[str, dict] = {}
market_listings: Dict[str, dict] = {}
live_sales: List[dict] = []
tasks: List[dict] = DEFAULT_TASKS.copy()
processed_invoices: set = set()

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
                                                                                                                        class FarmStates(StatesGroup):                                                                                              waiting_deposit_amount = State()
    waiting_withdraw_amount = State()
    waiting_withdraw_confirm = State()                                                                                      waiting_broadcast = State()
    waiting_find_user = State()
    waiting_give_ton = State()
    waiting_take_ton = State()                                                                                              waiting_give_item = State()
    waiting_ban_user = State()
    waiting_buy_seed_confirm = State()                                                                                      waiting_market_price = State()
    waiting_task_name = State()
    waiting_task_url = State()                                                                                              waiting_task_desc = State()
    waiting_task_reward_type = State()
    waiting_task_reward_amount = State()                                                                                    waiting_edit_task_select = State()
    waiting_edit_task_field = State()
    waiting_edit_task_value = State()
    waiting_delete_task = State()                                                                                           waiting_task_prize_user = State()
    waiting_task_prize_amount = State()
    waiting_buy_pet_confirm = State()
    waiting_buy_upgrade_confirm = State()                                                                                   waiting_buy_booster_confirm = State()
    waiting_market_buy_confirm = State()

def ensure_save_dir():                                                                                                      try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        return True
    except:
        return False

def save_data():                                                                                                            try:
        data = {
            "users": {str(k): v for k, v in users_data.items()},
            "market": market_listings,                                                                                              "tasks": tasks,
            "live_sales": live_sales[-200:],
            "processed_invoices": list(processed_invoices),
            "pending_invoices": pending_invoices,                                                                                   "timestamp": time.time()
        }
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)                                                                    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:                                                                                                      print(f"Save error: {e}")
        return False

def load_data():                                                                                                            global users_data, market_listings, tasks, live_sales, processed_invoices, pending_invoices
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:                                                                           data = json.load(f)
                users_data = {int(k): v for k, v in data.get("users", {}).items()}
                market_listings = data.get("market", {})
                tasks = data.get("tasks", DEFAULT_TASKS)                                                                                live_sales = data.get("live_sales", [])
                processed_invoices = set(data.get("processed_invoices", []))
                pending_invoices = data.get("pending_invoices", {})
                return True
    except Exception as e:
        print(f"Load error: {e}")
    return False

def auto_save_loop():
    while True:
        time.sleep(5)
        save_data()                                                                                                     
threading.Thread(target=auto_save_loop, daemon=True).start()

# ========== 🎮 ФУНКЦИИ ==========                                                                                      def get_user_data(user_id: int) -> dict:
    if user_id not in users_data:
        users_data[user_id] = {
            "balance": 0.0,                                                                                                         "farm_balance": 0.0,
            "level": 1,
            "xp": 0,                                                                                                                "energy": 100,
            "max_energy": 100,
            "plots": [],
            "max_plots": 2,
            "inventory": {},
            "pets": [],                                                                                                             "upgrades": {},
            "boosters": [],
            "stats": {                                                                                                                  "deposited": 0.0,
                "withdrawn": 0.0,
                "earned": 0.0,
                "spent": 0.0,                                                                                                           "harvested": 0,
                "planted": 0
            },
            "referrer": None,                                                                                                       "referrals": [],
            "username": None,
            "first_name": None,
            "joined_at": time.time(),                                                                                               "last_active": time.time(),
            "last_free_tulip": 0,
            "tasks_completed": [],
            "tasks_attempts": {},
            "banned": False,
            "current_task_index": 0,
            "subscribed": False                                                                                                 }
    return users_data[user_id]

async def check_subscription(user_id: int) -> bool:                                                                         try:
        member = await bot.get_chat_member(f"@{REQUIRED_CHANNEL}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:                                                                                                                     return False

def calculate_level_xp(level: int) -> int:
    return int(100 * (1.5 ** (level - 1)))                                                                              
def add_xp(user_id: int, xp: int) -> bool:
    user = get_user_data(user_id)
    user["xp"] += int(xp * 1.5)                                                                                             leveled_up = False

    while user["xp"] >= calculate_level_xp(user["level"]):
        user["xp"] -= calculate_level_xp(user["level"])                                                                         user["level"] += 1
        user["max_energy"] += 10
        user["energy"] = user["max_energy"]
        leveled_up = True                                                                                                       user["balance"] += user["level"] * 0.001

    return leveled_up
                                                                                                                        def get_growth_time(user_id: int, seed_id: str) -> int:
    user = get_user_data(user_id)
    base_time = SEEDS[seed_id]["time"]
    multiplier = 1.0

    if user["upgrades"].get("autowater", 0) > 0:
        multiplier *= (0.85 ** user["upgrades"]["autowater"])

    now = time.time()
    for booster in user["boosters"]:
        if booster["type"] == "speed" and booster["expires_at"] > now:
            multiplier *= 0.5                                                                                           
    return int(base_time * multiplier)

def get_reward(user_id: int, seed_id: str) -> float:                                                                        user = get_user_data(user_id)
    base_reward = SEEDS[seed_id]["reward"]
    multiplier = 1.0
                                                                                                                            if user["upgrades"].get("fertilizer", 0) > 0:
        multiplier *= (1.2 ** user["upgrades"]["fertilizer"])
    if user["upgrades"].get("genetics", 0) > 0:                                                                                 multiplier *= (1.35 ** user["upgrades"]["genetics"])
    if user["upgrades"].get("megafarm", 0) > 0:                                                                                 multiplier *= 1.3

    now = time.time()                                                                                                       for booster in user["boosters"]:
        if booster["type"] == "profit" and booster["expires_at"] > now:
            multiplier *= 2.0                                                                                                   if booster["type"] == "lucky" and booster["expires_at"] > now:
            if random.random() < 0.5:
                multiplier *= 2.0                                                                                       
    return base_reward * multiplier
                                                                                                                        def get_max_plots(user_id: int) -> int:
    user = get_user_data(user_id)
    max_plots = user["max_plots"]                                                                                           max_plots += user["upgrades"].get("greenhouse", 0)
    if user["upgrades"].get("megafarm", 0) > 0:
        max_plots += 3                                                                                                      return max_plots

def get_available_plots(user_id: int) -> int:                                                                               user = get_user_data(user_id)
    return get_max_plots(user_id) - len(user["plots"])
                                                                                                                        def format_time(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}с"                                                                                                elif seconds < 3600:
        return f"{seconds//60}м"
    elif seconds < 86400:                                                                                                       hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}ч {mins}м" if mins > 0 else f"{hours}ч"                                                             else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600                                                                                       return f"{days}д {hours}ч" if hours > 0 else f"{days}д"

def calculate_pet_hourly(pet_id: str, user_id: int = None) -> float:                                                        pet = PETS[pet_id]
    income = pet["income"]
    if user_id:                                                                                                                 user = get_user_data(user_id)
        if user["upgrades"].get("warehouse", 0) > 0:
            income *= 2                                                                                                     return income

# ========== ⌨️ КЛАВИАТУРЫ ==========                                                                                    def main_keyboard(user_id: int = None) -> ReplyKeyboardMarkup:
    # Новая раскладка кнопок в 3 ряда
    kb = [                                                                                                                      [KeyboardButton(text="🌾 Моя Ферма")],
        [KeyboardButton(text="🐾 Питомцы"), KeyboardButton(text="🏪 Рынок"), KeyboardButton(text="💰 Баланс")],
        [KeyboardButton(text="⬆️ Улучшения"), KeyboardButton(text="🚀 Бустеры"), KeyboardButton(text="🎒 Инвентарь")],           [KeyboardButton(text="🎯 Задания"), KeyboardButton(text="👥 Рефералы"), KeyboardButton(text="ℹ️ Помощь")]
    ]
                                                                                                                            if user_id == ADMIN_ID:
        kb.append([KeyboardButton(text="🔴 АДМИН ПАНЕЛЬ")])
                                                                                                                            return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def farm_keyboard() -> InlineKeyboardMarkup:                                                                                return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌱 Посадить семена", callback_data="plant_menu")],
        [InlineKeyboardButton(text="🧺 Собрать урожай", callback_data="harvest")],                                              [InlineKeyboardButton(text="🛒 Магазин семян", callback_data="seed_shop")],
        [InlineKeyboardButton(text="🟫 Статус грядок", callback_data="plots_status")]
    ])                                                                                                                  
def admin_keyboard() -> ReplyKeyboardMarkup:
    kb = [                                                                                                                      [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="💰 Прибыль")],
        [KeyboardButton(text="👤 Найти игрока"), KeyboardButton(text="💸 Выдать TON")],
        [KeyboardButton(text="💳 Забрать TON"), KeyboardButton(text="🎁 Выдать предмет")],                                      [KeyboardButton(text="🚫 Бан/Разбан"), KeyboardButton(text="📢 Рассылка")],
        [KeyboardButton(text="✅ Заявки на вывод"), KeyboardButton(text="🎯 Управление заданиями")],
        [KeyboardButton(text="📋 Логи"), KeyboardButton(text="⚙️ Настройки")],                                                   [KeyboardButton(text="🔙 Выйти")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)                                                       
# ========== 🌐 API ==========
async def crypto_request(method: str, params: dict = None):                                                                 url = f"{CRYPTO_API}/{method}"
    async with aiohttp.ClientSession() as session:
        if method in ["getMe", "getBalance", "getInvoices", "getExchangeRates"]:                                                    async with session.get(url, headers=HEADERS) as resp:
                return await resp.json()
        else:                                                                                                                       async with session.post(url, json=params, headers=HEADERS) as resp:
                return await resp.json()
                                                                                                                        async def create_invoice(amount: float, asset: str = "TON", payload: str = ""):
    return await crypto_request("createInvoice", {
        "asset": asset,
        "amount": str(amount),
        "description": "Пополнение фермы TON",
        "payload": payload,
        "paid_btn_name": "openBot",
        "paid_btn_url": f"https://t.me/{(await bot.me()).username}"
    })                                                                                                                  
async def transfer(user_id: int, asset: str, amount: str, spend_id: str):
    return await crypto_request("transfer", {
        "user_id": user_id,                                                                                                     "asset": asset,
        "amount": amount,
        "spend_id": spend_id
    })                                                                                                                  
# ========== ФОНОВАЯ ПРОВЕРКА ПОПОЛНЕНИЙ ==========
async def check_payments_loop():
    """Проверка оплат каждые 5 секунд - ТОЛЬКО после реальной оплаты!"""                                                    global processed_invoices

    while True:
        try:
            if pending_invoices:
                result = await crypto_request("getInvoices", {"status": "paid"})
                                                                                                                                        if result.get("ok"):
                    paid_items = result["result"]["items"]

                    for inv in paid_items:                                                                                                      invoice_id = str(inv["invoice_id"])

                        if invoice_id in pending_invoices and invoice_id not in processed_invoices:
                            info = pending_invoices[invoice_id]                                                                                     user_id = info["user_id"]
                            amount = info["amount"]

                            expected_payload = info.get("payload", "")                                                                              actual_payload = inv.get("payload", "")

                            if actual_payload != expected_payload:
                                continue                                                                                
                            if inv.get("status") != "paid":
                                continue
                                                                                                                                                    user = get_user_data(user_id)
                            old_balance = user["balance"]
                            user["balance"] += amount
                            user["stats"]["deposited"] += amount                                                        
                            processed_invoices.add(invoice_id)
                            pending_invoices[invoice_id]["status"] = "completed"
                                                                                                                                                    print(f"✅ ЗАЧИСЛЕНО: {amount} TON для {user_id} (было: {old_balance}, стало: {user['balance']})")                                                                                                                  
                            try:
                                await bot.send_message(
                                    user_id,
                                    f"<b>✅ Пополнение успешно!</b>\n\n"
                                    f"<b>💰 Зачислено:</b> <code>{amount:.3f} TON</code>\n"
                                    f"<b>💳 Баланс:</b> <code>{user['balance']:.3f} TON</code>",
                                    parse_mode="HTML"
                                )
                            except Exception as e:
                                print(f"Ошибка уведомления: {e}")
                                                                                                                                                    try:
                                await bot.send_message(
                                    ADMIN_ID,
                                    f"<b>💰 Новое пополнение!</b>\n\n"
                                    f"<b>👤 User ID:</b> <code>{user_id}</code>\n"
                                    f"<b>💎 Сумма:</b> <code>{amount:.3f} TON</code>\n"
                                    f"<b>🧾 Invoice:</b> <code>{invoice_id}</code>",
                                    parse_mode="HTML"
                                )
                            except:
                                pass
                                                                                                                                                    live_sales.insert(0, {
                                "type": "deposit",
                                "user_id": user_id,
                                "amount": amount,                                                                                                       "time": time.time()
                            })

        except Exception as e:                                                                                                      print(f"Ошибка проверки: {e}")

        await asyncio.sleep(5)
                                                                                                                        # ========== 🎯 КОМАНДЫ ==========
async def show_subscription_check(message: types.Message, user_id: int, ref_code: str = None):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url=REQUIRED_CHANNEL_URL)],
        [InlineKeyboardButton(text="✅ Проверить", callback_data=f"check_sub_{ref_code or 'none'}")]
    ])
                                                                                                                            await message.answer(
        f"<b>👋 Добро пожаловать!</b>\n\n"
        f"<b>🌾 Что вас ждет:</b>\n"
        f"• Выращивание растений\n"                                                                                             f"• Питомцы с доходом\n"
        f"• Торговля на рынке\n\n"
        f"<b>📢 Подпишитесь на канал:</b>\n"
        f"{REQUIRED_CHANNEL_URL}",                                                                                              parse_mode="HTML",
        reply_markup=keyboard
    )
                                                                                                                        async def process_start(message: types.Message, ref_code: str = None):
    """Обработка старта бота с учетом реферального кода"""
    user_id = message.from_user.id
    user = get_user_data(user_id)                                                                                       
    if user.get("banned", False):
        return await message.answer("<b>🚫 Вы заблокированы!</b>", parse_mode="HTML")
                                                                                                                            user["username"] = message.from_user.username
    user["first_name"] = message.from_user.first_name
    user["last_active"] = time.time()
                                                                                                                            # Обработка реферального кода ТОЛЬКО если еще нет реферера
    if ref_code and ref_code != "none" and ref_code.startswith("ref"):
        try:
            ref_id = int(ref_code[3:])                                                                                              if ref_id != user_id and not user["referrer"] and ref_id in users_data:
                user["referrer"] = ref_id
                ref_user = get_user_data(ref_id)
                ref_user["referrals"].append(user_id)

                bonus = 0.08
                ref_user["balance"] += bonus
                ref_user["stats"]["earned"] += bonus

                # УВЕДОМЛЕНИЕ АДМИНУ О РЕФЕРАЛЕ
                try:
                    await bot.send_message(
                        ADMIN_ID,
                        f"<b>👥 НОВЫЙ РЕФЕРАЛ!</b>\n\n"
                        f"<b>🎉 Кто пригласил:</b> <code>{ref_id}</code> (@{ref_user.get('username', 'N/A')})\n"
                        f"<b>👤 Кого пригласили:</b> <code>{user_id}</code> (@{user.get('username', 'N/A')})\n"
                        f"<b>💰 Бонус рефереру:</b> <code>{bonus:.3f} TON</code>\n"
                        f"<b>⏰ Время:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>",                                        parse_mode="HTML"
                    )
                except Exception as e:                                                                                                      print(f"Ошибка уведомления админу о реферале: {e}")

                try:                                                                                                                        await bot.send_message(
                        ref_id,
                        f"<b>🎉 Новый реферал!</b>\n\n"                                                                                         f"Пользователь {message.from_user.first_name} присоединился!\n"
                        f"<b>💰 Бонус:</b> <code>{bonus:.3f} TON</code>",
                        parse_mode="HTML"
                    )
                except:
                    pass
        except Exception as e:
            print(f"Ошибка обработки реферала: {e}")
                                                                                                                            welcome_text = (
        f"<b>🌾 Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
        f"<b>🎮 Возможности:</b>\n\n"                                                                                           f"<b>🌱 Фермерство:</b>\n"
        f"• Сажайте семена и собирайте урожай\n"
        f"• Чем дороже семя — тем больше прибыль\n\n"
        f"<b>🐾 Питомцы:</b>\n"
        f"• Пассивный доход каждый час\n"
        f"<b>🏪 Рынок:</b>\n"
        f"• Торгуйте питомцами\n\n"
        f"<b>🚀 Начните прямо сейчас!</b>"
    )

    await message.answer(welcome_text, parse_mode="HTML", reply_markup=main_keyboard(user_id))

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user = get_user_data(user_id)

    if user.get("banned", False):
        return await message.answer("<b>🚫 Вы заблокированы!</b>", parse_mode="HTML")

    is_subscribed = await check_subscription(user_id)
    if not is_subscribed:
        args = message.text.split()
        ref_code = None
        if len(args) > 1 and args[1].startswith("ref"):
            ref_code = args[1]
        return await show_subscription_check(message, user_id, ref_code)

    args = message.text.split()
    ref_code = None
    if len(args) > 1 and args[1].startswith("ref"):
        ref_code = args[1]

    await process_start(message, ref_code)                                                                              
@dp.callback_query(F.data.startswith("check_sub_"))
async def check_subscription_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id                                                                                         ref_code = callback.data[10:] if len(callback.data) > 10 else None

    is_subscribed = await check_subscription(user_id)
                                                                                                                            if is_subscribed:
        await callback.answer("✅ Подписка подтверждена!", show_alert=True)

        # Удаляем сообщение с проверкой подписки                                                                                try:
            await callback.message.delete()
        except:
            pass

        # Создаем фейковое сообщение для обработки старта
        class FakeMessage:                                                                                                          def __init__(self, user_id, username, first_name):
                self.from_user = type('obj', (object,), {
                    'id': user_id,
                    'username': username,                                                                                                   'first_name': first_name
                })()
                self.chat = type('obj', (object,), {'id': user_id})()
                                                                                                                                user = get_user_data(user_id)
        fake_message = FakeMessage(user_id, user.get("username"), user.get("first_name"))

        # Запускаем обработку старта с реферальным кодом                                                                        await process_start(fake_message, ref_code)
    else:
        await callback.answer("❌ Вы не подписаны!", show_alert=True)
                                                                                                                        # ========== 💰 БАЛАНС И ПЛАТЕЖИ ==========
@dp.message(F.text == "💰 Баланс")
async def balance(message: types.Message):
    user_id = message.from_user.id                                                                                      
    if not await check_subscription(user_id):
        return await show_subscription_check(message, user_id)
                                                                                                                            user = get_user_data(user_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Пополнить", callback_data="deposit")],                                                   [InlineKeyboardButton(text="💸 Вывести", callback_data="withdraw")],
        [InlineKeyboardButton(text="🔄 Фарм → Основной", callback_data="transfer_farm")]
    ])

    text = (
        f"<b>💰 Ваш баланс</b>\n\n"
        f"<b>💎 Основной:</b> <code>{user['balance']:.3f} TON</code>\n"
        f"<b>🏦 Фарм:</b> <code>{user['farm_balance']:.3f} TON</code>\n\n"
        f"<b>📊 Статистика:</b>\n"
        f"• Пополнено: <code>{user['stats']['deposited']:.3f} TON</code>\n"
        f"• Выведено: <code>{user['stats']['withdrawn']:.3f} TON</code>\n"
        f"• Заработано: <code>{user['stats']['earned']:.3f} TON</code>"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

@dp.callback_query(F.data == "transfer_farm")
async def transfer_farm(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)

    if user["farm_balance"] <= 0:
        return await callback.answer("❌ Фарм-баланс пуст!", show_alert=True)

    amount = user["farm_balance"]
    user["balance"] += amount
    user["farm_balance"] = 0.0

    await callback.answer(f"✅ Переведено {amount:.3f} TON!", show_alert=True)
    await balance(callback.message)                                                                                     
@dp.callback_query(F.data == "deposit")                                                                                 async def deposit_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(FarmStates.waiting_deposit_amount)
                                                                                                                            keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="main_menu")]
    ])
                                                                                                                            await callback.message.edit_text(
        f"<b>💳 Пополнение</b>\n\n"
        f"<b>Минимум:</b> {MIN_DEPOSIT} TON\n"                                                                                  f"<b>Комиссия:</b> 0%\n\n"
        f"<b>⚠️ Важно:</b> Без оплаты деньги не придут!\n\n"
        f"Введите сумму в TON:",                                                                                                parse_mode="HTML",
        reply_markup=keyboard
    )
                                                                                                                        @dp.message(FarmStates.waiting_deposit_amount, F.text.regexp(r"^\d+(\.\d+)?$"))
async def process_deposit(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
                                                                                                                            try:
        amount = float(message.text)
        if amount < MIN_DEPOSIT:
            return await message.answer(
                f"<b>❌ Минимум {MIN_DEPOSIT} TON!</b>",
                parse_mode="HTML"                                                                                                   )

        created_at = time.time()
        payload = f"deposit_{user_id}_{created_at}_{uuid.uuid4().hex[:8]}"
                                                                                                                                result = await create_invoice(amount, "TON", payload)

        if result.get("ok"):
            inv = result["result"]                                                                                                  invoice_id = str(inv["invoice_id"])

            pending_invoices[invoice_id] = {
                "user_id": user_id,                                                                                                     "amount": amount,
                "status": "pending",
                "created_at": created_at,
                "payload": payload                                                                                                  }

            print(f"📝 Счет {invoice_id} для {user_id} на {amount} TON")
                                                                                                                                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 ОПЛАТИТЬ", url=inv["pay_url"])],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
            ])                                                                                                          
            await message.answer(
                f"<b>💎 Счет создан!</b>\n\n"
                f"<b>🆔 Счет:</b> <code>#{inv['invoice_id']}</code>\n"                                                                  f"<b>💰 Сумма:</b> <code>{amount} TON</code>\n\n"
                f"<b>⚠️ Инструкция:</b>\n"
                f"1. Нажмите 'ОПЛАТИТЬ'\n"
                f"2. Оплатите в CryptoBot\n"                                                                                            f"3. <b>Баланс зачислится автоматически</b>",
                parse_mode="HTML",
                reply_markup=keyboard                                                                                               )
            await state.clear()
        else:
            error_msg = result.get('error', {}).get('message', 'Unknown error')                                                     await message.answer(f"<b>❌ Ошибка:</b>\n{error_msg}", parse_mode="HTML")

    except ValueError:
        await message.answer("<b>❌ Введите число!</b>", parse_mode="HTML")                                             
@dp.callback_query(F.data == "withdraw")
async def withdraw_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id                                                                                         user = get_user_data(user_id)

    if user["balance"] < MIN_WITHDRAW:
        return await callback.answer(                                                                                               f"❌ Минимум {MIN_WITHDRAW} TON!\nУ вас: {user['balance']:.3f} TON",
            show_alert=True
        )
                                                                                                                            await state.set_state(FarmStates.waiting_withdraw_amount)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="main_menu")]                                                 ])

    await callback.message.edit_text(
        f"<b>💸 Вывод</b>\n\n"                                                                                                  f"<b>Баланс:</b> <code>{user['balance']:.3f} TON</code>\n"
        f"<b>Минимум:</b> <code>{MIN_WITHDRAW} TON</code>\n"
        f"<b>Комиссия:</b> <code>{WITHDRAW_FEE*100}%</code>\n\n"
        f"Введите сумму:",                                                                                                      parse_mode="HTML",
        reply_markup=keyboard
    )
                                                                                                                        @dp.message(FarmStates.waiting_withdraw_amount, F.text.regexp(r"^\d+(\.\d+)?$"))
async def process_withdraw(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user_data(user_id)                                                                                       
    try:
        amount = float(message.text)
                                                                                                                                if amount < MIN_WITHDRAW:
            return await message.answer(
                f"<b>❌ Минимум {MIN_WITHDRAW} TON!</b>",
                parse_mode="HTML"                                                                                                   )

        if amount > user["balance"]:
            return await message.answer(                                                                                                f"<b>❌ Недостаточно средств!</b>\n"
                f"Баланс: {user['balance']:.3f} TON",
                parse_mode="HTML"
            )                                                                                                           
        fee = amount * WITHDRAW_FEE
        final_amount = amount - fee
                                                                                                                                await state.update_data(amount=amount, final_amount=final_amount)
        await state.set_state(FarmStates.waiting_withdraw_confirm)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[                                                                           [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_withdraw")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_withdraw")]
        ])
                                                                                                                                await message.answer(
            f"<b>💸 Подтверждение</b>\n\n"
            f"<b>Сумма:</b> <code>{amount:.3f} TON</code>\n"
            f"<b>Комиссия:</b> <code>{fee:.3f} TON</code>\n"                                                                        f"<b>Получите:</b> <code>{final_amount:.3f} TON</code>\n\n"
            f"<b>⏱ Займет 1-10 минут</b>\n\n"
            f"Подтверждаете?",
            parse_mode="HTML",                                                                                                      reply_markup=keyboard
        )

    except ValueError:
        await message.answer("<b>❌ Введите число!</b>", parse_mode="HTML")                                             
@dp.callback_query(F.data == "confirm_withdraw")
async def confirm_withdraw(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id                                                                                         user = get_user_data(user_id)

    data = await state.get_data()
    amount = data.get("amount")                                                                                             final_amount = data.get("final_amount")

    if not amount or user["balance"] < amount:
        await state.clear()                                                                                                     return await callback.answer("❌ Ошибка!", show_alert=True)

    req_id = f"wd_{user_id}_{uuid.uuid4().hex[:8]}"
                                                                                                                            pending_withdraws[req_id] = {
        "user_id": user_id,
        "amount": amount,
        "final_amount": final_amount,
        "created_at": time.time(),                                                                                              "status": "pending"
    }

    try:
        await bot.send_message(                                                                                                     ADMIN_ID,
            f"<b>🚨 ЗАЯВКА НА ВЫВОД!</b>\n\n"
            f"<b>🆔 ID:</b> <code>{req_id}</code>\n"
            f"<b>👤 User:</b> <code>{user_id}</code>\n"
            f"<b>💸 Сумма:</b> <code>{amount:.3f} TON</code>\n"                                                                     f"<b>💰 К получению:</b> <code>{final_amount:.3f} TON</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ ПОДТВЕРДИТЬ", callback_data=f"approve_{req_id}")],
                [InlineKeyboardButton(text="❌ ОТКЛОНИТЬ", callback_data=f"reject_{req_id}")]                                       ])
        )
    except Exception as e:
        print(f"Ошибка уведомления админа: {e}")                                                                        
    await state.clear()
                                                                                                                            await callback.message.edit_text(
        f"<b>⏳ Заявка создана!</b>\n\n"
        f"<b>🆔 ID:</b> <code>{req_id}</code>\n"                                                                                f"<b>Сумма:</b> <code>{amount:.3f} TON</code>\n"
        f"<b>Статус:</b> Ожидает подтверждения\n\n"
        f"<b>⏱ Обычно 1-10 минут</b>",                                                                                          parse_mode="HTML"
    )
                                                                                                                        @dp.callback_query(F.data == "cancel_withdraw")
async def cancel_withdraw(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()                                                                                                     await callback.answer("❌ Вывод отменен", show_alert=True)
    await balance(callback.message)

@dp.callback_query(F.data.startswith("approve_"))                                                                       async def approve_withdraw(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Нет доступа!", show_alert=True)                                                
    req_id = callback.data[8:]

    if req_id not in pending_withdraws:
        return await callback.answer("❌ Заявка не найдена!", show_alert=True)

    req = pending_withdraws[req_id]
    user_id = req["user_id"]
    amount = req["amount"]
    final_amount = req["final_amount"]

    user = get_user_data(user_id)

    if user["balance"] < amount:
        await callback.message.edit_text("<b>❌ Недостаточно средств!</b>", parse_mode="HTML")
        del pending_withdraws[req_id]
        return

    try:
        spend_id = f"withdraw_{req_id}_{int(time.time())}"
        result = await transfer(user_id, "TON", str(final_amount), spend_id)

        if result.get("ok"):
            user["balance"] -= amount
            user["stats"]["withdrawn"] += amount
            del pending_withdraws[req_id]

            try:
                await bot.send_message(
                    user_id,
                    f"<b>✅ Вывод выполнен!</b>\n\n"
                    f"<b>💸 Отправлено:</b> <code>{final_amount:.3f} TON</code>\n"
                    f"<b>ID:</b> <code>{spend_id}</code>",
                    parse_mode="HTML"
                )
            except:
                pass

            await callback.message.edit_text(
                f"<b>✅ ВЫВОД ВЫПОЛНЕН!</b>\n\n"
                f"Сумма: {final_amount:.3f} TON\n"
                f"User: {user_id}",
                parse_mode="HTML"
            )
        else:
            error = result.get('error', {}).get('name', 'Unknown')
            await callback.message.edit_text(f"<b>❌ Ошибка:</b> {error}", parse_mode="HTML")

    except Exception as e:
        await callback.message.edit_text(f"<b>❌ Ошибка:</b> {e}", parse_mode="HTML")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_withdraw(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Нет доступа!", show_alert=True)

    req_id = callback.data[7:]

    if req_id not in pending_withdraws:
        return await callback.answer("❌ Заявка не найдена!", show_alert=True)

    req = pending_withdraws[req_id]
    user_id = req["user_id"]

    del pending_withdraws[req_id]

    try:
        await bot.send_message(
            user_id,
            f"<b>❌ Заявка отклонена</b>\n\n"
            f"<b>ID:</b> <code>{req_id}</code>\n"
            f"<b>Сумма:</b> <code>{req['amount']:.3f} TON</code>",
            parse_mode="HTML"
        )
    except:
        pass

    await callback.message.edit_text(f"<b>❌ ОТКЛОНЕНО:</b> {req['amount']:.3f} TON", parse_mode="HTML")

# ========== 🌾 ФЕРМА ==========
@dp.message(F.text == "🌾 Моя Ферма")
async def my_farm(message: types.Message):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    user["last_active"] = time.time()

    if not await check_subscription(user_id):
        return await show_subscription_check(message, user_id)

    now = time.time()
    growing = 0
    ready = 0

    for plot in user["plots"]:
        grow_time = get_growth_time(user_id, plot["seed"])
        if now - plot["planted_at"] >= grow_time:
            ready += 1
        else:
            growing += 1

    max_plots = get_max_plots(user_id)

    text = (
        f"<b>🚜 Моя Ферма</b>\n\n"
        f"<b>👤 Уровень:</b> {user['level']}\n"
        f"<b>⭐ Опыт:</b> {user['xp']}/{calculate_level_xp(user['level'])}\n"
        f"<b>🌱 Грядки:</b> {len(user['plots'])}/{max_plots}\n"
        f"<b>🟡 Растет:</b> {growing} | <b>🟢 Готово:</b> {ready}\n\n"
        f"<b>💎 Баланс:</b> <code>{user['balance']:.3f} TON</code>\n"
        f"<b>🏦 Фарм:</b> <code>{user['farm_balance']:.3f} TON</code>"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=farm_keyboard())

@dp.callback_query(F.data == "plant_menu")
async def plant_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)

    available = get_available_plots(user_id)
    if available <= 0:
        return await callback.answer(
            "❌ Нет свободных грядок!\nКупите теплицу в улучшениях.",
            show_alert=True
        )

    buttons = []
    seeds_in_inv = {k: v for k, v in user["inventory"].items() if k.startswith("seed_")}

    if not seeds_in_inv:
        buttons.append([InlineKeyboardButton(
            text="❌ Нет семян — в магазин",
            callback_data="seed_shop"
        )])
    else:
        for item_id, count in seeds_in_inv.items():
            seed_id = item_id[5:]
            if seed_id in SEEDS:
                seed = SEEDS[seed_id]
                grow_time = format_time(get_growth_time(user_id, seed_id))
                reward = get_reward(user_id, seed_id)
                buttons.append([InlineKeyboardButton(
                    text=f"{seed['name']} x{count} | {grow_time} | +{reward:.3f}",
                    callback_data=f"plant_{seed_id}"
                )])

    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="farm_back")])

    await callback.message.edit_text(
        f"<b>🌱 Выберите семена</b>\n\n"
        f"<b>Свободно:</b> {available}/{get_max_plots(user_id)}\n\n"
        f"<b>Формат:</b> Название | Время | Прибыль",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("plant_"))
async def plant_seed(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    seed_id = callback.data[6:]

    if seed_id not in SEEDS:
        return await callback.answer("❌ Ошибка!", show_alert=True)

    seed = SEEDS[seed_id]

    if user["level"] < seed["level"]:
        return await callback.answer(
            f"❌ Нужен уровень {seed['level']}!",
            show_alert=True
        )

    inv_key = f"seed_{seed_id}"
    if user["inventory"].get(inv_key, 0) <= 0:
        return await callback.answer("❌ Нет семян!", show_alert=True)

    if get_available_plots(user_id) <= 0:
        return await callback.answer("❌ Нет грядок!", show_alert=True)

    user["inventory"][inv_key] -= 1
    if user["inventory"][inv_key] <= 0:
        del user["inventory"][inv_key]

    user["plots"].append({
        "seed": seed_id,
        "planted_at": time.time(),
        "boosted": False
    })

    user["stats"]["planted"] += 1

    grow_time = format_time(get_growth_time(user_id, seed_id))
    reward = get_reward(user_id, seed_id)

    await callback.answer(
        f"✅ {seed['name']} посажено!\n"
        f"⏱ {grow_time} | 💰 +{reward:.3f} TON",
        show_alert=True
    )
    await my_farm(callback.message)

@dp.callback_query(F.data == "harvest")
async def harvest_all(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)

    now = time.time()
    harvested = 0
    total_reward = 0.0
    total_xp = 0

    new_plots = []
    for plot in user["plots"]:
        grow_time = get_growth_time(user_id, plot["seed"])
        if now - plot["planted_at"] >= grow_time:                                                                                   seed = SEEDS[plot["seed"]]
            reward = get_reward(user_id, plot["seed"])
            total_reward += reward
            total_xp += seed["xp"]
            harvested += 1
        else:
            new_plots.append(plot)

    if harvested == 0:
        return await callback.answer(
            "⏳ Ничего не созрело!\nИспользуйте бустер мгновенного сбора.",
            show_alert=True
        )

    commission = total_reward * COMMISSION_FARM
    final_reward = total_reward - commission

    user["plots"] = new_plots
    user["farm_balance"] += final_reward
    user["stats"]["earned"] += final_reward
    user["stats"]["harvested"] += harvested

    leveled_up = add_xp(user_id, total_xp)

    text = (
        f"<b>🧺 Урожай собран!</b>\n\n"
        f"<b>Собрано:</b> {harvested}\n"
        f"<b>Прибыль:</b> <code>{total_reward:.4f} TON</code>\n"
        f"<b>Комиссия:</b> <code>{commission:.4f} TON</code>\n"
        f"<b>На фарм-баланс:</b> <code>{final_reward:.4f} TON</code>\n"
        f"<b>Опыт:</b> {total_xp} XP\n\n"
    )

    if leveled_up:
        text += f"<b>🎉 Новый уровень {user['level']}!</b>\n\n"

    text += f"<b>💡 Совет:</b> Переведите на основной баланс!"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="farm_back")]
    ])

    await callback.answer(f"✅ Собрано {harvested}! +{final_reward:.4f} TON", show_alert=True)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

@dp.callback_query(F.data == "seed_shop")
async def seed_shop(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)

    text = (
        f"<b>🛒 Магазин семян</b>\n"
        f"<b>Баланс:</b> <code>{user['balance']:.3f} TON</code>\n\n"
    )

    buttons = []

    for seed_id, seed in SEEDS.items():
        if seed_id == "tulip":
            cooldown = seed["free_cooldown"]
            time_left = max(0, user.get("last_free_tulip", 0) + cooldown - time.time())

            if time_left > 0:
                status = f"⏳ Через: {format_time(int(time_left))}"
                text += f"<b>{seed['name']}</b> — {status}\n\n"
            else:
                status = "✅ Бесплатно!"
                text += f"<b>{seed['name']}</b> — {status}\n"
                text += f"   🎁 Бесплатно | 3ч | +0.0005 TON\n\n"
                buttons.append([InlineKeyboardButton(
                    text="🆓 Получить тюльпан",
                    callback_data=f"buyseed_{seed_id}"
                )])

        else:
            if user["level"] >= seed["level"]:
                grow_time = format_time(seed["time"])

                text += f"<b>{seed['name']}</b> — {seed['price']:.2f} TON\n"
                text += f"   ⏱ {grow_time} | 💰 +{seed['reward']:.2f} TON\n"
                text += f"   ⭐ Уровень: {seed['level']}\n\n"

                buttons.append([InlineKeyboardButton(
                    text=f"Купить {seed['name']} — {seed['price']:.2f} TON",
                    callback_data=f"buyseed_{seed_id}"
                )])
            else:
                text += f"<b>{seed['name']}</b> — 🔒 Уровень {seed['level']}\n\n"

    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="farm_back")])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("buyseed_"))
async def buy_seed(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    seed_id = callback.data[8:]

    if seed_id not in SEEDS:
        return await callback.answer("❌ Ошибка!", show_alert=True)

    seed = SEEDS[seed_id]

    if seed_id == "tulip" and seed["price"] == 0:
        cooldown = seed["free_cooldown"]
        if time.time() - user.get("last_free_tulip", 0) < cooldown:
            time_left = int(user.get("last_free_tulip", 0) + cooldown - time.time())
            return await callback.answer(
                f"⏳ Подождите {format_time(time_left)}!",
                show_alert=True
            )

        user["last_free_tulip"] = time.time()
        user["inventory"]["seed_tulip"] = user["inventory"].get("seed_tulip", 0) + 1

        await callback.answer("✅ Тюльпан получен!", show_alert=True)
        return await seed_shop(callback)

    price = seed["price"]

    if user["balance"] < price:
        return await callback.answer(
            f"❌ Нужно: {price:.2f} TON\nУ вас: {user['balance']:.3f} TON",
            show_alert=True
        )

    grow_time = format_time(get_growth_time(user_id, seed_id))
    reward = get_reward(user_id, seed_id)

    await state.update_data(seed_id=seed_id, price=price)
    await state.set_state(FarmStates.waiting_buy_seed_confirm)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Купить", callback_data=f"confirm_buy_{seed_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="seed_shop")]
    ])

    await callback.message.edit_text(
        f"<b>🛒 Покупка</b>\n\n"
        f"<b>{seed['name']}</b>\n"
        f"<b>Время:</b> {grow_time}\n"
        f"<b>Прибыль:</b> +{reward:.3f} TON\n"
        f"<b>Цена:</b> {price:.2f} TON\n\n"
        f"Подтверждаете?",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("confirm_buy_"))
async def confirm_buy_seed(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    seed_id = callback.data[12:]

    if seed_id not in SEEDS:
        await state.clear()
        return await callback.answer("❌ Ошибка!", show_alert=True)

    seed = SEEDS[seed_id]
    price = seed["price"]

    if user["balance"] < price:
        await state.clear()
        return await callback.answer("❌ Недостаточно средств!", show_alert=True)

    user["balance"] -= price
    user["stats"]["spent"] += price
    user["inventory"][f"seed_{seed_id}"] = user["inventory"].get(f"seed_{seed_id}", 0) + 1

    await state.clear()

    await callback.answer(
        f"✅ {seed['name']} куплен!\n"
        f"💰 Списано: {price:.2f} TON",
        show_alert=True
    )
    await seed_shop(callback)

@dp.callback_query(F.data == "plots_status")
async def plots_status(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)

    now = time.time()
    text = "<b>🟫 Статус грядок</b>\n\n"

    if not user["plots"]:
        text += (
            "Нет посаженных растений.\n\n"
            "<b>Как начать:</b>\n"
            f"1. Купите семена\n"
            f"2. Нажмите '🌱 Посадить'\n"
            f"3. Ждите созревания!"
        )
    else:
        text += f"<b>Всего:</b> {len(user['plots'])}/{get_max_plots(user_id)}\n\n"

        for i, plot in enumerate(user["plots"], 1):
            seed = SEEDS[plot["seed"]]
            grow_time = get_growth_time(user_id, plot["seed"])
            elapsed = now - plot["planted_at"]
            remaining = max(0, grow_time - elapsed)
            progress = min(100, int((elapsed / grow_time) * 100))

            bar = "█" * (progress // 10) + "░" * (10 - progress // 10)

            if remaining <= 0:
                text += (
                    f"<b>{i}. {seed['name']}</b> ✅ ГОТОВО!\n"
                    f"   💰 +{get_reward(user_id, plot['seed']):.3f} TON\n\n"
                )
            else:
                text += (
                    f"<b>{i}. {seed['name']}</b>\n"
                    f"   [{bar}] {progress}%\n"
                    f"   ⏱ {format_time(int(remaining))}\n\n"
                )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="farm_back")]
    ])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

# ========== 🎒 ИНВЕНТАРЬ ==========
@dp.message(F.text == "🎒 Инвентарь")
async def inventory(message: types.Message):
    user_id = message.from_user.id

    if not await check_subscription(user_id):
        return await show_subscription_check(message, user_id)

    user = get_user_data(user_id)

    text = f"<b>🎒 Инвентарь</b>\n\n"

    if not user["inventory"]:
        text += (
            "Инвентарь пуст.\n\n"
            "<b>Как пополнить:</b>\n"
            "• Купите семена в магазине\n"
            "• Бесплатный тюльпан каждые 4ч\n"
            "• Выполняйте задания"
        )
    else:
        seeds = {k: v for k, v in user["inventory"].items() if k.startswith("seed_")}
        if seeds:
            text += "<b>🌱 Семена:</b>\n"
            for item, count in seeds.items():
                seed_id = item[5:]
                seed = SEEDS.get(seed_id, {})
                seed_name = seed.get("name", seed_id)
                grow_time = format_time(get_growth_time(user_id, seed_id))
                reward = get_reward(user_id, seed_id)
                text += f"  • {seed_name} — x{count} (⏱{grow_time} 💰+{reward:.3f})\n"

            text += f"\n<b>Всего:</b> {sum(seeds.values())}"

    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(user_id))

# ========== 🐾 ПИТОМЦЫ ==========
@dp.message(F.text == "🐾 Питомцы")
async def pets_menu(message: types.Message):
    user_id = message.from_user.id

    if not await check_subscription(user_id):
        return await show_subscription_check(message, user_id)

    user = get_user_data(user_id)
    now = time.time()

    available_pets = [p for p in user["pets"] if not p.get("market_id")]

    if not available_pets:
        text = (
            "<b>🐾 У вас нет питомцев</b>\n\n"
            "<b>Зачем нужны:</b>\n"
            "• Пассивный доход каждый час\n"
            "• Кормите раз в 12 часов\n\n"
            "<b>Доступные:</b>\n"
            "• 🐔 Курица — 2 TON (0.001/ч)\n"
            "• 🐰 Кролик — 5 TON (0.003/ч)\n"
            "• 🐑 Овечка — 15 TON (0.008/ч)\n"
            "• 🐄 Корова — 50 TON (0.025/ч)\n"
            "• 🐷 Свинья — 120 TON (0.060/ч)\n"
            "• 🐴 Лошадь — 300 TON (0.150/ч)\n"
            "• 🐉 Дракон — 1000 TON (0.500/ч)"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏪 В магазин", callback_data="pet_shop")]
        ])
    else:
        text = f"<b>🐾 Мои питомцы</b>\n\n"
        total_hourly = 0

        for i, pet in enumerate(available_pets, 1):
            pet_data = PETS[pet["type"]]
            fed = pet["fed_until"] > now
            hours_left = (pet["fed_until"] - now) / 3600
            hourly_income = calculate_pet_hourly(pet["type"], user_id)
            total_hourly += hourly_income if fed else 0

            if fed:
                status = f"🟢 Активен ({hours_left:.1f}ч)"
                income_text = f"💰 {hourly_income:.4f}/ч"
            else:
                status = f"🔴 Голоден!"
                income_text = "💰 0 (покормите!)"

            text += f"<b>{i}. {pet_data['name']}</b>\n"
            text += f"   {status} | {income_text}\n\n"

        daily_income = total_hourly * 24

        text += (
            f"<b>📊 Доход:</b>\n"
            f"• В час: {total_hourly:.4f} TON\n"
            f"• В день: {daily_income:.3f} TON\n\n"
            f"<b>💡 Кормите каждые 12ч!</b>"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🍖 Кормить всех", callback_data="feed_pets")],
            [InlineKeyboardButton(text="💰 Собрать", callback_data="claim_pets")],
            [InlineKeyboardButton(text="🏪 Купить еще", callback_data="pet_shop")]
        ])

    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

@dp.callback_query(F.data == "pet_shop")
async def pet_shop(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)

    owned_types = [p["type"] for p in user["pets"]]

    text = (
        f"<b>🏪 Магазин питомцев</b>\n"
        f"<b>Баланс:</b> <code>{user['balance']:.3f} TON</code>\n\n"
    )

    buttons = []

    for pet_id, pet in PETS.items():
        hourly = calculate_pet_hourly(pet_id, user_id)
        daily = hourly * 24

        if pet_id in owned_types:
            text += f"<b>{pet['name']}</b> — ✅ Есть\n"
            text += f"   💰 {hourly:.4f}/ч\n\n"
        elif user["level"] >= pet["level"]:
            text += f"<b>{pet['name']}</b> — {pet['price']:.2f} TON\n"
            text += f"   💰 {hourly:.4f}/ч ({daily:.3f}/день)\n"
            text += f"   ⭐ Уровень {pet['level']}\n\n"

            buttons.append([InlineKeyboardButton(
                text=f"Купить {pet['name']} — {pet['price']:.2f} TON",
                callback_data=f"buypet_{pet_id}"
            )])
        else:
            text += f"<b>{pet['name']}</b> — 🔒 Уровень {pet['level']}\n\n"

    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="pets_back")])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("buypet_"))
async def buy_pet(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    pet_id = callback.data[7:]

    if pet_id not in PETS:
        return await callback.answer("❌ Ошибка!", show_alert=True)

    if any(p["type"] == pet_id for p in user["pets"]):
        return await callback.answer("❌ Уже есть!", show_alert=True)

    pet = PETS[pet_id]

    if user["balance"] < pet["price"]:                                                                                          return await callback.answer(
            f"❌ Нужно: {pet['price']:.2f} TON",
            show_alert=True
        )                                                                                                               
    hourly = calculate_pet_hourly(pet_id, user_id)
    daily = hourly * 24                                                                                                 
    await state.update_data(pet_id=pet_id, price=pet["price"])
    await state.set_state(FarmStates.waiting_buy_pet_confirm)                                                           
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Купить", callback_data=f"confirm_pet_{pet_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="pet_shop")]
    ])                                                                                                                  
    await callback.message.edit_text(
        f"<b>🐾 {pet['name']}</b>\n\n"
        f"<b>Доход:</b> {hourly:.4f}/ч ({daily:.3f}/день)\n"
        f"<b>Цена:</b> {pet['price']:.2f} TON\n\n"                                                                              f"Подтверждаете?",
        parse_mode="HTML",
        reply_markup=keyboard
    )
                                                                                                                        @dp.callback_query(F.data.startswith("confirm_pet_"))
async def confirm_buy_pet(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    pet_id = callback.data[12:]                                                                                         
    if pet_id not in PETS:
        await state.clear()
        return await callback.answer("❌ Ошибка!", show_alert=True)                                                     
    pet = PETS[pet_id]

    if any(p["type"] == pet_id for p in user["pets"]):
        await state.clear()                                                                                                     return await callback.answer("❌ Уже есть!", show_alert=True)

    if user["balance"] < pet["price"]:
        await state.clear()
        return await callback.answer("❌ Недостаточно средств!", show_alert=True)
                                                                                                                            user["balance"] -= pet["price"]
    user["stats"]["spent"] += pet["price"]

    now = time.time()
    user["pets"].append({                                                                                                       "type": pet_id,
        "bought_at": now,
        "fed_until": now + pet["feed_time"],
        "last_collect": now
    })                                                                                                                  
    await state.clear()

    await callback.answer(
        f"🐾 {pet['name']} куплен!\n"                                                                                           f"💰 Списано: {pet['price']:.2f} TON",
        show_alert=True
    )
    await pets_menu(callback.message)                                                                                   
@dp.callback_query(F.data == "feed_pets")
async def feed_pets(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    now = time.time()

    hungry_pets = [p for p in user["pets"] if p["fed_until"] <= now and not p.get("market_id")]
                                                                                                                            if not hungry_pets:
        return await callback.answer("🟢 Все сыты!", show_alert=True)
                                                                                                                            for pet in hungry_pets:
        pet_data = PETS[pet["type"]]
        pet["fed_until"] = now + pet_data["feed_time"]                                                                          pet["last_collect"] = now

    await callback.answer(f"🍖 Накормлено {len(hungry_pets)}!", show_alert=True)
    await pets_menu(callback.message)                                                                                   
@dp.callback_query(F.data == "claim_pets")
async def claim_pets(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)                                                                                           now = time.time()

    total_income = 0.0
    fed_pets_count = 0
                                                                                                                            for pet in user["pets"]:
        if pet.get("market_id"):
            continue

        pet_data = PETS[pet["type"]]                                                                                    
        if pet["fed_until"] > now:
            hours_passed = (now - pet.get("last_collect", pet["bought_at"])) / 3600
            hours_passed = min(hours_passed, 12)

            income = pet_data["income"] * hours_passed                                                                  
            if user["upgrades"].get("warehouse", 0) > 0:
                income *= 2

            total_income += income                                                                                                  pet["last_collect"] = now
            fed_pets_count += 1

    if total_income <= 0:
        return await callback.answer("❌ Нет дохода! Покормите питомцев!", show_alert=True)                             
    commission = total_income * COMMISSION_PET_CLAIM
    final_income = total_income - commission

    user["farm_balance"] += final_income                                                                                    user["stats"]["earned"] += final_income

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="pets_back")]
    ])                                                                                                                  
    await callback.answer(f"💰 Собрано {final_income:.4f} TON!", show_alert=True)
    await callback.message.edit_text(
        f"<b>💰 Доход собран!</b>\n\n"                                                                                          f"<b>Питомцев:</b> {fed_pets_count}\n"
        f"<b>Сумма:</b> <code>{total_income:.4f} TON</code>\n"
        f"<b>Комиссия:</b> <code>{commission:.4f} TON</code>\n"
        f"<b>На фарм-баланс:</b> <code>{final_income:.4f} TON</code>",                                                          parse_mode="HTML",
        reply_markup=keyboard
    )
                                                                                                                        # ========== ⬆️ УЛУЧШЕНИЯ ==========
@dp.message(F.text == "⬆️ Улучшения")
async def upgrades_menu(message: types.Message):
    user_id = message.from_user.id

    if not await check_subscription(user_id):
        return await show_subscription_check(message, user_id)

    user = get_user_data(user_id)

    text = (
        f"<b>⬆️ Улучшения</b>\n"                                                                                                 f"<b>Баланс:</b> <code>{user['balance']:.3f} TON</code>\n\n"
    )

    buttons = []
                                                                                                                            for up_id, upg in UPGRADES.items():
        current = user["upgrades"].get(up_id, 0)

        if current >= upg["max"]:
            text += f"<b>✅ {upg['name']}</b> — Макс ({upg['max']}/{upg['max']})\n"                                                 text += f"   {upg['desc']}\n\n"
        else:
            text += f"<b>{upg['name']}</b> ({current}/{upg['max']}) — {upg['price']:.2f} TON\n"
            text += f"   {upg['desc']}\n\n"
                                                                                                                                    buttons.append([InlineKeyboardButton(
                text=f"Купить {upg['name']} — {upg['price']:.2f} TON",
                callback_data=f"upgrade_{up_id}"
            )])

    if not buttons:                                                                                                             text += "<b>🎉 Все куплены!</b>"

    await message.answer(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("upgrade_"))                                                                       async def buy_upgrade(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    up_id = callback.data[8:]
                                                                                                                            if up_id not in UPGRADES:
        return await callback.answer("❌ Ошибка!", show_alert=True)

    upg = UPGRADES[up_id]
    current = user["upgrades"].get(up_id, 0)                                                                            
    if current >= upg["max"]:
        return await callback.answer("❌ Максимум!", show_alert=True)

    if user["balance"] < upg["price"]:                                                                                          return await callback.answer("❌ Недостаточно средств!", show_alert=True)

    user["balance"] -= upg["price"]
    user["stats"]["spent"] += upg["price"]
    user["upgrades"][up_id] = current + 1                                                                               
    if up_id == "greenhouse":
        user["max_plots"] += upg["value"]
    elif up_id == "megafarm":
        user["max_plots"] += 3                                                                                          
    await callback.answer(
        f"✅ {upg['name']} улучшен!\n"
        f"Уровень: {user['upgrades'][up_id]}/{upg['max']}",
        show_alert=True
    )                                                                                                                       await upgrades_menu(callback.message)

# ========== 🏪 РЫНОК ==========
@dp.message(F.text == "🏪 Рынок")
async def market_menu(message: types.Message):                                                                              user_id = message.from_user.id

    if not await check_subscription(user_id):
        return await show_subscription_check(message, user_id)
                                                                                                                            keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Купить", callback_data="market_list")],
        [InlineKeyboardButton(text="➕ Продать", callback_data="market_sell_select")],
        [InlineKeyboardButton(text="🔍 Мои лоты", callback_data="market_my")]
    ])                                                                                                                  
    active_lots = len([l for l in market_listings.values() if not l["sold"] and l["expires_at"] > time.time()])

    await message.answer(
        f"<b>🏪 Рынок питомцев</b>\n\n"                                                                                         f"<b>💡 Комиссия:</b> {COMMISSION_MARKET*100}%\n\n"
        f"<b>📊 Активных лотов:</b> {active_lots}\n\n"
        f"Выберите действие:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "market_list")
async def market_list(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    active_lots = {
        k: v for k, v in market_listings.items()
        if not v["sold"] and v["expires_at"] > time.time()
    }

    if not active_lots:
        return await callback.message.edit_text(
            "<b>🏪 Рынок пуст</b>\n\n"
            "Нет активных лотов.\n"
            "Будьте первым! Продайте питомца.",
            parse_mode="HTML"
        )

    lots_list = sorted(active_lots.items(), key=lambda x: x[1]["created_at"], reverse=True)

    text = "<b>🏪 Доступные:</b>\n\n"
    buttons = []

    for lot_id, lot in lots_list[:10]:
        pet = PETS[lot["pet_type"]]
        time_left = max(0, lot["expires_at"] - time.time())

        text += f"<b>🐾 {pet['name']}</b>\n"
        text += f"   💰 {lot['price']:.2f} TON | ⏱ {format_time(int(time_left))}\n\n"

        if lot["seller_id"] != user_id:
            buttons.append([InlineKeyboardButton(
                text=f"Купить {pet['name']} за {lot['price']:.2f} TON",
                callback_data=f"market_buy_{lot_id}"
            )])

    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="market_back")])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("market_buy_"))
async def market_buy(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    lot_id = callback.data[11:]

    if lot_id not in market_listings:
        return await callback.answer("❌ Лот не найден!", show_alert=True)

    lot = market_listings[lot_id]

    if lot["sold"] or lot["expires_at"] <= time.time():
        return await callback.answer("❌ Лот недоступен!", show_alert=True)

    if lot["seller_id"] == user_id:
        return await callback.answer("❌ Это ваш лот!", show_alert=True)

    if user["balance"] < lot["price"]:
        return await callback.answer("❌ Недостаточно средств!", show_alert=True)

    if any(p["type"] == lot["pet_type"] for p in user["pets"]):
        return await callback.answer("❌ Уже есть такой!", show_alert=True)

    await state.update_data(lot_id=lot_id, price=lot["price"])
    await state.set_state(FarmStates.waiting_market_buy_confirm)

    pet = PETS[lot["pet_type"]]
    commission = lot["price"] * COMMISSION_MARKET

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Купить", callback_data=f"confirm_market_{lot_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="market_list")]
    ])

    await callback.message.edit_text(
        f"<b>🐾 {pet['name']}</b>\n\n"
        f"<b>Доход:</b> {pet['income']:.4f}/ч\n"
        f"<b>Цена:</b> {lot['price']:.2f} TON\n"
        f"<b>Комиссия:</b> {commission:.2f} TON\n\n"
        f"Подтверждаете?",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("confirm_market_"))
async def confirm_market_buy(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    lot_id = callback.data[15:]

    if lot_id not in market_listings:
        await state.clear()
        return await callback.answer("❌ Лот не найден!", show_alert=True)

    lot = market_listings[lot_id]

    if lot["sold"] or lot["expires_at"] <= time.time():
        await state.clear()
        return await callback.answer("❌ Лот недоступен!", show_alert=True)                                             
    if user["balance"] < lot["price"]:
        await state.clear()
        return await callback.answer("❌ Недостаточно средств!", show_alert=True)
                                                                                                                            commission = lot["price"] * COMMISSION_MARKET
    seller_gets = lot["price"] - commission

    user["balance"] -= lot["price"]
    seller = get_user_data(lot["seller_id"])                                                                                seller["balance"] += seller_gets

    pet_to_transfer = None
    for pet in seller["pets"]:
        if pet["type"] == lot["pet_type"] and pet.get("market_id") == lot_id:                                                       pet_to_transfer = pet
            break

    if pet_to_transfer:
        seller["pets"].remove(pet_to_transfer)
        del pet_to_transfer["market_id"]
        user["pets"].append(pet_to_transfer)

    lot["sold"] = True
    lot["buyer_id"] = user_id

    try:
        await bot.send_message(
            lot["seller_id"],
            f"<b>💰 Продано!</b>\n\n"
            f"<b>🐾</b> {PETS[lot['pet_type']]['name']}\n"
            f"<b>💵</b> Получено: {seller_gets:.2f} TON",
            parse_mode="HTML"
        )
    except:
        pass

    await state.clear()

    await callback.answer("✅ Куплено!", show_alert=True)
    await market_list(callback)

@dp.callback_query(F.data == "market_sell_select")
async def market_sell_select(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)

    available_pets = [p for p in user["pets"] if not p.get("market_id")]

    if not available_pets:
        return await callback.answer("❌ Нет питомцев для продажи!", show_alert=True)

    buttons = []
    for i, pet in enumerate(user["pets"]):
        if not pet.get("market_id"):
            pet_data = PETS[pet["type"]]
            buttons.append([InlineKeyboardButton(
                text=f"Продать {pet_data['name']}",
                callback_data=f"sellpet_{i}"
            )])

    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="market_back")])

    await callback.message.edit_text(
        "<b>➕ Продажа</b>\n\n"
        "Выберите питомца:\n\n"
        f"<b>💡 Комиссия:</b> {COMMISSION_MARKET*100}%\n"
        f"<b>⏱ Лот:</b> 24 часа",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("sellpet_"))
async def market_sell_price(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    pet_index = int(callback.data[8:])

    user = get_user_data(user_id)
    if pet_index >= len(user["pets"]):
        return await callback.answer("❌ Ошибка!", show_alert=True)

    pet = user["pets"][pet_index]

    if pet.get("market_id"):
        return await callback.answer("❌ Уже на продаже!", show_alert=True)

    pet_data = PETS[pet["type"]]

    await state.update_data(pet_index=pet_index, pet_type=pet["type"])
    await state.set_state(FarmStates.waiting_market_price)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="market_back")]
    ])

    await callback.message.edit_text(
        f"<b>➕ Продажа {pet_data['name']}</b>\n\n"
        f"<b>Рекомендуемая:</b> {pet_data['price']:.2f} TON\n\n"
        f"<b>💡 Цена:</b> 80-120% от базовой\n"
        f"<b>Минимум:</b> 0.1 TON\n\n"
        f"Введите цену:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.message(FarmStates.waiting_market_price, F.text.regexp(r"^\d+(\.\d+)?$"))
async def process_market_price(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    data = await state.get_data()
    pet_index = data["pet_index"]
    pet_type = data["pet_type"]

    try:
        price = float(message.text)
        if price < 0.1:
            return await message.answer("<b>❌ Минимум 0.1 TON!</b>", parse_mode="HTML")

        pet = user["pets"][pet_index]
        pet_data = PETS[pet_type]

        lot_id = f"lot_{user_id}_{int(time.time())}"
        pet["market_id"] = lot_id

        market_listings[lot_id] = {
            "seller_id": user_id,
            "pet_type": pet_type,
            "price": price,
            "created_at": time.time(),
            "expires_at": time.time() + 86400,
            "sold": False
        }

        await state.clear()

        await message.answer(
            f"<b>✅ Лот создан!</b>\n\n"
            f"<b>🐾</b> {pet_data['name']}\n"
            f"<b>💰</b> {price:.2f} TON\n"
            f"<b>⏱</b> 24 часа\n\n"
            f"Удачной продажи!",
            parse_mode="HTML",
            reply_markup=main_keyboard(user_id)
        )

    except Exception as e:
        await message.answer(f"<b>❌ Ошибка:</b> {e}", parse_mode="HTML")

@dp.callback_query(F.data == "market_my")
async def market_my(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    my_lots = {
        k: v for k, v in market_listings.items()
        if v["seller_id"] == user_id and not v["sold"]
    }                                                                                                                   
    if not my_lots:
        return await callback.message.edit_text(                                                                                    "<b>📭 Нет активных лотов</b>\n\n"
            "Создайте лот через '➕ Продать'",
            parse_mode="HTML"
        )                                                                                                               
    text = "<b>📋 Мои лоты:</b>\n\n"
    buttons = []

    for lot_id, lot in my_lots.items():
        pet = PETS[lot["pet_type"]]
        time_left = max(0, lot["expires_at"] - time.time())

        text += f"<b>🐾 {pet['name']}</b>\n"
        text += f"   💰 {lot['price']:.2f} TON | ⏱ {format_time(int(time_left))}\n\n"
                                                                                                                                buttons.append([InlineKeyboardButton(
            text=f"❌ Снять {pet['name']}",
            callback_data=f"market_cancel_{lot_id}"
        )])

    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="market_back")])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("market_cancel_"))
async def market_cancel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lot_id = callback.data[14:]

    if lot_id not in market_listings:
        return await callback.answer("❌ Лот не найден!", show_alert=True)

    lot = market_listings[lot_id]

    if lot["seller_id"] != user_id:
        return await callback.answer("❌ Не ваш лот!", show_alert=True)

    user = get_user_data(user_id)
    for pet in user["pets"]:
        if pet.get("market_id") == lot_id:
            del pet["market_id"]
            break

    del market_listings[lot_id]

    await callback.answer("✅ Снято с продажи!", show_alert=True)
    await market_menu(callback.message)
                                                                                                                        @dp.callback_query(F.data == "market_back")
async def market_back(callback: types.CallbackQuery):
    await market_menu(callback.message)                                                                                 
# ========== 🚀 БУСТЕРЫ ==========
@dp.message(F.text == "🚀 Бустеры")                                                                                     async def boosters_menu(message: types.Message):
    user_id = message.from_user.id

    if not await check_subscription(user_id):
        return await show_subscription_check(message, user_id)

    user = get_user_data(user_id)

    text = (
        f"<b>🚀 Бустеры</b>\n"
        f"<b>Баланс:</b> <code>{user['balance']:.3f} TON</code>\n\n"
    )

    buttons = []

    for boost_id, boost in BOOSTERS.items():
        duration_text = format_time(boost["duration"]) if boost["duration"] > 0 else "Мгновенно"

        text += f"{boost['emoji']} <b>{boost['name']}</b> — {boost['price']:.2f} TON\n"
        text += f"   {boost['desc']}\n"
        text += f"   ⏱ {duration_text}\n\n"

        buttons.append([InlineKeyboardButton(
            text=f"Купить {boost['name']} — {boost['price']:.2f} TON",
            callback_data=f"buyboost_{boost_id}"
        )])

    await message.answer(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("buyboost_"))
async def buy_booster(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    boost_id = callback.data[9:]

    if boost_id not in BOOSTERS:
        return await callback.answer("❌ Ошибка!", show_alert=True)

    boost = BOOSTERS[boost_id]

    if user["balance"] < boost["price"]:
        return await callback.answer("❌ Недостаточно средств!", show_alert=True)

    user["balance"] -= boost["price"]
    user["stats"]["spent"] += boost["price"]

    now = time.time()

    if boost_id == "instant":
        if not user["plots"]:
            return await callback.answer("❌ Нет растений!", show_alert=True)

        for plot in user["plots"]:
            plot["planted_at"] = 0

        await callback.answer("⏰ Все созрело!", show_alert=True)
    else:
        user["boosters"].append({
            "type": boost_id,
            "expires_at": now + boost["duration"],
            "started_at": now
        })

        await callback.answer(f"✅ {boost['name']} активирован!", show_alert=True)

    await boosters_menu(callback.message)

# ========== 🎯 ЗАДАНИЯ ==========
@dp.message(F.text == "🎯 Задания")
async def tasks_menu(message: types.Message):
    user_id = message.from_user.id

    if not await check_subscription(user_id):
        return await show_subscription_check(message, user_id)

    user = get_user_data(user_id)

    # Находим первое невыполненное задание
    current_task = None
    for task in tasks:
        if task["id"] not in user["tasks_completed"]:
            current_task = task
            break

    if not current_task:
        return await message.answer(
            "<b>🎉 Все выполнены!</b>\n\n"
            f"<b>Прогресс:</b> {len(user['tasks_completed'])}/{len(tasks)}",
            parse_mode="HTML",
            reply_markup=main_keyboard(user_id)
        )

    text = (
        f"<b>🎯 Текущее задание</b>\n\n"
        f"<b>{current_task['name']}</b>\n"
        f"{current_task['description']}\n\n"
        f"<b>🎁 Награда:</b> {current_task.get('reward_amount', 1)} семян тюльпана\n\n"
        f"<b>Прогресс:</b> {len(user['tasks_completed'])}/{len(tasks)}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Перейти", url=current_task["url"])],
        [InlineKeyboardButton(text="✅ Выполнил", callback_data=f"task_done_{current_task['id']}")]
    ])

    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("task_done_"))
async def task_done(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user_data(user_id)
    task_id = int(callback.data[10:])

    # Проверяем, не выполнено ли уже                                                                                        if task_id in user["tasks_completed"]:
        # Удаляем сообщение со старым заданием                                                                                  try:
            await callback.message.delete()                                                                                     except:
            pass
        # Показываем следующее задание
        return await show_next_task(callback.message, user_id)

    # Проверяем попытки
    attempts = user["tasks_attempts"].get(task_id, 0)

    if attempts < 1:
        user["tasks_attempts"][task_id] = attempts + 1                                                                          return await callback.answer(
            "❌ Проверьте выполнение!\nПопробуйте снова.",
            show_alert=True
        )                                                                                                               
    # Находим задание
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:                                                                                                                return await callback.answer("❌ Задание не найдено!", show_alert=True)

    # Отмечаем как выполненное
    user["tasks_completed"].append(task_id)                                                                             
    # Выдаем награду
    reward_type = task.get("reward_type", "seed_tulip")
    reward_amount = task.get("reward_amount", 1)                                                                            user["inventory"][reward_type] = user["inventory"].get(reward_type, 0) + reward_amount

    # Уведомляем о награде                                                                                                  await callback.answer(f"🎉 Получено: {reward_amount} семян!", show_alert=True)

    # Удаляем сообщение со старым заданием
    try:                                                                                                                        await callback.message.delete()
    except:
        pass
                                                                                                                            # Показываем следующее задание
    await show_next_task(callback.message, user_id)

async def show_next_task(message: types.Message, user_id: int):                                                             """Показывает следующее доступное задание"""                                                                            user = get_user_data(user_id)

    # Находим следующее невыполненное задание                                                                               next_task = None
    for task in tasks:
        if task["id"] not in user["tasks_completed"]:
            next_task = task                                                                                                        break

    if not next_task:
        # Все задания выполнены                                                                                                 await message.answer(
            "<b>🎉 Все задания выполнены!</b>\n\n"
            f"<b>Прогресс:</b> {len(user['tasks_completed'])}/{len(tasks)}",
            parse_mode="HTML",                                                                                                      reply_markup=main_keyboard(user_id)
        )
    else:
        # Показываем следующее задание                                                                                          text = (
            f"<b>🎯 Следующее задание</b>\n\n"
            f"<b>{next_task['name']}</b>\n"
            f"{next_task['description']}\n\n"
            f"<b>🎁 Награда:</b> {next_task.get('reward_amount', 1)} семян тюльпана\n\n"
            f"<b>Прогресс:</b> {len(user['tasks_completed'])}/{len(tasks)}"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Перейти", url=next_task["url"])],
            [InlineKeyboardButton(text="✅ Выполнил", callback_data=f"task_done_{next_task['id']}")]
        ])

        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

# ========== 👥 РЕФЕРАЛЫ ==========                                                                                     @dp.message(F.text == "👥 Рефералы")
async def referrals(message: types.Message):
    user_id = message.from_user.id

    if not await check_subscription(user_id):
        return await show_subscription_check(message, user_id)                                                          
    user = get_user_data(user_id)

    bot_info = await bot.me()                                                                                               ref_link = f"https://t.me/{bot_info.username}?start=ref{user_id}"

    earned = len(user["referrals"]) * 0.008
                                                                                                                            text = (
        f"<b>👥 Рефералы</b>\n\n"
        f"<b>💎 Бонус:</b> 0.008 TON за каждого\n\n"                                                                            f"<b>📊 Статистика:</b>\n"                                                                                              f"• Приглашено: {len(user['referrals'])}\n"
        f"• Заработано: <code>{earned:.3f} TON</code>\n\n"
        f"<b>🔗 Ваша ссылка:</b>\n"
        f"<code>{ref_link}</code>"                                                                                          )

    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(user_id))

# ========== ℹ️ ПОМОЩЬ ==========                                                                                        @dp.message(F.text == "ℹ️ Помощь")
async def help_menu(message: types.Message):                                                                                user_id = message.from_user.id

    if not await check_subscription(user_id):
        return await show_subscription_check(message, user_id)                                                          
    text = (
        f"<b>ℹ️ Помощь</b>\n\n"
        f"<b>🌱 Как начать:</b>\n"                                                                                              f"1. Пополните баланс\n"
        f"2. Купите семена\n"
        f"3. Сажайте и собирайте\n\n"
        f"<b>💰 Пополнение:</b>\n"                                                                                              f"• Минимум: {MIN_DEPOSIT} TON\n"
        f"• Автоматическое зачисление\n\n"
        f"<b>🐾 Питомцы:</b>\n"
        f"• Доход каждый час\n"                                                                                                 f"• Кормите раз в 12ч\n\n"
        f"<b>⬆️ Улучшения:</b>\n"
        f"• Авто-полив +15% скорости\n"
        f"• Удобрения +20% прибыли\n"                                                                                           f"• Теплицы — новые грядки\n\n"
        f"<b>💸 Вывод:</b>\n"
        f"• Минимум: {MIN_WITHDRAW} TON\n"
        f"• Комиссия: {WITHDRAW_FEE*100}%\n"                                                                                    f"• 1-10 минут"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(user_id))                                  
# ========== 🔴 АДМИН ПАНЕЛЬ ==========
@dp.message(F.text == "🔴 АДМИН ПАНЕЛЬ")
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("<b>❌ Нет доступа!</b>", parse_mode="HTML")

    await message.answer(
        "<b>🔴 Админ-панель</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )

@dp.message(F.text == "🔙 Выйти")
async def admin_exit(message: types.Message):                                                                               await message.answer(
        "<b>👋 Главное меню</b>",
        parse_mode="HTML",
        reply_markup=main_keyboard(message.from_user.id)
    )

@dp.message(F.text == "📊 Статистика")                                                                                  async def admin_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return                                                                                                          
    total_users = len(users_data)                                                                                           total_balance = sum(u["balance"] for u in users_data.values())                                                          total_farm_balance = sum(u["farm_balance"] for u in users_data.values())
    total_deposited = sum(u["stats"]["deposited"] for u in users_data.values())
    total_withdrawn = sum(u["stats"]["withdrawn"] for u in users_data.values())
                                                                                                                            text = (
        f"<b>📊 Статистика</b>\n\n"
        f"<b>👥 Пользователи:</b> {total_users}\n\n"                                                                            f"<b>💰 Балансы:</b>\n"
        f"• Основные: <code>{total_balance:.3f} TON</code>\n"
        f"• Фарм: <code>{total_farm_balance:.3f} TON</code>\n\n"
        f"<b>📈 Финансы:</b>\n"                                                                                                 f"• Пополнено: <code>{total_deposited:.3f} TON</code>\n"
        f"• Выведено: <code>{total_withdrawn:.3f} TON</code>\n"
        f"• Прибыль: <code>{total_deposited - total_withdrawn:.3f} TON</code>"                                              )

    await message.answer(text, parse_mode="HTML")
                                                                                                                        @dp.message(F.text == "💰 Прибыль")                                                                                     async def admin_profit(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return                                                                                                                                                                                                                                      total_deposited = sum(u["stats"]["deposited"] for u in users_data.values())
    total_withdrawn = sum(u["stats"]["withdrawn"] for u in users_data.values())
    profit = total_deposited - total_withdrawn                                                                                                                                                                                                      text = (
        f"<b>💰 Финансы</b>\n\n"
        f"<b>Обороты:</b>\n"                                                                                                    f"• Пополнено: <code>{total_deposited:.3f} TON</code>\n"                                                                f"• Выведено: <code>{total_withdrawn:.3f} TON</code>\n"
        f"• Прибыль: <code>{profit:.3f} TON</code>\n\n"
        f"<b>Комиссии:</b>\n"                                                                                                   f"• Ферма: {COMMISSION_FARM*100}%\n"
        f"• Питомцы: {COMMISSION_PET_CLAIM*100}%\n"
        f"• Рынок: {COMMISSION_MARKET*100}%"
    )                                                                                                                   
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "👤 Найти игрока")                                                                                async def admin_find_user(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
                                                                                                                            await state.set_state(FarmStates.waiting_find_user)
    await message.answer(
        "<b>🔍 Поиск</b>\n\n"
        "Введите ID или @username:",                                                                                            parse_mode="HTML"
    )

@dp.message(FarmStates.waiting_find_user)                                                                               async def process_find_user(message: types.Message, state: FSMContext):
    await state.clear()
    query = message.text.strip()
                                                                                                                            found = None
    if query.isdigit():
        uid = int(query)
        if uid in users_data:                                                                                                       found = (uid, users_data[uid])
    else:
        username = query.replace("@", "").lower()
        for uid, data in users_data.items():                                                                                        if data.get("username", "").lower() == username:
                found = (uid, data)
                break
                                                                                                                            if not found:
        return await message.answer("<b>❌ Не найден!</b>", parse_mode="HTML")

    uid, user = found                                                                                                   
    referrer_id = user.get("referrer")
    referrer_text = "Нет"
    if referrer_id and referrer_id in users_data:                                                                               ref_user = users_data[referrer_id]
        referrer_text = f"{referrer_id} (@{ref_user.get('username', 'N/A')})"
                                                                                                                            text = (
        f"<b>👤 {uid}</b>\n\n"
        f"<b>📝 Профиль:</b>\n"
        f"• @{user.get('username', 'N/A')}\n"                                                                                   f"• {user.get('first_name', 'N/A')}\n\n"
        f"<b>💰 Балансы:</b>\n"
        f"• Основной: {user['balance']:.3f} TON\n"
        f"• Фарм: {user['farm_balance']:.3f} TON\n\n"                                                                           f"<b>📈 Прогресс:</b>\n"
        f"• Уровень: {user['level']}\n"
        f"• Опыт: {user['xp']}/{calculate_level_xp(user['level'])}\n\n"
        f"<b>👥 Рефералы:</b>\n"
        f"• Пригласил: {referrer_text}\n"
        f"• Приглашено: {len(user['referrals'])}\n\n"
        f"<b>📊 Статистика:</b>\n"                                                                                              f"• Пополнено: {user['stats']['deposited']:.3f} TON\n"
        f"• Выведено: {user['stats']['withdrawn']:.3f} TON\n"
        f"• Заработано: {user['stats']['earned']:.3f} TON\n\n"
        f"<b>🔒 Статус:</b> {'🚫 Забанен' if user.get('banned') else '✅ Активен'}"                                         )

    await message.answer(text, parse_mode="HTML")
                                                                                                                        @dp.message(F.text == "💸 Выдать TON")
async def admin_give_ton(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return                                                                                                          
    await state.set_state(FarmStates.waiting_give_ton)
    await message.answer(
        "<b>💸 Выдача TON</b>\n\n"
        "Формат: ID сумма\n(например: 123456789 10.5)",
        parse_mode="HTML"
    )                                                                                                                   
@dp.message(FarmStates.waiting_give_ton)
async def process_give_ton(message: types.Message, state: FSMContext):
    await state.clear()                                                                                                     try:
        parts = message.text.split()
        user_id = int(parts[0])
        amount = float(parts[1])                                                                                        
        if user_id in users_data:
            users_data[user_id]["balance"] += amount
            await message.answer(                                                                                                       f"<b>✅ Выдано!</b>\n\n"
                f"User: {user_id}\n"
                f"Сумма: {amount} TON\n"
                f"Баланс: {users_data[user_id]['balance']:.3f} TON",                                                                    parse_mode="HTML"
            )
        else:
            await message.answer("<b>❌ Не найден!</b>", parse_mode="HTML")                                                 except:
        await message.answer("<b>❌ Ошибка!</b> Формат: ID сумма", parse_mode="HTML")

@dp.message(F.text == "💳 Забрать TON")                                                                                 async def admin_take_ton(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
                                                                                                                            await state.set_state(FarmStates.waiting_take_ton)
    await message.answer(
        "<b>💳 Изъятие</b>\n\n"
        "Формат: ID сумма",
        parse_mode="HTML"
    )

@dp.message(FarmStates.waiting_take_ton)
async def process_take_ton(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        parts = message.text.split()
        user_id = int(parts[0])
        amount = float(parts[1])
                                                                                                                                if user_id in users_data:                                                                                                   old_balance = users_data[user_id]["balance"]
            users_data[user_id]["balance"] = max(0, old_balance - amount)
            await message.answer(                                                                                                       f"<b>✅ Изъято!</b>\n\n"
                f"User: {user_id}\n"
                f"Было: {old_balance:.3f} TON\n"
                f"Стало: {users_data[user_id]['balance']:.3f} TON",                                                                     parse_mode="HTML"
            )
        else:
            await message.answer("<b>❌ Не найден!</b>", parse_mode="HTML")
    except:
        await message.answer("<b>❌ Ошибка!</b>", parse_mode="HTML")
                                                                                                                        @dp.message(F.text == "🎁 Выдать предмет")
async def admin_give_item(message: types.Message, state: FSMContext):                                                       if message.from_user.id != ADMIN_ID:
        return                                                                                                                                                                                                                                      await state.set_state(FarmStates.waiting_give_item)
    await message.answer(
        "<b>🎁 Выдача предмета</b>\n\n"                                                                                         "Формат: ID тип ID количество\n"                                                                                        "(например: 123456789 seed tulip 5)",
        parse_mode="HTML"
    )                                                                                                                                                                                                                                           @dp.message(FarmStates.waiting_give_item)
async def process_give_item(message: types.Message, state: FSMContext):
    await state.clear()
    try:                                                                                                                        parts = message.text.split()
        user_id = int(parts[0])                                                                                                 item_type = parts[1]
        item_id = parts[2]
        count = int(parts[3]) if len(parts) > 3 else 1
                                                                                                                                if user_id in users_data:                                                                                                   key = f"{item_type}_{item_id}"
            users_data[user_id]["inventory"][key] = users_data[user_id]["inventory"].get(key, 0) + count
            await message.answer(                                                                                                       f"<b>✅ Выдано!</b>\n\n"                                                                                                f"User: {user_id}\n"
                f"{key} x{count}",
                parse_mode="HTML"                                                                                                   )                                                                                                                   else:
            await message.answer("<b>❌ Не найден!</b>", parse_mode="HTML")
    except Exception as e:                                                                                                      await message.answer(f"<b>❌ Ошибка:</b> {e}", parse_mode="HTML")                                               
@dp.message(F.text == "🚫 Бан/Разбан")
async def admin_ban(message: types.Message, state: FSMContext):                                                             if message.from_user.id != ADMIN_ID:                                                                                        return

    await state.set_state(FarmStates.waiting_ban_user)                                                                      await message.answer(                                                                                                       "<b>🚫 Блокировка</b>\n\n"
        "Введите ID:",
        parse_mode="HTML"                                                                                                   )                                                                                                                   
@dp.message(FarmStates.waiting_ban_user)
async def process_ban(message: types.Message, state: FSMContext):
    await state.clear()                                                                                                     try:
        user_id = int(message.text.strip())
        if user_id in users_data and user_id != ADMIN_ID:
            users_data[user_id]["banned"] = not users_data[user_id].get("banned", False)
            status = "🚫 ЗАБАНЕН" if users_data[user_id]["banned"] else "✅ РАЗБАНЕН"
            await message.answer(f"<b>✅ {user_id} — {status}</b>", parse_mode="HTML")
        else:
            await message.answer("<b>❌ Ошибка!</b>", parse_mode="HTML")                                                    except:
        await message.answer("<b>❌ Ошибка!</b>", parse_mode="HTML")
                                                                                                                        @dp.message(F.text == "📢 Рассылка")                                                                                    async def admin_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:                                                                                        return
                                                                                                                            await state.set_state(FarmStates.waiting_broadcast)
    await message.answer(
        "<b>📢 Рассылка</b>\n\n"                                                                                                "Введите текст:",                                                                                                       parse_mode="HTML"
    )
                                                                                                                        @dp.message(FarmStates.waiting_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    await state.clear()
    text = message.text                                                                                                                                                                                                                             sent = 0
    failed = 0
                                                                                                                            await message.answer("<b>⏳ Рассылка...</b>", parse_mode="HTML")                                                    
    for user_id in list(users_data.keys()):
        try:                                                                                                                        await bot.send_message(                                                                                                     user_id,                                                                                                                f"<b>📢 Сообщение:</b>\n\n{text}",
                parse_mode="HTML"                                                                                                   )                                                                                                                       sent += 1                                                                                                               await asyncio.sleep(0.05)
        except:                                                                                                                     failed += 1
                                                                                                                            await message.answer(
        f"<b>✅ Готово!</b>\n\n"                                                                                                f"• Отправлено: {sent}\n"
        f"• Ошибок: {failed}",                                                                                                  parse_mode="HTML"
    )                                                                                                                   
@dp.message(F.text == "✅ Заявки на вывод")
async def admin_withdraws(message: types.Message):
    if message.from_user.id != ADMIN_ID:                                                                                        return                                                                                                          
    if not pending_withdraws:
        return await message.answer(                                                                                                "<b>📭 Нет заявок</b>",                                                                                                 parse_mode="HTML"
        )
                                                                                                                            text = "<b>📋 Заявки:</b>\n\n"                                                                                      
    for req_id, req in list(pending_withdraws.items())[:10]:
        time_ago = int(time.time() - req['created_at'])                                                                         text += (                                                                                                                   f"<b>🆔 {req_id}</b>\n"
            f"• User: {req['user_id']}\n"
            f"• Сумма: {req['amount']:.3f} TON\n"                                                                                   f"• Создана: {format_time(time_ago)} назад\n\n"                                                                     )

    await message.answer(text, parse_mode="HTML")                                                                                                                                                                                               @dp.message(F.text == "🎯 Управление заданиями")
async def admin_tasks_menu(message: types.Message):
    if message.from_user.id != ADMIN_ID:                                                                                        return                                                                                                          
    text = "<b>🎯 Задания</b>\n\n"
                                                                                                                            for task in tasks:                                                                                                          text += f"<b>ID {task['id']}:</b> {task['name']}\n"
                                                                                                                            keyboard = InlineKeyboardMarkup(inline_keyboard=[                                                                           [InlineKeyboardButton(text="➕ Добавить", callback_data="admin_add_task")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="admin_edit_task")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data="admin_delete_task")]                                         ])                                                                                                                  
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
                                                                                                                        @dp.callback_query(F.data == "admin_add_task")                                                                          async def admin_add_task_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Нет доступа!", show_alert=True)                                                                                                                                                                            await state.set_state(FarmStates.waiting_task_name)
    await callback.message.edit_text(
        "<b>➕ Добавление</b>\n\n"
        "Название:",                                                                                                            parse_mode="HTML"
    )                                                                                                                   
@dp.message(FarmStates.waiting_task_name)
async def process_task_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)                                                                              await state.set_state(FarmStates.waiting_task_url)
    await message.answer("<b>Шаг 2/5</b>\n\nURL:", parse_mode="HTML")

@dp.message(FarmStates.waiting_task_url)                                                                                async def process_task_url(message: types.Message, state: FSMContext):
    await state.update_data(url=message.text)                                                                               await state.set_state(FarmStates.waiting_task_desc)
    await message.answer("<b>Шаг 3/5</b>\n\nОписание:", parse_mode="HTML")                                              
@dp.message(FarmStates.waiting_task_desc)
async def process_task_desc(message: types.Message, state: FSMContext):                                                     await state.update_data(description=message.text)                                                                   
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌷 Тюльпан", callback_data="reward_seed_tulip")],                                           [InlineKeyboardButton(text="💰 TON", callback_data="reward_balance")]                                               ])

    await state.set_state(FarmStates.waiting_task_reward_type)                                                              await message.answer("<b>Шаг 4/5</b>\n\nТип награды:", parse_mode="HTML", reply_markup=keyboard)                    
@dp.callback_query(F.data.startswith("reward_"))
async def process_reward_type(callback: types.CallbackQuery, state: FSMContext):                                            reward_type = callback.data[7:]                                                                                         await state.update_data(reward_type=reward_type)
    await state.set_state(FarmStates.waiting_task_reward_amount)
    await callback.message.edit_text("<b>Шаг 5/5</b>\n\nКоличество:", parse_mode="HTML")                                
@dp.message(FarmStates.waiting_task_reward_amount)
async def process_reward_amount(message: types.Message, state: FSMContext):
    try:                                                                                                                        amount = int(message.text)
        data = await state.get_data()
        new_id = max([t["id"] for t in tasks], default=0) + 1
                                                                                                                                tasks.append({
            "id": new_id,
            "name": data["name"],
            "url": data["url"],                                                                                                     "description": data["description"],
            "reward_type": data["reward_type"],                                                                                     "reward_amount": amount
        })                                                                                                              
        await state.clear()
        await message.answer(                                                                                                       f"<b>✅ Задание #{new_id} добавлено!</b>",                                                                              parse_mode="HTML"
        )
    except:
        await message.answer("<b>❌ Ошибка!</b>", parse_mode="HTML")                                                    
@dp.callback_query(F.data == "admin_edit_task")
async def admin_edit_task_start(callback: types.CallbackQuery, state: FSMContext):                                          if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Нет доступа!", show_alert=True)                                                
    text = "<b>✏️ Редактирование</b>\n\n"                                                                                    for task in tasks:
        text += f"<b>ID {task['id']}:</b> {task['name']}\n"
                                                                                                                            await state.set_state(FarmStates.waiting_edit_task_select)                                                              await callback.message.edit_text(f"{text}\nВведите ID:", parse_mode="HTML")

@dp.message(FarmStates.waiting_edit_task_select)
async def process_edit_select(message: types.Message, state: FSMContext):                                                   try:
        task_id = int(message.text)
        task = next((t for t in tasks if t["id"] == task_id), None)
                                                                                                                                if not task:                                                                                                                await state.clear()
            return await message.answer("<b>❌ Не найдено!</b>", parse_mode="HTML")
                                                                                                                                await state.update_data(task_id=task_id)
        await state.set_state(FarmStates.waiting_edit_task_field)
        await message.answer(                                                                                                       f"<b>Редактирование #{task_id}</b>\n\n"                                                                                 f"Что редактировать?\n(name / url / desc / reward)",
            parse_mode="HTML"
        )
    except:                                                                                                                     await state.clear()
        await message.answer("<b>❌ Ошибка!</b>", parse_mode="HTML")

@dp.message(FarmStates.waiting_edit_task_field)
async def process_edit_field(message: types.Message, state: FSMContext):                                                    field = message.text.lower()
    await state.update_data(field=field)
    await state.set_state(FarmStates.waiting_edit_task_value)                                                               await message.answer("Новое значение:", parse_mode="HTML")
                                                                                                                        @dp.message(FarmStates.waiting_edit_task_value)                                                                         async def process_edit_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    task_id = data["task_id"]                                                                                               field = data["field"]                                                                                               
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        await state.clear()
        return await message.answer("<b>❌ Не найдено!</b>", parse_mode="HTML")                                         
    if field == "reward":
        try:
            parts = message.text.split()                                                                                            task["reward_type"] = parts[0]                                                                                          task["reward_amount"] = int(parts[1])
        except:
            await state.clear()                                                                                                     return await message.answer("<b>❌ Формат: тип количество</b>", parse_mode="HTML")
    else:
        task[field] = message.text                                                                                                                                                                                                                  await state.clear()
    await message.answer(f"<b>✅ Задание #{task_id} обновлено!</b>", parse_mode="HTML")

@dp.callback_query(F.data == "admin_delete_task")                                                                       async def admin_delete_task_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ Нет доступа!", show_alert=True)                                                
    text = "<b>🗑 Удаление</b>\n\n"                                                                                          for task in tasks:
        text += f"<b>ID {task['id']}:</b> {task['name']}\n"                                                             
    await state.set_state(FarmStates.waiting_delete_task)
    await callback.message.edit_text(f"{text}\nВведите ID:", parse_mode="HTML")                                                                                                                                                                 @dp.message(FarmStates.waiting_delete_task)
async def process_delete_task(message: types.Message, state: FSMContext):
    await state.clear()
    try:                                                                                                                        task_id = int(message.text)
        global tasks
        tasks = [t for t in tasks if t["id"] != task_id]
        await message.answer(f"<b>✅ Задание #{task_id} удалено!</b>", parse_mode="HTML")                                   except:                                                                                                                     await message.answer("<b>❌ Ошибка!</b>", parse_mode="HTML")

@dp.message(F.text == "📋 Логи")                                                                                        async def admin_logs(message: types.Message):
    if message.from_user.id != ADMIN_ID:                                                                                        return
                                                                                                                            recent_sales = live_sales[-20:]
    if not recent_sales:
        return await message.answer("<b>📭 Пусто</b>", parse_mode="HTML")                                                                                                                                                                           text = "<b>📋 Последние 20:</b>\n\n"

    for sale in recent_sales:
        time_ago = int(time.time() - sale["time"])
        if sale["type"] == "deposit":
            text += f"[{format_time(time_ago)}] 💎 +{sale['amount']:.2f} TON\n"
        elif sale["type"] == "market":
            text += f"[{format_time(time_ago)}] 🏪 Продажа\n"

    await message.answer(text, parse_mode="HTML")
                                                                                                                        @dp.message(F.text == "⚙️ Настройки")
async def admin_settings(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return                                                                                                          
    text = (
        f"<b>⚙️ Настройки</b>\n\n"
        f"<b>Комиссии:</b>\n"                                                                                                   f"• Ферма: {COMMISSION_FARM*100}%\n"
        f"• Питомцы: {COMMISSION_PET_CLAIM*100}%\n"
        f"• Рынок: {COMMISSION_MARKET*100}%\n\n"
        f"<b>Лимиты:</b>\n"                                                                                                     f"• Мин. депозит: {MIN_DEPOSIT} TON\n"
        f"• Мин. вывод: {MIN_WITHDRAW} TON\n"
        f"• Комиссия вывода: {WITHDRAW_FEE*100}%"
    )

    await message.answer(text, parse_mode="HTML")
                                                                                                                        # ========== НАЗАД ==========
@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.delete()                                                                                         await cmd_start(callback.message)

@dp.callback_query(F.data == "farm_back")
async def back_to_farm(callback: types.CallbackQuery):                                                                      await my_farm(callback.message)

@dp.callback_query(F.data == "pets_back")
async def back_to_pets(callback: types.CallbackQuery):                                                                      await pets_menu(callback.message)

# ========== ФОНОВЫЕ ЗАДАЧИ ==========
async def background_tasks():                                                                                               while True:
        await asyncio.sleep(60)

        try:                                                                                                                        now = time.time()
            expired = []
            for lot_id, lot in market_listings.items():
                if not lot["sold"] and now > lot["expires_at"]:                                                                             user = get_user_data(lot["seller_id"])
                    for pet in user["pets"]:
                        if pet.get("market_id") == lot_id:
                            del pet["market_id"]                                                                                                    break
                    expired.append(lot_id)

            for lot_id in expired:
                del market_listings[lot_id]

        except Exception as e:
            print(f"Background error: {e}")

# ========== ЗАПУСК ==========
async def main():                                                                                                           load_data()

    asyncio.create_task(check_payments_loop())                                                                              asyncio.create_task(background_tasks())                                                                             
    print("🚀 Бот запущен!")
    print(f"👑 Админ: {ADMIN_USERNAME}")                                                                                                                                                                                                            await dp.start_polling(bot)
                                                                                                                        if __name__ == "__main__":
    asyncio.run(main())
