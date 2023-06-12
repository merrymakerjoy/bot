from django.contrib.sites import requests
from django.shortcuts import render
from bs4 import BeautifulSoup
from .comands import *
from .info import *
from .zamovlenia import *
from .adm import *
from django.contrib.auth.models import User, Group

from django.shortcuts import render
from django.http import HttpRequest
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
import requests


bot = Bot('6271774025:AAEWBWg24J3UBGySkwT7OSvZxKcA1drreiQ')

#https://api.telegram.org/bot6271774025:AAEWBWg24J3UBGySkwT7OSvZxKcA1drreiQ/setWebHook?url=https://7197-188-190-190-33.ngrok-free.app/telegram/
# taskkill /IM ngrok.exe /F


@csrf_exempt
def telegram_webhook(request):
    data = json.loads(request.body)

    print(data)

    if 'message' in data:
        telegram_id = data['message']['chat']['id']
        message_id = data['message']['message_id']

        if 'photo' in data['message']:
            prof = TelegramUser.objects.get(telegram_id=telegram_id)
            if prof.step == 'rozsilka':
                rozsilkauser(message_id, telegram_id, bot, data)

            elif prof.step == 'повідомлення':
                messages_user(message_id, telegram_id, bot, data)

            elif prof.is_chat:
                vidpovid(message_id, telegram_id, bot, data)

        elif 'text' in data['message']:
            if '/start' in data['message']['text']:
                try:
                    TelegramUser.objects.get(telegram_id=telegram_id)
                except TelegramUser.DoesNotExist:
                    TelegramUser.objects.create(telegram_id=telegram_id)

                prof = TelegramUser.objects.get(telegram_id=telegram_id)

                if 'first_name' in data['message']['chat']:
                    prof.first_name = data['message']['chat']['first_name']
                if 'last_name' in data['message']['chat']:
                    prof.last_name = data['message']['chat']['last_name']
                if 'username' in data['message']['chat']:
                    prof.username = data['message']['chat']['username']
                prof.save()
                start(data, bot)

            elif 'contact' in data['message']:
                prof = TelegramUser.objects.get(telegram_id=telegram_id)
                prof.phone = data['message']['contact']['phone_number']
                prof.save

            elif 'Корзина' in data['message']['text']:
                korzina(message_id, telegram_id, bot)
            elif 'Обрані товари' in data['message']['text']:
                obrane(message_id, telegram_id, bot)
            elif 'Назад' in data['message']['text']:
                toys(message_id, telegram_id, bot)
            elif 'Додому' in data['message']['text']:
                toys(message_id, telegram_id, bot)
            elif 'Пошук' in data['message']['text']:
                search(message_id, telegram_id, bot)
            elif 'Інформація' in data['message']['text']:
                information(message_id, telegram_id, bot)
            elif 'Написати нам' in data['message']['text']:
                messages(message_id, telegram_id, bot, data)
            elif 'Історія замовлень' in data['message']['text']:
                history(message_id, telegram_id, bot, data)
            elif 'Вхід в панель адміністратора' in data['message']['text']:
                admin_panel(data, telegram_id, bot)

            elif data['message']['text'] != '':
                prof = TelegramUser.objects.get(telegram_id=telegram_id)
                if prof.is_chat:
                    vidpovid(message_id, telegram_id, bot, data)

                elif prof.step == 'search':
                    text = data['message']['text']
                    poshuk(message_id, telegram_id, bot, text)

                elif prof.step == 'повідомлення':
                    messages_user(message_id, telegram_id, bot, data)

                elif prof.step == 'пошуккористувача':
                    searchuser(message_id, telegram_id, bot, data)

                elif prof.step == 'rozsilka':
                    rozsilkauser(message_id, telegram_id, bot, data)

                elif prof.step == 'Коментарстатуса':
                    toaddkomentarstatysa(message_id, telegram_id, bot, data)

                elif prof.step == 'Додатковаінформація':
                    toaddkomentarszakaz(message_id, telegram_id, bot, data)
        else:
            pass

    if 'callback_query' in data:
        telegram_id = data['callback_query']['message']['chat']['id']
        message_id = data['callback_query']['message']['message_id']
        prof = TelegramUser.objects.get(telegram_id=telegram_id)

        if 'toys' in data['callback_query']['data']:
            toys(message_id, telegram_id, bot)

        elif 'previouspage' in data['callback_query']['data']:
            previouspage(message_id, telegram_id, bot)

        elif 'admin_panel' in data['callback_query']['data']:
            admin_panel(data, telegram_id, bot)

        elif 'write' in data['callback_query']['data']:
            write(data, telegram_id, bot)

        elif 'nextpage' in data['callback_query']['data']:
            nextpage(message_id, telegram_id, bot)

        elif 'korzina' in data['callback_query']['data']:
            korzina(message_id, telegram_id, bot)

        elif 'obrane' in data['callback_query']['data']:
            obrane(message_id, telegram_id, bot)

        elif 'oformytyzakaz' in data['callback_query']['data']:
            oformytyzakaz(message_id, telegram_id, bot)

        elif 'confirm' in data['callback_query']['data']:
            confirm(message_id, telegram_id, bot, data)

        elif 'dostavka' in data['callback_query']['data']:
            dostavka(message_id, telegram_id, bot)

        elif 'povernennia' in data['callback_query']['data']:
            povernennia(message_id, telegram_id, bot)

        elif 'pronas' in data['callback_query']['data']:
            pronas(message_id, telegram_id, bot)

        elif 'kontakty' in data['callback_query']['data']:
            kontakty(message_id, telegram_id, bot)

        elif 'information' in data['callback_query']['data']:
            information(message_id, telegram_id, bot)

        elif 'pidklychyty_user' in data['callback_query']['data']:
            pidklychyty_user(message_id, telegram_id, bot, data)

        elif 'vidklychyty_user' in data['callback_query']['data']:
            vidklychyty_user(message_id, telegram_id, bot, data)

        elif 'stop_user' in data['callback_query']['data']:
            stop_user(message_id, telegram_id, bot, data)

        elif 'zviazatisia' in data['callback_query']['data']:
            zviazatisia(message_id, telegram_id, bot, data)

        elif 'zatisia' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            id_kor = parsed_data[1]
            zatisia(message_id, telegram_id, bot, data, id_kor)

        elif 'messages' in data['callback_query']['data']:
            messages(message_id, telegram_id, bot, data)

        elif 'zavershytydialog' in data['callback_query']['data']:
            zavershytydialog(message_id, telegram_id, bot, data)

        elif 'rozsilka' in data['callback_query']['data']:
            rozsilka(message_id, telegram_id, bot, data)

        elif 'zavthshyty' in data['callback_query']['data']:
            zavthshyty(message_id, telegram_id, bot, data)

        elif 'history' in data['callback_query']['data']:
            history(message_id, telegram_id, bot, data)

        elif 'work' in data['callback_query']['data']:
            work(message_id, telegram_id, bot, data)

        elif 'Komentarstatusa' in data['callback_query']['data']:
            komentarstatusa(message_id, telegram_id, bot, data)

        elif 'arhivzakaz' in data['callback_query']['data']:
            arhivzakaz(message_id, telegram_id, bot, data)

        elif 'PDFarhiv' in data['callback_query']['data']:
            pdfarhiv(message_id, telegram_id, bot, data)

        elif 'detal_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            id_detal = parsed_data[1]
            detal(message_id, telegram_id, bot, id_detal)

        elif 'favorites_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            id_favorites = parsed_data[1]
            favorites(message_id, telegram_id, bot, id_favorites, data)

        elif 'bye_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            id_bye = parsed_data[1]
            bye(message_id, telegram_id, bot, id_bye, data)

        elif 'kupyty_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            id_kupyty = parsed_data[1]
            kupyty(message_id, telegram_id, bot, id_kupyty, data)

        elif 'delete_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            id_delete = parsed_data[1]
            delete(message_id, telegram_id, bot, id_delete, data)

        elif 'vydalyty_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            id_vydalyty = parsed_data[1]
            vydalyty(message_id, telegram_id, bot, id_vydalyty, data)

        elif 'add_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            id_add = parsed_data[1]
            add(message_id, telegram_id, bot, id_add, data)

        elif 'subtract_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            id_subtract = parsed_data[1]
            subtract(message_id, telegram_id, bot, id_subtract, data)

        elif 'user_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            id_user = parsed_data[1]
            user(message_id, telegram_id, bot, id_user, data)

        elif 'kor_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            kor = parsed_data[1]
            korwrite(message_id, telegram_id, bot, kor, data)

        elif 'storypage_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            historypage = parsed_data[1]
            history_page(message_id, telegram_id, bot, historypage, data)

        elif 'edit_order_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            order_id = parsed_data[2]
            edit_order(message_id, telegram_id, bot, order_id, data)

        elif 'change_status_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            order_id = parsed_data[2]
            change_status(message_id, telegram_id, bot, order_id, data)

        elif 'status_' in data['callback_query']['data']:
            if prof.step == 'change_status':
                parsed_data = data['callback_query']['data'].split('_')
                status_id = parsed_data[1]
                parsed_data = data['callback_query']['data'].split('_')
                order_id = parsed_data[2]
                status(message_id, telegram_id, bot,status_id, order_id, data)

        elif 'close_order_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            order_id = parsed_data[2]
            close_order(message_id, telegram_id, bot, order_id, data)

        elif 'info_order_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            order_id = parsed_data[2]
            info_order(message_id, telegram_id, bot, order_id, data)

        elif 'info_arhiv_' in data['callback_query']['data']:
            parsed_data = data['callback_query']['data'].split('_')
            order_id = parsed_data[2]
            info_arhiv(message_id, telegram_id, bot, order_id, data)

        elif 'id_' in data['callback_query']['data']:
            if prof.step == 'kategoria':
                parsed_data = data['callback_query']['data'].split('_')
                id_com = parsed_data[1]
                kategoria(message_id, telegram_id, bot, id_com)

            elif prof.step == 'podkategoria':
                parsed_data = data['callback_query']['data'].split('_')
                id_com = parsed_data[1]
                podkategoria(message_id, telegram_id, bot, id_com)

    else:
        pass

    return HttpResponse('Webhook received.')


