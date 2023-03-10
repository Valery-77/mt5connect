import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from math import fabs
import MetaTrader5 as Mt
import requests
from django.core.serializers.json import DjangoJSONEncoder

# from win32gui import PostMessage, GetAncestor, FindWindow

send_retcodes = {
    -700: ('CUSTOM_RETCODE_LIMITS_NOT_CHANGED', 'Уровни не изменены'),
    -600: ('CUSTOM_RETCODE_POSITION_NOT_MODIFIED', 'Объем сделки не изменен'),
    -500: ('CUSTOM_RETCODE_POSITION_NOT_MODIFIED', 'Объем сделки не изменен'),
    -400: ('CUSTOM_RETCODE_POSITION_NOT_MODIFIED', 'Объем сделки не изменен'),
    -300: ('CUSTOM_RETCODE_EQUAL_VOLUME', 'Новый объем сделки равен существующему'),
    -200: ('CUSTOM_RETCODE_WRONG_SYMBOL', 'Нет такого торгового символа'),
    -100: ('CUSTOM_RETCODE_NOT_ENOUGH_MARGIN', 'Нехватка маржи. Выбран режим - Не открывать сделку или Не выбрано'),
    10004: ('TRADE_RETCODE_REQUOTE', 'Реквота'),
    10006: ('TRADE_RETCODE_REJECT', 'Запрос отклонен'),
    10007: ('TRADE_RETCODE_CANCEL', 'Запрос отменен трейдером'),
    10008: ('TRADE_RETCODE_PLACED', 'Ордер размещен'),
    10009: ('TRADE_RETCODE_DONE', 'Заявка выполнена'),
    10010: ('TRADE_RETCODE_DONE_PARTIAL', 'Заявка выполнена частично'),
    10011: ('TRADE_RETCODE_ERROR', 'Ошибка обработки запроса'),
    10012: ('TRADE_RETCODE_TIMEOUT', 'Запрос отменен по истечению времени'),
    10013: ('TRADE_RETCODE_INVALID', 'Неправильный запрос'),
    10014: ('TRADE_RETCODE_INVALID_VOLUME', 'Неправильный объем в запросе'),
    10015: ('TRADE_RETCODE_INVALID_PRICE', 'Неправильная цена в запросе'),
    10016: ('TRADE_RETCODE_INVALID_STOPS', 'Неправильные стопы в запросе'),
    10017: ('TRADE_RETCODE_TRADE_DISABLED', 'Торговля запрещена'),
    10018: ('TRADE_RETCODE_MARKET_CLOSED', 'Рынок закрыт'),
    10019: ('TRADE_RETCODE_NO_MONEY', 'Нет достаточных денежных средств для выполнения запроса'),
    10020: ('TRADE_RETCODE_PRICE_CHANGED', 'Цены изменились'),
    10021: ('TRADE_RETCODE_PRICE_OFF', 'Отсутствуют котировки для обработки запроса'),
    10022: ('TRADE_RETCODE_INVALID_EXPIRATION', 'Неверная дата истечения ордера в запросе'),
    10023: ('TRADE_RETCODE_ORDER_CHANGED', 'Состояние ордера изменилось'),
    10024: ('TRADE_RETCODE_TOO_MANY_REQUESTS', 'Слишком частые запросы'),
    10025: ('TRADE_RETCODE_NO_CHANGES', 'В запросе нет изменений'),
    10026: ('TRADE_RETCODE_SERVER_DISABLES_AT', 'Автотрейдинг запрещен сервером'),
    10027: ('TRADE_RETCODE_CLIENT_DISABLES_AT', 'Автотрейдинг запрещен клиентским терминалом'),
    10028: ('TRADE_RETCODE_LOCKED', 'Запрос заблокирован для обработки'),
    10029: ('TRADE_RETCODE_FROZEN', 'Ордер или позиция заморожены'),
    10030: ('TRADE_RETCODE_INVALID_FILL', 'Указан неподдерживаемый тип исполнения ордера по остатку'),
    10031: ('TRADE_RETCODE_CONNECTION', 'Нет соединения с торговым сервером'),
    10032: ('TRADE_RETCODE_ONLY_REAL', 'Операция разрешена только для реальных счетов'),
    10033: ('TRADE_RETCODE_LIMIT_ORDERS', 'Достигнут лимит на количество отложенных ордеров'),
    10034: (
        'TRADE_RETCODE_LIMIT_VOLUME', 'Достигнут лимит на объем ордеров и позиций для данного символа'),
    10035: ('TRADE_RETCODE_INVALID_ORDER', 'Неверный или запрещённый тип ордера'),
    10036: ('TRADE_RETCODE_POSITION_CLOSED', 'Позиция с указанным POSITION_IDENTIFIER уже закрыта'),
    10038: ('TRADE_RETCODE_INVALID_CLOSE_VOLUME', 'Закрываемый объем превышает текущий объем позиции'),
    10039: ('TRADE_RETCODE_CLOSE_ORDER_EXIST', 'Для указанной позиции уже есть ордер на закрытие'),
    10040: ('TRADE_RETCODE_LIMIT_POSITIONS',
            'Количество открытых позиций, которое можно одновременно иметь на счете, '
            'может быть ограничено настройками сервера'),
    10041: (
        'TRADE_RETCODE_REJECT_CANCEL',
        'Запрос на активацию отложенного ордера отклонен, а сам ордер отменен'),
    10042: (
        'TRADE_RETCODE_LONG_ONLY',
        'Запрос отклонен, так как на символе установлено правило "Разрешены только '
        'длинные позиции"  (POSITION_TYPE_BUY)'),
    10043: ('TRADE_RETCODE_SHORT_ONLY',
            'Запрос отклонен, так как на символе установлено правило "Разрешены только '
            'короткие позиции" (POSITION_TYPE_SELL)'),
    10044: ('TRADE_RETCODE_CLOSE_ONLY',
            'Запрос отклонен, так как на символе установлено правило "Разрешено только '
            'закрывать существующие позиции"'),
    10045: ('TRADE_RETCODE_FIFO_CLOSE',
            'Запрос отклонен, так как для торгового счета установлено правило "Разрешено '
            'закрывать существующие позиции только по правилу FIFO" ('
            'ACCOUNT_FIFO_CLOSE=true)'),
    10046: (
        'TRADE_RETCODE_HEDGE_PROHIBITED',
        'Запрос отклонен, так как для торгового счета установлено правило '
        '"Запрещено открывать встречные позиции по одному символу"')}
last_errors = {
    1: ('RES_S_OK', 'generic success'),
    -1: ('RES_E_FAIL', 'generic fail'),
    -2: ('RES_E_INVALID_PARAMS', 'invalid arguments/parameters'),
    -3: ('RES_E_NO_MEMORY', 'no memory condition'),
    -4: ('RES_E_NOT_FOUND', 'no history'),
    -5: ('RES_E_INVALID_VERSION', 'invalid version'),
    -6: ('RES_E_AUTH_FAILED', 'authorization failed'),
    -7: ('RES_E_UNSUPPORTED', 'unsupported method'),
    -8: ('RES_E_AUTO_TRADING_DISABLED', 'auto-trading disabled'),
    -10000: ('RES_E_INTERNAL_FAIL', 'internal IPC general error'),
    -10001: ('RES_E_INTERNAL_FAIL_SEND', 'internal IPC send failed'),
    -10002: ('RES_E_INTERNAL_FAIL_RECEIVE', 'internal IPC recv failed'),
    -10003: ('RES_E_INTERNAL_FAIL_INIT', 'internal IPC initialization fail'),
    -10003: ('RES_E_INTERNAL_FAIL_CONNECT', 'internal IPC no ipc'),
    -10005: ('RES_E_INTERNAL_FAIL_TIMEOUT', 'internal timeout')}
