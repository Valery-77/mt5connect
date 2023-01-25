import MetaTrader5 as mt
from datetime import datetime
from math import fabs, floor
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

MT1_PATH = r'C:\Program Files\MetaTrader 5\terminal64.exe'
MT2_PATH = r'C:\Program Files\MetaTrader 5_2\terminal64.exe'
MT1_LOGIN = 805060
MT2_LOGIN = 805061
MT1_PASS = 'bsccvba1'
MT2_PASS = 'weax5szp'
MT1_SERVER = 'OpenInvestments-Demo'
MT2_SERVER = 'OpenInvestments-Demo'


def enable_algotrading():
    if not mt.terminal_info()._asdict()['trade_allowed']:
        mt_wmcmd_experts = 32851
        wm_command = 0x0111
        ga_root = 2
        terminal_handle = FindWindow('MetaQuotes::MetaTrader::5.00', None)
        PostMessage(GetAncestor(terminal_handle, ga_root), wm_command, mt_wmcmd_experts, 0)


def init_mt(login, server, password, path, need_login=False):
    if mt.initialize(login=login, server=server, password=password, path=path):
        print(f'Initialize account {login} : {datetime.now()}')
        if need_login:
            if not mt.login(login=login, password=password, server=server):
                print('Login NO', mt.last_error())
    else:
        print(f'Initialize account {login} : {datetime.now()} : ERROR >', mt.last_error())


def send_position(symbol, deal_type, lot, sender_ticket, magic=0, tp=0, sl=0, deviation=20):
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
        "deviation": deviation,
        "magic": magic,
        "comment": str(sender_ticket),
        "type_time": mt.ORDER_TIME_GTC,
        "type_filling": mt.ORDER_FILLING_RETURN,
    }

    result = mt.order_send(request)
    return result


init_mt(MT1_LOGIN, MT1_SERVER, MT1_PASS, MT1_PATH)
positions_sender = mt.positions_get()
if len(positions_sender) > 0:
    print(f'    Account {MT1_LOGIN} have {len(positions_sender)} opened positions')
    init_mt(MT2_LOGIN, MT2_SERVER, MT2_PASS, MT2_PATH)
    enable_algotrading()
    positions_receiver = mt.positions_get()
    for pos_snd in positions_sender:
        position_s = pos_snd._asdict()
        tp_p = sl_p = 0
        if position_s["tp"] > 0:
            tp_p = floor(fabs(position_s['price_open'] - position_s['tp']) / mt.symbol_info(position_s['symbol']).point)
        if position_s["sl"] > 0:
            sl_p = floor(fabs(position_s['price_open'] - position_s['sl']) / mt.symbol_info(position_s['symbol']).point)
        report = f'    In account {MT1_LOGIN} position {position_s["ticket"]} / {position_s["symbol"]} ' \
                 f'/ lot: {position_s["volume"]} / open price: {position_s["price_open"]} / ' \
                 f'tp: {position_s["tp"]} ({tp_p} pips) / sl: {position_s["sl"]} ({sl_p} pips) '
        skip_this = False
        existed_position = 0
        for pos_rec in positions_receiver:
            position_r = pos_rec._asdict()
            try:
                if position_s['ticket'] == int(position_r['comment']):
                    existed_position = position_r
                    skip_this = True
                    break
            except ValueError:
                continue
        if not skip_this:
            res = send_position(symbol=position_s['symbol'], deal_type=position_s['type'], lot=position_s['volume'],
                                sender_ticket=position_s['ticket'], magic=position_s['magic'], tp=tp_p, sl=sl_p)
            response = res._asdict()
            rsp_req = response["request"]._asdict()
            tp_p = sl_p = 0
            if rsp_req["tp"] > 0:
                tp_p = floor(fabs(response['price'] - rsp_req['tp']) / mt.symbol_info(rsp_req['symbol']).point)
            if rsp_req["sl"] > 0:
                sl_p = floor(fabs(response['price'] - rsp_req['sl']) / mt.symbol_info(rsp_req['symbol']).point)
            print(report, f'\n\t\t->\t {send_retcodes[response["retcode"]][1]}',
                  f'in account {MT2_LOGIN} position {response["order"]} /',
                  f'{rsp_req["symbol"]} / lot: {rsp_req["volume"]} / open price: {response["price"]} /',
                  f'tp: {rsp_req["tp"]} ({tp_p} pips) / sl: {rsp_req["sl"]} ({sl_p} pips) ')
        else:
            tp_p = sl_p = 0
            if existed_position["tp"] > 0:
                tp_p = floor(
                    fabs(existed_position['price_open'] - existed_position['tp']) / mt.symbol_info(
                        position_s['symbol']).point)
            if existed_position["sl"] > 0:
                sl_p = floor(
                    fabs(existed_position['price_open'] - existed_position['sl']) / mt.symbol_info(
                        position_s['symbol']).point)
            print(report, f'\n\t\t->\talready exist : in account {MT2_LOGIN} position {existed_position["ticket"]} /',
                  f'{existed_position["symbol"]} / lot: {existed_position["volume"]} /',
                  f'open price: {existed_position["price_open"]} /',
                  f'tp: {existed_position["tp"]} ({tp_p} pips) / sl: {existed_position["sl"]} ({sl_p} pips) ')
else:
    print(f'    Account {MT1_LOGIN} have {len(positions_sender)} opened positions')
mt.shutdown()
