import os
import ssl
import json
import sqlite3
from dotenv import load_dotenv
from litellm import completion
import urllib.request, urllib.parse, urllib.error

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
x_rapidapi_key = os.getenv("X_RAPIDAPI_KEY")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(base_dir,'memory.db'))
cur = conn.cursor()

def brain():
    cur.execute('''CREATE TABLE IF NOT EXISTS Brain(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    content TEXT,
    date TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    return None

def remember(limit: int=20):
    cur.execute('''SELECT role, content, date FROM Brain ORDER BY id DESC LIMIT ? ''', (limit,))
    rows = cur.fetchall()
    return [{'role': row[0], 'content': row[1]} for row in reversed(rows)]

def learn(role, content):
    cur.execute('''INSERT INTO Brain (role, content) VALUES (?,?)''', (role, content))
    conn.commit()
    return None

def generate_response(messages: list[dict]) -> str:
    response = completion(model = 'anthropic/claude-sonnet-4-6',
                          messages = messages,
                          max_tokens = 1300)
    return response.choices[0].message.content

def parse_terminate(response: str) -> str|None:
    try:
        if '```terminate' in response:
            json_string = response.split('```terminate')[1].split('```')[0]
            data = json.loads(json_string)
            return data.get('Terminate', 'Goodbye!')
    except (IndexError, json.JSONDecodeError):
        pass
    return None

def parse_action(response: str) -> dict:
    print('  [🔍 Consultando API...]\n')
    try:
        if '```action' in response:
            json_string = response.split('```action')[1].split('```')[0]
        else:
            json_string = response
        data = json.loads(json_string)
        tool_name = data.get('tool_name', None)
        args = data.get('args', None)
        if tool_name is None or args is None:
            return {'tool_name': 'error', 'args': {'message':'Invalid response format. Missing "tool_name" or "args".'}}
        return {'tool_name': tool_name, 'args': args}
    except(IndexError, json.JSONDecodeError):
        return {'tool_name': 'error', 'args': {'message': 'Invalid JSON Format.'}}

def connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period):
    try:
        headers = {
        "x-rapidapi-key": x_rapidapi_key,
        "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "application/json",
        }

        if endpoint == 'market_tickers':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v2/markets/tickers"
        elif endpoint == 'search':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/search"
        elif endpoint == 'market_quotes_realtime':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/quote"
        elif endpoint == 'market_quotes_snapshots':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/stock/quotes"
        elif endpoint == 'market_screener':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/screener"
        elif endpoint == 'insider_trades':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/insider-trades"
        elif endpoint == 'market_news_v2':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v2/markets/news"
        elif endpoint == 'market_news_v1':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/news"
        elif endpoint == 'stock_history_v2':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v2/markets/stock/history"
        elif endpoint == 'stock_history_v1':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/stock/history"
        elif endpoint == 'calendar_earnings':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/calendar/earnings"
        elif endpoint == 'calendar_dividends':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/calendar/dividends"
        elif endpoint == 'calendar_economic_events':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/calendar/economic_events"
        elif endpoint == 'calendar_public_offerings':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/calendar/public_offerings"
        elif endpoint == 'calendar_ipo':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/calendar/ipo"
        elif endpoint == 'calendar_stock_splits':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/calendar/stock-splits"
        elif endpoint == 'options':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/options"
        elif endpoint == 'unusual_options_activity':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/options/unusual-options-activity"
        elif endpoint == 'most_active':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/options/most-active"
        elif endpoint == 'indicator_sma':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/indicators/sma"
        elif endpoint == 'indicator_rsi':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/indicators/rsi"
        elif endpoint == 'indicator_adx':
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/indicators/adx"
        else:
            base_url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/indicators/macd"

        full_endpoint_params = {
            'symbol': symbol,
            'ticker': ticker,
            'search': search,
            'type': type_,
            'list': list_,
            'page': page,
            'date' : date,
            'interval' : interval,
            'limit' : limit,
            'dividend': dividend,
            'diffandsplits': diffandsplits,
            'expiration' : expiration,
            'display': display,
            'time_period': time_period,
            'series_type' : series_type,
            'fast_period': fast_period,
            'slow_period' : slow_period,
            'signal_period': signal_period    
        }

        params = {k: v for k, v in full_endpoint_params.items() if v is not None}

        request_string = urllib.parse.urlencode(params)

        full_url = base_url + '?' + request_string

        req = urllib.request.Request(full_url, headers = headers)
        access = urllib.request.urlopen(req, context = ctx)

        info = access.read().decode()

        data = json.loads(info)

        results = []

        # ── Mercado general ─────────────────────────────────────
        if endpoint == 'market_tickers':
            meta = data["meta"]
            tickers = data["body"]
            results.append({
                "total_records" : meta["totalrecords"]
            })
            for ticker in tickers:
                results.append({
                    "symbol" : ticker.get("symbol"),
                    "name" : ticker.get("name"),
                    "last_sale" : ticker.get("lastsale"),
                    "net_change" : ticker.get("netchange"),
                    "pct_change" : ticker.get("pctchange"),
                    "market_cap" : ticker.get("marketCap"),
                })
            return results

        elif endpoint == 'search':
            matches = data["body"]
            for match in matches:
                results.append({
                    "symbol" : match.get("symbol"),
                    "short_name" : match.get("shortname"),
                    "long_name" : match.get("longname"),
                    "quote_type" : match.get("quoteType"),
                    "type_disp" : match.get("typeDisp"),
                    "exchange" : match.get("exchDisp"),
                    "sector" : match.get("sector"),
                    "industry" : match.get("industry"),
                })
            return results

        elif endpoint == 'market_quotes_realtime':
            quote = data["body"]
            primary = quote["primaryData"]
            key_stats = quote.get("keyStats") or {}
            results.append({
                "symbol" : quote.get("symbol"),
                "company_name" : quote.get("companyName"),
                "stock_type" : quote.get("stockType"),
                "exchange" : quote.get("exchange"),
                "asset_class" : quote.get("assetClass"),
                "market_status" : quote.get("marketStatus"),
                "last_price" : primary.get("lastSalePrice"),
                "net_change" : primary.get("netChange"),
                "percentage_change" : primary.get("percentageChange"),
                "bid_price" : primary.get("bidPrice"),
                "ask_price" : primary.get("askPrice"),
                "volume" : primary.get("volume"),
                "currency" : primary.get("currency"),
                "is_real_time" : primary.get("isRealTime"),
                "last_trade_timestamp" : primary.get("lastTradeTimestamp"),
                "fifty_two_week_high_low" : (key_stats.get("fiftyTwoWeekHighLow") or {}).get("value"),
                "day_range" : (key_stats.get("dayrange") or {}).get("value"),
            })
            return results

        elif endpoint == 'market_quotes_snapshots':
            quotes = data["body"]
            for quote in quotes:
                results.append({
                    "symbol" : quote.get("symbol"),
                    "short_name" : quote.get("shortName"),
                    "long_name" : quote.get("longName"),
                    "quote_type" : quote.get("quoteType"),
                    "currency" : quote.get("currency"),
                    "exchange" : quote.get("fullExchangeName"),
                    "market_state" : quote.get("marketState"),
                    "price" : quote.get("regularMarketPrice"),
                    "change" : quote.get("regularMarketChange"),
                    "change_percent" : quote.get("regularMarketChangePercent"),
                    "open_price" : quote.get("regularMarketOpen"),
                    "high" : quote.get("regularMarketDayHigh"),
                    "low" : quote.get("regularMarketDayLow"),
                    "previous_close" : quote.get("regularMarketPreviousClose"),
                    "volume" : quote.get("regularMarketVolume"),
                    "avg_volume_3m" : quote.get("averageDailyVolume3Month"),
                    "market_cap" : quote.get("marketCap"),
                    "year_high" : quote.get("fiftyTwoWeekHigh"),
                    "year_low" : quote.get("fiftyTwoWeekLow"),
                    "pe_ratio" : quote.get("trailingPE"),
                    "forward_pe" : quote.get("forwardPE"),
                    "eps_ttm" : quote.get("epsTrailingTwelveMonths"),
                    "dividend_yield" : quote.get("dividendYield"),
                })
            return results

        elif endpoint == 'market_screener':
            meta = data["meta"]
            stocks = data["body"]
            results.append({
                "description" : meta.get("description"),
                "count" : meta.get("count"),
                "total" : meta.get("total"),
            })
            for stock in stocks:
                results.append({
                    "symbol" : stock.get("symbol"),
                    "short_name" : stock.get("shortName"),
                    "long_name" : stock.get("longName"),
                    "exchange" : stock.get("fullExchangeName"),
                    "currency" : stock.get("currency"),
                    "price" : stock.get("regularMarketPrice"),
                    "change" : stock.get("regularMarketChange"),
                    "change_percent" : stock.get("regularMarketChangePercent"),
                    "volume" : stock.get("regularMarketVolume"),
                    "avg_volume_3m" : stock.get("averageDailyVolume3Month"),
                    "market_cap" : stock.get("marketCap"),
                    "year_high" : stock.get("fiftyTwoWeekHigh"),
                    "year_low" : stock.get("fiftyTwoWeekLow"),
                    "pe_ratio" : stock.get("trailingPE"),
                })
            return results

        elif endpoint == 'insider_trades':
            trades = data["body"]
            for trade in trades:
                results.append({
                    "symbol" : trade.get("symbol"),
                    "company_name" : trade.get("symbolName"),
                    "insider_name" : trade.get("fullName"),
                    "job_title" : trade.get("shortJobTitle"),
                    "transaction_type" : trade.get("transactionType"),
                    "amount" : trade.get("amount"),
                    "reported_price" : trade.get("reportedPrice"),
                    "usd_value" : trade.get("usdValue"),
                    "eod_holding" : trade.get("eodHolding"),
                    "transaction_date" : trade.get("transactionDate"),
                })
            return results

        elif endpoint == 'market_news_v2':
            news = data["body"]
            for article in news:
                results.append({
                    "title" : article.get("title"),
                    "text" : article.get("text"),
                    "source" : article.get("source"),
                    "type" : article.get("type"),
                    "url" : article.get("url"),
                    "tickers" : article.get("tickers"),
                    "time" : article.get("time"),
                    "ago" : article.get("ago"),
                })
            return results

        elif endpoint == 'market_news_v1':
            news = data["body"]
            for article in news:
                results.append({
                    "title" : article.get("title"),
                    "description" : article.get("description"),
                    "link" : article.get("link"),
                    "pub_date" : article.get("pubDate"),
                })
            return results

        # ── Historial de precios ────────────────────────────────
        elif endpoint == 'stock_history_v2':
            meta = data["meta"]
            candles = data["body"]
            results.append({
                "symbol" : meta.get("ticker"),
                "interval" : meta.get("interval"),
            })
            for candle in candles:
                results.append({
                    "timestamp" : candle.get("timestamp"),
                    "timestamp_unix" : candle.get("timestamp_unix"),
                    "open" : candle.get("open"),
                    "high" : candle.get("high"),
                    "low" : candle.get("low"),
                    "close" : candle.get("close"),
                    "volume" : candle.get("volume"),
                })
            return results

        elif endpoint == 'stock_history_v1':
            meta = data["meta"]
            candles = data["body"]          # OJO: aquí body es un diccionario {timestamp: vela}
            results.append({
                "symbol" : meta.get("symbol"),
                "name" : meta.get("longName"),
                "currency" : meta.get("currency"),
                "exchange" : meta.get("fullExchangeName"),
                "interval" : meta.get("dataGranularity"),
                "range" : meta.get("range"),
                "price" : meta.get("regularMarketPrice"),
                "year_high" : meta.get("fiftyTwoWeekHigh"),
                "year_low" : meta.get("fiftyTwoWeekLow"),
            })
            for candle in candles.values():
                results.append({
                    "date" : candle.get("date"),
                    "date_utc" : candle.get("date_utc"),
                    "open" : candle.get("open"),
                    "high" : candle.get("high"),
                    "low" : candle.get("low"),
                    "close" : candle.get("close"),
                    "volume" : candle.get("volume"),
                })
            return results

        # ── Calendario de eventos ───────────────────────────────
        elif endpoint == 'calendar_earnings':
            earnings = data["body"]
            for event in earnings:
                results.append({
                    "symbol" : event.get("symbol"),
                    "name" : event.get("name"),
                    "time" : event.get("time"),
                    "market_cap" : event.get("marketCap"),
                    "fiscal_quarter_ending" : event.get("fiscalQuarterEnding"),
                    "eps_forecast" : event.get("epsForecast"),
                    "number_of_estimates" : event.get("noOfEsts"),
                    "last_year_report_date" : event.get("lastYearRptDt"),
                    "last_year_eps" : event.get("lastYearEPS"),
                })
            return results

        elif endpoint == 'calendar_dividends':
            dividends = data["body"]
            for event in dividends:
                results.append({
                    "symbol" : event.get("symbol"),
                    "company_name" : event.get("companyName"),
                    "ex_dividend_date" : event.get("dividend_Ex_Date"),
                    "record_date" : event.get("record_Date"),
                    "payment_date" : event.get("payment_Date"),
                    "announcement_date" : event.get("announcement_Date"),
                    "dividend_rate" : event.get("dividend_Rate"),
                    "annual_dividend" : event.get("indicated_Annual_Dividend"),
                })
            return results

        elif endpoint == 'calendar_economic_events':
            events = data["body"]
            for event in events:
                results.append({
                    "time_gmt" : event.get("gmt"),
                    "country" : event.get("country"),
                    "event_name" : event.get("eventName"),
                    "actual" : event.get("actual"),
                    "consensus" : event.get("consensus"),
                    "previous" : event.get("previous"),
                    "description" : event.get("description"),
                })
            return results

        elif endpoint in ('calendar_public_offerings', 'calendar_ipo'):
            offerings = data["body"]        # dict con listas: priced, upcoming, filed, withdrawn
            for status in ['priced', 'upcoming', 'filed', 'withdrawn']:
                deals = offerings.get(status) or []
                if not isinstance(deals, list):
                    continue
                for deal in deals:
                    results.append({
                        "status" : status,
                        "ticker" : deal.get("proposedTickerSymbol"),
                        "company_name" : deal.get("companyName"),
                        "exchange" : deal.get("proposedExchange"),
                        "share_price" : deal.get("proposedSharePrice"),
                        "shares_offered" : deal.get("sharesOffered"),
                        "dollar_value" : deal.get("dollarValueOfSharesOffered"),
                        "priced_date" : deal.get("pricedDate"),
                        "filed_date" : deal.get("filedDate"),
                        "withdraw_date" : deal.get("withdrawDate"),
                        "deal_status" : deal.get("dealStatus"),
                    })
            return results

        elif endpoint == 'calendar_stock_splits':
            splits = data["body"]
            for split in splits:
                results.append({
                    "symbol" : split.get("ticker"),
                    "company_name" : split.get("companyshortname"),
                    "date" : split.get("startdatetime"),
                    "old_share_worth" : split.get("old_share_worth"),
                    "new_share_worth" : split.get("share_worth"),
                    "optionable" : split.get("optionable"),
                })
            return results

        # ── Opciones ────────────────────────────────────────────
        elif endpoint == 'options':
            chain = data["body"][0]
            quote = chain.get("quote") or {}
            results.append({
                "symbol" : chain.get("underlyingSymbol"),
                "name" : quote.get("longName"),
                "price" : quote.get("regularMarketPrice"),
                "expiration_dates" : chain.get("expirationDates"),
            })
            for option_set in chain.get("options", []):
                for side in ['calls', 'puts']:
                    for contract in option_set.get(side, []):
                        results.append({
                            "side" : side,
                            "contract_symbol" : contract.get("contractSymbol"),
                            "strike" : contract.get("strike"),
                            "last_price" : contract.get("lastPrice"),
                            "change" : contract.get("change"),
                            "percent_change" : contract.get("percentChange"),
                            "bid" : contract.get("bid"),
                            "ask" : contract.get("ask"),
                            "volume" : contract.get("volume"),
                            "open_interest" : contract.get("openInterest"),
                            "implied_volatility" : contract.get("impliedVolatility"),
                            "in_the_money" : contract.get("inTheMoney"),
                            "expiration" : contract.get("expiration"),
                        })
            return results

        elif endpoint == 'unusual_options_activity':
            activity = data["body"]
            for option in activity:
                results.append({
                    "symbol" : option.get("symbol"),
                    "base_symbol" : option.get("baseSymbol"),
                    "base_last_price" : option.get("baseLastPrice"),
                    "option_type" : option.get("symbolType"),
                    "strike_price" : option.get("strikePrice"),
                    "expiration_date" : option.get("expirationDate"),
                    "days_to_expiration" : option.get("daysToExpiration"),
                    "bid_price" : option.get("bidPrice"),
                    "ask_price" : option.get("askPrice"),
                    "last_price" : option.get("lastPrice"),
                    "volume" : option.get("volume"),
                    "open_interest" : option.get("openInterest"),
                    "volume_oi_ratio" : option.get("volumeOpenInterestRatio"),
                    "volatility" : option.get("volatility"),
                    "delta" : option.get("delta"),
                    "trade_time" : option.get("tradeTime"),
                })
            return results

        elif endpoint == 'most_active':
            actives = data["body"]
            for asset in actives:
                results.append({
                    "symbol" : asset.get("symbol"),
                    "name" : asset.get("symbolName"),
                    "type" : asset.get("symbolType"),
                    "last_price" : asset.get("lastPrice"),
                    "price_change" : asset.get("priceChange"),
                    "percent_change" : asset.get("percentChange"),
                    "iv_rank_1y" : asset.get("optionsImpliedVolatilityRank1y"),
                    "options_total_volume" : asset.get("optionsTotalVolume"),
                    "put_volume_percent" : asset.get("optionsPutVolumePercent"),
                    "call_volume_percent" : asset.get("optionsCallVolumePercent"),
                    "put_call_ratio" : asset.get("optionsPutCallVolumeRatio"),
                    "trade_time" : asset.get("tradeTime"),
                })
            return results

        # ── Indicadores técnicos ────────────────────────────────
        elif endpoint in ('indicator_sma', 'indicator_rsi', 'indicator_adx'):
            meta = data["meta"]
            values = data["body"]
            indicator = meta.get("indicator")          # "SMA", "RSI" o "ADX"
            results.append({
                "symbol" : meta.get("symbol"),
                "indicator" : indicator,
                "interval" : meta.get("interval"),
                "series_type" : meta.get("series_type"),
                "time_period" : meta.get("time_period"),
            })
            for value in values:
                results.append({
                    "timestamp" : value.get("timestamp"),
                    "value" : value.get(indicator),
                })
            return results

        elif endpoint == 'indicator_macd':
            meta = data["meta"]
            values = data["body"]
            results.append({
                "symbol" : meta.get("symbol"),
                "indicator" : meta.get("indicator"),
                "interval" : meta.get("interval"),
                "series_type" : meta.get("series_type"),
                "fast_period" : meta.get("fast_period"),
                "slow_period" : meta.get("slow_period"),
                "signal_period" : meta.get("signal_period"),
            })
            for value in values:
                results.append({
                    "timestamp" : value.get("timestamp"),
                    "macd" : value.get("MACD"),
                    "macd_signal" : value.get("MACD_Signal"),
                    "macd_hist" : value.get("MACD_Hist"),
                })
            return results

    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        return {'error': f'HTTP {e.code} - {e.reason}: {body}'}
    except urllib.error.URLError as e:
        return {'error': f'URL error occurred: {e.reason}'}



def router(parse_action_result) -> dict:

    # Todos los params de todos los endpoints arrancan en None
    symbol = None
    ticker = None
    search = None
    type_ = None
    list_ = None
    page = None
    date = None
    interval = None
    limit = None
    dividend = None
    diffandsplits = None
    expiration = None
    display = None
    time_period = None
    series_type = None
    fast_period = None
    slow_period = None
    signal_period = None

    # ── Mercado general ─────────────────────────────────────
    if parse_action_result['tool_name'] == 'market_tickers':
        endpoint = parse_action_result['tool_name']
        page = parse_action_result['args'].get('page', None)
        type_ = parse_action_result['args'].get('type', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'search':
        endpoint = parse_action_result['tool_name']
        search = parse_action_result['args'].get('search', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'market_quotes_realtime':
        endpoint = parse_action_result['tool_name']
        ticker = parse_action_result['args'].get('ticker', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'market_quotes_snapshots':
        endpoint = parse_action_result['tool_name']
        ticker = parse_action_result['args'].get('ticker', None)
        type_ = parse_action_result['args'].get('type', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'market_screener':
        endpoint = parse_action_result['tool_name']
        list_ = parse_action_result['args'].get('list', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'insider_trades':
        endpoint = parse_action_result['tool_name']
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'market_news_v2':
        endpoint = parse_action_result['tool_name']
        ticker = parse_action_result['args'].get('ticker', None)
        type_ = parse_action_result['args'].get('type', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'market_news_v1':
        endpoint = parse_action_result['tool_name']
        ticker = parse_action_result['args'].get('ticker', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    # ── Historial de precios ────────────────────────────────
    elif parse_action_result['tool_name'] == 'stock_history_v2':
        endpoint = parse_action_result['tool_name']
        symbol = parse_action_result['args'].get('symbol', None)
        interval = parse_action_result['args'].get('interval', None)
        limit = parse_action_result['args'].get('limit', None)
        dividend = parse_action_result['args'].get('dividend', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'stock_history_v1':
        endpoint = parse_action_result['tool_name']
        symbol = parse_action_result['args'].get('symbol', None)
        interval = parse_action_result['args'].get('interval', None)
        diffandsplits = parse_action_result['args'].get('diffandsplits', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    # ── Calendario de eventos ───────────────────────────────
    elif parse_action_result['tool_name'] == 'calendar_earnings':
        endpoint = parse_action_result['tool_name']
        date = parse_action_result['args'].get('date', None)
        ticker = parse_action_result['args'].get('ticker', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'calendar_dividends':
        endpoint = parse_action_result['tool_name']
        date = parse_action_result['args'].get('date', None)
        ticker = parse_action_result['args'].get('ticker', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'calendar_economic_events':
        endpoint = parse_action_result['tool_name']
        date = parse_action_result['args'].get('date', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'calendar_public_offerings':
        endpoint = parse_action_result['tool_name']
        date = parse_action_result['args'].get('date', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'calendar_ipo':
        endpoint = parse_action_result['tool_name']
        date = parse_action_result['args'].get('date', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'calendar_stock_splits':
        endpoint = parse_action_result['tool_name']
        date = parse_action_result['args'].get('date', None)
        page = parse_action_result['args'].get('page', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    # ── Opciones ────────────────────────────────────────────
    elif parse_action_result['tool_name'] == 'options':
        endpoint = parse_action_result['tool_name']
        ticker = parse_action_result['args'].get('ticker', None)
        expiration = parse_action_result['args'].get('expiration', None)
        display = parse_action_result['args'].get('display', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'unusual_options_activity':
        endpoint = parse_action_result['tool_name']
        type_ = parse_action_result['args'].get('type', None)
        page = parse_action_result['args'].get('page', None)
        date = parse_action_result['args'].get('date', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'most_active':
        endpoint = parse_action_result['tool_name']
        type_ = parse_action_result['args'].get('type', None)
        page = parse_action_result['args'].get('page', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    # ── Indicadores técnicos ────────────────────────────────
    elif parse_action_result['tool_name'] == 'indicator_sma':
        endpoint = parse_action_result['tool_name']
        symbol = parse_action_result['args'].get('symbol', None)
        interval = parse_action_result['args'].get('interval', None)
        time_period = parse_action_result['args'].get('time_period', None)
        series_type = parse_action_result['args'].get('series_type', None)
        limit = parse_action_result['args'].get('limit', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'indicator_rsi':
        endpoint = parse_action_result['tool_name']
        symbol = parse_action_result['args'].get('symbol', None)
        interval = parse_action_result['args'].get('interval', None)
        time_period = parse_action_result['args'].get('time_period', None)
        series_type = parse_action_result['args'].get('series_type', None)
        limit = parse_action_result['args'].get('limit', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'indicator_adx':
        endpoint = parse_action_result['tool_name']
        symbol = parse_action_result['args'].get('symbol', None)
        interval = parse_action_result['args'].get('interval', None)
        time_period = parse_action_result['args'].get('time_period', None)
        series_type = parse_action_result['args'].get('series_type', None)
        limit = parse_action_result['args'].get('limit', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}

    elif parse_action_result['tool_name'] == 'indicator_macd':
        endpoint = parse_action_result['tool_name']
        symbol = parse_action_result['args'].get('symbol', None)
        interval = parse_action_result['args'].get('interval', None)
        series_type = parse_action_result['args'].get('series_type', None)
        fast_period = parse_action_result['args'].get('fast_period', None)
        slow_period = parse_action_result['args'].get('slow_period', None)
        signal_period = parse_action_result['args'].get('signal_period', None)
        limit = parse_action_result['args'].get('limit', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(endpoint, tool, symbol, ticker, search, type_, list_, page, date, interval, limit, dividend, diffandsplits, expiration, display, time_period, series_type, fast_period, slow_period, signal_period)
        return {'result': api_data}
    elif parse_action_result['tool_name'] == 'error':
        return {'result': parse_action_result['args']['message']}
    else:
        return {'result': f'Unknown tool_name>>>  {parse_action_result["tool_name"]}'}

def action(messages: list[dict]):
    while True:
        user_prompt = input("You: ")
        if not user_prompt.strip():
            print('\nYou have to insert a valid prompt. Try again.\n')
            continue
        learn('user', user_prompt)
        messages.append({'role':'user', 'content': user_prompt})


        while True:
            response = generate_response(messages)
            learn('assistant', response)
            messages.append({'role':'assistant', 'content': response})

            if '```action' in response:
                parse_action_result = parse_action(response)
                api_result = router(parse_action_result)
                learn('user', json.dumps(api_result))
                messages.append({'role': 'user', 'content': json.dumps(api_result)})

            else:
                print(f'Charlie: {response}')

                if '```terminate' in response:
                    terminate_message = parse_terminate(response)
                    print('Termination message:', terminate_message)
                    return
                break

if __name__ == "__main__":
    with open(os.path.join(base_dir, 'system_prompt.txt'), 'r', encoding='utf-8') as pattern:
        behavior = pattern.read()

    brain()

    messages = [{'role': 'system', 'content': behavior}]

    print('-------------------------------------------------------------------------------------------------------------\n\n')
    print("Hi! Im Charlie, your AI financial advisor and analyst Agent. Im here to help you about finance and investing. You can ask me questions")
    print('-------------------------------------------------------------------------------------------------------------\n\n')

    recall = remember(limit=20)
    if recall:
        print("Recalling previous conversations:")
        messages.extend(recall)

    action(messages)