reasons_code = {
    '01': 'Открыто СКС',
    '02': 'Блеклист',
    '03': 'Закрыто по команде пользователя',
    '04': 'Ключ APi истек',
    '05': 'Нет связи с биржей',
    '06': 'Закрыто инвестором',
    '07': 'Закрыто по условию стоп-лосс',
    '08': 'Объем изменен',
    '09': 'Лимиты изменены',
}


class DealComment:
    # comment = {
    #     'lieder_ticket': -1,
    #     'reason': '',  # Закрыто лидером, Закрыто по условию стоп-лосс
    # }

    lieder_ticket: int
    reason: str
    SEPARATOR = '-'

    def __init__(self):
        self.lieder_ticket = -1
        self.reason = ''

    @staticmethod
    def is_valid_string(string: str):
        if len(string) > 0:
            sliced = string.split(DealComment.SEPARATOR)
            if len(sliced) == 2:
                if sliced[1] not in reasons_code:
                    return False
                try:
                    ticket = int(sliced[0])
                    if ticket < 0:
                        return False
                except ValueError:
                    return False
            else:
                return False
        return True

    def string(self):
        return f'{self.lieder_ticket}' + DealComment.SEPARATOR + f'{self.reason}'

    def obj(self):
        return {'lieder_ticket': self.lieder_ticket, 'reason': self.reason}

    def set_from_string(self, string: str):
        if DealComment.SEPARATOR in string:
            split_str = string.split(DealComment.SEPARATOR)
            lid_str = split_str[0]
            cause = split_str[1]
        elif len(string) > 0:
            lid_str = string
            cause = ''
        else:
            lid_str = '-1'
            cause = ''
        try:
            self.lieder_ticket = int(lid_str)
            self.reason = cause
        except ValueError:
            self.lieder_ticket = -1
            self.reason = ''
        return self

    def set_from_ticket(self, ticket: int):
        self.lieder_ticket = ticket
        self.reason = ''


class LinkedPositions:
    lieder_ticket: int
    positions: list
    volume: float
    symbol: str
    type: int

    def __init__(self, lieder_ticket, investor_positions=None):
        self.lieder_ticket = lieder_ticket
        self.positions = []
        self.symbol = ''
        self.type = -1
        if not investor_positions:
            investor_positions = get_investor_positions()
        for pos in investor_positions:
            comment = DealComment().set_from_string(pos.comment)
            if comment.lieder_ticket == self.lieder_ticket:
                self.positions.append(pos)
                if self.symbol == '':
                    self.symbol = pos.symbol
                if self.type < 0:
                    self.type = pos.type
        volume = 0.0
        for _ in self.positions:
            volume += _.volume
        min_lot = Mt.symbol_info(self.symbol).volume_min
        decimals = str(min_lot)[::-1].find('.')
        self.volume = round(volume, decimals)

    @staticmethod
    def get_positions_lieder_ticket(position):
        """Получение тикета позиции лидера из позиции инвестора"""
        if DealComment.is_valid_string(position.comment):
            comment = DealComment().set_from_string(position.comment)
            return comment.lieder_ticket
        return -1

    @staticmethod
    def get_linked_positions_table():
        """Получение таблицы позиций инвестора, сгруппированных по тикету позиции лидера"""
        stored_ticket = []
        positions_table = []
        investor_positions = get_investor_positions()
        for pos in investor_positions:
            lid_ticket = LinkedPositions.get_positions_lieder_ticket(pos)
            if lid_ticket not in stored_ticket:
                stored_ticket.append(lid_ticket)
                linked_positions = LinkedPositions(lieder_ticket=lid_ticket, investor_positions=investor_positions)
                positions_table.append(linked_positions)
        return positions_table

    def string(self):
        result = "\t"
        result += self.symbol + ' ' + str(self.lieder_ticket) + ' ' + str(self.volume) + " " + str(len(self.positions))
        for _ in self.positions:
            result += '\n\t\t' + str(_)
        return result

    def modify_volume(self, new_volume):
        """Изменение объема связанных позиций"""
        print('  Текущий объем:', self.volume, ' Новый:', new_volume)
        min_lot = Mt.symbol_info(self.symbol).volume_min
        decimals = str(min_lot)[::-1].find('.')
        new_comment = DealComment()
        new_comment.lieder_ticket = self.lieder_ticket
        new_comment.reason = '08'
        new_comment_str = new_comment.string()
        if new_volume > self.volume:  # Увеличение объема
            vol = round(new_volume - self.volume, decimals)
            print('\t Увеличение объема на', vol)
            request = {
                "action": Mt.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": vol,
                "type": self.type,
                "price": Mt.symbol_info_tick(
                    self.symbol).bid if self.type == Mt.POSITION_TYPE_SELL else Mt.symbol_info_tick(self.symbol).ask,
                "deviation": DEVIATION,
                "magic": MAGIC,
                "comment": new_comment_str,
                "type_time": Mt.ORDER_TIME_GTC,
                "type_filling": Mt.ORDER_FILLING_FOK,
            }
            result = Mt.order_send(request)
            return result
        elif new_volume < self.volume:  # Уменьшение объема
            target_volume = round(self.volume - new_volume, decimals)
            for pos in reversed(self.positions):
                if pos.volume <= target_volume:  # Если объем позиции меньше либо равен целевому, то закрыть позицию
                    print('\t Уменьшение объема. Закрытие позиции', pos.ticket, ' объем:', pos.volume)
                    request = {
                        'action': Mt.TRADE_ACTION_DEAL,
                        'position': pos.ticket,
                        'symbol': pos.symbol,
                        'volume': pos.volume,
                        "type": Mt.ORDER_TYPE_SELL if pos.type == Mt.POSITION_TYPE_BUY else Mt.ORDER_TYPE_BUY,
                        'price': Mt.symbol_info_tick(
                            self.symbol).bid if self.type == Mt.POSITION_TYPE_SELL else Mt.symbol_info_tick(
                            self.symbol).ask,
                        'deviation': DEVIATION,
                        'magic:': MAGIC,
                        'comment': new_comment_str,
                        'type_tim': Mt.ORDER_TIME_GTC,
                        'type_filing': Mt.ORDER_FILLING_IOC
                    }
                    result = Mt.order_send(request)
                    print('\t', send_retcodes[result.retcode], ':', result.retcode)
                    target_volume = round(target_volume - pos.volume,
                                          decimals)  # Уменьшить целевой объем на объем закрытой позиции
                elif pos.volume > target_volume:  # Если объем позиции больше целевого, то закрыть часть позиции
                    print('\t Уменьшение объема. Частичное закрытие позиции', pos.ticket, 'объем:', pos.volume,
                          'на', target_volume)
                    request = {
                        "action": Mt.TRADE_ACTION_DEAL,
                        "symbol": pos.symbol,
                        "volume": target_volume,
                        "type": Mt.ORDER_TYPE_SELL if pos.type == Mt.POSITION_TYPE_BUY else Mt.ORDER_TYPE_BUY,
                        "position": pos.ticket,
                        'price': Mt.symbol_info_tick(
                            self.symbol).bid if self.type == Mt.POSITION_TYPE_SELL else Mt.symbol_info_tick(
                            self.symbol).ask,
                        "deviation": DEVIATION,
                        "magic": MAGIC,
                        "comment": new_comment_str,
                        'type_tim': Mt.ORDER_TIME_GTC,
                        "type_filling": Mt.ORDER_FILLING_FOK,
                    }
                    if target_volume > 0:
                        result = Mt.order_send(request)
                        print('\t', send_retcodes[result.retcode], ':', result.retcode)
                    else:
                        print('\t Частичное закрытие объема = 0.0')
                    break


