import asyncio
import json
from datetime import datetime, timedelta
from math import fabs
import MetaTrader5 as Mt
# from win32gui import PostMessage, GetAncestor, FindWindow
import requests
from django.core.serializers.json import DjangoJSONEncoder

send_retcodes = {
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
    10034: ('TRADE_RETCODE_LIMIT_VOLUME', 'Достигнут лимит на объем ордеров и позиций для данного символа'),
    10035: ('TRADE_RETCODE_INVALID_ORDER', 'Неверный или запрещённый тип ордера'),
    10036: ('TRADE_RETCODE_POSITION_CLOSED', 'Позиция с указанным POSITION_IDENTIFIER уже закрыта'),
    10038: ('TRADE_RETCODE_INVALID_CLOSE_VOLUME', 'Закрываемый объем превышает текущий объем позиции'),
    10039: ('TRADE_RETCODE_CLOSE_ORDER_EXIST', 'Для указанной позиции уже есть ордер на закрытие'),
    10040: ('TRADE_RETCODE_LIMIT_POSITIONS', 'Количество открытых позиций, которое можно одновременно иметь на счете, '
                                             'может быть ограничено настройками сервера'),
    10041: ('TRADE_RETCODE_REJECT_CANCEL', 'Запрос на активацию отложенного ордера отклонен, а сам ордер отменен'),
    10042: ('TRADE_RETCODE_LONG_ONLY', 'Запрос отклонен, так как на символе установлено правило "Разрешены только '
                                       'длинные позиции"  (POSITION_TYPE_BUY)'),
    10043: ('TRADE_RETCODE_SHORT_ONLY', 'Запрос отклонен, так как на символе установлено правило "Разрешены только '
                                        'короткие позиции" (POSITION_TYPE_SELL)'),
    10044: ('TRADE_RETCODE_CLOSE_ONLY', 'Запрос отклонен, так как на символе установлено правило "Разрешено только '
                                        'закрывать существующие позиции"'),
    10045: ('TRADE_RETCODE_FIFO_CLOSE', 'Запрос отклонен, так как для торгового счета установлено правило "Разрешено '
                                        'закрывать существующие позиции только по правилу FIFO" ('
                                        'ACCOUNT_FIFO_CLOSE=true)'),
    10046: ('TRADE_RETCODE_HEDGE_PROHIBITED', 'Запрос отклонен, так как для торгового счета установлено правило '
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

TIMEOUT_INIT = 10_000  # время ожидания при инициализации терминала (рекомендуемое 60_000 millisecond)
MAGIC = 9876543210  # идентификатор эксперта
DEVIATION = 20  # допустимое отклонение цены в пунктах при совершении сделки
START_DATE = datetime(2023, 2, 1)  # начальное время с которого ведется расчет по истории

lieder_account = {'terminal_path': r'C:\Program Files\MetaTrader 5\terminal64.exe'}
investors_list = [{'terminal_path': r'C:\Program Files\MetaTrader 5_2\terminal64.exe'},
                  {'terminal_path': r'C:\Program Files\MetaTrader 5_3\terminal64.exe'}]
settings = {}
# investor_accounts = []
output_report = []  # сюда выводится отчет
# report_stamp = {'id': -1, 'code': 0, 'message': 'null'}
lieder_balance = 0  # default var
lieder_equity = 0  # default var
lieder_positions = []  # default var
trading_event = asyncio.Event()  # init async event
host = 'https://my.atimex.io:8000/api/demo_mt5/last'


def disable_copy():
    url = 'https://my.atimex.io:8000/api/demo_mt5/list'
    response = requests.get(url).json()
    url = f'https://my.atimex.io:8000/api/%27demo_mt5/patch/<int:{len(response)}>/'
    requests.patch(url=url, data={"access": False})


def get_start_info():
    response = requests.get(host).json()
    global lieder_account, investors_list, settings
    if len(response) > 0:
        lieder_account = {
            'terminal_path': r'C:\Program Files\MetaTrader 5\terminal64.exe',
            'login': int(response['leader_login']),
            'password': response['leader_password'],
            'server': response['leader_server']
        }
        investors_list = [
            {
                'path': r'C:\Program Files\MetaTrader 5_2\terminal64.exe',
                'login': int(response['investor_one_login']),
                'password': response['investor_one_password'],
                'server': response['investor_one_server'],
                'investment_size': response['investment_one_size']
            },
            {
                'path': r'C:\Program Files\MetaTrader 5_3\terminal64.exe',
                'login': int(response['investor_two_login']),
                'password': response['investor_two_password'],
                'server': response['investor_two_server'],
                'investment_size': response['investment_two_size']
            }
        ]
        settings = {
            "deal_in_plus": response['deal_in_plus'],
            "deal_in_minus": response['deal_in_minus'],
            "waiting_time": response['waiting_time'],
            "ask_an_investor": response['ask_an_investor'],
            "price_refund": response['price_refund'],
            "multiplier": response['multiplier'],
            "multiplier_value": response['multiplier_value'],
            "changing_multiplier": response['changing_multiplier'],
            "stop_loss": response['stop_loss'],
            "stop_value": response['stop_value'],
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
            "relevance": response['relevance'],
            "access": response['access'],
            "update_at": response['update_at']
        }
        check_income_data(response)
    else:
        pass


def check_income_data(json_response):
    # print(len(json_response))
    if 'leader_login' in json_response and json_response["leader_login"] != "":
        try:
            lieder_account['login'] = int(json_response["leader_login"])
        except ValueError or TypeError:
            lieder_account['login'] = 805060
    else:
        lieder_account['login'] = 805060
    if 'leader_login' in json_response and json_response["leader_password"] != "":
        lieder_account['password'] = json_response["leader_password"]
    else:
        lieder_account['password'] = 'bsccvba1'
    if 'leader_server' in json_response and json_response["leader_server"] != "":
        lieder_account['server'] = json_response["leader_server"]
    else:
        lieder_account['server'] = 'OpenInvestments-Demo'
    # -----------------------------------------
    if 'investor_one_login' in json_response and json_response["investor_one_login"] != "":
        try:
            investors_list[0]['login'] = int(json_response["investor_one_login"])
        except ValueError:
            investors_list[0]['login'] = 805061
    else:
        investors_list[0]['login'] = 805061
    if 'investor_one_password' in json_response and json_response["investor_one_password"] != "":
        investors_list[0]['password'] = json_response["investor_one_password"]
    else:
        investors_list[0]['password'] = 'weax5szp'
    if 'investor_one_server' in json_response and json_response["investor_one_server"] != "":
        investors_list[0]['server'] = json_response["investor_one_server"]
    else:
        investors_list[0]['server'] = 'OpenInvestments-Demo'
    if 'investment_one_size' in json_response and json_response["investment_one_size"] != "":
        try:
            investors_list[0]['investment_size'] = float(json_response["investment_one_size"])
        except ValueError:
            investors_list[0]['investment_size'] = 10000.0
    else:
        investors_list[0]['investment_size'] = 10000.0
        # -----------------------------------------
    if 'investor_two_login' in json_response and json_response["investor_two_login"] != "":
        try:
            investors_list[1]['login'] = int(json_response["investor_two_login"])
        except ValueError:
            investors_list[1]['login'] = 5009942758
    else:
        investors_list[1]['login'] = 5009942758
    if 'investor_two_password' in json_response and json_response["investor_two_password"] != "":
        investors_list[1]['password'] = json_response["investor_two_password"]
    else:
        investors_list[1]['password'] = 'rdb1toxf'
    if 'investor_two_server' in json_response and json_response["investor_two_server"] != "":
        investors_list[1]['server'] = json_response["investor_two_server"]
    else:
        investors_list[1]['server'] = 'MetaQuotes-Demo'
    if 'investment_two_size' in json_response and json_response["investment_two_size"] != "":
        try:
            investors_list[1]['investment_size'] = float(json_response["investment_two_size"])
        except ValueError:
            investors_list[1]['investment_size'] = 10000.0
    else:
        investors_list[1]['investment_size'] = 10000.0
        # -----------------------------------------
    if 'deal_in_plus' in json_response and json_response["deal_in_plus"] != "":
        try:
            settings['deal_in_plus'] = float(json_response["deal_in_plus"])
        except ValueError:
            settings['deal_in_plus'] = 0.1
    else:
        settings['deal_in_plus'] = 0.1
    if 'deal_in_minus' in json_response and json_response["deal_in_minus"] != "":
        try:
            settings['deal_in_minus'] = float(json_response["deal_in_minus"])
        except ValueError:
            settings['deal_in_minus'] = -0.1
    else:
        settings['deal_in_minus'] = -0.1
    if 'waiting_time' in json_response and json_response["waiting_time"] != "":
        try:
            settings['waiting_time'] = int(json_response["waiting_time"])
        except ValueError:
            settings['waiting_time'] = 1
    else:
        settings['waiting_time'] = 1
    if 'ask_an_investor' in json_response and json_response["ask_an_investor"] in ['Все', 'Плюс', 'Минус']:
        settings['ask_an_investor'] = json_response["ask_an_investor"]
    else:
        settings['ask_an_investor'] = 'Все'
    if 'price_refund' in json_response and json_response["price_refund"] in ['Да', 'Нет']:
        settings['price_refund'] = json_response["price_refund"]
    else:
        settings['price_refund'] = 'Да'
        # -----------------------------------------
    if 'multiplier' in json_response and json_response["multiplier"] in ['Баланс', 'Средства']:
        settings['multiplier'] = json_response["multiplier"]
    else:
        settings['multiplier'] = 'Баланс'
    if 'multiplier_value' in json_response and json_response["multiplier_value"] != "":
        try:
            settings['multiplier_value'] = float(json_response["multiplier_value"])
        except ValueError:
            settings['multiplier_value'] = 10.0
    else:
        settings['multiplier_value'] = 10.0
    if 'changing_multiplier' in json_response and json_response["changing_multiplier"] in ['Да', 'Нет']:
        settings['changing_multiplier'] = json_response["changing_multiplier"]
    else:
        settings['changing_multiplier'] = 'Да'
        # -----------------------------------------
    if 'stop_loss' in json_response and json_response["stop_loss"] in ['Процент', 'Валюта']:
        settings['stop_loss'] = json_response["stop_loss"]
    else:
        settings['stop_loss'] = 'Процент'
    if 'stop_value' in json_response and json_response["stop_value"] != "":
        try:
            settings['stop_value'] = float(json_response["stop_value"])
        except ValueError:
            settings['stop_value'] = 20.0
    else:
        settings['stop_value'] = 20.0
    if 'open_trades' in json_response and json_response["open_trades"] in ['Закрыть', 'Закрыть и отключить']:
        settings['open_trades'] = json_response["open_trades"]
    else:
        settings['open_trades'] = 'Закрыть'
        # -----------------------------------------
    if 'shutdown_initiator' in json_response and json_response["shutdown_initiator"] in ['Инвестор', 'Админ',
                                                                                         'Система']:
        settings['shutdown_initiator'] = json_response["shutdown_initiator"]
    else:
        settings['shutdown_initiator'] = 'Инвестор'
    if 'disconnect' in json_response and json_response["disconnect"] in ['Да', 'Нет']:
        settings['disconnect'] = json_response["disconnect"]
    else:
        settings['disconnect'] = 'Нет'
    if 'open_trades_disconnect' in json_response and json_response["open_trades_disconnect"] in ['Закрыть', 'Оставить']:
        settings['open_trades_disconnect'] = json_response["open_trades_disconnect"]
    else:
        settings['open_trades_disconnect'] = 'Закрыть'
    if 'notification' in json_response and json_response["notification"] in ['Да', 'Нет']:
        settings['notification'] = json_response["notification"]
    else:
        settings['notification'] = 'Нет'
    if 'blacklist' in json_response and json_response["blacklist"] in ['Да', 'Нет']:
        settings['blacklist'] = json_response["blacklist"]
    else:
        settings['blacklist'] = 'Нет'
    if 'accompany_transactions' in json_response and json_response["accompany_transactions"] in ['Да', 'Нет']:
        settings['accompany_transactions'] = json_response["accompany_transactions"]
    else:
        settings['accompany_transactions'] = 'Нет'
    # -----------------------------------------=
    if 'no_exchange_connection' in json_response and json_response["no_exchange_connection"] in ['Да', 'Нет']:
        settings['no_exchange_connection'] = json_response["accompany_transactions"]
    else:
        settings['no_exchange_connection'] = 'Нет'
    if 'api_key_expired' in json_response and json_response["api_key_expired"] in ['Да', 'Нет']:
        settings['api_key_expired'] = json_response["api_key_expired"]
    else:
        settings['api_key_expired'] = 'Нет'
    # -----------------------------------------
    if 'closed_deals_myself' in json_response and json_response["closed_deals_myself"] in ['Переоткрывать',
                                                                                           'Не переоткрывать']:
        settings['closed_deals_myself'] = json_response["closed_deals_myself"]
    else:
        settings['closed_deals_myself'] = 'Переоткрывать'
    if 'reconnected' in json_response and json_response["reconnected"] in ['Переоткрывать', 'Не переоткрывать']:
        settings['reconnected'] = json_response["reconnected"]
    else:
        settings['reconnected'] = 'Переоткрывать'
    # -----------------------------------------
    if 'recovery_model' in json_response and json_response["recovery_model"] in ['Корректировать объем',
                                                                                 'Не корректировать']:
        settings['recovery_model'] = json_response["recovery_model"]
    else:
        settings['recovery_model'] = 'Не корректировать'
    if 'buy_hold_model' in json_response and json_response["buy_hold_model"] in ['Корректировать объем',
                                                                                 'Не корректировать']:
        settings['buy_hold_model'] = json_response["buy_hold_model"]
    else:
        settings['buy_hold_model'] = 'Не корректировать'
    # -----------------------------------------
    if 'not_enough_margin' in json_response and json_response["not_enough_margin"] in ['Минимальный объем',
                                                                                       'Достаточный объем',
                                                                                       'Не открывать']:
        settings['not_enough_margin'] = json_response["not_enough_margin"]
    else:
        settings['not_enough_margin'] = 'Минимальный объем'
    if 'accounts_in_diff_curr' in json_response and json_response["accounts_in_diff_curr"] in ['Рубли', 'Евро',
                                                                                               'Доллары']:
        settings['accounts_in_diff_curr'] = json_response["accounts_in_diff_curr"]
    else:
        settings['accounts_in_diff_curr'] = 'Доллары'
    # -----------------------------------------
    if 'synchronize_deals' in json_response and json_response["synchronize_deals"] in ['Да', 'Нет']:
        settings['synchronize_deals'] = json_response["synchronize_deals"]
    else:
        settings['synchronize_deals'] = 'Нет'
    if 'deals_not_opened' in json_response and json_response["deals_not_opened"] in ['Да', 'Нет']:
        settings['deals_not_opened'] = json_response["deals_not_opened"]
    else:
        settings['deals_not_opened'] = 'Нет'
    if 'closed_deal_investor' in json_response and json_response["closed_deal_investor"] in ['Да', 'Нет']:
        settings['closed_deal_investor'] = json_response["closed_deal_investor"]
    else:
        settings['closed_deal_investor'] = 'Нет'
    # "opening_deal": null,
    # "closing_deal": null,
    # "target_and_stop": null,
    # "signal_relevance": null,
    # "profitability": null,
    # "risk": null,
    # "profit": null,
    # "comment": null,
    # "relevance": false,
    # "access": false,
    # "update_at": "2023-02-14T12:19:22.704830Z"


def get_pips_tp(position, price=None):
    """Расчет Тейк-профит в пунктах"""
    if price is None:
        price = position.price_open
    result = 0.0
    if position.tp > 0:
        result = round(fabs(price - position.tp) / Mt.symbol_info(position.symbol).point)
    return result


def get_pips_sl(position, price=None):
    """Расчет Стоп-лосс в пунктах"""
    if price is None:
        price = position.price_open
    result = 0.0
    if position.sl > 0:
        result = round(fabs(price - position.sl) / Mt.symbol_info(position.symbol).point)
    return result


def get_positions_profit():
    """Расчет прибыли текущих позиций"""
    active_positions = Mt.positions_get()
    result = 0
    own_positions = []
    try:
        if len(active_positions) > 0:
            for pos in active_positions:
                if pos.magic == MAGIC:
                    own_positions.append(pos)
        if len(own_positions) > 0:
            for pos in own_positions:
                if pos.type < 2:
                    result += pos.profit  # + pos.commission
    except AttributeError:
        print('ERROR in get_positions_profit() : wrong positions list')
        result = None
    return result


def get_history_profit():
    """Расчет прибыли по истории"""
    date_from = START_DATE
    date_to = datetime.today().replace(microsecond=0) + timedelta(days=1)
    history_deals = Mt.history_deals_get(date_from, date_to)
    result = 0
    own_positions = []
    try:
        if len(history_deals) > 0:
            for pos in history_deals:
                if pos.magic == MAGIC:
                    linked_pos = Mt.history_deals_get(position=pos.position_id)
                    for lp in linked_pos:
                        own_positions.append(lp)
        if len(own_positions) > 0:
            for pos in own_positions:
                if pos.type < 2:
                    result += pos.profit  # + pos.commission
    except AttributeError:
        print('ERROR in get_history_profit() : wrong positions list')
        result = None
    return result


def check_stop_limits(investor):
    """Проверка стоп-лимита по проценту либо абсолютному показателю"""
    start_balance = investor['investment_size']
    if start_balance <= 0:
        start_balance = 1
    limit_size = settings['stop_value']
    calc_limit_in_percent = True if settings['stop_loss'] == 'Проценты' else False
    history_profit = get_history_profit()
    current_profit = get_positions_profit()
    # SUMM TOTAL PROFIT
    if history_profit is None or current_profit is None:
        return
    close_positions = False
    total_profit = history_profit + current_profit
    print('\t', 'Прибыль' if total_profit >= 0 else 'Убыток', 'торговли c', START_DATE, ':', round(total_profit, 3),
          'USD')
    # CHECK LOST SIZE FOR CLOSE ALL
    if total_profit < 0:
        if calc_limit_in_percent:
            current_percent = fabs(total_profit / start_balance) * 100
            if current_percent >= limit_size:
                close_positions = True
        else:
            if fabs(total_profit) >= limit_size:
                close_positions = True
        # CLOSE ALL POSITIONS
        active_positions = Mt.positions_get()
        if close_positions:
            print('     Закрытие всех позиций по условию стоп-лосс')
            for act_pos in active_positions:
                if act_pos.magic == MAGIC:
                    close_position(act_pos)
            if settings['open_trades'] == 'Закрыть и отключить':
                disable_copy(investor=investor, data={"active_action": False})


def check_transaction(lieder_position):
    """Проверка открытия позиции"""
    price_refund = True if settings['price_refund'] == 'Да' else False
    if not price_refund:  # если не возврат цены
        timeout = settings['waiting_time'] * 60
        deal_time = lieder_position.time_update
        curr_time = round(datetime.timestamp(datetime.now().replace(microsecond=0)))
        delta_time = curr_time - deal_time
        if delta_time > timeout:  # если время больше заданного
            return False

    transaction_type = 0
    if settings['ask_an_investor'] == 'Плюс':
        transaction_type = 1
    elif settings['ask_an_investor'] == 'Минус':
        transaction_type = -1
    deal_profit = lieder_position.profit
    if transaction_type > 0 > deal_profit:  # если открывать только + и профит < 0
        return False
    if deal_profit > 0 > transaction_type:  # если открывать только - и профит > 0
        return False

    transaction_plus = settings['deal_in_plus']
    transaction_minus = settings['deal_in_minus']
    price_open = lieder_position.price_open
    price_current = lieder_position.price_current

    res = None
    if lieder_position.type == 0:  # Buy
        res = (price_current - price_open) / price_open * 100  # Расчет сделки покупки по формуле
    elif lieder_position.type == 1:  # Sell
        res = (price_open - price_current) / price_open * 100  # Расчет сделки продажи по формуле
    return True if res is not None and transaction_plus >= res >= transaction_minus else False  # Проверка на заданные отклонения


def get_deals_volume(investor, lieder_volume, lieder_balance_value):
    """Расчет множителя"""
    multiplier = settings['multiplier_value']
    get_for_balance = True if settings['multiplier'] == 'Баланс' else False
    investment_size = investor['investment_size']
    ext_k = 1.0
    if get_for_balance:
        ext_k = (investment_size + get_history_profit()) / lieder_balance_value
    else:
        ext_k = (investment_size + get_history_profit() + get_positions_profit()) / lieder_balance_value
    return round(lieder_volume * multiplier * ext_k, 4)


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


def init_mt(init_data, need_login=False):
    """Инициализация терминала"""
    if Mt.initialize(login=init_data['login'], server=init_data['server'], password=init_data['password'],
                     path=init_data['terminal_path'], timeout=TIMEOUT_INIT):
        # print(f'INVESTOR account {init_data["login"]} : {datetime.now()}')
        if need_login:
            if not Mt.login(login=init_data['login'], server=init_data['server'], password=init_data['password']):
                print('Login ERROR', Mt.last_error())
    else:
        print(f'>>>>> account {init_data["login"]} : {datetime.now()} : ERROR', Mt.last_error(),
              f': timeout = {TIMEOUT_INIT}')
        exit()


def open_position(symbol, deal_type, lot, sender_ticket, tp=0, sl=0):
    """Открытие позиции"""
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
        "comment": str(sender_ticket),
        "type_time": Mt.ORDER_TIME_GTC,
        "type_filling": Mt.ORDER_FILLING_RETURN,
    }
    result = Mt.order_send(request)
    return result


def close_position(position):
    """Закрытие указанной позиции"""
    tick = Mt.symbol_info_tick(position.symbol)
    request = {
        'action': Mt.TRADE_ACTION_DEAL,
        'position': position.ticket,
        'symbol': position.symbol,
        'volume': position.volume,
        'type': Mt.ORDER_TYPE_BUY if position.type == 1 else Mt.ORDER_TYPE_SELL,
        'price': tick.ask if position.type == 1 else tick.bid,
        'deviation': DEVIATION,
        'magic:': MAGIC,
        'comment': 'CLOSED_BY_EXPERT',  # position.comment,
        'type_tim': Mt.ORDER_TIME_GTC,
        'type_filing': Mt.ORDER_FILLING_IOC
    }
    result = Mt.order_send(request)
    return result


def get_investors_positions_count(investor):
    """Количество открытых позиций"""
    init_mt(init_data=investor)
    return Mt.positions_total()


def force_close_all_positions(investor):
    """Принудительное закрытие всех позиций аккаунта"""
    init_mt(init_data=investor)
    positions = Mt.positions_get()
    if len(positions) > 0:
        for position in positions:
            if position.magic == MAGIC:
                close_position(position)
    Mt.shutdown()


def close_positions_by_lieder(positions_lieder, positions_investor):
    """Закрытие позиций инвестора, которые закрылись у лидера"""
    non_existed_positions = []
    for ip in positions_investor:
        position_exist = False
        for lp in positions_lieder:
            if int(ip.comment) == lp.ticket:
                position_exist = True
                break
        if not position_exist:
            non_existed_positions.append(ip)
    for pos in non_existed_positions:
        print('     close position:', pos.comment)
        close_position(pos)


def is_position_exist_in_list(position, list_positions, check_for_comment=False):
    if len(list_positions) <= 0:
        return False
    try:
        for pos in list_positions:
            value = int(pos.comment) if check_for_comment else pos.ticket
            if position.ticket == value:
                return True
    except ValueError:
        return False
    return False


# def is_positions_changed(prev_positions, curr_positions):
#     prev_len = len(prev_positions)
#     curr_len = len(curr_positions)
#     if prev_len != curr_len:
#         return True
#     for cur in curr_positions:
#         if not is_position_exist_in_list(cur, prev_positions):
#             return True
#     return False

# ----------------------------------------------------------------------------  async

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
            patch_url = f'http://127.0.0.1:8000/exchange/update/{i}/'
            requests.request("PATCH", patch_url, headers=headers, data=payload)
        except Exception as e:
            print("Exception in patching_quotes:", e)


async def execute_lieder(sleep_size=5):
    global lieder_balance, lieder_equity
    global lieder_positions
    global investors_list
    while True:
        get_start_info()
        if len(settings) > 0:
            init_mt(init_data=lieder_account)
            lieder_balance = Mt.account_info().balance
            lieder_equity = Mt.account_info().equity
            lieder_positions = Mt.positions_get()
            Mt.shutdown()
            print(f'\nLIEDER {lieder_account["login"]} - {len(lieder_positions)} positions',
                      datetime.now().time())
            trading_event.set()
        await asyncio.sleep(sleep_size)


async def execute_investor(investor):
    init_mt(init_data=investor)
    # enable_algotrading()
    global output_report
    output_report = []
    investor_positions = Mt.positions_get()
    print(f' - {investor["login"]} - {len(investor_positions)} positions : {datetime.now()}')
    check_stop_limits(investor=investor)
    for pos_lid in lieder_positions:
        inv_tp = get_pips_tp(pos_lid)
        inv_sl = get_pips_sl(pos_lid)
        if not is_position_exist_in_list(position=pos_lid, list_positions=investor_positions, check_for_comment=True):

            if check_transaction(lieder_position=pos_lid):
                volume = 1.0 \
                    if settings['changing_multiplier'] == 'Нет' \
                    else get_deals_volume(investor, lieder_volume=pos_lid.volume,
                                          lieder_balance_value=lieder_balance
                                          if settings['multiplier'] == 'Баланс' else lieder_equity)
                response = open_position(symbol=pos_lid.symbol, deal_type=pos_lid.type, lot=volume,
                                         sender_ticket=pos_lid.ticket, tp=inv_tp, sl=inv_sl)
                rpt = {'code': response.retcode, 'message': send_retcodes[response.retcode][1]}
                output_report.append(rpt)

                if response.retcode == 10014:
                    print('-----------------VOLUME', volume)

    close_positions_by_lieder(positions_lieder=lieder_positions, positions_investor=Mt.positions_get())
    if len(output_report) > 0:
        print('    ', output_report)
    Mt.shutdown()


async def task_manager():
    while True:
        await trading_event.wait()
        for _ in investors_list:
            event_loop.create_task(execute_investor(_))
        time_now = datetime.now()
        current_time = time_now.strftime("%H:%M:%S")
        if current_time == "10:00:00":
            await patching_quotes()
        trading_event.clear()


if __name__ == '__main__':
    event_loop = asyncio.new_event_loop()
    event_loop.create_task(execute_lieder(sleep_size=1))
    event_loop.create_task(task_manager())
    event_loop.run_forever()
