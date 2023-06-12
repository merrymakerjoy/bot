import telegram
from telegram import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
import glob
from telegram import ParseMode
from .views import *
from .comands import *
from .zamovlenia import *
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
from django.contrib.auth.models import User, Group



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


def information(message_id, telegram_id, bot):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    message =f"Обери що тебе цікавить:"
    keyboard = [
        [InlineKeyboardButton("💳 Оплата та доставка 🚚", callback_data=f"dostavka")],
         [InlineKeyboardButton("🔄 Обмін та повернення 🔄", callback_data=f"povernennia")],
        [InlineKeyboardButton("ℹ️ Про нас ℹ️", callback_data="pronas")],
         [InlineKeyboardButton("📞 Контакти 📞", callback_data="kontakty")],
        [InlineKeyboardButton("📚 Історія покупок 🧾", callback_data="history")],

        # [InlineKeyboardButton("🏠 Додому 🏠", callback_data="toys")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(telegram_id, message, reply_markup=reply_markup)


def dostavka(message_id, telegram_id, bot):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)

    with open('infoopys/dostavka.txt', 'r', encoding='utf-8') as file:
        contact_info = file.read()
    message_1 =f"💳 Оплата та доставка 🚚\n\n"
    message = message_1+contact_info
    keyboard = [
        [InlineKeyboardButton("🏠 Додому", callback_data="toys"),
         InlineKeyboardButton("🔙 Назад", callback_data="information")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(telegram_id, message, reply_markup=reply_markup)


def povernennia(message_id, telegram_id, bot):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)

    with open('infoopys/povernennia.txt', 'r', encoding='utf-8') as file:
        contact_info = file.read()
    message_1 =f"🔄 Обмін та повернення\n\n"

    message = message_1 + contact_info
    keyboard = [
        [InlineKeyboardButton("🏠 Додому", callback_data="toys"),
         InlineKeyboardButton("🔙 Назад", callback_data="information")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(telegram_id, message, reply_markup=reply_markup)


def pronas(message_id, telegram_id, bot):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)

    with open('infoopys/pronas.txt', 'r', encoding='utf-8') as file:
        contact_info = file.read()
    message_1 =f"ℹ️ Про нас:\n\n"
    message = message_1 + contact_info

    keyboard = [
        [InlineKeyboardButton("🏠 Додому", callback_data="toys"),
         InlineKeyboardButton("🔙 Назад", callback_data="information")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(telegram_id, message, reply_markup=reply_markup)


def kontakty(message_id, telegram_id, bot):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)

    with open('infoopys/konakty.txt', 'r', encoding='utf-8') as file:
        contact_info = file.read()

    message_1 = "📞 Контакти:\n\n"
    message_2 = contact_info
    message = message_1 + message_2
    keyboard = [
        [InlineKeyboardButton("📱 Зв'язатися з нами", callback_data="messages")],
        [InlineKeyboardButton("🏠 Додому", callback_data="toys"),
         InlineKeyboardButton("🔙 Назад", callback_data="information")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(telegram_id, message, reply_markup=reply_markup)


def messages(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    prof.step = "повідомлення"
    prof.is_chat = False
    prof.save()

    message = "✉️ Введи повідомлення"
    bot.sendMessage(telegram_id, message)


def messages_user(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    admin_users = User.objects.filter(groups__name='administrator', is_staff=True)

    text = data['message'].get('text')
    photo_data = data['message'].get('photo')
    caption = data['message'].get('caption')

    if admin_users.exists():
        admin_usernames = admin_users.values_list('username', flat=True)
        admin_chat_ids = [int(username) for username in admin_usernames]

        for chat_id in admin_chat_ids:
            admin = TelegramUser.objects.get(telegram_id=chat_id)
            admin.variable_1 = telegram_id
            admin.save()

            admin_message = f"У Вас нове повідомлення✉️ \nВід користувача: \n{prof}!!!\n"

            if caption and photo_data:
                photo = photo_data[-1]  # Вибираємо останню фотографію зі списку
                photo_id = photo['file_id']

                bot.send_message(chat_id=chat_id, text=admin_message)
                bot.send_photo(chat_id=chat_id, photo=photo_id, caption=caption)

            elif photo_data:
                photo = photo_data[-1]  # Вибираємо останню фотографію зі списку
                photo_id = photo['file_id']

                bot.send_message(chat_id=chat_id, text=admin_message)
                bot.send_photo(chat_id=chat_id, photo=photo_id)

            elif text:
                admin_message += text
                bot.send_message(chat_id=chat_id, text=admin_message)

            keyboard = [
                [InlineKeyboardButton("Зв'язатися з користувачем", callback_data="zviazatisia")],
                [InlineKeyboardButton("Адмін панель", callback_data="admin_panel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id=chat_id, text='↑↑↑', reply_markup=reply_markup)

    message = "✉️ Для продовження введи повідомлення або нажми 'Завершити діалог', для завершення"
    keyboard = [
        [InlineKeyboardButton("Завершити діалог", callback_data="zavershytydialog")],
        [InlineKeyboardButton("Додому", callback_data="toys"),
         InlineKeyboardButton("Назад", callback_data="information")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(telegram_id, message, reply_markup=reply_markup)


def zavershytydialog(message_id, telegram_id, bot, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    prof.step = "пусто"
    prof.is_chat = False
    prof.save()

    message = "🏁 Діалог завершено! Найблищим часом з Вами зв'яжеться наш менеджер! Дякуємо за звернення!"
    bot.sendMessage(telegram_id, message)
    knonka(message_id, telegram_id, bot)