TIMEOUT_INIT = 60_000  # время ожидания при инициализации терминала (рекомендуемое 60_000 millisecond)
MAGIC = 9876543210  # идентификатор эксперта
DEVIATION = 20  # допустимое отклонение цены в пунктах при совершении сделки
lieder_balance = 0  # default var
lieder_equity = 0  # default var
lieder_positions = []  # default var
lieder_existed_position_tickets = []  # default var
UTC_OFFSET = datetime.now() - datetime.utcnow()
SERVER_DELTA_TIME = timedelta(hours=4)
investors_disconnect_store = [[], []]
old_investors_balance = {}
start_date_utc = datetime.now().replace(microsecond=0)
trading_event = asyncio.Event()  # init async event

EURUSD = USDRUB = EURRUB = -1
send_messages = True  # отправлять сообщения в базу
sleep_lieder_update = 3  # пауза для обновления лидера

host = 'https://my.atimex.io:8000/api/demo_mt5/'

source = {
    # 'lieder': {},
    # 'investors': [{}, {}],
    # 'settings': {}
}


# def enable_algotrading():
#     """Принудительное включение режима Аготрейдинга на терминале"""
#     try:
#         if not Mt.terminal_info().trade_allowed:
#             mt_wmcmd_experts = 32851
#             wm_command = 0x0111
#             ga_root = 2
#             terminal_handle = FindWindow('MetaQuotes::MetaTrader::5.00', None)
#             PostMessage(GetAncestor(terminal_handle, ga_root), wm_command, mt_wmcmd_experts, 0)
#     except AttributeError:
#         print(f'Невозможно подключиться к терминалу : {datetime.now()}')
#         exit()

async def check_notification(investor):
    if investor['notification'] == 'Да':
        await set_comment('Вы должны оплатить вознаграждение')
        return True
    return False


def set_dummy_data():
    global send_messages, start_date_utc
    send_messages = False
    investment_size = 1000
    source['lieder'] = {
        'terminal_path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
        'login': 66587203,
        'password': '3hksvtko',
        'server': 'MetaQuotes-Demo'
    }
    source['investors'] = [
        {
            'terminal_path': r'C:\Program Files\MetaTrader 5_2\terminal64.exe',
            'login': 65766034,
            'password': 'h0nmgczo',
            'server': 'MetaQuotes-Demo',
            'investment_size': investment_size,
            'dcs_access': True,

            'deal_in_plus': 0.1,
            'deal_in_minus': -0.1,
            'waiting_time': 1,
            'ask_an_investor': 'Все',
            'price_refund': 'Да',
            # -----------------------------------------
            'multiplier': 'Баланс',
            'multiplier_value': 100.0,
            'changing_multiplier': 'Да',
            # -----------------------------------------
            'stop_loss': 'Процент',
            'stop_value': 20.0,
            'open_trades': 'Закрыть',
            # -----------------------------------------
            'shutdown_initiator': 'Инвестор',
            'disconnect': 'Нет',
            'open_trades_disconnect': 'Закрыть',
            'notification': 'Нет',
            'blacklist': 'Нет',
            'accompany_transactions': 'Нет',
            # -----------------------------------------=
            'no_exchange_connection': 'Нет',
            'api_key_expired': 'Нет',
            # -----------------------------------------
            'closed_deals_myself': 'Переоткрывать',
            'reconnected': 'Переоткрывать',
            # -----------------------------------------
            'recovery_model': 'Не корректировать',
            'buy_hold_model': 'Не корректировать',
            # -----------------------------------------
            'not_enough_margin': 'Минимальный объем',
            'accounts_in_diff_curr': 'Доллары',
            # -----------------------------------------
            'synchronize_deals': 'Нет',
            'deals_not_opened': 'Нет',
            'closed_deal_investor': 'Нет',
            # -----------------------------------------
        }
    ]
    source['investors'].append(source['investors'][0].copy())
    source['investors'][1]['terminal_path'] = r'C:\Program Files\MetaTrader 5_3\terminal64.exe'
    source['investors'][1]['login'] = 5009600048
    source['investors'][1]['password'] = 'sbbsapv5'
    source['settings'] = {
        "relevance": True,
        "update_at": str(start_date_utc),
        "create_at": str(start_date_utc)
        # "access": response['access'],
    }


def store_change_disconnect_state():
    if len(source) > 0:
        for investor in source['investors']:
            index = source['investors'].index(investor)
            # print('---------------------', index, investor['disconnect'])
            if len(investors_disconnect_store[index]) == 0 or \
                    investor['disconnect'] != investors_disconnect_store[index][-1]:
                investors_disconnect_store[index].append(investor['disconnect'])


def get_disconnect_change(investor):
    result = None
    idx = -1
    for _ in source['investors']:
        if _['login'] == investor['login']:
            idx = source['investors'].index(_)
    if idx > -1:
        if investors_disconnect_store[idx][-1] == 'Да':
            result = 'Disabled'
        elif investors_disconnect_store[idx][-1] == 'Нет':
            result = 'Enabled'
    if len(investors_disconnect_store[idx]) <= 1:
        result = 'Unchanged'
    # print(investors_disconnect_store)
    return result


async def disable_dcs(investor):
    if not send_messages:
        return
    async with aiohttp.ClientSession() as session:
        investor_id = -1
        for _ in source['investors']:
            if _['login'] == investor['login']:
                investor_id = source['investors'].index(_)
                break
        if investor_id < 0:
            return
        id_shift = '_' + str(investor_id + 1)
        url = host + 'last'
        response = requests.get(url).json()[0]
        numb = response['id']
        url = host + f'patch/{numb}/'
        name = "access" + id_shift
        async with session.patch(url=url, data={name: False}) as resp:
            await resp.json()


async def enable_dcs(investor):
    if not send_messages:
        return
    async with aiohttp.ClientSession() as session:
        investor_id = -1
        for _ in source['investors']:
            if _['login'] == investor['login']:
                investor_id = source['investors'].index(_)
                break
        if investor_id < 0:
            return
        id_shift = '_' + str(investor_id + 1)
        url = host + 'last'
        response = requests.get(url).json()[0]
        numb = response['id']
        url = host + f'patch/{numb}/'
        name = "access" + id_shift
        async with session.patch(url=url, data={name: True}) as resp:
            await resp.json()


