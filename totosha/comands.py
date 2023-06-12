import telegram
from telegram import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
import glob
from telegram import ParseMode
from .views import *
from .info import *
from .zamovlenia import *
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


def start(data, bot):
    try:
        telegram_id = data['message']['chat']['id']
        message = f"👋 Привіт, {data['message']['chat']['first_name']} {data['message']['chat']['last_name']}. Я великий магазин іграшок 🏬🧸, \n В мене є все або майже все🎉 🎁."
    except:
        telegram_id = data['callback_query']['message']['chat']['id']
        message = "👋 Привіт!"

    keyboard = [
        [
            InlineKeyboardButton("🎳 🧸  Іграшки. 👇Нажимай сюди! 🎲 🎯", callback_data='toys')
        ],

    ]

    admin_users = User.objects.filter(groups__name='administrator', is_staff=True)
    if admin_users.exists():
        admin_usernames = admin_users.values_list('username', flat=True)
        admin_chat_ids = [int(username) for username in admin_usernames]
        if telegram_id in admin_chat_ids:
            keyboard.append([InlineKeyboardButton("Вхід в адмін панель", callback_data='admin_panel')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.sendMessage(telegram_id, message, reply_markup=reply_markup)


def toys(message_id, telegram_id, bot):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    prof.step = "kategoria"
    prof.save()

    url = url_site
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    dropdown = soup.find('div', class_='dropdown')
    submenu_list = dropdown.find('ul', class_='submenu-list')
    submenu_items = submenu_list.find_all('li', class_='submenu-item')

    buttons = []
    row = []

    href_table = []

    for submenu_item in submenu_items:
        submenu_link = submenu_item.find('a', class_='submenu-link')
        if submenu_link:
            category = submenu_link.text.strip()
            href = str(submenu_link['href'])

            href_table.append({'href': href, 'category': category})

            entry = HrefTable.objects.filter(category=category, href=href, telegram_user=prof).first()
            if not entry:
                entry = HrefTable.objects.create(category=category, href=href, telegram_user=prof)

            callback_data = f"id_{entry.id}"

            if category:
                row.append(InlineKeyboardButton(category, callback_data=callback_data))
                if len(row) >= 1:
                    buttons.append(row)
                    row = []

    if row:
        buttons.append(row)

    reply_markup = InlineKeyboardMarkup(buttons, resize_keyboard=True)

    message = "🎲 🚂 Обери категорію: 🧸 🧩\n\n"
    delete_telegram_message(message_id, telegram_id, bot)

    bot.send_message(telegram_id, message, reply_markup=reply_markup)
    knonka(message_id, telegram_id, bot)


def kategoria(message_id, telegram_id, bot, id_com):

    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    prof.step = "podkategoria"
    prof.save()
    entry = HrefTable.objects.get(id=id_com)
    url_cat = url_site + entry.href
    name_cat = entry.category
    url = url_cat

    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    try:

        dropdown = soup.find('div', class_='filter-item__content')
        submenu_list = dropdown.find('div', class_='filter-item__list')
        submenu_items = submenu_list.find_all('div', class_='filter-item__item')

        buttons = []
        row = []
        href_table = []

        for submenu_item in submenu_items:
            submenu_link = submenu_item.find('a', class_='filter-item__link')
            if submenu_link:
                category = submenu_link.text.strip()
                href = str(submenu_link['href'])

                href_table.append({'href': href, 'category': category})

                entry = HrefTable.objects.filter(category=category, href=href, telegram_user=prof).first()
                if not entry:
                    entry = HrefTable.objects.create(category=category, href=href, telegram_user=prof)

                callback_data = f"id_{entry.id}"

                if category:
                    row.append(InlineKeyboardButton(category, callback_data=callback_data))
                    if len(row) >= 1:
                        buttons.append(row)
                        row = []

        if row:
            buttons.append(row)

        reply_markup = InlineKeyboardMarkup(buttons, resize_keyboard=True)
        message = f"🎠 {name_cat}:\n\n"
        delete_telegram_message(message_id, telegram_id, bot)

        bot.sendMessage(telegram_id, message, reply_markup=reply_markup)
    except:
        pass
    try:
        podkategoria(message_id, telegram_id, bot, id_com)
    except:
        pass

    knonka(message_id, telegram_id, bot)


def podkategoria(message_id, telegram_id, bot, id_com):

    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    # prof.step = "tovar"
    # prof.save()

    # Delete existing files in the media folder
    existing_files = glob.glob('media/site/*')
    for file_path in existing_files:
        os.remove(file_path)

    entry = HrefTable.objects.get(id=id_com)
    url_cat = url_site + entry.href
    name_cat = entry.category
    url = url_cat

    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    pagination_div = soup.find('div', class_='pagination')
    pagination_items_active = pagination_div.find_all('li', class_='pagination-item is-active')
    pagination_items = pagination_div.find_all('li', class_='pagination-item')
    all_page = len(pagination_items)
    if all_page:
        all_page = all_page - 2
    else:
        all_page = 1
    page = 1  # Initialize page to 1
    for item in pagination_items_active:
        link_active = item.find('a', class_='pagination-link')
        if link_active:
            data_page = link_active.get('data-page')
            page = int(data_page) + 1

    product_items = soup.find_all('div', class_='col-md-6 col-lg-4')
    message_parts = []
    row = []  # Створення порожнього списку для рядків
    for product_item in product_items:
        description = product_item.find('div', class_='product-item')
        if description:
            submenu_link = description.find('a', class_='product-item__title')
            product_link = description.find('a', class_='product-item__link')

            price_element = description.find('div', class_='product-item__bottom')
            price_element = price_element.find('div', class_='product-item__price')
            price_span = price_element.find('span')

            if submenu_link:
                category = submenu_link.text.strip()
                href = str(submenu_link['href'])
                price = price_span.text.strip()

                entry = Toys.objects.filter(category=category, href=href, telegram_user=prof).first()
                if not entry:
                    entry = Toys.objects.create(category=category, href=href, telegram_user=prof)

                # Об'єднання тексту з category та price
                category_with_price = f"💰 Вартість: {price} - {category}"

            if product_link:
                image_element = product_link.find('img', class_='product-item__image')
                if image_element:
                    image_url = image_element['data-src']
                    # Завантаження зображення
                    image_name = f"{entry.id}.jpg"
                    image_path = os.path.join('media/site', image_name)
                    urllib.request.urlretrieve(image_url, image_path)
                    # Додавання зображення до повідомлення
                    row.append({'type': 'photo', 'file': image_path, 'category': category_with_price, 'ent': entry.id})
                    # Перевірка довжини рядка
                    if len(row) >= 1:
                        message_parts.append(row)  # Додавання рядка до повідомлення
                        row = []  # Очищення рядка для наступного рядка
    # Додавання останнього рядка, якщо необхідно
    if row:
        message_parts.append(row)
    # Відправлення повідомлення з фото, кнопками і текстом
    delete_telegram_message(message_id, telegram_id, bot)

    bot.send_message(chat_id=telegram_id, text=name_cat)
    for row in message_parts:
        for part in row:
            with open(part['file'], 'rb') as photo:
                bot.send_photo(telegram_id, photo=photo.read())
            keyboard = [
                [InlineKeyboardButton("ℹ️ Детальшіше...", callback_data=f"detal_{part['ent']}"),
                 InlineKeyboardButton("🛒 Купити", callback_data=f"bye_{part['ent']}"),
                 InlineKeyboardButton("💖 В обране", callback_data=f"favorites_{part['ent']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(telegram_id, part['category'], reply_markup=reply_markup)

    keyboard = [
        [InlineKeyboardButton("⬅️ Попередня сторінка", callback_data="previouspage"),
         InlineKeyboardButton("Наступна сторінка ➡️", callback_data="nextpage")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=telegram_id, text=f"📃 Сторінка № {page}, Всього - {all_page} 🔢", reply_markup=reply_markup)

    definition_page(message_id, telegram_id, bot, url, id_com)


def definition_page(message_id, telegram_id, bot, url, id_com):
    # delete_telegram_message(message_id, telegram_id, bot)
    prof = TelegramUser.objects.get(telegram_id=telegram_id)

    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    pagination_div = soup.find('div', class_='pagination')
    pagination_items_active = pagination_div.find_all('li', class_='pagination-item is-active')
    pagination_items = pagination_div.find_all('li', class_='pagination-item')
    all_page = len(pagination_items)
    if all_page:
        all_page = all_page-2

    for item in pagination_items_active:
        link_active = item.find('a', class_='pagination-link')
        if link_active:
            data_page = link_active.get('data-page')

    for item in pagination_items:
        link_prev = item.find('a', class_='pagination-link page-link page-linkPrev')
        link_next = item.find('a', class_='pagination-link page-link page-linkNext')

        if link_prev:
            href = link_prev['href']
            prof.prev_page = href
            prof.save()

        if link_next:
            href = link_next['href']
            prof.next_page = href
            prof.save()

    prof.href = id_com
    prof.save()


def previouspage(message_id, telegram_id, bot):
    # Delete existing files in the media folder
    existing_files = glob.glob('media/site/*')
    for file_path in existing_files:
        os.remove(file_path)

    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    id_com = prof.href
    # entry = HrefTable.objects.get(id=id_com)
    try:
        entry = HrefTable.objects.get(id=id_com)
    except:
        return
    url_cat = url_site + prof.prev_page
    name_cat = entry.category
    url = url_cat

    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    pagination_div = soup.find('div', class_='pagination')
    pagination_items_active = pagination_div.find_all('li', class_='pagination-item is-active')
    pagination_items = pagination_div.find_all('li', class_='pagination-item')
    all_page = len(pagination_items)
    if all_page:
        all_page = all_page - 2
    else:
        all_page = 1
    page = 1  # Initialize page to 1
    for item in pagination_items_active:
        link_active = item.find('a', class_='pagination-link')
        if link_active:
            data_page = link_active.get('data-page')
            page = int(data_page) + 1
    product_items = soup.find_all('div', class_='col-md-6 col-lg-4')
    message_parts = []
    row = []  # Створення порожнього списку для рядків
    for product_item in product_items:
        description = product_item.find('div', class_='product-item')
        if description:
            submenu_link = description.find('a', class_='product-item__title')
            product_link = description.find('a', class_='product-item__link')
            price_element = description.find('div', class_='product-item__bottom')
            price_element = price_element.find('div', class_='product-item__price')
            price_span = price_element.find('span')

            if submenu_link:
                category = submenu_link.text.strip()
                href = str(submenu_link['href'])
                price = price_span.text.strip()

                entry = Toys.objects.filter(category=category, href=href, telegram_user=prof).first()
                if not entry:
                    entry = Toys.objects.create(category=category, href=href, telegram_user=prof)

                # Об'єднання тексту з category та price
                category_with_price = f"💸 Вартість: {price} - {category}"

            if product_link:
                image_element = product_link.find('img', class_='product-item__image')
                if image_element:
                    image_url = image_element['data-src']
                    # Завантаження зображення
                    image_name = f"{entry.id}.jpg"
                    image_path = os.path.join('media/site', image_name)
                    urllib.request.urlretrieve(image_url, image_path)
                    # Додавання зображення до повідомлення
                    row.append({'type': 'photo', 'file': image_path, 'category': category_with_price, 'ent': entry.id})
                    # Перевірка довжини рядка
                    if len(row) >= 1:
                        message_parts.append(row)  # Додавання рядка до повідомлення
                        row = []  # Очищення рядка для наступного рядка
    # Додавання останнього рядка, якщо необхідно
    if row:
        message_parts.append(row)
    delete_telegram_message(message_id, telegram_id, bot)

    # Відправлення повідомлення з фото, кнопками і текстом

    bot.send_message(chat_id=telegram_id, text=name_cat)
    for row in message_parts:
        for part in row:
            with open(part['file'], 'rb') as photo:
                bot.send_photo(telegram_id, photo=photo.read())
            keyboard = [
                [InlineKeyboardButton("ℹ️ Детальшіше...", callback_data=f"detal_{part['ent']}"),
                 InlineKeyboardButton("🛒 Купити", callback_data=f"bye_{part['ent']}"),
                 InlineKeyboardButton("💖 В обране", callback_data=f"favorites_{part['ent']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(telegram_id, part['category'], reply_markup=reply_markup)

    keyboard = [
        [InlineKeyboardButton("⬅️ Попередня сторінка", callback_data="previouspage"),
         InlineKeyboardButton("Наступна сторінка ➡️", callback_data="nextpage")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=telegram_id, text=f"🗒️ Сторінка № {page}, Всього - {all_page} 🔢", reply_markup=reply_markup)

    definition_page(message_id, telegram_id, bot, url, id_com)


def nextpage(message_id, telegram_id, bot):
    # Delete existing files in the media folder
    existing_files = glob.glob('media/site/*')
    for file_path in existing_files:
        os.remove(file_path)

    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    id_com = prof.href
    # entry = HrefTable.objects.get(id=id_com)
    try:
        entry = HrefTable.objects.get(id=id_com)
    except:
        return
    url_cat = url_site + prof.next_page
    name_cat = entry.category
    url = url_cat

    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    pagination_div = soup.find('div', class_='pagination')
    pagination_items_active = pagination_div.find_all('li', class_='pagination-item is-active')
    pagination_items = pagination_div.find_all('li', class_='pagination-item')
    all_page = len(pagination_items)
    if all_page:
        all_page = all_page - 2
    else:
        all_page = 1
    page = 1  # Initialize page to 1
    for item in pagination_items_active:
        link_active = item.find('a', class_='pagination-link')
        if link_active:
            data_page = link_active.get('data-page')
            page = int(data_page) + 1
    product_items = soup.find_all('div', class_='col-md-6 col-lg-4')
    message_parts = []
    row = []  # Створення порожнього списку для рядків
    for product_item in product_items:
        description = product_item.find('div', class_='product-item')
        if description:
            submenu_link = description.find('a', class_='product-item__title')
            product_link = description.find('a', class_='product-item__link')
            price_element = description.find('div', class_='product-item__bottom')
            price_element = price_element.find('div', class_='product-item__price')
            price_span = price_element.find('span')

            if submenu_link:
                category = submenu_link.text.strip()
                href = str(submenu_link['href'])
                price = price_span.text.strip()

                entry = Toys.objects.filter(category=category, href=href, telegram_user=prof).first()
                if not entry:
                    entry = Toys.objects.create(category=category, href=href, telegram_user=prof)

                # Об'єднання тексту з category та price
                category_with_price = f"💰 Вартість: {price} - {category}"

            if product_link:
                image_element = product_link.find('img', class_='product-item__image')
                if image_element:
                    image_url = image_element['data-src']
                    # Завантаження зображення
                    image_name = f"{entry.id}.jpg"
                    image_path = os.path.join('media/site', image_name)
                    urllib.request.urlretrieve(image_url, image_path)
                    # Додавання зображення до повідомлення
                    row.append({'type': 'photo', 'file': image_path, 'category': category_with_price, 'ent': entry.id})
                    # Перевірка довжини рядка
                    if len(row) >= 1:
                        message_parts.append(row)  # Додавання рядка до повідомлення
                        row = []  # Очищення рядка для наступного рядка
    # Додавання останнього рядка, якщо необхідно
    if row:
        message_parts.append(row)
    delete_telegram_message(message_id, telegram_id, bot)

    # Відправлення повідомлення з фото, кнопками і текстом
    bot.send_message(chat_id=telegram_id, text=name_cat)
    for row in message_parts:
        for part in row:
            with open(part['file'], 'rb') as photo:
                bot.send_photo(telegram_id, photo=photo.read())
            keyboard = [
                [InlineKeyboardButton("ℹ️ Детальшіше...", callback_data=f"detal_{part['ent']}"),
                 InlineKeyboardButton("🛒 Купити", callback_data=f"bye_{part['ent']}"),
                 InlineKeyboardButton("💖 В обране", callback_data=f"favorites_{part['ent']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(telegram_id, part['category'], reply_markup=reply_markup)

    keyboard = [
        [InlineKeyboardButton("⬅️ Попередня сторінка", callback_data="previouspage"),
         InlineKeyboardButton("Наступна сторінка ➡️", callback_data="nextpage")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=telegram_id, text=f"🗒️ Сторінка № {page}, Всього - {all_page} 🔢", reply_markup=reply_markup)

    definition_page(message_id, telegram_id, bot, url, id_com)


def detal(message_id, telegram_id, bot, id_detal):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)

    entry = Toys.objects.get(id=id_detal)
    url_cat = url_site + str(entry)
    name_toys = entry.category
    url = url_cat

    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Фото
    image_name = f"{id_detal}.jpg"
    image_path = os.path.join('media/site', image_name)
    absolute_image_path = os.path.abspath(image_path)
    try:
        with open(absolute_image_path, 'rb') as photo:
            bot.send_photo(telegram_id, photo=photo.read())
    except FileNotFoundError:
        # Handle the case when the file is not found
        bot.send_message(telegram_id, "Photo not found.")
    #Ціна
    product_price = soup.find('div', class_='product-price__block')
    if product_price:
        price_element = product_price.find('div', class_='product-price')
        if price_element:
            price = price_element.get_text(strip=True)
    #Опис
    product_description = soup.find("div", class_="tabs-item is-show", id="product-description")
    if product_description:
        description = product_description.find("div", class_="wysiwyg").get_text(strip=True)

    message =f"💰 Вартість: {price} {name_toys} \n\n{description}"
    keyboard = [
        [InlineKeyboardButton("🛒 Купити", callback_data=f"bye_{id_detal}"),
         InlineKeyboardButton("💚 Добавити в обране", callback_data=f"favorites_{id_detal}")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    delete_telegram_message(message_id, telegram_id, bot)

    bot.send_message(telegram_id, message, reply_markup=reply_markup)


def favorites(message_id, telegram_id, bot, id_favorites, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    entry = Toys.objects.get(id=id_favorites)
    url_cat = url_site + str(entry)
    name_toys = entry.category
    url = url_cat

    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Фото
    image_name = f"{id_favorites}.jpg"
    source_image_path = os.path.join('media/site', image_name)
    destination_image_path = os.path.join('media/obrane', image_name)
    # Копіювання фото з джерела до призначення
    copyfile(source_image_path, destination_image_path)

    # Ціна
    product_price = soup.find('div', class_='product-price__block')
    if product_price:
        price_element = product_price.find('div', class_='product-price')
        if price_element:
            price = price_element.get_text(strip=True)
    #Артикул
    product_info = soup.find('div', class_='product-info')
    if product_info:
        article_element = product_info.find('div', class_='product-info__article')
        if article_element:
            article = article_element.get_text(strip=True)

    favorites_toys = Obrane.objects.filter(name_toys=name_toys, price_toys=price, artikul_toys=article).first()
    if not favorites_toys:
        favorites_toys = Obrane.objects.create(name_toys=name_toys, price_toys=price, artikul_toys=article,
                                               telegram_user=prof)
        favorites_toys.photo_toys.save(image_name, open(destination_image_path, 'rb'), save=True)
    message = "⭐️ Товар додано до обраного! ⭐️"
    bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)


def bye(message_id, telegram_id, bot, id_bye, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    entry = Toys.objects.get(id=id_bye)
    url_cat = url_site + str(entry)
    name_toys = entry.category
    url = url_cat

    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Фото
    image_name = f"{id_bye}.jpg"
    source_image_path = os.path.join('media/site', image_name)
    destination_image_path = os.path.join('media/korzina', image_name)
    # Копіювання фото з джерела до призначення
    copyfile(source_image_path, destination_image_path)

    # Ціна
    product_price = soup.find('div', class_='product-price__block')
    if product_price:
        price_element = product_price.find('div', class_='product-price')
        if price_element:
            price = price_element.get_text(strip=True)
    # Артикул
    product_info = soup.find('div', class_='product-info')
    if product_info:
        article_element = product_info.find('div', class_='product-info__article')
        if article_element:
            article = article_element.get_text(strip=True)

    favorites_toys = Korzina.objects.filter(name_toys=name_toys, price_toys=price, artikul_toys=article).first()
    if not favorites_toys:
        favorites_toys = Korzina.objects.create(name_toys=name_toys, price_toys=price, artikul_toys=article, amount_toys=1,
                                               telegram_user=prof)
        favorites_toys.photo_toys.save(image_name, open(destination_image_path, 'rb'), save=True)
    message = "🛒 Товар додано до корзини! 📥"
    bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)


def korzina(message_id, telegram_id, bot):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    korzina_items = Korzina.objects.filter(telegram_user=prof)
    delete_telegram_message(message_id, telegram_id, bot)

    if not korzina_items:
        bot.send_message(chat_id=telegram_id, text="🤷‍♂️ В корзині пусто. Давай швидше щось обирай 😉")
        return

    bot.send_message(chat_id=telegram_id, text="💙 Товари, які Ви обрали:")

    total_cost = 0

    for item in korzina_items:
        name_toys = item.name_toys
        price_toy = "".join([x for x in item.price_toys if x.isdigit()])
        price_toys = int(price_toy)
        artikul_toys = item.artikul_toys
        amount_toys = int(item.amount_toys)
        photo_toys = item.photo_toys.path if item.photo_toys else None

        # Create the buttons
        buttons = [
            InlineKeyboardButton("🗑️ Видалити", callback_data=f"delete_{item.id}"),
            InlineKeyboardButton("➖ 1", callback_data=f"subtract_{item.id}"),
            InlineKeyboardButton("➕ 1", callback_data=f"add_{item.id}")
        ]
        if photo_toys:
            with open(photo_toys, 'rb') as photo:
                bot.send_photo(chat_id=telegram_id, photo=photo)
        total_price = float(price_toys) * amount_toys
        total_cost += total_price  # Calculate the total cost based on price and quantity

        # Create the keyboard markup and attach it to the message
        reply_markup = InlineKeyboardMarkup([buttons])
        bot.send_message(chat_id=telegram_id, text=f"✔️Назва: {name_toys}\nЦіна: {price_toys} грн.\nКількість: {amount_toys}\nВартість:{total_price} грн\nАртикул: {artikul_toys}", reply_markup=reply_markup)
    message = f"💰Загальна вартість замовлення становить - {total_cost} грн.🤑🤑🤑"
    keyboard = [
        [InlineKeyboardButton("🛒✅ Оформити замовлення", callback_data=f"oformytyzakaz")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup)

    knonka(message_id, telegram_id, bot)


def delete(message_id, telegram_id, bot, id_delete, data):
    delete_telegram_message(message_id, telegram_id, bot)

    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    korzina_item = Korzina.objects.filter(telegram_user=prof, id=id_delete).first()

    if korzina_item:
        korzina_item.delete()
    message = "🗑️ Товар видалено з корзини!"
    bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)
    korzina(message_id, telegram_id, bot)

    keyboard = [
        [KeyboardButton(text="🛒 Корзина"), KeyboardButton(text="💖 Обрані товари")],
        [KeyboardButton(text="🏠 Додому"), KeyboardButton(text="🔙 Назад")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    random_emoji = random.choice(emoji)
    bot.send_message(telegram_id, text=random_emoji, reply_markup=reply_markup)


def add(message_id, telegram_id, bot, id_add, data):
    delete_telegram_message(message_id, telegram_id, bot)

    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    korzina_item = Korzina.objects.filter(telegram_user=prof, id=id_add).first()

    if korzina_item:
        korzina_item.amount_toys = int(korzina_item.amount_toys) + 1  # Increase the amount by 1
        korzina_item.save()  # Save the updated value

        message = "👍 Додано +1 позицію"
        bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)
        delete_telegram_message(message_id, telegram_id, bot)

        korzina(message_id, telegram_id, bot)
    else:
        message = "🔴 Помилка"
        bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)
        knonka(message_id, telegram_id, bot)


def subtract(message_id, telegram_id, bot, id_subtract, data):
    delete_telegram_message(message_id, telegram_id, bot)

    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    korzina_item = Korzina.objects.filter(telegram_user=prof, id=id_subtract).first()

    if korzina_item:
        amount_toys = int(korzina_item.amount_toys)  # Convert to integer
        if amount_toys > 1:
            korzina_item.amount_toys = str(amount_toys - 1)  # Decrease the amount by 1
            korzina_item.save()  # Save the updated value

            message = "🗑️ Видалено 1 позицію"
            bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)
            delete_telegram_message(message_id, telegram_id, bot)

            korzina(message_id, telegram_id, bot)
        else:
            message = "⚠️ Кількість позицій вже мінімальна"
            bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)
    else:
        message = "⚠️ Помилка"
        bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)


def obrane(message_id, telegram_id, bot):
    delete_telegram_message(message_id, telegram_id, bot)

    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    obrane_items = Obrane.objects.filter(telegram_user=prof)

    if not obrane_items:
        bot.send_message(chat_id=telegram_id, text="🤷‍♂️ Ви ще не добавили нічого до обраного. Нажимай на 💖 і товар з'явиться тут😉")
        return
    bot.send_message(chat_id=telegram_id, text="💖💖💖Товари які Ви обрали:💖💖💖")

    for item in obrane_items:
        name_toys = item.name_toys
        price_toys = item.price_toys
        artikul_toys = item.artikul_toys
        photo_toys = item.photo_toys.path if item.photo_toys else None
        buttons = [
            InlineKeyboardButton("❌ Видалити", callback_data=f"vydalyty_{item.id}"),
            InlineKeyboardButton("💰 Купити 💸 ", callback_data=f"kupyty_{item.id}"),
            # InlineKeyboardButton("Кількість +1", callback_data=f"add_{item.id}")
        ]

        if photo_toys:
            with open(photo_toys, 'rb') as photo:
                bot.send_photo(chat_id=telegram_id, photo=photo)

        # Create the keyboard markup and attach it to the message
        reply_markup = InlineKeyboardMarkup([buttons])
        bot.send_message(chat_id=telegram_id,
                         text=f"✔️Назва: {name_toys}\nЦіна: {price_toys}.\nАртикул: {artikul_toys}",
                         reply_markup=reply_markup)

    knonka(message_id, telegram_id, bot)


def vydalyty(message_id, telegram_id, bot, id_vydalyty, data):
    delete_telegram_message(message_id, telegram_id, bot)
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    vydalyty_item = Obrane.objects.filter(telegram_user=prof, id=id_vydalyty).first()

    if vydalyty_item:
        vydalyty_item.delete()
    message = "🗑️ Товар видалено з обраного!"
    bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)
    obrane(message_id, telegram_id, bot)
    knonka(message_id, telegram_id, bot)


def kupyty(message_id, telegram_id, bot, id_kupyty, data):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    entry = Obrane.objects.get(id=id_kupyty)

    # Копіювання фото
    image_name = f"{id_kupyty}.jpg"
    source_image_path = entry.photo_toys.path
    destination_image_path = os.path.join('media/korzina', image_name)
    copyfile(source_image_path, destination_image_path)

    # Отримання даних
    name_toys = entry.name_toys
    price_toys = entry.price_toys
    artikul_toys = entry.artikul_toys

    favorites_toys = Korzina.objects.filter(name_toys=name_toys, price_toys=price_toys, artikul_toys=artikul_toys).first()
    if not favorites_toys:
        # Створення нового запису в таблиці Korzina
        favorites_toys = Korzina.objects.create(
            name_toys=name_toys,
            price_toys=price_toys,
            artikul_toys=artikul_toys,
            amount_toys=1,
            telegram_user=prof
        )
        favorites_toys.photo_toys.save(image_name, open(destination_image_path, 'rb'), save=True)

    message = "🛒 Товар додано до корзини!"
    bot.answer_callback_query(callback_query_id=data['callback_query']['id'], text=message, show_alert=True)


def oformytyzakaz(message_id, telegram_id, bot):
    delete_telegram_message(message_id, telegram_id, bot)
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    zakaz_all = Korzina.objects.filter(telegram_user=prof)

    total_cost = 0
    messages = ""

    for zakaz in zakaz_all:
        name_toys = zakaz.name_toys
        price_toy = "".join([x for x in zakaz.price_toys if x.isdigit()])
        price_toys = int(price_toy)
        artikul_toys = zakaz.artikul_toys
        amount_toys = int(zakaz.amount_toys)

        total_price = price_toys * amount_toys
        total_cost += total_price
        messages += f"✔️{name_toys}, Ціна: {total_price} грн,кількість - {amount_toys}  шт.\n\n"

    keyboard = [
            [InlineKeyboardButton("✅ Підтвердити", callback_data='confirm'),
             InlineKeyboardButton("❌ Скасувати", callback_data='korzina')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(chat_id=telegram_id, text=f"🛍️Ваше замовлення:\n\n{messages}\n💳 Сума до сплати: {total_cost} грн", reply_markup=reply_markup)


def search(message_id, telegram_id, bot):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    prof.step = "search"
    prof.save()
    message = "Введіть інформацію ℹ️ для пошуку 🔎"

    bot.sendMessage(chat_id=telegram_id, text=message)


def poshuk(message_id, telegram_id, bot, text):
    prof = TelegramUser.objects.get(telegram_id=telegram_id)
    modified_text = quote(text)

    url_search = f"/catalog/catalog/search?filter%5Bsearch%5D={modified_text}&id="

    # Delete existing files in the media folder
    existing_files = glob.glob('media/site/*')
    for file_path in existing_files:
        os.remove(file_path)

    id_com = prof.href
    # entry = HrefTable.objects.get(id=id_com)
    try:
        entry = HrefTable.objects.get(id=id_com)
    except HrefTable.DoesNotExist:
        entry = 1
    url_cat = url_site + url_search
    name_cat = f'😄{text}'
    url = url_cat

    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    pagination_div = soup.find('div', class_='pagination')
    pagination_items_active = pagination_div.find_all('li', class_='pagination-item is-active')
    pagination_items = pagination_div.find_all('li', class_='pagination-item')
    all_page = len(pagination_items)
    if all_page:
        all_page = all_page - 2
    else:
        all_page = 1
    page = 1  # Initialize page to 1
    for item in pagination_items_active:
        link_active = item.find('a', class_='pagination-link')
        if link_active:
            data_page = link_active.get('data-page')
            page = int(data_page) + 1
    product_items = soup.find_all('div', class_='col-md-6 col-lg-4')
    message_parts = []
    row = []  # Створення порожнього списку для рядків
    for product_item in product_items:
        description = product_item.find('div', class_='product-item')
        if description:
            submenu_link = description.find('a', class_='product-item__title')
            product_link = description.find('a', class_='product-item__link')
            price_element = description.find('div', class_='product-item__bottom')
            price_element = price_element.find('div', class_='product-item__price')
            price_span = price_element.find('span')

            if submenu_link:
                category = submenu_link.text.strip()
                href = str(submenu_link['href'])
                price = price_span.text.strip()

                entry = Toys.objects.filter(category=category, href=href, telegram_user=prof).first()
                if not entry:
                    entry = Toys.objects.create(category=category, href=href, telegram_user=prof)

                # Об'єднання тексту з category та price
                category_with_price = f"💸 Вартість: {price} - {category}"

            if product_link:
                image_element = product_link.find('img', class_='product-item__image')
                if image_element:
                    image_url = image_element['data-src']
                    # Завантаження зображення
                    image_name = f"{entry.id}.jpg"
                    image_path = os.path.join('media/site', image_name)
                    urllib.request.urlretrieve(image_url, image_path)
                    # Додавання зображення до повідомлення
                    row.append({'type': 'photo', 'file': image_path, 'category': category_with_price, 'ent': entry.id})
                    # Перевірка довжини рядка
                    if len(row) >= 1:
                        message_parts.append(row)  # Додавання рядка до повідомлення
                        row = []  # Очищення рядка для наступного рядка

    if not product_items:
        name_cat = "😔 Нажаль за Вашим запитом нічого не знайдено. 😔\n🔄 Спробуйте ще раз!"

    # Додавання останнього рядка, якщо необхідно
    if row:
        message_parts.append(row)
    delete_telegram_message(message_id, telegram_id, bot)

    # Відправлення повідомлення з фото, кнопками і текстом

    bot.send_message(chat_id=telegram_id, text=name_cat)
    for row in message_parts:
        for part in row:
            with open(part['file'], 'rb') as photo:
                bot.send_photo(telegram_id, photo=photo.read())
            keyboard = [
                [InlineKeyboardButton("ℹ️ Детальшіше...", callback_data=f"detal_{part['ent']}"),
                 InlineKeyboardButton("🛒 Купити", callback_data=f"bye_{part['ent']}"),
                 InlineKeyboardButton("💖 В обране", callback_data=f"favorites_{part['ent']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(telegram_id, part['category'], reply_markup=reply_markup)

    keyboard = [
        [InlineKeyboardButton("⬅️ Попередня сторінка", callback_data="previouspage"),
         InlineKeyboardButton("Наступна сторінка ➡️", callback_data="nextpage")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=telegram_id, text=f"🗒️ Сторінка № {page}, Всього - {all_page} 🔢",
                     reply_markup=reply_markup)

    definition_page(message_id, telegram_id, bot, url, id_com)
    knonka(message_id, telegram_id, bot)

