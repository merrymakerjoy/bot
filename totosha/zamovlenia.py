import telegram
from telegram import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
import glob
from telegram import ParseMode
from .views import *
from .info import *
from .comands import *
from .adm import *
from django.contrib.auth.models import User, Group
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from telegram import ReplyKeyboardMarkup, KeyboardButton
from django.utils.translation import activate, gettext as _
import os
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import urllib.request
from shutil import copyfile
from django.core.files import File
import random
from urllib.parse import quote
import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from telegram import InputFile


url_site = 'https://totosha.com.ua'
emoji = ['🤔', '🎈', '🎮', '🚀', '🚂', '🎢', '🚗', '⚽', '🏀', '🦖', '🐝', '🐶', '📲', '🇺🇦']


def delete_telegram_message(message_id, telegram_id, bot):
    pass
    # for i in range(message_id - 50, message_id + 1):
    #     try:
    #         bot.delete_message(chat_id=telegram_id, message_id=i)
    #     except:
    #         pass


def knonka(message_id, telegram_id, bot):
    keyboard = [
        [KeyboardButton(text="🛒 Корзина"), KeyboardButton(text="💖 Обрані товари")],
        [KeyboardButton(text="🔍 Пошук"), KeyboardButton(text="📚 Історія замовлень")],
        [KeyboardButton(text="💬 Написати нам"), KeyboardButton(text="ℹ️ Інформація")],
        [KeyboardButton(text="🏠 Додому")]
    ]

    admin_users = User.objects.filter(groups__name='administrator', is_staff=True)
    if admin_users.exists():
        admin_usernames = admin_users.values_list('username', flat=True)
        admin_chat_ids = [int(username) for username in admin_usernames]
        if telegram_id in admin_chat_ids:
            keyboard.append([KeyboardButton(text="Вхід в панель адміністратора")])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    random_emoji = random.choice(emoji)
    bot.send_message(telegram_id, text=random_emoji, reply_markup=reply_markup)



