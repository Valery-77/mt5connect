import MetaTrader5 as mt

MT1_PATH = r'C:\Program Files\MetaTrader 5\terminal64.exe'
MT2_PATH = r'C:\Program Files\MetaTrader 5_2\terminal64.exe'
MT1_LOGIN = 805060
MT2_LOGIN = 805061
MT1_PASS = 'bsccvba1'
MT2_PASS = 'weax5szp'
MT1_SERVER = 'OpenInvestments-Demo'
MT2_SERVER = 'OpenInvestments-Demo'


def init_mt(login, server, password, path, need_login=False):
    if mt.initialize(login=login, server=server, password=password, path=path):
        if need_login:
            if not mt.login(login=login, password=password, server=server):
                print('Login NO', mt.last_error())
    else:
        print("Init NO", mt.last_error())


def send_position(symbol, deal_type, lot, sender_ticket, magic=0, tp=0, sl=0, deviation=20):
    point = mt.symbol_info(symbol).point

    price = tp_in = sl_in = 0.0
    if deal_type == 1:                                          # BUY
        deal_type = mt.ORDER_TYPE_BUY
        price = mt.symbol_info_tick(symbol).ask
        if tp != 0:
            tp_in = price + tp * point
        if sl != 0:
            sl_in = price - sl * point
    elif deal_type == 0:                                        # SELL
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
        "type": deal_type,  # mt.ORDER_TYPE_BUY,
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
    init_mt(MT2_LOGIN, MT2_SERVER, MT2_PASS, MT2_PATH)
    positions_receiver = mt.positions_get()
    for pos_snd in positions_sender:
        position_s = pos_snd._asdict()
        skip_this = False
        for pos_rec in positions_receiver:
            position_r = pos_rec._asdict()
            if position_s['ticket'] == int(position_r['comment']):
                skip_this = True
                break
        if not skip_this:
            res = send_position(symbol=position_s['symbol'], deal_type=position_s['type'], lot=position_s['volume'],
                                sender_ticket=position_s['ticket'], magic=position_s['magic'], tp=0, sl=0)
            print(res)
        else:
            print('Position with ticket:', position_s['ticket'], 'exist in receiver')
else:
    print('Nothing to add')
mt.shutdown()