async def access_starter(investor):
    # print(get_disconnect_change(investor))
    if not investor['dcs_access'] and get_disconnect_change(investor) == 'Enabled':
        await enable_dcs(investor)


async def set_comment(comment):
    if not send_messages:
        return
    if not comment or comment == 'None':
        return
    async with aiohttp.ClientSession() as session:
        url = host + 'last'
        rsp = requests.get(url)
        if not rsp:
            return
        response = rsp.json()[0]
        numb = response['id']
        url = host + f'patch/{numb}/'
        async with session.patch(url=url, data={"comment": comment}) as resp:
            await resp.json()


async def disable_synchronize(exe_flag=False):
    if not send_messages or not exe_flag:
        return
    async with aiohttp.ClientSession() as session:
        url = host + 'last'
        answer = requests.get(url).json()
        if not answer or len(answer) == 0:
            return
        response = answer[0]
        numb = response['id']
        url = host + f'patch/{numb}/'
        async with session.patch(url=url, data={"synchronize_deals": 'Нет'}) as resp:
            await resp.json()


async def execute_conditions(investor):
    # if investor['blacklist'] == 'Да':  # если в блек листе
    #     force_close_all_positions(investor, reason='02')
    #     await disable_dcs(investor)
    if investor['disconnect'] == 'Да':
        await set_comment('Инициатор отключения: ' + investor['shutdown_initiator'])

        if get_investors_positions_count(investor=investor, only_own=True) == 0:  # если нет открытых сделок
            await disable_dcs(investor)

        if investor['open_trades_disconnect'] == 'Закрыть':  # если сделки закрыть
            force_close_all_positions(investor, reason='03')
            await disable_dcs(investor)

        elif investor['accompany_transactions'] == 'Нет':  # если сделки оставить и не сопровождать
            await disable_dcs(investor)


def init_mt(init_data):
    """Инициализация терминала"""
    res = Mt.initialize(login=init_data['login'], server=init_data['server'], password=init_data['password'],
                        path=init_data['terminal_path'], timeout=TIMEOUT_INIT, port=8223)
    return res


def get_pos_pips_tp(position, price=None):
    """Расчет Тейк-профит в пунктах"""
    if price is None:
        price = position.price_open
    result = 0.0
    if position.tp > 0:
        result = round(fabs(price - position.tp) / Mt.symbol_info(position.symbol).point)
    return result


def get_pos_pips_sl(position, price=None):
    """Расчет Стоп-лосс в пунктах"""
    if price is None:
        price = position.price_open
    result = 0.0
    if position.sl > 0:
        result = round(fabs(price - position.sl) / Mt.symbol_info(position.symbol).point)
    return result


def get_investor_positions(only_own=True):
    """Количество открытых позиций"""
    result = []
    if len(source) > 0:
        positions = Mt.positions_get()
        if not positions:
            positions = []
        if only_own and len(positions) > 0:
            for _ in positions:
                if positions[positions.index(_)].magic == MAGIC and DealComment.is_valid_string(_.comment):
                    result.append(_)
        else:
            result = positions
    return result


def get_investors_positions_count(investor, only_own=True):
    """Количество открытых позиций"""
    return len(get_investor_positions(investor)) if only_own else len(get_investor_positions(False))


def is_lieder_position_in_investor(lieder_position):
    invest_positions = get_investor_positions(only_own=False)
    if len(invest_positions) > 0:
        for pos in invest_positions:
            if DealComment.is_valid_string(pos.comment):
                comment = DealComment().set_from_string(pos.comment)
                if lieder_position.ticket == comment.lieder_ticket:
                    return True
    return False


def is_lieder_position_in_investor_history(lieder_position):
    date_from = start_date_utc + SERVER_DELTA_TIME
    date_to = datetime.today().replace(microsecond=0) + timedelta(days=1)
    deals = Mt.history_deals_get(date_from, date_to)
    if not deals:
        deals = []
    result = None
    result_sl = None
    if len(deals) > 0:
        for pos in deals:
            if DealComment.is_valid_string(pos.comment):
                comment = DealComment().set_from_string(pos.comment)
                if lieder_position.ticket == comment.lieder_ticket:
                    result = pos
                    if comment.reason == '07':
                        result_sl = pos
            if result and result_sl:
                break
    return result, result_sl


def is_position_opened(lieder_position, investor):
    """Проверка позиции лидера на наличие в списке позиций и истории инвестора"""
    init_mt(init_data=investor)
    if is_lieder_position_in_investor(lieder_position=lieder_position):
        return True

    exist_position, closed_by_sl = is_lieder_position_in_investor_history(lieder_position=lieder_position)
    if exist_position:
        if not closed_by_sl:
            if investor['closed_deals_myself'] == 'Переоткрывать':
                return False
            # if investor['reconnected'] == 'Переоткрывать' and get_disconnect_change(investor) == 'Enabled':
            #     return False
        return True
    return False


def get_positions_profit():
    """Расчет прибыли текущих позиций"""
    positions = get_investor_positions(only_own=True)
    result = 0
    if len(positions) > 0:
        for pos in positions:
            if pos.type < 2:
                result += pos.profit  # + pos.commission
    return result


def get_history_profit():
    """Расчет прибыли по истории"""
    date_from = start_date_utc + SERVER_DELTA_TIME
    date_to = datetime.now().replace(microsecond=0) + timedelta(days=1)
    deals = Mt.history_deals_get(date_from, date_to)

    # inf = Mt.symbol_info_tick('EURUSD')
    # print('>>>>', start_date_utc, ':', date_from, ' :: ', datetime.fromtimestamp(inf.time))
    # prof = 0
    # for _ in deals:
    #     if _.profit == 0:
    #         continue
    #     print(datetime.utcfromtimestamp(_.time), ' ', _.ticket, ' ', _.profit)
    #     prof += _.profit
    # print('>>>>', prof)

    # exit()

    if not deals:
        deals = []
    result = 0
    own_deals = []
    try:
        pos_tickets = []
        if len(deals) > 0:
            for pos in deals:
                if DealComment.is_valid_string(pos.comment):
                    linked_pos = Mt.history_deals_get(position=pos.position_id)
                    for lp in linked_pos:
                        if lp.ticket not in pos_tickets:
                            # print(linked_pos.index(lp), datetime.utcfromtimestamp(lp.time), ' ', lp.ticket, ' ',
                            #       lp.profit)
                            pos_tickets.append(lp.ticket)
                            own_deals.append(lp)
        if len(own_deals) > 0:
            for pos in own_deals:
                # print(datetime.utcfromtimestamp(pos.time), ' ', pos.ticket, ' ', pos.profit)
                if pos.type < 2:
                    result += pos.profit  # + pos.commission
    except Exception as ex:
        print('ERROR get_history_profit():', ex)
        result = None
    return result


