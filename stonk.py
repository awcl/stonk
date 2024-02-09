import argparse, json, sys, http.client
from datetime import datetime, timezone, timedelta

def fetch_stock_data(symbol, duration):
    connection = http.client.HTTPSConnection("query1.finance.yahoo.com")
    url = f'/v8/finance/chart/{symbol}?interval=1d&range={duration}'
    try:
        connection.request("GET", url)
        response = connection.getresponse()
        data = json.loads(response.read().decode('utf-8'))
        if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
            raise ValueError('No data found for the specified symbol')
        return data['chart']['result'][0]
    except Exception as error:
        print(f'Error fetching data: {error}')
        sys.exit(1)
    finally:
        connection.close()

def plot_stock_prices(stock_data, duration, currency_symbol):
    buffer = 2
    max_content_length = 13
    max_column_length = max_content_length + buffer

    color_reset = '\033[0m'
    color_length = len(color_reset)

    def get_color(current, previous):
        if current < previous:
            return f"\033[91m↓ "
        elif current > previous:
            return f"\033[92m↑ "
        elif current == previous:
            return f"\033[93m- "

    def adjust_width(cell, width):
        whitespace = ' ' * (width - len(cell) + cell.count('\033[') * color_length - 1)
        return f"{cell}{whitespace}"

    def is_market_open(date):
        current_time = datetime.now(timezone.utc)
        est_time = current_time.astimezone(timezone(-timedelta(hours=5)))
        market_open_time = est_time.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close_time = est_time.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open_time <= est_time <= market_close_time and est_time.weekday() < 5 and date.date() == est_time.date()

    if 'timestamp' not in stock_data or 'indicators' not in stock_data or 'quote' not in stock_data['indicators'] or not stock_data['indicators']['quote']:
        print("Error: No stock data available.")
        return

    quote_data = stock_data['indicators']['quote'][0]

    dates = [datetime.fromtimestamp(date, timezone.utc) for date in stock_data['timestamp']]
    data_rows = sorted(zip(dates, quote_data['open'], quote_data['high'], quote_data['low'], quote_data['close'], quote_data['volume']))

    header_separator = f"+{'-' * max_column_length}+{'-' * max_column_length}+{'-' * max_column_length}+{'-' * max_column_length}+{'-' * max_column_length}+{'-' * max_column_length}+"

    header_row = f"| {'YYYY-MM-DD':<{max_content_length}} | {'Open':<{max_content_length}} | {'High':<{max_content_length}} | {'Low':<{max_content_length}} | {'Close':<{max_content_length}} | {'Volume':<{max_content_length}} |"
    separator_row = header_separator

    data_to_print = []
    prev_close = None
    prev_volume = None

    for i, (date, open_price, high, low, close, volume) in enumerate(data_rows):
        date_str = date.strftime('%Y-%m-%d')
        open_str = f"  {currency_symbol} {open_price:.2f}"
        high_str = f"  {currency_symbol} {high:.2f}"
        low_str = f"  {currency_symbol} {low:.2f}"
        close_str = f"  {currency_symbol} {close:.2f}" if not is_market_open(date) else "    Open"
        volume_str = f"  {volume}"

        if prev_close is not None:
            prev_open, prev_high, prev_low, prev_close, prev_volume = data_rows[i - 1][1:6]
            open_color = get_color(open_price, prev_open)
            high_color = get_color(high, prev_high)
            low_color = get_color(low, prev_low)
            close_color = '\033[33m' if is_market_open(date) else get_color(close, prev_close)
            volume_color = get_color(volume, prev_volume)

            open_str = adjust_width(f"{open_color}{open_str[2:]}{color_reset}", max_column_length)
            high_str = adjust_width(f"{high_color}{high_str[2:]}{color_reset}", max_column_length)
            low_str = adjust_width(f"{low_color}{low_str[2:]}{color_reset}", max_column_length)
            close_str = adjust_width(f"{close_color}{close_str[2:]}{color_reset}", max_column_length)
            volume_str = adjust_width(f"{volume_color}{volume_str[2:]}{color_reset}", max_column_length)

        prev_close = close
        prev_volume = volume

        data_to_print.append(f"| {date_str:<{max_content_length}} | {open_str:<{max_content_length}} | {high_str:<{max_content_length}} | {low_str:<{max_content_length}} | {close_str:<{max_content_length}} | {volume_str:<{max_content_length}} |")

    print(header_separator)
    print(header_row)
    print(header_separator)

    for row in reversed(data_to_print):
        print(row)

    print(header_separator)

