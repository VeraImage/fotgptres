from __future__ import annotations

import asyncio
import httpx
import config
from functools import wraps

from asyncio.proactor_events import _ProactorBasePipeTransport

"""Это фиск RuntimeError. (Не выводит громоздкий варнинг на всю консоль.)"""


def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise

    return wrapper


_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)


class Payment:
    """Класс сгенерированной оплаты.
    """

    def __init__(self, payment_id: str, default_params: dict, amount: int = None) -> None:
        self.amount = amount
        self.id = payment_id
        self.authdata_to_request = {
            'auth_login': default_params["auth_login"],
            'auth_secret': default_params["auth_secret"],
            'id': self.id

        }
        self.url = f"https://pay.crystalpay.io/?i={self.id}"
        self.api_url = "https://api.crystalpay.io/v2/invoice/info/"
        self.paymethod = None

    async def is_paid(self) -> bool:

        async with httpx.AsyncClient() as client:
            result = await client.post(self.api_url, json=self.authdata_to_request)

        result = result.json()

        if result['error']:
            raise CheckPaymentErr(f"Ошибка проверки платежа: {result['errors']}")

        if result['state'] == "payed":
            self.paymethod = result['method']
            return True
        return False

    async def get_amount(self) -> None:
        async with httpx.AsyncClient() as client:
            result = await client.post(self.api_url, json=self.authdata_to_request)
        result = result.json()
        if result['error']:
            raise CheckPaymentErr(f"Ошибка проверки платежа: {result['errors']}")
        self.amount = result['amount']


class AIOCrystalPay:

    def __init__(self, cash_name: str, secret_1: str) -> None:
        """cash_name - имя кассы/логин
        secret_1 - секретный ключ 1
        """
        self.cash_name = cash_name
        self.secret_1 = secret_1
        self.api_url = "https://api.crystalpay.io/v2/invoice/create/"
        self.def_params = dict(auth_login=self.cash_name, auth_secret=self.secret_1, type='purchase', lifetime=30)

    async def create_invoice(self,
                             amount: int,
                             payment_type: str = None,
                             currency: str = None,
                             lifetime: int = None,
                             redirect_url: str = None,
                             callback: str = None,
                             extra: str = None,
                             payment_system: str = None,
                             ) -> Payment:
        """Метод генерации ссылки для оплаты
        amount - сумма на оплату(целочисл.)
        currency -     Валюта суммы (конвертируется в рубли) (USD, BTC, ETH, LTC…) (необязательно)
        liftetime - Время жизни счёта для оплаты, в минутах (необязательно)
        redirect - Ссылка для перенаправления после оплаты (необязательно)
        callback - Ссылка на скрипт, на который будет отправлен запрос, после успешного зачисления средств на счёт кассы (необязательно)
        extra - Любые текстовые данные, пометка/комментарий. Будет передано в callback или при проверке статуса платежа (необязательно)
        payment_system - Если нужно принудительно указать платежную систему (необязательно).
        """

        params = self.def_params

        params['amount'] = amount

        if currency:
            params['amount_currency'] = currency
        if payment_type:
            params['type'] = payment_type
        if lifetime:
            params['lifetime'] = lifetime
        if redirect_url:
            params['redirect_url'] = redirect_url
        if callback:
            params['callback'] = callback
        if extra:
            params['extra'] = extra
        if payment_system:
            params['m'] = payment_system

        async with httpx.AsyncClient() as client:
            result = await client.post(self.api_url, json=params)

        result = result.json()

        if result['error']:
            raise CreatePaymentError(f"Ошибка создания платежа: {result['errors']}")

        try:
            return Payment(result['id'], self.def_params, amount)
        except Exception as e:
            raise CreatePaymentError(f"Ошибка создания платежа: {e}")

    async def construct_payment_by_id(self, paymnet_id) -> Payment:
        payment = Payment(paymnet_id, self.def_params)
        await payment.get_amount()
        return payment


class AuthError(Exception):
    pass


class CreatePaymentError(Exception):
    pass


class CheckPaymentErr(Exception):
    pass


