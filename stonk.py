import argparse, json, sys, http.client
from datetime import datetime, timezone

def fetch_stock_data(symbol, duration):
    conn = http.client.HTTPSConnection("query1.finance.yahoo.com")
    url = f'/v8/finance/chart/{symbol}?interval=1d&range={duration}'
    try:
        conn.request("GET", url)
        response = conn.getresponse()
        data = json.loads(response.read().decode('utf-8'))
        if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
            raise ValueError('No data found for the specified symbol')
        return data['chart']['result'][0]
    except Exception as e:
        print(f'Error fetching data: {e}')
        sys.exit(1)
    finally:
        conn.close()

def plot_stock_prices(stock_data, duration):
    if 'timestamp' not in stock_data or 'indicators' not in stock_data or 'quote' not in stock_data['indicators'] or not stock_data['indicators']['quote']:
        print("Error: No stock data available.")
        return

    quote_data = stock_data['indicators']['quote'][0]
    if 'timestamp' not in stock_data:
        print("Error: No timestamp data available.")
        return

    dates = [datetime.fromtimestamp(date, timezone.utc) for date in stock_data['timestamp']]
    currency_code = stock_data['meta']['currency']
    currency_symbols = {"AED":"د.إ","AFN":"؋","ALL":"L","AMD":"֏","ANG":"ƒ","AOA":"Kz","ARS":"$","AUD":"$","AWG":"ƒ","AZN":"₼","BAM":"KM","BBD":"$","BDT":"৳","BGN":"лв","BHD":"ب.د","BIF":"FBu","BMD":"$","BND":"$","BOB":"Bs.","BRL":"R$","BSD":"$","BTN":"Nu.","BWP":"P","BYN":"Br","BYR":"Br","BZD":"$","CAD":"$","CDF":"FC","CHF":"CHF","CLP":"$","CNY":"¥","COP":"$","CRC":"₡","CUP":"₱","CVE":"Esc","CZK":"Kč","DJF":"Fdj","DKK":"kr","DOP":"RD$","DZD":"دج","EGP":"E£","ERN":"Nfk","ETB":"Br","EUR":"€","FJD":"$","FKP":"£","FOK":"kr","GBP":"£","GEL":"₾","GGP":"£","GHS":"₵","GIP":"£","GMD":"D","GNF":"FG","GTQ":"Q","GYD":"$","HKD":"HK$","HNL":"L","HRK":"kn","HTG":"G","HUF":"Ft","IDR":"Rp","ILS":"₪","IMP":"£","INR":"₹","IQD":"ع.د","IRR":"﷼","ISK":"kr","JEP":"£","JMD":"J$","JOD":"د.ا","JPY":"¥","KES":"KSh","KGS":"лв","KHR":"៛","KID":"$","KMF":"CF","KRW":"₩","KWD":"د.ك","KYD":"$","KZT":"₸","LAK":"₭","LBP":"ل.ل","LKR":"Rs","LRD":"$","LSL":"M","LYD":"ل.د","MAD":"د.م.","MDL":"L","MGA":"Ar","MKD":"ден","MMK":"K","MNT":"₮","MOP":"MOP$","MRU":"UM","MUR":"Rs","MVR":"Rf","MWK":"MK","MXN":"$","MYR":"RM","MZN":"MT","NAD":"$","NGN":"₦","NIO":"C$","NOK":"kr","NPR":"नेरू","NZD":"$","OMR":"ر.ع.","PAB":"B/.","PEN":"S/.","PGK":"K","PHP":"₱","PKR":"₨","PLN":"zł","PRB":"р.","PYG":"₲","QAR":"ر.ق","RON":"lei","RSD":"дин","RUB":"₽","RWF":"FRw","SAR":"ر.س","SBD":"$","SCR":"Rs","SDG":"ج.س.","SEK":"kr","SGD":"$","SHP":"£","SLL":"Le","SOS":"Sh.","SRD":"$","SSP":"£","STN":"Db","SYP":"£","SZL":"E","THB":"฿","TJS":"ЅМ","TMT":"T","TND":"د.ت","TOP":"T$","TRY":"₺","TTD":"TT$","TVD":"$","TWD":"NT$","TZS":"Sh","UAH":"₴","UGX":"USh","USD":"$","UYU":"$U","UZS":"soʻm","VES":"Bs.","VND":"₫","VUV":"VT","WST":"T","XAF":"FCFA","XCD":"$","XDR":"SDR","XOF":"CFA","XPF":"₣","YER":"﷼","ZAR":"R","ZMW":"ZK"}
    currency_symbol = currency_symbols.get(currency_code, currency_code)

    data_rows = sorted(zip(dates, quote_data['open'], quote_data['high'], quote_data['low'], quote_data['close'], quote_data['volume']), reverse=True)

    max_date_width = max(len(date.strftime('%Y-%m-%d')) for date, *_ in data_rows)
    max_price_width = max(max(len(f"{currency_symbol} {price:.2f}") for price in (open_, high, low, close)) for _, open_, high, low, close, _ in data_rows)
    max_volume_width = max(len(str(volume)) for _, _, _, _, _, volume in data_rows)

    date_column_width = max_date_width + 2
    price_column_width = max_price_width + len(currency_symbol) + 1
    volume_column_width = max_volume_width + 2

    price_column_width_with_symbol = price_column_width + len(f"{currency_symbol} ")
    header_separator = f"+{'-' * date_column_width}+{'-' * price_column_width_with_symbol}+{'-' * price_column_width_with_symbol}+{'-' * price_column_width_with_symbol}+{'-' * price_column_width_with_symbol}+{'-' * (volume_column_width)}+"

    print(header_separator)
    print(f"| {'YYYY-MM-DD':<{max_date_width}} | {'Open':<{price_column_width}} | {'High':<{price_column_width}} | {'Low':<{price_column_width}} | {'Close':<{price_column_width}} | {'Volume':<{max_volume_width}} |")
    print(header_separator)

    for date, open_, high, low, close, volume in data_rows:
        date_str = date.strftime('%Y-%m-%d')
        open_str = f"{currency_symbol} {open_:.2f}"
        high_str = f"{currency_symbol} {high:.2f}"
        low_str = f"{currency_symbol} {low:.2f}"
        close_str = f"{currency_symbol} {close:.2f}"
        print(f"| {date_str:<{max_date_width}} | {open_str:<{price_column_width}} | {high_str:<{price_column_width}} | {low_str:<{price_column_width}} | {close_str:<{price_column_width}} | {volume:<{max_volume_width}} |")

    print(header_separator)

def main():
    parser = argparse.ArgumentParser(description='Fetch and display stock price data for a symbol')
    parser.add_argument('symbol', type=str, nargs='?', default='SAVE', help='Stock Symbol (e.g., SAVE)')
    parser.add_argument('duration', type=str, nargs='?', default='5d', choices=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"], help='Duration (default: 5d)')
    args = parser.parse_args()

    try:
        stock_data = fetch_stock_data(args.symbol, args.duration)
        print(f'Stock Symbol: {args.symbol.upper()}')
        plot_stock_prices(stock_data, args.duration)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()