def main():
    parser = argparse.ArgumentParser(description='Fetch and display stock price data for a symbol')
    parser.add_argument('symbol', type=str, nargs='?', default='SAVE', help='Stock Symbol (default: SAVE)')
    parser.add_argument('duration', type=str, nargs='?', default='5d', choices=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"], help='Duration (default: 5d)')
    args = parser.parse_args()

    currency_symbols = {"AED": "د.إ", "AFN": "؋", "ALL": "L", "AMD": "֏", "ANG": "ƒ", "AOA": "Kz", "ARS": "$", "AUD": "$", "AWG": "ƒ", "AZN": "₼", "BAM": "KM", "BBD": "$", "BDT": "৳", "BGN": "лв", "BHD": "ب.د", "BIF": "FBu", "BMD": "$", "BND": "$", "BOB": "Bs.", "BRL": "R$", "BSD": "$", "BTN": "Nu.", "BWP": "P", "BYN": "Br", "BYR": "Br", "BZD": "$", "CAD": "$", "CDF": "FC", "CHF": "CHF", "CLP": "$", "CNY": "¥", "COP": "$", "CRC": "₡", "CUP": "₱", "CVE": "Esc", "CZK": "Kč", "DJF": "Fdj", "DKK": "kr", "DOP": "RD$", "DZD": "دج", "EGP": "E£", "ERN": "Nfk", "ETB": "Br", "EUR": "€", "FJD": "$", "FKP": "£", "FOK": "kr", "GBP": "£", "GEL": "₾", "GGP": "£", "GHS": "₵", "GIP": "£", "GMD": "D", "GNF": "FG", "GTQ": "Q", "GYD": "$", "HKD": "HK$", "HNL": "L", "HRK": "kn", "HTG": "G", "HUF": "Ft", "IDR": "Rp", "ILS": "₪", "IMP": "£", "INR": "₹", "IQD": "ع.د", "IRR": "﷼", "ISK": "kr", "JEP": "£", "JMD": "J$", "JOD": "د.ا", "JPY": "¥", "KES": "KSh", "KGS": "лв", "KHR": "៛", "KID": "$", "KMF": "CF", "KRW": "₩", "KWD": "د.ك", "KYD": "$", "KZT": "₸", "LAK": "₭", "LBP": "ل.ل", "LKR": "Rs", "LRD": "$", "LSL": "M", "LYD": "ل.د", "MAD": "د.م.", "MDL": "L", "MGA": "Ar", "MKD": "ден", "MMK": "K", "MNT": "₮", "MOP": "MOP$", "MRU": "UM", "MUR": "Rs", "MVR": "Rf", "MWK": "MK", "MXN": "$", "MYR": "RM", "MZN": "MT", "NAD": "$", "NGN": "₦", "NIO": "C$", "NOK": "kr", "NPR": "नेरू", "NZD": "$", "OMR": "ر.ع.", "PAB": "B/.", "PEN": "S/.", "PGK": "K", "PHP": "₱", "PKR": "₨", "PLN": "zł", "PRB": "р.", "PYG": "₲", "QAR": "ر.ق", "RON": "lei", "RSD": "дин", "RUB": "₽", "RWF": "FRw", "SAR": "ر.س", "SBD": "$", "SCR": "Rs", "SDG": "ج.س.", "SEK": "kr", "SGD": "$", "SHP": "£", "SLL": "Le", "SOS": "Sh.", "SRD": "$", "SSP": "£", "STN": "Db", "SYP": "£", "SZL": "E", "THB": "฿", "TJS": "ЅМ", "TMT": "T", "TND": "د.ت", "TOP": "T$", "TRY": "₺", "TTD": "TT$", "TVD": "$", "TWD": "NT$", "TZS": "Sh", "UAH": "₴", "UGX": "USh", "USD": "$", "UYU": "$U", "UZS": "soʻm", "VES": "Bs.", "VND": "₫", "VUV": "VT", "WST": "T", "XAF": "FCFA", "XCD": "$", "XDR": "SDR", "XOF": "CFA", "XPF": "₣", "YER": "﷼", "ZAR": "R", "ZMW": "ZK"}

    currency_symbol = "$"

    try:
        stock_data = fetch_stock_data(args.symbol, args.duration)
        currency_symbol = currency_symbols[stock_data["meta"]["currency"]]
        print(f'Stock Symbol: {args.symbol.upper()} | Current Price: {currency_symbol} {stock_data["meta"]["regularMarketPrice"]:.2f}')
        plot_stock_prices(stock_data, args.duration, currency_symbol)
    except Exception as error:
        print(f'Error: {error}')
        sys.exit(1)

if __name__ == "__main__":
    main()
