import ftx
import requests
import config
from threading import Timer

api_endpoint = "https://ftx.com/api/markets/RAY-PERP/orderbook?depth=100"

client = ftx.FtxClient(api_key=config.API_KEY, api_secret=config.API_SECRET)

order_id_bid = 0
order_id_ask = 0
empty_bid = False
empty_ask = False
current_price_bid = 0
current_price_ask = 0


def process(json_data, count):
    global client
    global current_price_bid
    global current_price_ask
    global order_id_bid
    global order_id_ask
    global empty_bid
    global empty_ask

    min_k = 0
    max_k = 0
    k = 0
    k_target = 0
    max_target_found = False
    min_price_target_found = False
    min_price_target = 0
    min_interval = 0.1
    UP_BID = 15000
    UP_ASK = 15000
    VOL_BID = 1
    VOL_ASK = 1
    min_price = 0
    print('----------------------------------------------------------------------------------')

    best_bid = json_data['result']['bids'][0][0]

    best_ask = json_data['result']['asks'][0][0]

    for item in json_data['result']['bids']:

        k = k + item[1]

        if (k > 2000) and (not max_target_found):
            max_price = item[0]
            min_k = k
            max_target_found = True

        if k < UP_BID:
            min_price = item[0]
            max_k = k
        elif not min_price_target_found:
            min_price_target = item[0]
            k_target = k
            min_price_target_found = True

    print('BID ' + str(count).ljust(6) + (str(min_k) + ' (' + str(max_price) + ')').ljust(18) + ' <-> ' + (str(max_k) + ' (' + str(min_price) + ')').ljust(18) + ': Cur = ' + str(current_price_bid).ljust(7) + ' [' + str(min_price_target).ljust(7) + '] MaxVol=' + str(k_target))

    print(order_id_bid)

    if (not empty_bid) and (count == 1):
        client.cancel_order(order_id_bid)
        empty_bid = True
    else:
        if empty_bid and (best_bid - current_price_bid > min_interval):
            result = client.place_order('RAY-PERP', 'buy', min_price_target + 0.0001, VOL_BID)
            order_id_bid = result['id']
            print('          *** Bid Place order ' + str(order_id_bid) + ' ***')
            current_price_bid = min_price_target + 0.0001
            empty_bid = False
        elif (not empty_bid) and ((current_price_bid < min_price) or (current_price_bid > max_price) or (min_price >= max_price) or (best_bid - current_price_bid <= min_interval)):
            client.cancel_order(order_id_bid)
            print('          Bid order ' + str(order_id_bid) + ' CANCELED')
            empty_bid = True
            if current_price_bid < min_price:
                print('          current_price_bid < min_price')
            if best_bid - current_price_bid <= min_interval:
                print('          best_bid - current_price_bid <= min_interval')

    min_k = 0
    max_k = 0
    k = 0
    k_target = 0
    min_price_target_found = False
    max_price_target_found = False
    max_price_target = 0

    for item in json_data['result']['asks']:

        k = k + item[1]

        if (k > 2000) and (not min_price_target_found):
            min_price = item[0]
            min_k = k
            min_price_target_found = True

        if k < UP_ASK:
            max_price = item[0]
            max_k = k
        elif not max_price_target_found:
            max_price_target = item[0]
            k_target = k
            max_price_target_found = True

    print('ASK ' + str(count).ljust(6) + (str(min_k) + ' (' + str(min_price) + ')').ljust(18) + ' <-> ' + (str(max_k) + ' (' + str(max_price) + ')').ljust(18) + ': Cur = ' + str(current_price_ask).ljust(7) + ' [' + str(max_price_target).ljust(7) + '] MaxVol=' + str(k_target))

    if (not empty_ask) and (count == 1):
        client.cancel_order(order_id_ask)
        empty_ask = True
    else:
        if empty_ask and (current_price_ask - best_ask > min_interval):
            result = client.place_order('RAY-PERP', 'sell', max_price_target - 0.0001, VOL_ASK)
            order_id_ask = result['id']
            print('          *** Ask Place order ' + str(order_id_ask) + ' ***')
            current_price_ask = max_price_target - 0.0001
            empty_ask = False
        elif (not empty_ask) and ((current_price_ask < min_price) or (current_price_ask > max_price) or (min_price >= max_price) or (current_price_ask - best_ask <= min_interval)):
            client.cancel_order(order_id_ask)
            print('          Ask order ' + str(order_id_ask) + ' CANCELED')
            empty_ask = True
            if current_price_ask > max_price:
                print('          current_price_ask > max_price')
            if current_price_ask - best_ask <= min_interval:
                print('          current_price_ask - best_ask <= min_interval')


def main():

    count = 0

    global current_price_bid
    global current_price_ask
    global client
    global order_id_bid
    global order_id_ask
    global empty_bid
    global empty_ask

    result = client.place_order('RAY-PERP', 'buy', 1, 1)
    result_ask = client.place_order('RAY-PERP', 'sell', 50, 1)
    order_id_bid = result['id']
    order_id_ask = result_ask['id']

    current_price_ask = 9999

    empty_bid = False
    empty_ask = False

    while 1:
        count += 1
        json_data = requests.get(api_endpoint).json()

        process(json_data, count)


if __name__ == '__main__':
    main()
