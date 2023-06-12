from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User


class TelegramUser(models.Model):
    language_code = models.CharField(max_length=50, blank=True, default='en')
    telegram_id = models.IntegerField(unique=True)
    secret_key = models.CharField(max_length=50, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    is_authenticated = models.BooleanField(default=False)
    is_chat = models.BooleanField(default=False)
    step = models.CharField(max_length=50, blank=True)
    variable = models.CharField(max_length=50, blank=True)
    variable_1 = models.CharField(max_length=50, blank=True)
    variable_2 = models.CharField(max_length=50, blank=True)
    variable_3 = models.CharField(max_length=50, blank=True)
    variable_4 = models.CharField(max_length=50, blank=True)
    href = models.CharField(max_length=255, blank=True)
    prev_page = models.CharField(max_length=255, blank=True)
    next_page = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.telegram_id})'


class HrefTable(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    href = models.TextField(blank=True)
    category = models.TextField(blank=True)

    def __str__(self):
        return self.href


class Toys(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    href = models.TextField(blank=True)
    category = models.TextField(blank=True)

    def __str__(self):
        return self.href


class Obrane(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    name_toys = models.CharField(max_length=255, blank=True)
    price_toys = models.CharField(max_length=255, blank=True)
    artikul_toys = models.CharField(max_length=255, blank=True)
    photo_toys = models.ImageField(upload_to='media/obrane/', blank=True)

    def __str__(self):
        return self.name_toys


class Korzina(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    name_toys = models.CharField(max_length=255, blank=True)
    price_toys = models.CharField(max_length=255, blank=True)
    artikul_toys = models.CharField(max_length=255, blank=True)
    photo_toys = models.ImageField(upload_to='media/korzina/', blank=True)
    amount_toys = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name_toys


class History(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    name_toys = models.CharField(max_length=255, blank=True)
    price_toys = models.CharField(max_length=255, blank=True)
    artikul_toys = models.CharField(max_length=255, blank=True)
    photo_toys = models.ImageField(upload_to='media/history/', blank=True)
    amount_toys = models.CharField(max_length=255, blank=True)
    info = models.CharField(max_length=255, blank=True)
    status = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_toys


class Work(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    info_user = models.TextField(blank=True)
    order_info = models.TextField(blank=True)
    total_price = models.CharField(max_length=255, blank=True)
    info = models.TextField(blank=True)
    info_zakaz = models.TextField(blank=True)

    status_1 = models.BooleanField(default=False)#Контакт з клієнтом
    info_status_1 = models.CharField(max_length=255, blank=True)
    datetime_status_1 = models.DateTimeField(null=True, blank=True)

    status_2 = models.BooleanField(default=False)#Підтвердження замовлення
    info_status_2 = models.CharField(max_length=255, blank=True)
    datetime_status_2 = models.DateTimeField(null=True, blank=True)

    status_3 = models.BooleanField(default=False)#Оплата
    info_status_3 = models.CharField(max_length=255, blank=True)
    datetime_status_3 = models.DateTimeField(null=True, blank=True)

    status_4 = models.BooleanField(default=False)#Доставка
    info_status_4 = models.CharField(max_length=255, blank=True)
    datetime_status_4 = models.DateTimeField(null=True, blank=True)

    status_5 = models.BooleanField(default=False)#Закриття замовлення
    info_status_5 = models.CharField(max_length=255, blank=True)
    datetime_status_5 = models.DateTimeField(null=True, blank=True)

    status_6 = models.BooleanField(default=False)#Повернення/Відмова
    info_status_6 = models.CharField(max_length=255, blank=True)
    datetime_status_6 = models.DateTimeField(null=True, blank=True)

    datetime = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Оновлюємо дату для кожного статусу, якщо відбулася зміна на True
        if self.status_1 and not self.datetime_status_1:
            self.datetime_status_1 = timezone.now()
        if self.status_2 and not self.datetime_status_2:
            self.datetime_status_2 = timezone.now()
        if self.status_3 and not self.datetime_status_3:
            self.datetime_status_3 = timezone.now()
        if self.status_4 and not self.datetime_status_4:
            self.datetime_status_4 = timezone.now()
        if self.status_5 and not self.datetime_status_5:
            self.datetime_status_5 = timezone.now()
        if self.status_6 and not self.datetime_status_6:
            self.datetime_status_6 = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.telegram_user)


class Arhivzamovlen(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    info_user = models.TextField(blank=True)
    order_info = models.TextField(blank=True)
    total_price = models.CharField(max_length=255, blank=True)
    info = models.TextField(blank=True)
    info_zakaz = models.TextField(blank=True)

    status_1 = models.BooleanField(default=False)#Контакт з клієнтом
    info_status_1 = models.CharField(max_length=255, blank=True)
    datetime_status_1 = models.DateTimeField(null=True, blank=True)

    status_2 = models.BooleanField(default=False)#Підтвердження замовлення
    info_status_2 = models.CharField(max_length=255, blank=True)
    datetime_status_2 = models.DateTimeField(null=True, blank=True)

    status_3 = models.BooleanField(default=False)#Оплата
    info_status_3 = models.CharField(max_length=255, blank=True)
    datetime_status_3 = models.DateTimeField(null=True, blank=True)

    status_4 = models.BooleanField(default=False)#Доставка
    info_status_4 = models.CharField(max_length=255, blank=True)
    datetime_status_4 = models.DateTimeField(null=True, blank=True)

    status_5 = models.BooleanField(default=False)#Закриття замовлення
    info_status_5 = models.CharField(max_length=255, blank=True)
    datetime_status_5 = models.DateTimeField(null=True, blank=True)

    status_6 = models.BooleanField(default=False)#Повернення/Відмова
    info_status_6 = models.CharField(max_length=255, blank=True)
    datetime_status_6 = models.DateTimeField(null=True, blank=True)

    datetime = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.telegram_user)