async def check_stop_limits(investor):
    """Проверка стоп-лимита по проценту либо абсолютному показателю"""
    start_balance = investor['investment_size']
    if start_balance <= 0:
        start_balance = 1
    limit_size = investor['stop_value']
    calc_limit_in_percent = True if investor['stop_loss'] == 'Процент' else False
    init_mt(investor)
    history_profit = get_history_profit()
    current_profit = get_positions_profit()
    # SUMM TOTAL PROFIT
    if history_profit is None or current_profit is None:
        return
    close_positions = False
    total_profit = history_profit + current_profit
    print(f' - {investor["login"]} [{investor["currency"]}] - {len(Mt.positions_get())} positions. Access:',
          investor['dcs_access'], end='')
    print('\t', 'Прибыль' if total_profit >= 0 else 'Убыток', 'торговли c', start_date_utc,
          ':', round(total_profit, 2), investor['currency'],
          '{curr.', round(current_profit, 2), ': hst. ' + str(round(history_profit, 2)) + '}')
    # CHECK LOST SIZE FOR CLOSE ALL
    if total_profit < 0:
        if calc_limit_in_percent:
            current_percent = fabs(total_profit / start_balance) * 100
            if current_percent >= limit_size:
                close_positions = True
        elif fabs(total_profit) >= limit_size:
            close_positions = True
        # CLOSE ALL POSITIONS
        active_positions = get_investor_positions()
        if close_positions and len(active_positions) > 0:
            print('     Закрытие всех позиций по условию стоп-лосс')
            await set_comment('Закрытие всех позиций по условию стоп-лосс. Убыток торговли c' + str(
                start_date_utc.replace(microsecond=0)) + ':' + str(round(total_profit, 2)))
            for act_pos in active_positions:
                if act_pos.magic == MAGIC:
                    close_position(investor, act_pos, '07')
            if investor['open_trades'] == 'Закрыть и отключить':
                await disable_dcs(investor)


def get_currency_coefficient(investor):
    global EURUSD, EURRUB, USDRUB
    lid_currency = source['lieder']['currency']
    inv_currency = investor['currency']
    eurusd = usdrub = eurrub = -1

    rub_tick = Mt.symbol_info_tick('USDRUB')
    if rub_tick:
        usdrub = rub_tick.bid
    eur_tick = Mt.symbol_info_tick('EURUSD')
    if eur_tick:
        eurusd = eur_tick.bid
    if rub_tick and eur_tick:
        eurrub = usdrub * eurusd

    # rub_rates = Mt.copy_rates_range("USDRUB", Mt.TIMEFRAME_M1, 0, 1)
    # # print('---rub--', rub_rates, end='')
    # if rub_rates:
    #     usdrub = rub_rates[0][4]
    #     # print('  usdrub:', usdrub, end='')
    # eur_rates = Mt.copy_rates_from_pos('EURUSD', Mt.TIMEFRAME_M1, 0, 1)
    # # print('---eur--', eur_rates, end='')
    # if eur_rates:
    #     eurusd = eur_rates[0][4]
    #     # print('  eurusd:', eurusd)
    # if eur_rates and rub_rates:
    #     eurrub = usdrub * eurusd
    #     # print('    eurrub:', eurrub)
    if eurusd > 0:
        EURUSD = eurusd
    if usdrub > 0:
        USDRUB = usdrub
    if eurrub > 0:
        EURRUB = eurrub
    currency_coefficient = 1
    try:
        if lid_currency == inv_currency:
            currency_coefficient = 1
        elif lid_currency == 'USD':
            if inv_currency == 'EUR':
                currency_coefficient = 1 / eurusd
            elif inv_currency == 'RUB':
                currency_coefficient = usdrub
        elif lid_currency == 'EUR':
            if inv_currency == 'USD':
                currency_coefficient = eurusd
            elif inv_currency == 'RUB':
                currency_coefficient = eurrub
        elif lid_currency == 'RUB':
            if inv_currency == 'USD':
                currency_coefficient = 1 / usdrub
            elif inv_currency == 'EUR':
                currency_coefficient = 1 / eurrub
    except Exception as e:
        print('Except in get_currency_coefficient()', e)
        currency_coefficient = 1
    # print(lid_currency + '/' + inv_currency, currency_coefficient)
    return currency_coefficient


def check_transaction(investor, lieder_position):
    """Проверка открытия позиции"""
    price_refund = True if investor['price_refund'] == 'Да' else False
    if not price_refund:  # если не возврат цены
        timeout = investor['waiting_time'] * 60
        deal_time = int(lieder_position.time_update - datetime.utcnow().timestamp())  # get_time_offset(investor))
        curr_time = int(datetime.timestamp(datetime.utcnow().replace(microsecond=0)))
        delta_time = curr_time - deal_time
        if delta_time > timeout:  # если время больше заданного
            # print('Время истекло')
            return False

    transaction_type = 0
    if investor['ask_an_investor'] == 'Плюс':
        transaction_type = 1
    elif investor['ask_an_investor'] == 'Минус':
        transaction_type = -1
    deal_profit = lieder_position.profit
    if transaction_type > 0 > deal_profit:  # если открывать только + и профит < 0
        return False
    if deal_profit > 0 > transaction_type:  # если открывать только - и профит > 0
        return False

    transaction_plus = investor['deal_in_plus']
    transaction_minus = investor['deal_in_minus']
    price_open = lieder_position.price_open
    price_current = lieder_position.price_current

    res = None
    if lieder_position.type == 0:  # Buy
        res = (price_current - price_open) / price_open * 100  # Расчет сделки покупки по формуле
    elif lieder_position.type == 1:  # Sell
        res = (price_open - price_current) / price_open * 100  # Расчет сделки продажи по формуле
    return True if res is not None and transaction_plus >= res >= transaction_minus else False  # Проверка на заданные отклонения


def multiply_deal_volume(investor, lieder_position):
    """Расчет множителя"""
    lieder_balance_value = lieder_balance if investor['multiplier'] == 'Баланс' else lieder_equity
    symbol = lieder_position.symbol
    lieder_volume = lieder_position.volume
    multiplier = investor['multiplier_value']
    investment_size = investor['investment_size']
    get_for_balance = True if investor['multiplier'] == 'Баланс' else False
    if get_for_balance:
        ext_k = (investment_size + get_history_profit()) / lieder_balance_value
    else:
        ext_k = (investment_size + get_history_profit() + get_positions_profit()) / lieder_balance_value
    try:
        min_lot = Mt.symbol_info(symbol).volume_min
        decimals = str(min_lot)[::-1].find('.')
    except AttributeError:
        decimals = 2
    if investor['changing_multiplier'] == 'Нет':
        result = round(lieder_volume * ext_k, decimals)
    else:
        result = round(lieder_volume * multiplier * ext_k, decimals)
    return result


