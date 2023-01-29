import MetaTrader5 as mt
from datetime import datetime
from math import fabs
from win32gui import PostMessage, GetAncestor, FindWindow

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

TIMEOUT_INIT = 6000  # DEFAULT = 60_000 millisecond
MT1_PATH = r'C:\Program Files\MetaTrader 5\terminal64.exe'
MT2_PATH = r'C:\Program Files\MetaTrader 5_2\terminal64.exe'
MT1_LOGIN = 805060
MT2_LOGIN = 805061
MT1_PASS = 'bsccvba1'
MT2_PASS = 'weax5szp'
MT1_SERVER = 'OpenInvestments-Demo'
MT2_SERVER = 'OpenInvestments-Demo'

MAGIC = 0
DEVIATION = 20
START_DATE = datetime(2020, 1, 1)

input_investment_size = 1000
input_volume_multiplier = 1.0
input_check_stop_limit_in_percent = True
input_stop_limit = 20


def get_pips_tp(position):
    result = 0.0
    if position.tp > 0:
        result = round(fabs(position.price_open - position.tp) / mt.symbol_info(position.symbol).point)
    return result


def get_pips_sl(position):
    result = 0.0
    if position.sl > 0:
        result = round(fabs(position.price_open - position.sl) / mt.symbol_info(position.symbol).point)
    return result


def get_positions_profit(positions: list):
    result = 0
    own_positions = []
    try:
        if len(positions) > 0:
            for pos in positions:
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


# stop limits
def check_stop_limits(start_balance=input_investment_size, limit_size=input_stop_limit, calc_limit_in_percent=True):
    # CHECK HISTORY POSITIONS
    date_from = START_DATE
    date_to = datetime.now()
    history_positions = mt.history_deals_get(date_from, date_to)
    history_profit = get_positions_profit(history_positions)
    # CHECK CURRENT POSITIONS
    active_positions = mt.positions_get()
    current_profit = get_positions_profit(active_positions)
    # SUMM TOTAL PROFIT
    if not history_profit or not current_profit:
        return
    close_all_positions = False
    total_profit = history_profit + current_profit
    print('\t', 'Прибыль' if total_profit >= 0 else 'Убыток', 'торговли c', START_DATE, ':', round(total_profit, 2),
          'USD')
    # CHECK LOST SIZE FOR CLOSE ALL
    if total_profit < 0:
        if calc_limit_in_percent:
            current_percent = fabs(total_profit / start_balance) * 100
            if current_percent >= limit_size:
                close_all_positions = True
        else:
            if fabs(total_profit) >= limit_size:
                close_all_positions = True
        # CLOSE ALL POSITIONS
        if close_all_positions:
            print('     Закрытие всех позиций по условию убытка')
            for act_pos in active_positions:
                if act_pos.magic == MAGIC:
                    close_position(act_pos)
            exit()

# simple multiplier
def get_deals_volume(volume=1.0, multiplier=input_volume_multiplier):
    return volume * multiplier


def enable_algotrading():
    try:
        if not mt.terminal_info()._asdict()['trade_allowed']:
            mt_wmcmd_experts = 32851
            wm_command = 0x0111
            ga_root = 2
            terminal_handle = FindWindow('MetaQuotes::MetaTrader::5.00', None)
            PostMessage(GetAncestor(terminal_handle, ga_root), wm_command, mt_wmcmd_experts, 0)
    except AttributeError:
        print(f'Невозможно подключиться к терминалу : {datetime.now()}')
        exit()


def init_mt(login, server, password, path, need_login=False):  # timeout default = 60_000
    if mt.initialize(login=login, server=server, password=password, path=path, timeout=TIMEOUT_INIT):
        print(f'Initialize account {login} : {datetime.now()}')
        if need_login:
            if not mt.login(login=login, password=password, server=server):
                print('Login NO', mt.last_error())
    else:
        print(f'Initialize account {login} : {datetime.now()} : ERROR', mt.last_error(), f': timeout = {TIMEOUT_INIT}')
        exit()


