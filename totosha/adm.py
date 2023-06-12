import telegram
from telegram import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
import glob
from telegram import ParseMode
from .views import *
from .info import *
from .comands import *
from .zamovlenia import *
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
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
import tempfile
import os


emoji = ['🤔', '🎈', '🎮', '🚀', '🚂', '🎢', '🚗', '⚽', '🏀', '🦖', '🐝', '🐶', '📲', '🇺🇦']


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


def admin_panel(data, telegram_id, bot):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    admin_users = User.objects.filter(groups__name='administrator', is_staff=True)
    if admin_users.exists():
        admin_usernames = admin_users.values_list('username', flat=True)
        admin_chat_ids = [int(username) for username in admin_usernames]
        if telegram_id in admin_chat_ids:
            prof.is_authenticated = True
            prof.save()
            if prof.is_authenticated:
                admin_chat_id = telegram_id
                admin_message = f"Привіт, {prof.first_name} {prof.last_name}. Вітаю тебе в панелі адміністратора!!!"
                bot.send_message(chat_id=admin_chat_id, text=admin_message)
                message = "Обери дію:"
                keyboard = [
                    [InlineKeyboardButton("Написати користувачеві", callback_data="write")],
                     [InlineKeyboardButton("Зробити розсилку️", callback_data="rozsilka")],
                     [InlineKeyboardButton("Замовлення в роботі️", callback_data="work")],
                     [InlineKeyboardButton("Архів замовлень️", callback_data="arhivzakaz")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=telegram_id, text="В тебе немає достутпу!!!")

def write(data, telegram_id, bot):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        users = TelegramUser.objects.all()  # Отримуємо всіх користувачів
        total_users = len(users)
        page_size = 10  # Кількість користувачів на одній сторінці
        current_page = 1
        max_pages = (total_users + page_size - 1) // page_size  # Кількість сторінок
        start_index = (current_page - 1) * page_size
        end_index = start_index + page_size
        prof.step = "пошуккористувача"
        prof.save()
        buttons = []

        for user in users[start_index:end_index]:
            button_text = f"{user.first_name} {user.last_name} ({user.telegram_id})"
            callback_data = f"user_{user.telegram_id}"
            buttons.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        reply_markup = InlineKeyboardMarkup(buttons)

        if total_users > page_size:
            if current_page > 1:
                previous_page_callback = "kor_previouspage"
                reply_markup.row(InlineKeyboardButton("Назад", callback_data=previous_page_callback))
            if current_page < max_pages:
                next_page_callback = "kor_nextpage"
                reply_markup.row(InlineKeyboardButton("Вперед", callback_data=next_page_callback))

        bot.sendMessage(telegram_id, "Обери користувача, або для пошуку введи його ID", reply_markup=reply_markup)


def korwrite(message_id, telegram_id, bot, kor, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        users = TelegramUser.objects.all()  # Отримуємо всіх користувачів
        total_users = len(users)
        page_size = 10  # Кількість користувачів на одній сторінці
        current_page = 1
        max_pages = (total_users + page_size - 1) // page_size  # Кількість сторінок
        start_index = (current_page - 1) * page_size
        end_index = start_index + page_size

        if kor == "kor_previouspage":
            if current_page > 1:
                current_page -= 1
        elif kor == "kor_nextpage":
            if current_page < max_pages:
                current_page += 1

        start_index = (current_page - 1) * page_size
        end_index = start_index + page_size

        prof.step = "пошуккористувача"
        prof.save()
        buttons = []

        for user in users[start_index:end_index]:
            button_text = f"{user.first_name} {user.last_name} ({user.telegram_id})"
            callback_data = f"user_{user.telegram_id}"
            buttons.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        reply_markup = InlineKeyboardMarkup(buttons)

        if total_users > page_size:
            if current_page > 1:
                previous_page_callback = "kor_previouspage"
                reply_markup.row(InlineKeyboardButton("Назад", callback_data=previous_page_callback))
            if current_page < max_pages:
                next_page_callback = "kor_nextpage"
                reply_markup.row(InlineKeyboardButton("Вперед", callback_data=next_page_callback))

        bot.sendMessage(telegram_id, "Обери користувача, або для пошуку введи його ID", reply_markup=reply_markup)


def searchuser(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        text = data['message'].get('text')
        try:
            id_kor = int(text)
            print(id_kor)
            user = TelegramUser.objects.get(telegram_id=id_kor)  # Знаходимо користувача з вказаним id_kor
            button_text = f"{user.first_name} {user.last_name} ({user.telegram_id})"
            callback_data = f"user_{user.telegram_id}"
            buttons = [[InlineKeyboardButton(button_text, callback_data=callback_data)]]
            reply_markup = InlineKeyboardMarkup(buttons)
            bot.sendMessage(telegram_id, "Обери користувача", reply_markup=reply_markup)
        except:
            message = "Помилка. Користувача не знайдено, спробуй ще раз"
            bot.sendMessage(telegram_id, message)



def rozsilka(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        prof.step = "rozsilka"
        prof.save()
        text = 'Введи повідомлення для розсилки всім користувачам, або натисни "Завершити", для виходу'
        keyboard = [
            [InlineKeyboardButton("Завершити", callback_data="zavthshyty")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=telegram_id, text=text, reply_markup=reply_markup)


def rozsilkauser(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        users = TelegramUser.objects.all()
        text = data['message'].get('text')
        photo_data = data['message'].get('photo')
        caption = data['message'].get('caption')
        if caption and photo_data:
            photo = photo_data[-1]  # Вибираємо останню фотографію зі списку
            photo_id = photo['file_id']
            for user in users:
                bot.send_photo(chat_id=user.telegram_id, photo=photo_id, caption=caption)

        elif photo_data:
            photo = photo_data[-1]  # Вибираємо останню фотографію зі списку
            photo_id = photo['file_id']
            for user in users:
                bot.send_photo(chat_id=user.telegram_id, photo=photo_id)

        elif text:
            for user in users:
                bot.send_message(chat_id=user.telegram_id, text=text)

    rozsilka(message_id, telegram_id, bot, data)



def zavthshyty(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        prof.step = "пусто"
        prof.save()
        bot.send_message(chat_id=telegram_id, text="Розсилка повідомлень ВИМКНЕНА!!!")
        knonka(message_id, telegram_id, bot)
        users = TelegramUser.objects.all()
        for user in users:
            keyboard = [
                [InlineKeyboardButton("📱 Написати нам", callback_data="messages")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id=user.telegram_id, text="📱", reply_markup=reply_markup)


def zviazatisia(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        prof.is_chat = True
        id_user = prof.variable_1
        prof.save()
        user(message_id, telegram_id, bot, id_user, data)


def zatisia(message_id, telegram_id, bot, data, id_kor):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        prof.is_chat = True
        id_user = id_kor
        prof.save()
        user(message_id, telegram_id, bot, id_user, data)


def user(message_id, telegram_id, bot, id_user, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        prof.is_chat = True
        prof.variable_1 = id_user
        prof.save()

        users = TelegramUser.objects.get(telegram_id=id_user)

        message = "✉️ Введи повідомлення"
        bot.sendMessage(telegram_id, message)
        if users.is_chat == False:
            message = f"Підключити користувача {users} до розмови?"
            keyboard = [
                [InlineKeyboardButton("Підключити", callback_data="pidklychyty_user")],
                [InlineKeyboardButton("Завершити діалог", callback_data="stop_user")]
            ]
        elif users.is_chat:
            message = f"Відключити користувача {users} до розмови?"
            keyboard = [
                [InlineKeyboardButton("Відключити", callback_data="vidklychyty_user")],
                [InlineKeyboardButton("Завершити діалог", callback_data="stop_user")]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)


def pidklychyty_user(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        users = TelegramUser.objects.get(telegram_id=prof.variable_1)
        users.is_chat = True
        users.variable_1 = telegram_id
        users.save()
        vidpovid(message_id, telegram_id, bot, data)

        message = f"Користувача: {users} підключено. Він може надсилати вам повідомлення."
        keyboard = [
            [InlineKeyboardButton("Відключити", callback_data="vidklychyty_user")],
            [InlineKeyboardButton("Завершити діалог", callback_data="stop_user")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)
        bot.send_message(chat_id=prof.variable_1, text="Вас підключено до розмови!!!")



def vidklychyty_user(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        users = TelegramUser.objects.get(telegram_id=prof.variable_1)
        users.is_chat = False
        users.save()

        message = f"Користувача: {users} відключено від розмови"
        keyboard = [
            [InlineKeyboardButton("Підключити", callback_data="pidklychyty_user")],
            [InlineKeyboardButton("Завершити діалог", callback_data="stop_user")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)
        bot.send_message(chat_id=prof.variable_1, text="Вас відключено від розмови!!!")


def stop_user(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)

    if prof.is_authenticated:
        users = TelegramUser.objects.get(telegram_id=prof.variable_1)
        users.is_chat = False
        # users.variable_1 = "00000"
        users.save()

        prof.is_chat = False
        # prof.variable_1 = "00000"
        prof.save()
        message = "🏁 Діалог завершено"

        keyboard = [
            [InlineKeyboardButton("Назад", callback_data="write")],
            [InlineKeyboardButton("Адмін панель", callback_data="admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)
        bot.send_message(chat_id=prof.variable_1, text=message)
        knonka(message_id, telegram_id, bot)


def vidpovid(message_id, telegram_id, bot, data):
    prof_1 = TelegramUser.objects.get(telegram_id=telegram_id)
    try:
        text = data['message'].get('text')
        photo_data = data['message'].get('photo')
        caption = data['message'].get('caption')
        send_id = prof_1.variable_1

        if caption and photo_data:
            photo = photo_data[-1]  # Вибираємо останню фотографію зі списку
            photo_id = photo['file_id']
            bot.send_photo(chat_id=send_id, photo=photo_id, caption=caption)
        elif photo_data:
            photo = photo_data[-1]  # Вибираємо останню фотографію зі списку
            photo_id = photo['file_id']
            bot.send_photo(chat_id=send_id, photo=photo_id)
        elif text:
            bot.send_message(chat_id=send_id, text=text)

        else:
            None
    except:
        None


def work(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        # Отримати всі замовлення з таблиці Work
        try:
            orders = Work.objects.all()
        except:
            return
        if orders.exists():
            for order in orders:
                # Отримати назву користувача для замовлення
                username = order.telegram_user
                # Отримати всі статуси замовлення
                statuses = []
                if order.status_1:
                    statuses.append("- Контакт з клієнтом")
                if order.status_2:
                    statuses.append("- Підтвердження замовлення")
                if order.status_3:
                    statuses.append("- Оплата")
                if order.status_4:
                    statuses.append("- Доставка")
                if order.status_5:
                    statuses.append("- Закриття замовлення")
                if order.status_6:
                    statuses.append("- Повернення/Відмова")
                # Створити рядок з кожним статусом в новому рядку з відступом табуляції
                status = "\n\t".join(statuses)
                message = f"Замовлення № {order.id}\n"
                message += f"Користувач: {username}\n"
                message += f"Статус:\n\t{status}\n"
                message += f"Сума: {order.total_price}грн.\n\n"
                # Додати кнопки для кожного замовлення
                keyboard = [
                    [InlineKeyboardButton("Добавити додаткову інформацію", callback_data=f"edit_order_{order.id}"),
                     InlineKeyboardButton("Змінити статус", callback_data=f"change_status_{order.id}")],
                    [InlineKeyboardButton("Перенести в архів", callback_data=f"close_order_{order.id}"),
                     InlineKeyboardButton("Інформація про замовлення", callback_data=f"info_order_{order.id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)
        else:
            message = "Немає доступних замовлень."
            bot.send_message(chat_id=telegram_id, text=message)
        knonka(message_id, telegram_id, bot)


def edit_order(message_id, telegram_id, bot, order_id, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        orders = Work.objects.get(id=order_id)
        prof.step = "Додатковаінформація"
        prof.variable = order_id
        prof.save()
        message = "Введи додаткову інформацію про замовлення"
        bot.send_message(chat_id=telegram_id, text=message)


def toaddkomentarszakaz(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        prof.step = "Пусто"
        prof.save()
        order_id = prof.variable
        text = data['message']['text']
        orders = Work.objects.get(id=order_id)
        orders.info_zakaz += text
        orders.save()
        message = f"✅ Коментар добавлено!!!."
        keyboard = [
            [InlineKeyboardButton("Назад", callback_data=f"work")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)


def change_status(message_id, telegram_id, bot, order_id, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        prof.step = 'change_status'
        prof.save()
        orders = Work.objects.get(id=order_id)
        statuses = []
        buttons = []
        if not orders.status_1:
            statuses.append("- Контакт з клієнтом")
            buttons.append([InlineKeyboardButton("Контакт з клієнтом", callback_data=f"status_1_{order_id}")])
        if not orders.status_2:
            statuses.append("- Підтвердження замовлення")
            buttons.append([InlineKeyboardButton("Підтвердження замовлення", callback_data=f"status_2_{order_id}")])
        if not orders.status_3:
            statuses.append("- Оплата")
            buttons.append([InlineKeyboardButton("Оплата", callback_data=f"status_3_{order_id}")])
        if not orders.status_4:
            statuses.append("- Доставка")
            buttons.append([InlineKeyboardButton("Доставка", callback_data=f"status_4_{order_id}")])
        if not orders.status_5:
            statuses.append("- Закриття замовлення")
            buttons.append([InlineKeyboardButton("Закриття замовлення", callback_data=f"status_5_{order_id}")])
        if not orders.status_6:
            statuses.append("- Повернення/Відмова")
            buttons.append([InlineKeyboardButton("Повернення/Відмова", callback_data=f"status_6_{order_id}")])
        message = f"Замовлення № {orders.id}, від {orders.telegram_user} \nЗмінити статус на: \n"
        reply_markup = InlineKeyboardMarkup(buttons)
        bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)


def close_order(message_id, telegram_id, bot, order_id, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        try:
            order = Work.objects.get(id=order_id)
        except:
            return
        # Створення нового запису в таблиці Arhivzamovlen
        arhiv_order = Arhivzamovlen.objects.create(
            telegram_user=order.telegram_user,
            info_user=order.info_user,
            order_info=order.order_info,
            total_price=order.total_price,
            info=order.info,
            info_zakaz=order.info_zakaz,
            status_1=order.status_1,
            info_status_1=order.info_status_1,
            datetime_status_1=order.datetime_status_1,
            status_2=order.status_2,
            info_status_2=order.info_status_2,
            datetime_status_2=order.datetime_status_2,
            status_3=order.status_3,
            info_status_3=order.info_status_3,
            datetime_status_3=order.datetime_status_3,
            status_4=order.status_4,
            info_status_4=order.info_status_4,
            datetime_status_4=order.datetime_status_4,
            status_5=order.status_5,
            info_status_5=order.info_status_5,
            datetime_status_5=order.datetime_status_5,
            status_6=order.status_6,
            info_status_6=order.info_status_6,
            datetime_status_6=order.datetime_status_6,
            datetime=order.datetime
        )
        # Видалення запису з таблиці Work
        order.delete()
        message = "Замовлення закрите. Дані перенесені до архіву."
        bot.send_message(chat_id=telegram_id, text=message)


def info_order(message_id, telegram_id, bot, order_id, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        orders = Work.objects.get(id=order_id)
        statuses = []
        if orders.status_1:
            statuses.append(f"- Контакт з клієнтом\n  кометар: {orders.info_status_1}\n  дата: {orders.datetime_status_1}")
        if orders.status_2:
            statuses.append(f"- Підтвердження замовлення\n  кометар: {orders.info_status_2}\n  дата: {orders.datetime_status_2}")
        if orders.status_3:
            statuses.append(f"- Оплата\n  кометар: {orders.info_status_3}\n  дата: {orders.datetime_status_3}")
        if orders.status_4:
            statuses.append(f"- Доставка\n  кометар: {orders.info_status_4}\n  дата: {orders.datetime_status_4}")
        if orders.status_5:
            statuses.append(f"- Закриття замовлення\n  кометар: {orders.info_status_5}\n  дата: {orders.datetime_status_5}")
        if orders.status_6:
            statuses.append(f"- Повернення/Відмова\n  кометар: {orders.info_status_6}\n  дата: {orders.datetime_status_6}")
        # Створити рядок з кожним статусом в новому рядку з відступом табуляції
        status = "\n\t".join(statuses)
        message = f"Інформація про замовлення № {order_id}\n\n"
        message += f"Статус: \n{status}\n\n"
        message += f"{orders.info_user}\n\n"
        message += f"{orders.order_info}\n\n"
        message += f"{orders.info}\n\n"
        message += f"Додаткова інформація: {orders.info_zakaz}\n\n"
        message += f"Сума: {orders.total_price}грн.\n\n"
        # Додати кнопки для кожного замовлення
        keyboard = [
            [InlineKeyboardButton("Добавити додаткову інформацію", callback_data=f"edit_order_{order_id}"),
             InlineKeyboardButton("Змінити статус", callback_data=f"change_status_{order_id}")],
            [InlineKeyboardButton("Перенести в архів", callback_data=f"close_order_{order_id}"),
             InlineKeyboardButton("Назад", callback_data=f"work")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)


def status(message_id, telegram_id, bot, status_id, order_id, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        prof.variable = order_id
        prof.variable_1 = status_id
        prof.save()
        orders = Work.objects.get(id=order_id)
        # Зміна відповідного статусу на True
        if status_id == '1':
            orders.status_1 = True
        elif status_id == '2':
            orders.status_2 = True
        elif status_id == '3':
            orders.status_3 = True
        elif status_id == '4':
            orders.status_4 = True
        elif status_id == '5':
            orders.status_5 = True
        elif status_id == '6':
            orders.status_6 = True
        orders.save()
        # message = f"✅ Статус замовлення зміненно!!!."
        # bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)
        message = "За потреби напиши коментар"
        keyboard = [
            [InlineKeyboardButton("Добавити коментар до статуса", callback_data=f"Komentarstatusa"),
             InlineKeyboardButton("Назад", callback_data=f"work")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)


def komentarstatusa(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        prof.step = "Коментарстатуса"
        prof.save()
        message = "Напиши та відправ текст комента"
        bot.send_message(chat_id=telegram_id, text=message)


def toaddkomentarstatysa(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        prof.step = "Пусто"
        prof.save()
        text = data['message']['text']
        order_id = prof.variable
        status_id = prof.variable_1
        orders = Work.objects.get(id=order_id)
        # Зміна відповідного статусу
        if status_id == '1':
            orders.info_status_1 = text
        elif status_id == '2':
            orders.info_status_2 = text
        elif status_id == '3':
            orders.info_status_3 = text
        elif status_id == '4':
            orders.info_status_4 = text
        elif status_id == '5':
            orders.info_status_5 = text
        elif status_id == '6':
            orders.info_status_6 = text
        orders.save()
        message = f"✅ Коментар добавлено!!!."
        keyboard = [
            [InlineKeyboardButton("Змінити коментар", callback_data=f"Komentarstatusa"),
             InlineKeyboardButton("Назад", callback_data=f"work")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)


def arhivzakaz(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        try:
            orders = Arhivzamovlen.objects.order_by('-id')[:10]  # Вибірка останніх 10 замовлень за полем 'id'
        except:
            return
        if orders.exists():
            for order in orders:
                # Отримати назву користувача для замовлення
                username = order.telegram_user
                message = f"Замовлення № {order.id}\n"
                message += f"Користувач: {username}\n"
                message += f"Сума: {order.total_price}грн.\n\n"
                # Додати кнопки для кожного замовлення
                keyboard = [
                    [InlineKeyboardButton("Назад", callback_data=f"admin_panel"),
                     InlineKeyboardButton("Додаткова інформація", callback_data=f"info_arhiv_{order.id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)
            message_1 = f"Сформувати весь архів в файл"
            keyboard = [
                [InlineKeyboardButton("Отримати файл", callback_data="PDFarhiv")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id=telegram_id, text=message_1, reply_markup=reply_markup)
        else:
            message = "Немає доступних замовлень."
            bot.send_message(chat_id=telegram_id, text=message)
        knonka(message_id, telegram_id, bot)


def info_arhiv(message_id, telegram_id, bot, order_id, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        orders = Arhivzamovlen.objects.get(id=order_id)
        statuses = []
        if orders.status_1:
            statuses.append(
                f"- Контакт з клієнтом\n  кометар: {orders.info_status_1}\n  дата: {orders.datetime_status_1}")
        if orders.status_2:
            statuses.append(
                f"- Підтвердження замовлення\n  кометар: {orders.info_status_2}\n  дата: {orders.datetime_status_2}")
        if orders.status_3:
            statuses.append(f"- Оплата\n  кометар: {orders.info_status_3}\n  дата: {orders.datetime_status_3}")
        if orders.status_4:
            statuses.append(f"- Доставка\n  кометар: {orders.info_status_4}\n  дата: {orders.datetime_status_4}")
        if orders.status_5:
            statuses.append(
                f"- Закриття замовлення\n  кометар: {orders.info_status_5}\n  дата: {orders.datetime_status_5}")
        if orders.status_6:
            statuses.append(
                f"- Повернення/Відмова\n  кометар: {orders.info_status_6}\n  дата: {orders.datetime_status_6}")
        # Створити рядок з кожним статусом в новому рядку з відступом табуляції
        status = "\n\t".join(statuses)
        message = f"Інформація про замовлення № {order_id}\n\n"
        message += f"Статус: \n{status}\n\n"
        message += f"{orders.info_user}\n\n"
        message += f"{orders.order_info}\n\n"
        message += f"{orders.info}\n\n"
        message += f"Додаткова інформація: {orders.info_zakaz}\n\n"
        message += f"Сума: {orders.total_price}грн.\n\n"

        # Додати кнопки для кожного замовлення
        keyboard = [
             [InlineKeyboardButton("Назад", callback_data=f"admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)


def pdfarhiv(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    if prof.is_authenticated:
        try:
            orders = Arhivzamovlen.objects.all()
        except:
            return
        if orders.exists():
            file_path = 'arhiv.txt'  # File path
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("Кількість замовлень № {}\n\n".format(len(orders)))
                for i, order in enumerate(orders, start=1):
                    file.write("ЗАМОВЛЕННЯ № {}\n".format(i))
                    file.write("Статус:\n")
                    if order.status_1:
                        file.write("- Контакт з клієнтом\n  коментар: {}\n  дата: {}\n".format(order.info_status_1,
                                                                                               order.datetime_status_1))
                    if order.status_2:
                        file.write(
                            "- Підтвердження замовлення\n  коментар: {}\n  дата: {}\n".format(order.info_status_2,
                                                                                              order.datetime_status_2))
                    if order.status_3:
                        file.write("- Оплата\n  коментар: {}\n  дата: {}\n".format(order.info_status_3,
                                                                                   order.datetime_status_3))
                    if order.status_4:
                        file.write("- Доставка\n  коментар: {}\n  дата: {}\n".format(order.info_status_4,
                                                                                     order.datetime_status_4))
                    if order.status_5:
                        file.write("- Закриття замовлення\n  коментар: {}\n  дата: {}\n".format(order.info_status_5,
                                                                                                order.datetime_status_5))
                    if order.status_6:
                        file.write("- Повернення/Відмова\n  коментар: {}\n  дата: {}\n".format(order.info_status_6,
                                                                                               order.datetime_status_6))
                    file.write("\nІнформація про користувача: {}\n".format(order.info_user))
                    file.write("\nІнформація про замовлення: {}\n".format(order.order_info))
                    file.write("\nДодаткова інформація: {}\n".format(order.info_zakaz))
                    file.write("\nСума: {} грн\n".format(order.total_price))
                    file.write("\n===========================================================================\n\n")

            with open(file_path, 'rb') as file:
                bot.send_document(chat_id=telegram_id, document=file, filename='arhiv.txt')
        else:
            message = "Немає доступних замовлень."
            bot.send_message(chat_id=telegram_id, text=message)
        knonka(message_id, telegram_id, bot)