async def open_position(investor, symbol, deal_type, lot, sender_ticket: int, tp=0.0, sl=0.0):
    """Открытие позиции"""
    try:
        point = Mt.symbol_info(symbol).point
        price = tp_in = sl_in = 0.0
        if deal_type == 0:  # BUY
            deal_type = Mt.ORDER_TYPE_BUY
            price = Mt.symbol_info_tick(symbol).ask
        if tp != 0:
            tp_in = price + tp * point
        if sl != 0:
            sl_in = price - sl * point
        elif deal_type == 1:  # SELL
            deal_type = Mt.ORDER_TYPE_SELL
            price = Mt.symbol_info_tick(symbol).bid
            if tp != 0:
                tp_in = price - tp * point
            if sl != 0:
                sl_in = price + sl * point
    except AttributeError:
        return {'retcode': -200}
    comment = DealComment()
    comment.lieder_ticket = sender_ticket
    comment.reason = '01'
    request = {
        "action": Mt.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": deal_type,
        "price": price,
        "sl": sl_in,
        "tp": tp_in,
        "deviation": DEVIATION,
        "magic": MAGIC,
        "comment": comment.string(),
        "type_time": Mt.ORDER_TIME_GTC,
        "type_filling": Mt.ORDER_FILLING_RETURN,
    }
    checked_request = await edit_volume_for_margin(investor, request)  # Проверка и расчет объема при недостатке маржи
    if not checked_request:
        return {'retcode': -100}
    elif checked_request != 'EMPTY_REQUEST' and checked_request != 'MORE_THAN_MAX_VOLUME':
        result = Mt.order_send(checked_request)
        return result


async def edit_volume_for_margin(investor, request):
    """Расчет объема при недостатке маржи и проверка на максимальный"""
    init_mt(investor)
    response = Mt.order_check(request)
    if not response or len(response) <= 0:
        return 'EMPTY_REQUEST'
    if response.retcode == 10019 or response.retcode == 10014:  # Неправильный объем # Нет достаточных денежных средств для выполнения запроса
        info = Mt.symbol_info(request['symbol'])
        max_vol = info.volume_max
        # min_vol = info.volume_min
        if request['volume'] > max_vol:
            print(investor['login'], f'Объем сделки [{request["volume"]}] больше максимального [{max_vol}]. ')
            await set_comment('Объем сделки больше максимального')
            return 'MORE_THAN_MAX_VOLUME'
        if investor['not_enough_margin'] == 'Минимальный объем':
            request['volume'] = Mt.symbol_info(request['symbol']).volume_min
        elif investor['not_enough_margin'] == 'Достаточный объем':
            acc_inf = Mt.account_info()
            margin = acc_inf.margin if acc_inf else 0
            symbol_coefficient = 100 if 'Forex' in info.path else 1
            start_mrg = info.margin_initial if info.margin_initial and info.margin_initial > 0 else 1
            shoulder = 1 / start_mrg * symbol_coefficient
            contract_specification = info.trade_contract_size
            price = Mt.symbol_info_tick(request['symbol']).bid
            lot_price = contract_specification * price
            hst_profit = get_history_profit()
            cur_profit = get_positions_profit()
            balance = investor['investment_size'] + hst_profit + cur_profit - margin
            min_lot = info.volume_min
            decimals = str(min_lot)[::-1].find('.')
            result_vol = round((balance / lot_price) / shoulder, decimals)
            print('((' + str(investor['investment_size']), '+', hst_profit, '+', cur_profit, '- ', str(margin) + ')',
                  '/', lot_price, ') / ', shoulder, '=', result_vol)
            if result_vol < min_lot:
                result_vol = min_lot
            request['volume'] = result_vol
        elif investor['not_enough_margin'] == 'Не открывать' \
                or investor['not_enough_margin'] == 'Не выбрано':
            request = None
    return request


def close_position(investor, position, reason):
    """Закрытие указанной позиции"""
    init_mt(init_data=investor)
    tick = Mt.symbol_info_tick(position.symbol)
    if not tick:
        return
    new_comment_str = position.comment
    if DealComment.is_valid_string(position.comment):
        comment = DealComment().set_from_string(position.comment)
        comment.reason = reason
        new_comment_str = comment.string()
    request = {
        'action': Mt.TRADE_ACTION_DEAL,
        'position': position.ticket,
        'symbol': position.symbol,
        'volume': position.volume,
        'type': Mt.ORDER_TYPE_BUY if position.type == 1 else Mt.ORDER_TYPE_SELL,
        'price': tick.ask if position.type == 1 else tick.bid,
        'deviation': DEVIATION,
        'magic:': MAGIC,
        'comment': new_comment_str,
        'type_tim': Mt.ORDER_TIME_GTC,
        'type_filing': Mt.ORDER_FILLING_IOC
    }
    result = Mt.order_send(request)
    # print(result)
    return result


def force_close_all_positions(investor, reason):
    """Принудительное закрытие всех позиций аккаунта"""
    init_res = init_mt(init_data=investor)
    if init_res:
        positions = get_investor_positions(only_own=False)
        if len(positions) > 0:
            for position in positions:
                if position.magic == MAGIC and DealComment.is_valid_string(position.comment):
                    close_position(investor, position, reason=reason)
        # Mt.shutdown()


def close_positions_by_lieder(investor):
    """Закрытие позиций инвестора, которые закрылись у лидера"""
    init_mt(init_data=investor)
    positions_investor = get_investor_positions()
    non_existed_positions = []
    if positions_investor:
        for ip in positions_investor:
            position_exist = False
            for lp in lieder_positions:
                comment = DealComment().set_from_string(ip.comment)
                if comment.lieder_ticket == lp.ticket:
                    position_exist = True
                    break
            if not position_exist:
                non_existed_positions.append(ip)
    for pos in non_existed_positions:
        print('     close position:', pos.comment)
        close_position(investor, pos, reason='06')


def synchronize_positions_volume(investor):
    try:
        investors_balance = investor['investment_size']
        global old_investors_balance
        login = investor.get("login")
        if login not in old_investors_balance:
            old_investors_balance[login] = investors_balance
        if "Корректировать объем" in (investor["recovery_model"], investor["buy_hold_model"]):
            if investors_balance != old_investors_balance[login]:
                volume_change_coefficient = investors_balance / old_investors_balance[login]
                if volume_change_coefficient != 1.0:
                    init_mt(investor)
                    investors_positions_table = LinkedPositions.get_linked_positions_table()
                    for _ in investors_positions_table:
                        min_lot = Mt.symbol_info(_.symbol).volume_min
                        decimals = str(min_lot)[::-1].find('.')
                        volume = _.volume
                        new_volume = round(volume_change_coefficient * volume, decimals)
                        if volume != new_volume:
                            _.modify_volume(new_volume)
                old_investors_balance[login] = investors_balance
    except Exception as e:
        print("Exception in synchronize_positions_volume():", e)


