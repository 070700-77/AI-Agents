import os
import ssl
import json
import sqlite3
from litellm import completion
from dotenv import load_dotenv
import urllib.request, urllib.parse, urllib.error

load_dotenv()
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
X_RAPIDAPI_KEY = os.environ.get('X_RAPIDAPI_KEY')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn =sqlite3.connect('memory.db')
cur = conn.cursor()


def brain():
    cur.execute('''CREATE TABLE IF NOT EXISTS Brain (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    content TEXT,
    date TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    return None


def remember(limit: int = 20):
    cur.execute('''SELECT role, content FROM Brain ORDER BY id DESC LIMIT (?)''', (limit,))
    rows = cur.fetchall()
    
    return [{'role': row[0], 'content': row[1]} for row in reversed(rows)]


def learn(role: str, content: str):
    cur.execute('''INSERT INTO Brain (role, content) VALUES (?,?)''', (role, content))
    conn.commit()
    
    return None


def generate_response(messages : list[dict]) -> str:
    response = completion(
    model = 'anthropic/claude-sonnet-4-6',
    messages = messages,
    max_tokens = 1024
    )
    
    return response.choices[0].message.content


def parse_terminate(response: str) -> str|None:
    try:
        
        if '```terminate' in response:
            json_string = response.split('```terminate')[1].split('```')[0].strip()
            data = json.loads(json_string)
            return data.get('Terminate','Goodbye!')
        
    except (IndexError, json.JSONDecodeError):
        pass
    
    return None


def parse_action(response) -> dict:
    print('  [🔍 Consultando API...]\n')
    try:
        if '```action' in response:
            json_string = response.split('```action')[1].split('```')[0].strip()
            
        else:
            json_string = response
            
        data = json.loads(json_string)
        tool_name = data.get('tool_name', None)
        args = data.get('args', None)
        
        if tool_name is None or args is None:
            return {'tool_name': 'error', 'args': {'message': 'Invalid response. You must respond with tool_name and args.'}}
        return {'tool_name': tool_name, 'args': args}
    
    except (IndexError, json.JSONDecodeError):
        return {'tool_name': 'error', 'args': {'message': 'invalid JSON format'}}
    
    return None


def connect_api(search,ticker,type_,module,symbol,interval,limit_,dividend,list_):
    try:
        headers = {
        "x-rapidapi-key": X_RAPIDAPI_KEY,
        "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com",
        "Content-Type": "application/json"
        }
        
        consolidated_endpoint_params = {
        'search': search,
        'ticker': ticker,
        'type': type_,
        'module': module,
        'symbol': symbol,
        'interval': interval,
        'limit': limit_,
        'dividend': dividend,
        'list': list_
        }
        
        query_string = {key: value for key, value in consolidated_endpoint_params.items() if value is not None and value != ""}
        encoded_query_string = urllib.parse.urlencode(query_string)
        
        if 'search' in query_string:
            base_url = 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/search'
        elif 'ticker' in query_string and 'type' in query_string:
            base_url = 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/quote'
        elif 'ticker' in query_string and 'module' in query_string:
            base_url = 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/stock/modules'
        elif 'symbol' in query_string and 'interval' in query_string and 'limit' in query_string and 'dividend' in query_string:
            base_url = 'https://yahoo-finance15.p.rapidapi.com/api/v2/markets/stock/history'
        elif 'list' in query_string:
            base_url = 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/screener'
        else:
            base_url = 'https://yahoo-finance15.p.rapidapi.com/api/v2/markets/news'
        
        encoded_url = base_url + "?" + encoded_query_string
        
        req = urllib.request.Request(encoded_url, headers = headers)
        access = urllib.request.urlopen(req, context = ctx)
        
        read = access.read().decode()
        data = json.loads(read)
        
        results = []
        
        if base_url == 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/search':
            for item in data['body']:
                results.append({
                'shortname': item.get('shortname'),
                'quoteType': item.get('quoteType'),
                'symbol': item.get('symbol'),
                'index': item.get('index'),
                'score': item.get('score'),
                'typeDisp': item.get('typeDisp'),
                'longname': item.get('longname'),
                'exchange': item.get('exchDisp'),
                'sector': item.get('sector'),
                'sectorDisp': item.get('sectorDisp'),
                'industry': item.get('industry'),
                'industryDisp': item.get('industryDisp')
                })
            return results
        elif base_url == 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/quote':
            items = data if isinstance(data, list) else [data]
            for item in items:
                results.append({
                # Identificación
                'symbol': item.get('symbol'),
                'shortName': item.get('shortName'),
                'longName': item.get('longName'),
                'displayName': item.get('displayName'),
                'quoteType': item.get('quoteType'),
                'typeDisp': item.get('typeDisp'),
                # Mercado y bolsa
                'market': item.get('market'),
                'marketState': item.get('marketState'),
                'exchange': item.get('exchange'),
                'fullExchangeName': item.get('fullExchangeName'),
                'currency': item.get('currency'),
                'financialCurrency': item.get('financialCurrency'),
                # Precio actual
                'regularMarketPrice': item.get('regularMarketPrice'),
                'regularMarketChange': item.get('regularMarketChange'),
                'regularMarketChangePercent': item.get('regularMarketChangePercent'),
                'regularMarketPreviousClose': item.get('regularMarketPreviousClose'),
                'regularMarketOpen': item.get('regularMarketOpen'),
                'regularMarketDayHigh': item.get('regularMarketDayHigh'),
                'regularMarketDayLow': item.get('regularMarketDayLow'),
                'regularMarketDayRange': item.get('regularMarketDayRange'),
                # Pre-market
                'preMarketPrice': item.get('preMarketPrice'),
                'preMarketChange': item.get('preMarketChange'),
                'preMarketChangePercent': item.get('preMarketChangePercent'),
                # Volumen
                'regularMarketVolume': item.get('regularMarketVolume'),
                'averageDailyVolume3Month': item.get('averageDailyVolume3Month'),
                'averageDailyVolume10Day': item.get('averageDailyVolume10Day'),
                # Valorización
                'marketCap': item.get('marketCap'),
                'sharesOutstanding': item.get('sharesOutstanding'),
                'bookValue': item.get('bookValue'),
                'priceToBook': item.get('priceToBook'),
                # Múltiplos
                'trailingPE': item.get('trailingPE'),
                'forwardPE': item.get('forwardPE'),
                'epsTrailingTwelveMonths': item.get('epsTrailingTwelveMonths'),
                'epsForward': item.get('epsForward'),
                'epsCurrentYear': item.get('epsCurrentYear'),
                'priceEpsCurrentYear': item.get('priceEpsCurrentYear'),
                # Dividendos
                'dividendRate': item.get('dividendRate'),
                'dividendYield': item.get('dividendYield'),
                'trailingAnnualDividendRate': item.get('trailingAnnualDividendRate'),
                'trailingAnnualDividendYield': item.get('trailingAnnualDividendYield'),
                'dividendDate': item.get('dividendDate'),
                # Promedios móviles
                'fiftyDayAverage': item.get('fiftyDayAverage'),
                'fiftyDayAverageChange': item.get('fiftyDayAverageChange'),
                'fiftyDayAverageChangePercent': item.get('fiftyDayAverageChangePercent'),
                'twoHundredDayAverage': item.get('twoHundredDayAverage'),
                'twoHundredDayAverageChange': item.get('twoHundredDayAverageChange'),
                'twoHundredDayAverageChangePercent': item.get('twoHundredDayAverageChangePercent'),
                # Rango 52 semanas
                'fiftyTwoWeekRange': item.get('fiftyTwoWeekRange'),
                'fiftyTwoWeekLow': item.get('fiftyTwoWeekLow'),
                'fiftyTwoWeekHigh': item.get('fiftyTwoWeekHigh'),
                'fiftyTwoWeekLowChange': item.get('fiftyTwoWeekLowChange'),
                'fiftyTwoWeekLowChangePercent': item.get('fiftyTwoWeekLowChangePercent'),
                'fiftyTwoWeekHighChange': item.get('fiftyTwoWeekHighChange'),
                'fiftyTwoWeekHighChangePercent': item.get('fiftyTwoWeekHighChangePercent'),
                'fiftyTwoWeekChangePercent': item.get('fiftyTwoWeekChangePercent'),
                # Analistas
                'averageAnalystRating': item.get('averageAnalystRating'),
                # Earnings
                'earningsTimestamp': item.get('earningsTimestamp'),
                'earningsTimestampStart': item.get('earningsTimestampStart'),
                'earningsTimestampEnd': item.get('earningsTimestampEnd'),
                # Bid / Ask
                'bid': item.get('bid'),
                'ask': item.get('ask'),
                'bidSize': item.get('bidSize'),
                'askSize': item.get('askSize'),
                # Metadata técnica útil
                'quoteSourceName': item.get('quoteSourceName'),
                'sourceInterval': item.get('sourceInterval'),
                'exchangeDataDelayedBy': item.get('exchangeDataDelayedBy'),
                'exchangeTimezoneName': item.get('exchangeTimezoneName'),
                'exchangeTimezoneShortName': item.get('exchangeTimezoneShortName'),
                'regularMarketTime': item.get('regularMarketTime'),
                'preMarketTime': item.get('preMarketTime'),
                'firstTradeDateMilliseconds': item.get('firstTradeDateMilliseconds')
                })
            return results

        elif  base_url == 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/stock/modules':
            for item in data['data']:
                asset = item.get('assetProfile', {})
                earnings = item.get('earnings', {})
                financial = item.get('financialData', {})
                results.append({
                # Perfil de la empresa
                'address': asset.get('address1'),
                'city': asset.get('city'),
                'state': asset.get('state'),
                'country': asset.get('country'),
                'zip': asset.get('zip'),
                'phone': asset.get('phone'),
                'website': asset.get('website'),
                'sector': asset.get('sector'),
                'industry': asset.get('industry'),
                'fullTimeEmployees': asset.get('fullTimeEmployees'),
                'longBusinessSummary': asset.get('longBusinessSummary'),
                # Riesgos corporativos
                'auditRisk': asset.get('auditRisk'),
                'boardRisk': asset.get('boardRisk'),
                'compensationRisk': asset.get('compensationRisk'),
                'shareHolderRightsRisk': asset.get('shareHolderRightsRisk'),
                'overallRisk': asset.get('overallRisk'),
                # Datos financieros principales
                'financialCurrency': financial.get('financialCurrency'),
                'currentPrice': financial.get('currentPrice', {}).get('raw'),
                'targetHighPrice': financial.get('targetHighPrice', {}).get('raw'),
                'targetLowPrice': financial.get('targetLowPrice', {}).get('raw'),
                'targetMeanPrice': financial.get('targetMeanPrice', {}).get('raw'),
                'targetMedianPrice': financial.get('targetMedianPrice', {}).get('raw'),
                'recommendationKey': financial.get('recommendationKey'),
                'recommendationMean': financial.get('recommendationMean', {}).get('raw'),
                'numberOfAnalystOpinions': financial.get('numberOfAnalystOpinions', {}).get('raw'),
                # Rentabilidad y crecimiento
                'revenueGrowth': financial.get('revenueGrowth', {}).get('raw'),
                'earningsGrowth': financial.get('earningsGrowth', {}).get('raw'),
                'grossMargins': financial.get('grossMargins', {}).get('raw'),
                'ebitdaMargins': financial.get('ebitdaMargins', {}).get('raw'),
                'operatingMargins': financial.get('operatingMargins', {}).get('raw'),
                'profitMargins': financial.get('profitMargins', {}).get('raw'),
                'returnOnAssets': financial.get('returnOnAssets', {}).get('raw'),
                'returnOnEquity': financial.get('returnOnEquity', {}).get('raw'),
                # Liquidez y deuda
                'currentRatio': financial.get('currentRatio', {}).get('raw'),
                'quickRatio': financial.get('quickRatio', {}).get('raw'),
                'debtToEquity': financial.get('debtToEquity', {}).get('raw'),
                'totalCash': financial.get('totalCash', {}).get('raw'),
                'totalDebt': financial.get('totalDebt', {}).get('raw'),
                'totalCashPerShare': financial.get('totalCashPerShare', {}).get('raw'),
                # Ingresos, flujo y EBITDA
                'totalRevenue': financial.get('totalRevenue', {}).get('raw'),
                'revenuePerShare': financial.get('revenuePerShare', {}).get('raw'),
                'grossProfits': financial.get('grossProfits', {}).get('raw'),
                'ebitda': financial.get('ebitda', {}).get('raw'),
                'freeCashflow': financial.get('freeCashflow', {}).get('raw'),
                'operatingCashflow': financial.get('operatingCashflow', {}).get('raw'),
                # Earnings
                'earningsCurrency': earnings.get('financialCurrency'),
                'currentQuarterEstimate': earnings.get('earningsChart', {}).get('currentQuarterEstimate', {}).get('raw'),
                'currentQuarterEstimateDate': earnings.get('earningsChart', {}).get('currentQuarterEstimateDate'),
                'currentQuarterEstimateYear': earnings.get('earningsChart', {}).get('currentQuarterEstimateYear'),
                'earningsDate': earnings.get('earningsChart', {}).get('earningsDate', []),
                # Histórico financiero
                'quarterlyEarnings': earnings.get('financialsChart', {}).get('quarterly', []),
                'yearlyEarnings': earnings.get('financialsChart', {}).get('yearly', []),
                'quarterlyEps': earnings.get('earningsChart', {}).get('quarterly', [])
                })
            return results

        elif  base_url == 'https://yahoo-finance15.p.rapidapi.com/api/v2/markets/stock/history':
            meta = data.get('meta', {})
            items = data.get('items', {})
            for timestamp, item in items.items():
                results.append({
                # Identificación del activo
                'symbol': meta.get('symbol'),
                'currency': meta.get('currency'),
                'exchangeName': meta.get('exchangeName'),
                'instrumentType': meta.get('instrumentType'),
                # Información del mercado
                'timezone': meta.get('timezone'),
                'exchangeTimezoneName': meta.get('exchangeTimezoneName'),
                'gmtoffset': meta.get('gmtoffset'),
                'dataGranularity': meta.get('dataGranularity'),
                'range': meta.get('range'),
                # Precio de referencia del mercado
                'regularMarketPrice': meta.get('regularMarketPrice'),
                'chartPreviousClose': meta.get('chartPreviousClose'),
                'previousClose': meta.get('previousClose'),
                'regularMarketTime': meta.get('regularMarketTime'),
                # Timestamp del registro
                'timestamp': timestamp,
                'date': item.get('date'),
                'date_utc': item.get('date_utc'),
                # Datos OHLCV
                'open': item.get('open'),
                'high': item.get('high'),
                'low': item.get('low'),
                'close': item.get('close'),
                'volume': item.get('volume')
                })
            return results

        elif  base_url == 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/screener':
            meta = data.get('meta', {})
            for item in data.get('body', []):
                results.append({
                # Metadata general del screener
                'screenerDescription': meta.get('description'),
                'processedTime': meta.get('processedTime'),
                'offset': meta.get('offset'),
                'count': meta.get('count'),
                'total': meta.get('total'),
                'status': meta.get('status'),
                # Identificación del activo
                'symbol': item.get('symbol'),
                'shortName': item.get('shortName'),
                'longName': item.get('longName'),
                'displayName': item.get('displayName'),
                'quoteType': item.get('quoteType'),
                'typeDisp': item.get('typeDisp'),
                # Mercado y bolsa
                'market': item.get('market'),
                'marketState': item.get('marketState'),
                'exchange': item.get('exchange'),
                'fullExchangeName': item.get('fullExchangeName'),
                'currency': item.get('currency'),
                'financialCurrency': item.get('financialCurrency'),
                # Precio y variación del día
                'regularMarketPrice': item.get('regularMarketPrice'),
                'regularMarketChange': item.get('regularMarketChange'),
                'regularMarketChangePercent': item.get('regularMarketChangePercent'),
                'regularMarketPreviousClose': item.get('regularMarketPreviousClose'),
                'regularMarketOpen': item.get('regularMarketOpen'),
                'regularMarketDayHigh': item.get('regularMarketDayHigh'),
                'regularMarketDayLow': item.get('regularMarketDayLow'),
                'regularMarketDayRange': item.get('regularMarketDayRange'),
                'regularMarketTime': item.get('regularMarketTime'),
                # Volumen
                'regularMarketVolume': item.get('regularMarketVolume'),
                'averageDailyVolume3Month': item.get('averageDailyVolume3Month'),
                'averageDailyVolume10Day': item.get('averageDailyVolume10Day'),
                # Bid / Ask
                'bid': item.get('bid'),
                'ask': item.get('ask'),
                'bidSize': item.get('bidSize'),
                'askSize': item.get('askSize'),
                # Capitalización y acciones
                'marketCap': item.get('marketCap'),
                'sharesOutstanding': item.get('sharesOutstanding'),
                'impliedSharesOutstanding': item.get('impliedSharesOutstanding'),
                'bookValue': item.get('bookValue'),
                'priceToBook': item.get('priceToBook'),
                # EPS y múltiplos
                'epsTrailingTwelveMonths': item.get('epsTrailingTwelveMonths'),
                'epsForward': item.get('epsForward'),
                'epsCurrentYear': item.get('epsCurrentYear'),
                'priceEpsCurrentYear': item.get('priceEpsCurrentYear'),
                'trailingPE': item.get('trailingPE'),
                'forwardPE': item.get('forwardPE'),
                # Dividendos
                'dividendRate': item.get('dividendRate'),
                'dividendYield': item.get('dividendYield'),
                'dividendDate': item.get('dividendDate'),
                'trailingAnnualDividendRate': item.get('trailingAnnualDividendRate'),
                'trailingAnnualDividendYield': item.get('trailingAnnualDividendYield'),
                # Rango 52 semanas
                'fiftyTwoWeekHigh': item.get('fiftyTwoWeekHigh'),
                'fiftyTwoWeekLow': item.get('fiftyTwoWeekLow'),
                'fiftyTwoWeekRange': item.get('fiftyTwoWeekRange'),
                'fiftyTwoWeekLowChange': item.get('fiftyTwoWeekLowChange'),
                'fiftyTwoWeekLowChangePercent': item.get('fiftyTwoWeekLowChangePercent'),
                'fiftyTwoWeekHighChange': item.get('fiftyTwoWeekHighChange'),
                'fiftyTwoWeekHighChangePercent': item.get('fiftyTwoWeekHighChangePercent'),
                'fiftyTwoWeekChangePercent': item.get('fiftyTwoWeekChangePercent'),
                # Promedios móviles
                'fiftyDayAverage': item.get('fiftyDayAverage'),
                'fiftyDayAverageChange': item.get('fiftyDayAverageChange'),
                'fiftyDayAverageChangePercent': item.get('fiftyDayAverageChangePercent'),
                'twoHundredDayAverage': item.get('twoHundredDayAverage'),
                'twoHundredDayAverageChange': item.get('twoHundredDayAverageChange'),
                'twoHundredDayAverageChangePercent': item.get('twoHundredDayAverageChangePercent'),
                # Analistas
                'averageAnalystRating': item.get('averageAnalystRating'),
                # Earnings
                'earningsTimestamp': item.get('earningsTimestamp'),
                'earningsTimestampStart': item.get('earningsTimestampStart'),
                'earningsTimestampEnd': item.get('earningsTimestampEnd'),
                'earningsCallTimestampStart': item.get('earningsCallTimestampStart'),
                'earningsCallTimestampEnd': item.get('earningsCallTimestampEnd'),
                'isEarningsDateEstimate': item.get('isEarningsDateEstimate'),
                # Corporate actions
                'corporateActions': item.get('corporateActions'),
                # Información técnica
                'quoteSourceName': item.get('quoteSourceName'),
                'sourceInterval': item.get('sourceInterval'),
                'exchangeDataDelayedBy': item.get('exchangeDataDelayedBy'),
                'exchangeTimezoneName': item.get('exchangeTimezoneName'),
                'exchangeTimezoneShortName': item.get('exchangeTimezoneShortName'),
                'gmtOffSetMilliseconds': item.get('gmtOffSetMilliseconds'),
                'firstTradeDateMilliseconds': item.get('firstTradeDateMilliseconds'),
                'priceHint': item.get('priceHint'),
                # Flags
                'triggerable': item.get('triggerable'),
                'customPriceAlertConfidence': item.get('customPriceAlertConfidence'),
                'esgPopulated': item.get('esgPopulated'),
                'tradeable': item.get('tradeable'),
                'cryptoTradeable': item.get('cryptoTradeable'),
                'hasPrePostMarketData': item.get('hasPrePostMarketData'),
                # Cambios de nombre / IPO
                'prevName': item.get('prevName'),
                'nameChangeDate': item.get('nameChangeDate'),
                'ipoExpectedDate': item.get('ipoExpectedDate'),
                # Métricas adicionales del screener
                'lastCloseTevEbitLtm': item.get('lastCloseTevEbitLtm'),
                'lastClosePriceToNNWCPerShare': item.get('lastClosePriceToNNWCPerShare'),
                'messageBoardId': item.get('messageBoardId'),
                'language': item.get('language'),
                'region': item.get('region')
                })
            return results

        else:
            for item in data['body']:
                results.append({
                'guid': item.get('guid'),
                'title': item.get('title'),
                'source': item.get('source'),
                'link': item.get('link'),
                'pubDate': item.get('pubDate')
                })
            return results
        
    except urllib.error.URLError as e:
        return {'result': str(e)}
    
    return None


def router(parse_action_result):

    if parse_action_result['tool_name'] == 'v1_search':
        search = parse_action_result['args']['search']
        connect = connect_api(search,"","","","","","","","")
        return {'result': connect}
    
    elif parse_action_result['tool_name'] == 'v1_market_quotes':
        ticker = parse_action_result['args']['ticker']
        type_ = parse_action_result['args']['type']
        connect = connect_api("",ticker, type_,"","","","","","")
        return {'result': connect}
    
    elif parse_action_result['tool_name'] == 'v1_stock_modules':
        ticker = parse_action_result['args']['ticker']
        module = parse_action_result['args']['module']
        connect = connect_api("",ticker,"",module,"","","","","")
        return {'result': connect}
    
    elif parse_action_result['tool_name'] == 'v2_stock_history':
        symbol = parse_action_result['args']['symbol']
        interval = parse_action_result['args']['interval']
        limit_ = parse_action_result['args']['limit']
        dividend = parse_action_result['args']['dividend']
        connect = connect_api("","","","",symbol, interval, limit_, dividend,"")
        return {'result': connect}
    
    elif parse_action_result['tool_name'] == 'v1_market_screener':
        list_ = parse_action_result['args']['list']
        connect = connect_api("","","","","","","","",list_)
        return {'result': connect}
    
    elif parse_action_result['tool_name'] == 'v2_market_news':
        ticker = parse_action_result['args']['ticker']
        connect = connect_api("",ticker,"","","","","","","")
        return {'result': connect}
    
    elif parse_action_result['tool_name'] == 'error':
        file_error = parse_action_result['args']['message']
        return {'error': file_error} 
    
    elif parse_action_result['tool_name'] == 'terminate':
        print('Tool use has been ceased...\n')
        return '```terminate'
    
    else: 
        return {'error': 'Unknown tool' + parse_action_result['tool_name']}
    return None


def action(messages: list[dict]):
    while True:
        prompt = input('You: ')
        if not prompt.strip():
            print('\nEnter a valid input. Try again.\n')
            continue
            
        messages.append({'role': 'user', 'content': prompt})
        learn('user', prompt)
        
        while True:
            response = generate_response(messages)
            
            messages.append({'role': 'assistant', 'content': response})
            learn('assistant', response)
            
            if '```action' in response:
                parse_action_result = parse_action(response)
                get_api_info = router(parse_action_result)
                messages.append({'role': 'user', 'content': json.dumps(get_api_info)})
                learn('user', json.dumps(get_api_info))
            else:
                print(f'\nWarren: {response}')
                if '```terminate' in response:
                    parse_terminate(response)
                    print('\n'+'-'*55)
                    print("  It's always a pleasure helping you, Santi.")
                    print('  Feel free to reach me out anytime. Goodbye! :)')
                    conn.commit()
                    cur.close()
                    conn.close()
                    return
                break
    return None 

if __name__ == '__main__':
    with open('system_prompt.txt','r', encoding = 'utf-8') as pattern:
        behavior = pattern.read()
        
    brain()
    
    print('\n'+'='*55)
    print('Hi! Im Warren, your AI financial expert agent. Whats on your mind today?')
    print('='*55 + '\n')
    
    messages = [{'role': 'system', 'content': behavior}]
    
    recall = remember(limit = 20)
    if recall:
        print(f'\n  [📚 Loading {len(recall)} previous sessions messages...]')
        messages.extend(recall)
    
    action(messages)
