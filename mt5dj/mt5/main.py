import asyncio
from datetime import datetime, timedelta
from math import fabs
import MetaTrader5 as mt
# from win32gui import PostMessage, GetAncestor, FindWindow
import requests

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
lieder_account = {
    'terminal_path': r'C:\Users\Данил\Desktop\MetaTrader 5_1\terminal64.exe',
    'login': 805060,
    'password': 'bsccvba1',
    'server': 'OpenInvestments-Demo'
}  # данные лидера для инициализации

MAGIC = 5555555553  # идентификатор эксперта
DEVIATION = 20  # допустимое отклонение цены в пунктах при совершении сделки
START_DATE = datetime(2022, 2, 1, 0, 0, 0)  # начальное время с которого ведется расчет по истории

investor_accounts = []
output_report = []  # сюда выводится отчет
# report_stamp = {'id': -1, 'code': 0, 'message': 'null'}
lieder_balance = 0  # default var
lieder_equity = 0  # default var
lieder_positions = []  # default var
trading_event = asyncio.Event()  # init async event
host = 'http://127.0.0.1:8000/api/investors/'


# input_investment_size = 10000  # стартовый депозит инвестора
# input_get_multiplier_for_balance = True  # False  если считаем множитель по средствам
# input_volume_multiplier = 10.0  # множитель
# input_check_stop_limit_in_percent = True  # False если считаем стоп-лимит по абсолютному значению
# input_stop_limit = 20.05  # значение стоп-лимита (% или USD)
# input_transaction_plus = 0.1
# input_transaction_minus = -0.1

def change_investor_data(investor, data):
    url = host + '?id=' + str(investor['id']) + f'&data={data}'  # '&data={"active_action": False}'
    requests.patch(url=url)


def get_investors_list():
    url = host + '?user=all'
    response = requests.get(url).json()
    investors_list = []
    for investor in response:

        if investor['active_action']:  # если инвестор активен

            if investor['in_blacklist'] == 'Да':  # если в блек листе
                force_close_all_positions(investor)
                change_investor_data(investor=investor, data={"active_action": False})
                continue

            if investor['disconnect'] == 'Да':  # если отключиться
                if get_investors_positions_count(investor) == 0:  # если нет открыты сделок
                    change_investor_data(investor=investor, data={"active_action": False})
                    continue

                if investor['w_positions'] == 'Закрыть':  # если сделки закрыть
                    force_close_all_positions(investor)
                    # change_investor_data(investor=investor, data={"active_action": False})
                    continue

                if investor['w_positions'] == 'Оставить' and investor[
                    'after'] == 'Нет':  # если сделки оставить и не сопровождать
                    change_investor_data(investor=investor, data={"active_action": False})
                    continue

            investors_list.append(investor)

    return investors_list


def get_pips_tp(position, price=None):
    """Расчет Тейк-профит в пунктах"""
    if price is None:
        price = position.price_open
    result = 0.0
    if position.tp > 0:
        result = round(fabs(price - position.tp) / mt.symbol_info(position.symbol).point)
    return result


def get_pips_sl(position, price=None):
    """Расчет Стоп-лосс в пунктах"""
    if price is None:
        price = position.price_open
    result = 0.0
    if position.sl > 0:
        result = round(fabs(price - position.sl) / mt.symbol_info(position.symbol).point)
    return result


def get_positions_profit():
    """Расчет прибыли текущих позиций"""
    active_positions = mt.positions_get()
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
    history_deals = mt.history_deals_get(date_from, date_to)
    result = 0
    own_positions = []
    try:
        if len(history_deals) > 0:
            for pos in history_deals:
                if pos.magic == MAGIC:
                    linked_pos = mt.history_deals_get(position=pos.position_id)
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
    limit_size = investor['volume_stop_limit']
    calc_limit_in_percent = True if investor['stop_limit_type'] == 'Проценты' else False
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
        active_positions = mt.positions_get()
        if close_positions:
            print('     Закрытие всех позиций по условию стоп-лосс')
            for act_pos in active_positions:
                if act_pos.magic == MAGIC:
                    close_position(act_pos)
            if investor['stop_limit_after'] == 'Закрыть и отключить':
                change_investor_data(investor=investor, data={"active_action": False})


def checking_an_open_transaction(transaction_plus, transaction_minus, price_open, price_current, type_of_order,
                                 ask_investor=False, price_return=False, timer=60):
    """Проверка открытой позиции"""
    if type_of_order == 0:
        res = (price_current - price_open) / price_open * 100  # Расчет сделки покупки по формуле
    elif type_of_order == 1:
        res = (price_open - price_current) / price_open * 100  # Расчет сделки продажи по формуле
    # ask_investor = requests.post('http://127.0.0.1:8000/ask/', json={'ask': 'test'})    # JSON-запрос к серверу
    if transaction_plus >= res >= transaction_minus:  # Проверка на заданные отклонения
        return True
    else:
        return False


def get_deals_volume(investor, lieder_volume, lieder_balance_value):
    """Расчет множителя"""
    multiplier = investor['volume_multiplier']
    get_for_balance = True if investor['multiplier_type'] == 'Баланс' else False
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
#         if not mt.terminal_info().trade_allowed:
#             mt_wmcmd_experts = 32851
#             wm_command = 0x0111
#             ga_root = 2
#             terminal_handle = FindWindow('MetaQuotes::MetaTrader::5.00', None)
#             PostMessage(GetAncestor(terminal_handle, ga_root), wm_command, mt_wmcmd_experts, 0)
#     except AttributeError:
#         print(f'Невозможно подключиться к терминалу : {datetime.now()}')
#         exit()
#