def open_position(symbol, deal_type, lot, sender_ticket, tp=0, sl=0):
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
    tick = mt.symbol_info_tick(position.symbol)
    request = {
        'action': mt.TRADE_ACTION_DEAL,
        'position': position.ticket,
        'symbol': position.symbol,
        'volume': position.volume,
        'type': mt.ORDER_TYPE_BUY if position.type == 1 else mt.ORDER_TYPE_SELL,
        'price': tick.ask if position.type == 1 else tick.bid,
        'deviation': DEVIATION,
        'magic:': position.magic,
        'comment': '',
        'type_tim': mt.ORDER_TIME_GTC,
        'type_filing': mt.ORDER_FILLING_IOC
    }
    result = mt.order_send(request)
    return result


def main():
    init_mt(MT1_LOGIN, MT1_SERVER, MT1_PASS, MT1_PATH)
    positions_sender = mt.positions_get()
    if len(positions_sender) > 0:
        print(f'    Account {MT1_LOGIN} have {len(positions_sender)} opened positions')
        init_mt(MT2_LOGIN, MT2_SERVER, MT2_PASS, MT2_PATH)
        check_stop_limits(calc_limit_in_percent=input_check_stop_limit_in_percent)
        enable_algotrading()
        positions_receiver = mt.positions_get()
        for pos_snd in positions_sender:
            sender_tp = get_pips_tp(pos_snd)
            sender_sl = get_pips_sl(pos_snd)
            report = f'    In account {MT1_LOGIN} position {pos_snd.ticket} / {pos_snd.symbol} ' \
                     f'/ lot: {pos_snd.volume} / open price: {pos_snd.price_open} / ' \
                     f'tp: {pos_snd.tp} ({sender_tp} pips) / sl: {pos_snd.sl} ({sender_sl} pips) '
            position_exist = False
            existed_position = 0
            for pos_rec in positions_receiver:
                try:
                    if pos_snd.ticket == int(pos_rec.comment):
                        existed_position = pos_rec
                        position_exist = True
                        break
                except ValueError:
                    continue
            if not position_exist:  # POSITION NOT EXIST
                res = open_position(symbol=pos_snd.symbol, deal_type=pos_snd.type,
                                    lot=get_deals_volume(pos_snd.volume, input_volume_multiplier),
                                    sender_ticket=pos_snd.ticket, tp=sender_tp, sl=sender_sl)
                response = res._asdict()
                rsp_req = response["request"]._asdict()
                receiver_tp = receiver_sl = 0
                if rsp_req["tp"] > 0:
                    receiver_tp = round(
                        fabs(response['price'] - rsp_req['tp']) / mt.symbol_info(rsp_req['symbol']).point)
                if rsp_req["sl"] > 0:
                    receiver_sl = round(
                        fabs(response['price'] - rsp_req['sl']) / mt.symbol_info(rsp_req['symbol']).point)
                print(report, f'\n\t\t->\t {send_retcodes[response["retcode"]][1]}',
                      f'in account {MT2_LOGIN} position {response["order"]} /',
                      f'{rsp_req["symbol"]} / lot: {rsp_req["volume"]} / open price: {response["price"]} /',
                      f'tp: {rsp_req["tp"]} ({receiver_tp} pips) / sl: {rsp_req["sl"]} ({receiver_sl} pips) ')
            else:  # POSITION ALREADY EXIST
                receiver_tp = get_pips_tp(existed_position)
                receiver_sl = get_pips_sl(existed_position)
                print(report,
                      f'\n\t\t->\t already exist : in account {MT2_LOGIN} position {existed_position.ticket} /',
                      f'{existed_position.symbol} / lot: {existed_position.volume} /',
                      f'open price: {existed_position.price_open} /',
                      f'tp: {existed_position.tp} ({receiver_tp} pips) / sl: {existed_position.sl} ({receiver_sl} pips)')
    else:
        print(f'    Account {MT1_LOGIN} no have opened positions')
    mt.shutdown()


main()