def confirm(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    zakaz_all = Korzina.objects.filter(telegram_user=prof)

    total_cost = 0

    for zakaz in zakaz_all:
        name_toys = zakaz.name_toys
        price_toy = "".join([x for x in zakaz.price_toys if x.isdigit()])
        price_toys = int(price_toy)
        artikul_toys = zakaz.artikul_toys
        amount_toys = int(zakaz.amount_toys)

        total_price = price_toys * amount_toys
        total_cost += total_price

        # Створення об'єкту History і збереження в базі даних
        history_item = History.objects.create(
            telegram_user=prof,
            name_toys=name_toys,
            price_toys=price_toy,
            artikul_toys=artikul_toys,
            amount_toys=amount_toys,
            status=False
        )
        history_item.save()

        zakaz.delete()

    # Повна інформація про замовлення
    order_info = f"Інформація про замовлення:\n"
    for zakaz in zakaz_all:
        order_info += f"Назва товару: {zakaz.name_toys}\n"
        order_info += f"Ціна товару: {zakaz.price_toys} \n"
        order_info += f"Артикул товару: {zakaz.artikul_toys}\n"
        order_info += f"Кількість: {zakaz.amount_toys}\n\n"

    # Інформація про користувача
    user_info = f"Інформація про користувача:\n"
    user_info += f"ID: {prof.telegram_id}\n"
    user_info += f"Логін: {prof.username}\n"
    user_info += f"Ім'я: {prof.first_name}\n"
    user_info += f"Прізвище: {prof.last_name}\n"
    user_info += f"Телефон: {prof.phone}\n"
    user_info += f"Email: {prof.email}\n"

    # Збереження інформації в таблицю Work
    work_item = Work.objects.create(
        telegram_user=prof,
        info_user=user_info,
        order_info=order_info,
        total_price=str(total_cost),

    )
    work_item.save()

    admin_users = User.objects.filter(groups__name='administrator', is_staff=True)
    if admin_users.exists():
        admin_usernames = admin_users.values_list('username', flat=True)
        admin_chat_id = ", ".join(admin_usernames)
        admin_chat_ids = admin_chat_id.split(', ')  # Розділяємо значення admin_chat_id на окремі ID

    for chat_id in admin_chat_ids:
        admin_message = f"⚠️ОТРИМАНО НОВЕ ЗАМОВЛЕННЯ!!!\n\n{order_info}\n\nЗагальна вартість замовлення: {total_cost}грн\n\n\n{user_info}"
        keyboard = [
            [InlineKeyboardButton("Зв'язатися з користувачем", callback_data=f"zatisia_{prof.telegram_id}")],
            [InlineKeyboardButton("Адмін панель", callback_data="admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=int(chat_id), text=admin_message, reply_markup=reply_markup)

    message = f"✅ Замовлення оформлено!\nНайближчим часом з Вами зв'яжеться менеджер для уточнення деталей."
    bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)



def history(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    user_history = History.objects.filter(telegram_user=prof).order_by('-datetime')
    total_records = user_history.count()
    page_size = 10  # Кількість записів на одній сторінці

    if total_records > 0:
        page = 1
        max_pages = (total_records + page_size - 1) // page_size  # Кількість сторінок

        if 'page' in data:  # Перевірка наявності параметра 'page' у запиті
            page = int(data['page'])

        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        user_history = user_history[start_index:end_index]

        message = "📚 Історія Ваших покупок:\n\n"

        for history in user_history:
            formatted_datetime = history.datetime.strftime("%Y-%m-%d %H:%M")
            message += f"{formatted_datetime}\n"
            message += f"{history.name_toys}\n"
            message += f"Ціна: {history.price_toys}\n"
            message += f"{history.artikul_toys}\n"
            message += f"Кількість: {history.amount_toys}\n\n"
            # message += f"Додаткова інформація: {history.info}\n"
            # message += f"Статус: {'Purchased' if history.status else 'Not purchased'}\n"

        keyboard = []
        if page > 1:
            prev_page = page - 1
            keyboard.append([InlineKeyboardButton("🔙 Попердня сторінка", callback_data=f"storypage_{prev_page}")])
        if page < max_pages:
            next_page = page + 1
            keyboard.append([InlineKeyboardButton("Наступна сторінка 🔜", callback_data=f"storypage_{next_page}")])

        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="information")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(telegram_id, message, reply_markup=reply_markup)
    else:
        bot.send_message(telegram_id, "🤷‍♂️ Ви ще нічого не придбали. Давай сміливіше! 😉")


def history_page(message_id, telegram_id, bot, historypage, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    user_history = History.objects.filter(telegram_user=prof).order_by('-datetime')
    total_records = user_history.count()
    page_size = 10  # Кількість записів на одній сторінці

    if total_records > 0:
        page = 1
        max_pages = (total_records + page_size - 1) // page_size  # Кількість сторінок

        if historypage.isdigit():  # Перевірка, чи historypage є числом
            page = int(historypage)
            if page < 1:
                page = 1
            elif page > max_pages:
                page = max_pages

        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        user_history = user_history[start_index:end_index]

        message = "📚 Історія Ваших покупок:\n\n"

        for history in user_history:
            formatted_datetime = history.datetime.strftime("%Y-%m-%d %H:%M")
            message += f"{formatted_datetime}\n"
            message += f"{history.name_toys}\n"
            message += f"Ціна: {history.price_toys}\n"
            message += f"{history.artikul_toys}\n"
            message += f"Кількість: {history.amount_toys}\n\n"
            # message += f"Додаткова інформація: {history.info}\n"
            # message += f"Статус: {'Purchased' if history.status else 'Not purchased'}\n"

        keyboard = []
        if page > 1:
            prev_page = page - 1
            keyboard.append([InlineKeyboardButton("🔙 Попередня сторінка", callback_data=f"historypage_{prev_page}")])
        if page < max_pages:
            next_page = page + 1
            keyboard.append([InlineKeyboardButton("Наступна сторінка 🔜", callback_data=f"historypage_{next_page}")])

        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="information")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(telegram_id, message, reply_markup=reply_markup)
    else:
        bot.send_message(telegram_id, "🤷‍♂️️ Ви ще нічого не придбали. Давай сміливіше! 😉")