def init_mt(init_data, need_login=False):
    """Инициализация терминала"""
    if mt.initialize(login=init_data['login'], server=init_data['server'], password=init_data['password'],
                     path=init_data['terminal_path'], timeout=TIMEOUT_INIT):
        print(f'INVESTOR account {init_data["login"]} : {datetime.now()}')
        if need_login:
            if not mt.login(login=init_data['login'], server=init_data['server'], password=init_data['password']):
                print('Login ERROR', mt.last_error())
    else:
        print(f'>>>>> account {init_data["login"]} : {datetime.now()} : ERROR', mt.last_error(),
              f': timeout = {TIMEOUT_INIT}')
        exit()


def open_position(symbol, deal_type, lot, sender_ticket, tp=0, sl=0):
    """Открытие позиции"""
    point = mt.symbol_info(symbol).point
    price = tp_in = sl_in = 0.0
    if deal_type == 0:  # BUY
        deal_type = mt.ORDER_TYPE_BUY
        price = mt.symbol_info_tick(symbol).ask
        if tp != 0:
            tp_in = price + tp * point
        if sl != 0:
            sl_in = price - sl * point
    elif deal_type == 1:  # SELL
        deal_type = mt.ORDER_TYPE_SELL
        price = mt.symbol_info_tick(symbol).bid
        if tp != 0:
            tp_in = price - tp * point
        if sl != 0:
            sl_in = price + sl * point
    request = {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": deal_type,
        "price": price,
        "sl": sl_in,
        "tp": tp_in,
        "deviation": DEVIATION,
        "magic": MAGIC,
        "comment": str(sender_ticket),
        "type_time": mt.ORDER_TIME_GTC,
        "type_filling": mt.ORDER_FILLING_RETURN,
    }
    result = mt.order_send(request)
    return result


def close_position(position):
    """Закрытие указанной позиции"""
    tick = mt.symbol_info_tick(position.symbol)
    request = {
        'action': mt.TRADE_ACTION_DEAL,
        'position': position.ticket,
        'symbol': position.symbol,
        'volume': position.volume,
        'type': mt.ORDER_TYPE_BUY if position.type == 1 else mt.ORDER_TYPE_SELL,
        'price': tick.ask if position.type == 1 else tick.bid,
        'deviation': DEVIATION,
        'magic:': MAGIC,
        'comment': 'CLOSED_BY_EXPERT',  # position.comment,
        'type_tim': mt.ORDER_TIME_GTC,
        'type_filing': mt.ORDER_FILLING_IOC
    }
    result = mt.order_send(request)
    return result


def get_investors_positions_count(investor):
    """Количество открытых позиций"""
    init_mt(init_data=investor)
    return mt.positions_total()


def force_close_all_positions(investor):
    """Принудительное закрытие всех позиций аккаунта"""
    init_mt(init_data=investor)
    positions = mt.positions_get()
    if len(positions) > 0:
        for position in positions:
            if position.magic == MAGIC:
                close_position(position)
    mt.shutdown()


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
async def execute_lieder(sleep_size=5):
    global lieder_balance, lieder_equity
    global lieder_positions
    global investor_accounts
    while True:
        investor_accounts = get_investors_list()
        init_mt(init_data=lieder_account)
        lieder_balance = mt.account_info().balance
        lieder_equity = mt.account_info().equity
        lieder_positions = mt.positions_get()
        mt.shutdown()
        if True:
            print(f'\nLIEDER {lieder_account["login"]} - {len(lieder_positions)} positions',
                  datetime.now().time())
            trading_event.set()
            await asyncio.sleep(sleep_size)


async def execute_investor(investor):
    init_mt(init_data=investor)
    global output_report
    output_report = []
    investor_positions = mt.positions_get()
    print(f' - {investor["email"]} [{investor["login"]}] - {len(investor_positions)} positions : {datetime.now()}')
    check_stop_limits(investor=investor)
    # enable_algotrading()
    for pos_lid in lieder_positions:
        inv_tp = get_pips_tp(pos_lid)
        inv_sl = get_pips_sl(pos_lid)
        if not is_position_exist_in_list(position=pos_lid, list_positions=investor_positions, check_for_comment=True):
            if checking_an_open_transaction(transaction_plus=investor['transaction_plus'],
                                            transaction_minus=investor['transaction_minus'],
                                            price_open=pos_lid.price_open, price_current=pos_lid.price_current,
                                            type_of_order=pos_lid.type):
                volume = 1.0\
                    if investor['change_multiplier'] == 'Нет' \
                    else get_deals_volume(investor, lieder_volume=pos_lid.volume,
                                          lieder_balance_value=lieder_balance
                                          if investor['multiplier_type'] == 'Баланс' else lieder_equity)
                print('-----------------VOLUME', volume)
                response = open_position(symbol=pos_lid.symbol, deal_type=pos_lid.type, lot=volume,
                                         sender_ticket=pos_lid.ticket, tp=inv_tp, sl=inv_sl)
                rpt = {'investor_id': investor_accounts.index(investor), 'code': response.retcode,
                       'message': send_retcodes[response.retcode][1]}
                output_report.append(rpt)
    close_positions_by_lieder(positions_lieder=lieder_positions, positions_investor=mt.positions_get())
    if len(output_report) > 0:
        print('    ', output_report)
    mt.shutdown()


async def task_manager():
    while True:
        await trading_event.wait()
        for _ in investor_accounts:
            event_loop.create_task(execute_investor(_))
        trading_event.clear()


if __name__ == '__main__':
    event_loop = asyncio.new_event_loop()
    event_loop.create_task(execute_lieder(sleep_size=1))
    event_loop.create_task(task_manager())
    event_loop.run_forever()