def synchronize_positions_limits(investor):
    """Изменение уровней ТП и СЛ указанной позиции"""
    init_mt(investor)
    for l_pos in lieder_positions:
        l_tp = get_pos_pips_tp(l_pos)
        l_sl = get_pos_pips_sl(l_pos)
        if l_tp > 0 or l_sl > 0:
            for i_pos in get_investor_positions():
                request = []
                new_comment_str = comment = ''
                if DealComment.is_valid_string(i_pos.comment):
                    comment = DealComment().set_from_string(i_pos.comment)
                    comment.reason = '09'
                    new_comment_str = comment.string()
                if comment.lieder_ticket == l_pos.ticket:
                    i_tp = get_pos_pips_tp(i_pos)
                    i_sl = get_pos_pips_sl(i_pos)
                    sl_lvl = tp_lvl = 0.0
                    if i_pos.type == Mt.POSITION_TYPE_BUY:
                        sl_lvl = i_pos.price_open - l_sl * Mt.symbol_info(i_pos.symbol).point
                        tp_lvl = i_pos.price_open + l_tp * Mt.symbol_info(i_pos.symbol).point
                    elif i_pos.type == Mt.POSITION_TYPE_SELL:
                        sl_lvl = i_pos.price_open + l_sl * Mt.symbol_info(i_pos.symbol).point
                        tp_lvl = i_pos.price_open - l_tp * Mt.symbol_info(i_pos.symbol).point
                    if i_tp != l_tp or i_sl != l_sl:
                        request = {
                            "action": Mt.TRADE_ACTION_SLTP,
                            "position": i_pos.ticket,
                            "symbol": i_pos.symbol,
                            "sl": sl_lvl,
                            "tp": tp_lvl,
                            "magic": MAGIC,
                            "comment": new_comment_str
                        }
                if request:
                    result = Mt.order_send(request)
                    print('Лимит изменен:', result)


async def patching_quotes():
    utc_to = datetime.combine(datetime.today(), datetime.min.time())
    utc_from = utc_to - timedelta(days=1)
    quotes = ['EURUSD', 'USDRUB', 'EURRUB']
    for i, quote in enumerate(quotes):
        i = i + 1
        try:
            if quote == 'EURRUB':
                eurusd = Mt.copy_rates_range("EURUSD", Mt.TIMEFRAME_H4, utc_from, utc_to)[-1][4]
                usdrub = Mt.copy_rates_range("USDRUB", Mt.TIMEFRAME_H4, utc_from, utc_to)[-1][4]
                data = {"currencies": quote,
                        "close": eurusd * usdrub}
            else:
                data = {"currencies": quote,
                        "close": Mt.copy_rates_range(quote, Mt.TIMEFRAME_H4, utc_from, utc_to)[-1][4]}
            payload = json.dumps(data,
                                 sort_keys=True,
                                 indent=1,
                                 cls=DjangoJSONEncoder)
            headers = {'Content-Type': 'application/json'}
            patch_url = host + f'update/{i}/'
            requests.request("PATCH", patch_url, headers=headers, data=payload)
        except Exception as e:
            print("Exception in patching_quotes:", e)


async def check_connection_exchange(investor):
    close_reason = None
    try:
        if investor['api_key_expired'] == "Да":
            close_reason = '04'
            # force_close_all_positions(investor=investor, reason=close_reason)
        elif investor['no_exchange_connection'] == 'Да':
            close_reason = '05'
            # force_close_all_positions(investor=investor, reason=close_reason)
        if close_reason:
            await set_comment(comment=reasons_code[close_reason])
    except Exception as e:
        print("Exception in patching_connection_exchange:", e)
    return True if close_reason else False


async def update_setup():
    global investors_disconnect_store
    while True:
        await source_setup()
        await asyncio.sleep(.5)


async def source_setup():
    global start_date_utc, source, lieder_existed_position_tickets
    main_source = {}
    url = host + 'last'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as get_response:
                response = await get_response.json()  # .text()
    except Exception as e:
        print(e)
        response = []
    if len(response) > 0:
        response = response[0]
        main_source['lieder'] = {
            'terminal_path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
            'login': int(response['leader_login']),
            'password': response['leader_password'],
            'server': response['leader_server']
        }
        main_source['investors'] = [
            {
                'terminal_path': r'C:\Program Files\MetaTrader 5_2\terminal64.exe',
                'login': int(response['investor_one_login']),
                'password': response['investor_one_password'],
                'server': response['investor_one_server'],
                'investment_size': float(response['investment_one_size']),
                'dcs_access': response['access_1'],

                "deal_in_plus": float(response['deal_in_plus']),
                "deal_in_minus": float(response['deal_in_minus']),
                "waiting_time": int(response['waiting_time']),
                "ask_an_investor": response['ask_an_investor'],
                "price_refund": response['price_refund'],
                "multiplier": response['multiplier'],
                "multiplier_value": float(response['multiplier_value']),
                "changing_multiplier": response['changing_multiplier'],
                "stop_loss": response['stop_loss'],
                "stop_value": float(response['stop_value']),
                "open_trades": response['open_trades'],
                "shutdown_initiator": response['shutdown_initiator'],
                "disconnect": response['disconnect'],
                "open_trades_disconnect": response['open_trades_disconnect'],
                "notification": response['notification'],
                "blacklist": response['blacklist'],
                "accompany_transactions": response['accompany_transactions'],
                "no_exchange_connection": response['no_exchange_connection'],
                "api_key_expired": response['api_key_expired'],
                "closed_deals_myself": response['closed_deals_myself'],
                "reconnected": response['reconnected'],
                "recovery_model": response['recovery_model'],
                "buy_hold_model": response['buy_hold_model'],
                "not_enough_margin": response['not_enough_margin'],
                "accounts_in_diff_curr": response['accounts_in_diff_curr'],
                "synchronize_deals": response['synchronize_deals'],
                "deals_not_opened": response['deals_not_opened'],
                "closed_deal_investor": response['closed_deal_investor'],
                "opening_deal": response['opening_deal'],
                "closing_deal": response['closing_deal'],
                "target_and_stop": response['target_and_stop'],
                "signal_relevance": response['signal_relevance'],
                "profitability": response['profitability'],
                "risk": response['risk'],
                "profit": response['profit'],
                "comment": response['comment'],
            },
            {
                'terminal_path': r'C:\Program Files\MetaTrader 5_3\terminal64.exe',
                'login': int(response['investor_two_login']),
                'password': response['investor_two_password'],
                'server': response['investor_two_server'],
                'investment_size': float(response['investment_two_size']),
                'dcs_access': response['access_2'],

                "deal_in_plus": float(response['deal_in_plus']),
                "deal_in_minus": float(response['deal_in_minus']),
                "waiting_time": int(response['waiting_time']),
                "ask_an_investor": response['ask_an_investor'],
                "price_refund": response['price_refund'],
                "multiplier": response['multiplier'],
                "multiplier_value": float(response['multiplier_value']),
                "changing_multiplier": response['changing_multiplier'],
                "stop_loss": response['stop_loss'],
                "stop_value": float(response['stop_value']),
                "open_trades": response['open_trades'],
                "shutdown_initiator": response['shutdown_initiator'],
                "disconnect": response['disconnect'],
                "open_trades_disconnect": response['open_trades_disconnect'],
                "notification": response['notification'],
                "blacklist": response['blacklist'],
                "accompany_transactions": response['accompany_transactions'],
                "no_exchange_connection": response['no_exchange_connection'],
                "api_key_expired": response['api_key_expired'],
                "closed_deals_myself": response['closed_deals_myself'],
                "reconnected": response['reconnected'],
                "recovery_model": response['recovery_model'],
                "buy_hold_model": response['buy_hold_model'],
                "not_enough_margin": response['not_enough_margin'],
                "accounts_in_diff_curr": response['accounts_in_diff_curr'],
                "synchronize_deals": response['synchronize_deals'],
                "deals_not_opened": response['deals_not_opened'],
                "closed_deal_investor": response['closed_deal_investor'],
                "opening_deal": response['opening_deal'],
                "closing_deal": response['closing_deal'],
                "target_and_stop": response['target_and_stop'],
                "signal_relevance": response['signal_relevance'],
                "profitability": response['profitability'],
                "risk": response['risk'],
                "profit": response['profit'],
                "comment": response['comment'],
            }
        ]
        main_source['settings'] = {
            "relevance": response['relevance'],
            "update_at": response['update_at'],
            "created_at": response['created_at']
            # "access": response['access'],
        }
        prev_date = main_source['settings']['created_at'].split('.')
        start_date_utc = datetime.strptime(prev_date[0], "%Y-%m-%dT%H:%M:%S")

        init_mt(main_source['lieder'])
        inf = Mt.account_info()
        main_source['lieder']['currency'] = inf.currency if inf else '-'
        for _ in main_source['investors']:
            idx = main_source['investors'].index(_)
            init_mt(main_source['investors'][idx])
            inf = Mt.account_info()
            main_source['investors'][idx]['currency'] = inf.currency if inf else '-'
            # main_source['lieder']['currency_coefficient'] = Mt.account_info().currency
    else:
        lieder_existed_position_tickets = []
        # if main_source:
    #     for _ in main_source['investors']:  # пересчет стартового капитала под валюту счета
    #         _['investment_size'] *= get_currency_coefficient(
    #             main_source['investors'][main_source['investors'].index(_)])

    source = main_source.copy()


