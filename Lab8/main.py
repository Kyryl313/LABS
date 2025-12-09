import telebot
import os
from dotenv import load_dotenv
load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from products import products
from delivery import delivery_methods, delivery_locations
from jobs import jobs_list

orders = {}  # поточні замовлення користувачів

# --- меню ---
def main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🛒 Асортимент", callback_data="products"))
    kb.add(InlineKeyboardButton("🚚 Доставка", callback_data="delivery"))
    kb.add(InlineKeyboardButton("💼 Вакансії", callback_data="jobs"))
    return kb

def make_kb(options, prefix):
    kb = InlineKeyboardMarkup()
    for key, text in options.items():
        kb.add(InlineKeyboardButton(text, callback_data=f"{prefix}_{key}"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="main"))
    return kb

# --- старт ---
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "Виберіть дію:", reply_markup=main_menu())

# --- обробка callback ---
@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    chat = c.message.chat.id
    data = c.data

    # --- Головне меню ---
    if data == "main":
        bot.send_message(chat, "Виберіть дію:", reply_markup=main_menu())
        return

    # --- Асортимент ---
    if data == "products":
        items = {pid: f"{item['name']} — {item['price']}" for pid, item in products.items()}
        kb = make_kb(items, "item")
        bot.send_message(chat, "Асортимент:", reply_markup=kb)
        return

    # --- Вибір товару ---
    if data.startswith("item_"):
        pid = int(data.split("_")[1])
        item = products[pid]
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🛍 Замовити", callback_data=f"buy_{pid}"))
        kb.add(InlineKeyboardButton("⬅ Назад", callback_data="products"))
        bot.send_photo(chat, item["photo"], caption=f"{item['name']}\nЦіна: {item['price']}", reply_markup=kb)
        return

    # --- Початок замовлення ---
    if data.startswith("buy_"):
        pid = int(data.split("_")[1])
        orders[chat] = {"product": pid}
        kb = {m: m for m in delivery_methods}
        bot.send_message(chat, "Оберіть спосіб доставки:", reply_markup=make_kb(kb, "method"))
        return

    # --- Вибір способу доставки ---
    if data.startswith("method_"):
        method = data.replace("method_", "")
        orders[chat]["method"] = method
        if method == "Самовивіз":
            finalize_order(chat)
        else:
            kb = {l: l for l in delivery_locations}
            bot.send_message(chat, "Оберіть район доставки:", reply_markup=make_kb(kb, "loc"))
        return

    # --- Вибір району ---
    if data.startswith("loc_"):
        loc = data.replace("loc_", "")
        orders[chat]["location"] = loc
        finalize_order(chat)
        return

    # --- Вакансії ---
    if data == "jobs":
        kb = {j: j for j in jobs_list}
        bot.send_message(chat, "💼 Вакансії:", reply_markup=make_kb(kb, "none"))
        return

# --- оформлення замовлення ---
def finalize_order(chat):
    pid = orders[chat]["product"]
    item = products[pid]
    delivery = orders[chat].get("method", "")
    location = orders[chat].get("location", "Не вказано")
    print(f"\n--- НОВЕ ЗАМОВЛЕННЯ ---")
    print(f"ID: {chat}")
    print(f"Товар: {item['name']} — {item['price']}")
    print(f"Спосіб доставки: {delivery}")
    print(f"Район: {location}")
    print("------------------------\n")
    bot.send_message(chat, "✅ Замовлення оформлено!", reply_markup=main_menu())

bot.infinity_polling()  