async def update_lieder_info(sleep=sleep_lieder_update):
    global lieder_balance, lieder_equity, lieder_positions, source, lieder_existed_position_tickets
    while True:
        if len(source) > 0:
            init_res = init_mt(init_data=source['lieder'])
            if not init_res:
                await set_comment('Ошибка инициализации лидера')
                await asyncio.sleep(sleep)
                continue
            lieder_balance = Mt.account_info().balance
            lieder_equity = Mt.account_info().equity
            input_positions = Mt.positions_get()

            if len(lieder_existed_position_tickets) == 0:
                for _ in input_positions:
                    lieder_existed_position_tickets.append(_.ticket)

            lieder_positions = []
            if source['investors'][0]['reconnected'] == 'Не переоткрывать':
                for _ in input_positions:
                    if _.ticket not in lieder_existed_position_tickets:
                        lieder_positions.append(_)
            else:
                if len(lieder_existed_position_tickets) > 0:
                    lieder_existed_position_tickets = []
                lieder_positions = input_positions
                # lieder_positions = list(set(input_positions) - set(lieder_existed_position_tickets)) \
                # else input_positions
            # print('NEW')
            # for _ in input_positions:
            #     print(_)
            # print('EXIST')
            # for _ in lieder_existed_position_tickets:
            #     print(_)
            # print('RESULT')
            # for _ in lieder_positions:
            #     print(_)

            # exit()

            # Mt.shutdown()
            store_change_disconnect_state()  # сохранение Отключился в список
            print(
                f'\nLIEDER {source["lieder"]["login"]} [{source["lieder"]["currency"]}] - {len(lieder_positions)} positions :',
                datetime.utcnow().replace(microsecond=0),
                ' [EURUSD', EURUSD, ': USDRUB', USDRUB, ': EURRUB', str(round(EURRUB, 3)) + ']',
                ' Comments:', send_messages)
            trading_event.set()
        await asyncio.sleep(sleep)


async def execute_investor(investor):
    await access_starter(investor)
    if investor['blacklist'] == 'Да':
        print(investor['login'], 'in blacklist')
        return
    if await check_notification(investor):
        print(investor['login'], 'not pay - notify')
        return
    if await check_connection_exchange(investor):
        print(investor['login'], 'API expired or Broker disconnected')
        return
    synchronize = True if investor['deals_not_opened'] == 'Да' or investor['synchronize_deals'] == 'Да' else False
    if investor['synchronize_deals'] == 'Да':  # если "синхронизировать"
        await disable_synchronize(synchronize)
    if not synchronize:
        return

    init_res = init_mt(init_data=investor)
    if not init_res:
        await set_comment('Ошибка инициализации инвестора ' + str(investor['login']))
        return
    # print(f' - {investor["login"]} [{investor["currency"]}] - {len(Mt.positions_get())} positions. Access:',
    #       investor['dcs_access'])  # , end='')
    # enable_algotrading()

    # for _ in get_investor_positions():
    #     print('\n', Mt.symbol_info(_.symbol).path)

    if investor['dcs_access']:
        await execute_conditions(investor=investor)  # проверка условий кейса закрытия
    if investor['dcs_access']:
        await check_stop_limits(investor=investor)  # проверка условий стоп-лосс
    if investor['dcs_access']:

        synchronize_positions_volume(investor)  # коррекция объемов позиций
        synchronize_positions_limits(investor)  # коррекция лимитов позиций

        for pos_lid in lieder_positions:
            inv_tp = get_pos_pips_tp(pos_lid)
            inv_sl = get_pos_pips_sl(pos_lid)
            init_mt(investor)
            if not is_position_opened(pos_lid, investor):
                ret_code = None
                if check_transaction(investor=investor, lieder_position=pos_lid):
                    volume = multiply_deal_volume(investor, lieder_position=pos_lid)

                    min_lot = Mt.symbol_info(pos_lid.symbol).volume_min
                    decimals = str(min_lot)[::-1].find('.')
                    volume = round(volume / get_currency_coefficient(investor), decimals)
                    # print(get_currency_coefficient(investor))
                    response = await open_position(investor=investor, symbol=pos_lid.symbol, deal_type=pos_lid.type,
                                                   lot=volume, sender_ticket=pos_lid.ticket,
                                                   tp=inv_tp, sl=inv_sl)
                    if response:
                        try:
                            ret_code = response.retcode
                        except AttributeError:
                            ret_code = response['retcode']
                if ret_code:
                    msg = str(investor['login']) + ' ' + send_retcodes[ret_code][1] + ' : ' + str(ret_code)
                    if ret_code != 10009:  # Заявка выполнена
                        await set_comment('\t' + msg)
                    print(msg)
        # else:
        #     set_comment('Не выполнено условие +/-')

    # закрытие позиций от лидера
    if (investor['dcs_access'] or  # если сопровождать сделки или доступ есть
            (not investor['dcs_access'] and investor['accompany_transactions'] == 'Да')):
        close_positions_by_lieder(investor)

    # Mt.shutdown()


async def task_manager():
    while True:
        await trading_event.wait()

        if datetime.now().strftime("%H:%M:%S") == "10:00:00":
            await patching_quotes()

        if len(source) > 0:
            for _ in source['investors']:
                event_loop.create_task(execute_investor(_))

        trading_event.clear()


if __name__ == '__main__':
    # set_dummy_data()
    event_loop = asyncio.new_event_loop()
    event_loop.create_task(update_setup())  # для теста без сервера закомментировать
    event_loop.create_task(update_lieder_info())
    event_loop.create_task(task_manager())
    event_loop.run_forever()
