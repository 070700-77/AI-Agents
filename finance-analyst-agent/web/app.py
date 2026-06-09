import os
import ssl
import json
import sqlite3
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from litellm import completion
from dotenv import load_dotenv
import urllib.request, urllib.parse, urllib.error

load_dotenv()
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
X_RAPIDAPI_KEY = os.environ.get('X_RAPIDAPI_KEY')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

DB_PATH = 'memory.db'

TOOL_LABELS = {
    'v1_search':          '🔍 Buscando activo...',
    'v1_market_quotes':   '📈 Obteniendo cotización en tiempo real...',
    'v1_stock_modules':   '🏢 Cargando fundamentos de la empresa...',
    'v2_stock_history':   '📊 Descargando historial de precios...',
    'v1_market_screener': '🔎 Ejecutando screener de mercado...',
    'v2_market_news':     '📰 Buscando noticias recientes...',
}

app = FastAPI(title='Warren – AI Financial Analyst')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


# ─── Database helpers ────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Brain (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        role    TEXT,
        content TEXT,
        date    TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    return conn, cur


def remember(limit: int = 20) -> list[dict]:
    conn, cur = get_db()
    cur.execute('SELECT role, content FROM Brain ORDER BY id DESC LIMIT (?)', (limit,))
    rows = cur.fetchall()
    conn.close()
    return [{'role': r[0], 'content': r[1]} for r in reversed(rows)]


def learn(role: str, content: str):
    conn, cur = get_db()
    cur.execute('INSERT INTO Brain (role, content) VALUES (?,?)', (role, content))
    conn.commit()
    conn.close()


# ─── Agent core ──────────────────────────────────────────────────────────────

def generate_response(messages: list[dict]) -> str:
    response = completion(
        model='anthropic/claude-sonnet-4-6',
        messages=messages,
        max_tokens=2048,
    )
    return response.choices[0].message.content


def parse_action(response: str) -> dict:
    try:
        if '```action' in response:
            json_string = response.split('```action')[1].split('```')[0].strip()
        else:
            json_string = response
        data = json.loads(json_string)
        tool_name = data.get('tool_name')
        args = data.get('args')
        if tool_name is None or args is None:
            return {'tool_name': 'error', 'args': {'message': 'Respuesta inválida del agente.'}}
        return {'tool_name': tool_name, 'args': args}
    except (IndexError, json.JSONDecodeError):
        return {'tool_name': 'error', 'args': {'message': 'JSON malformado en la respuesta del agente.'}}


def parse_terminate(response: str) -> str | None:
    try:
        if '```terminate' in response:
            json_string = response.split('```terminate')[1].split('```')[0].strip()
            data = json.loads(json_string)
            return data.get('Terminate', '¡Hasta pronto!')
    except (IndexError, json.JSONDecodeError):
        pass
    return None


# ─── Yahoo Finance API ────────────────────────────────────────────────────────

def connect_api(search, ticker, type_, module, symbol, interval, limit_, dividend, list_):
    try:
        headers = {
            'x-rapidapi-key': X_RAPIDAPI_KEY,
            'x-rapidapi-host': 'yahoo-finance15.p.rapidapi.com',
            'Content-Type': 'application/json',
        }
        params = {
            'search': search, 'ticker': ticker, 'type': type_,
            'module': module, 'symbol': symbol, 'interval': interval,
            'limit': limit_, 'dividend': dividend, 'list': list_,
        }
        query = {k: v for k, v in params.items() if v is not None and v != ''}
        encoded = urllib.parse.urlencode(query)

        if 'search' in query:
            base = 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/search'
        elif 'ticker' in query and 'type' in query:
            base = 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/quote'
        elif 'ticker' in query and 'module' in query:
            base = 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/stock/modules'
        elif 'symbol' in query and 'interval' in query and 'limit' in query and 'dividend' in query:
            base = 'https://yahoo-finance15.p.rapidapi.com/api/v2/markets/stock/history'
        elif 'list' in query:
            base = 'https://yahoo-finance15.p.rapidapi.com/api/v1/markets/screener'
        else:
            base = 'https://yahoo-finance15.p.rapidapi.com/api/v2/markets/news'

        req = urllib.request.Request(base + '?' + encoded, headers=headers)
        access = urllib.request.urlopen(req, context=ctx)
        data = json.loads(access.read().decode())
        results = []

        if base.endswith('/search'):
            for item in data.get('body', []):
                results.append({
                    'shortname': item.get('shortname'), 'quoteType': item.get('quoteType'),
                    'symbol': item.get('symbol'), 'index': item.get('index'),
                    'score': item.get('score'), 'typeDisp': item.get('typeDisp'),
                    'longname': item.get('longname'), 'exchange': item.get('exchDisp'),
                    'sector': item.get('sector'), 'industry': item.get('industry'),
                })

        elif base.endswith('/quote'):
            for item in data.get('body', []):
                results.append({
                    'symbol': item.get('symbol'), 'shortName': item.get('shortName'),
                    'longName': item.get('longName'), 'quoteType': item.get('quoteType'),
                    'market': item.get('market'), 'marketState': item.get('marketState'),
                    'exchange': item.get('fullExchangeName'), 'currency': item.get('currency'),
                    'regularMarketPrice': item.get('regularMarketPrice'),
                    'regularMarketChange': item.get('regularMarketChange'),
                    'regularMarketChangePercent': item.get('regularMarketChangePercent'),
                    'regularMarketPreviousClose': item.get('regularMarketPreviousClose'),
                    'regularMarketOpen': item.get('regularMarketOpen'),
                    'regularMarketDayHigh': item.get('regularMarketDayHigh'),
                    'regularMarketDayLow': item.get('regularMarketDayLow'),
                    'regularMarketVolume': item.get('regularMarketVolume'),
                    'averageDailyVolume3Month': item.get('averageDailyVolume3Month'),
                    'marketCap': item.get('marketCap'),
                    'sharesOutstanding': item.get('sharesOutstanding'),
                    'bookValue': item.get('bookValue'), 'priceToBook': item.get('priceToBook'),
                    'trailingPE': item.get('trailingPE'), 'forwardPE': item.get('forwardPE'),
                    'epsTrailingTwelveMonths': item.get('epsTrailingTwelveMonths'),
                    'epsForward': item.get('epsForward'),
                    'dividendRate': item.get('dividendRate'), 'dividendYield': item.get('dividendYield'),
                    'trailingAnnualDividendYield': item.get('trailingAnnualDividendYield'),
                    'fiftyDayAverage': item.get('fiftyDayAverage'),
                    'twoHundredDayAverage': item.get('twoHundredDayAverage'),
                    'fiftyTwoWeekRange': item.get('fiftyTwoWeekRange'),
                    'fiftyTwoWeekLow': item.get('fiftyTwoWeekLow'),
                    'fiftyTwoWeekHigh': item.get('fiftyTwoWeekHigh'),
                    'fiftyTwoWeekChangePercent': item.get('fiftyTwoWeekChangePercent'),
                    'averageAnalystRating': item.get('averageAnalystRating'),
                    'preMarketPrice': item.get('preMarketPrice'),
                    'preMarketChangePercent': item.get('preMarketChangePercent'),
                    'bid': item.get('bid'), 'ask': item.get('ask'),
                })

        elif base.endswith('/modules'):
            for item in data.get('data', []):
                asset = item.get('assetProfile', {})
                earnings = item.get('earnings', {})
                financial = item.get('financialData', {})
                results.append({
                    'country': asset.get('country'), 'sector': asset.get('sector'),
                    'industry': asset.get('industry'),
                    'fullTimeEmployees': asset.get('fullTimeEmployees'),
                    'longBusinessSummary': asset.get('longBusinessSummary'),
                    'website': asset.get('website'),
                    'auditRisk': asset.get('auditRisk'), 'overallRisk': asset.get('overallRisk'),
                    'currentPrice': financial.get('currentPrice', {}).get('raw'),
                    'targetHighPrice': financial.get('targetHighPrice', {}).get('raw'),
                    'targetLowPrice': financial.get('targetLowPrice', {}).get('raw'),
                    'targetMeanPrice': financial.get('targetMeanPrice', {}).get('raw'),
                    'recommendationKey': financial.get('recommendationKey'),
                    'numberOfAnalystOpinions': financial.get('numberOfAnalystOpinions', {}).get('raw'),
                    'revenueGrowth': financial.get('revenueGrowth', {}).get('raw'),
                    'earningsGrowth': financial.get('earningsGrowth', {}).get('raw'),
                    'grossMargins': financial.get('grossMargins', {}).get('raw'),
                    'ebitdaMargins': financial.get('ebitdaMargins', {}).get('raw'),
                    'operatingMargins': financial.get('operatingMargins', {}).get('raw'),
                    'profitMargins': financial.get('profitMargins', {}).get('raw'),
                    'returnOnAssets': financial.get('returnOnAssets', {}).get('raw'),
                    'returnOnEquity': financial.get('returnOnEquity', {}).get('raw'),
                    'currentRatio': financial.get('currentRatio', {}).get('raw'),
                    'quickRatio': financial.get('quickRatio', {}).get('raw'),
                    'debtToEquity': financial.get('debtToEquity', {}).get('raw'),
                    'totalCash': financial.get('totalCash', {}).get('raw'),
                    'totalDebt': financial.get('totalDebt', {}).get('raw'),
                    'totalRevenue': financial.get('totalRevenue', {}).get('raw'),
                    'grossProfits': financial.get('grossProfits', {}).get('raw'),
                    'ebitda': financial.get('ebitda', {}).get('raw'),
                    'freeCashflow': financial.get('freeCashflow', {}).get('raw'),
                    'operatingCashflow': financial.get('operatingCashflow', {}).get('raw'),
                    'earningsCurrency': earnings.get('financialCurrency'),
                    'currentQuarterEstimate': earnings.get('earningsChart', {}).get('currentQuarterEstimate', {}).get('raw'),
                    'yearlyEarnings': earnings.get('financialsChart', {}).get('yearly', []),
                    'quarterlyEps': earnings.get('earningsChart', {}).get('quarterly', []),
                })

        elif base.endswith('/history'):
            meta = data.get('meta', {})
            items = data.get('items', {})
            # Return only last 30 entries to keep payload manageable
            entries = list(items.items())[-30:]
            for timestamp, item in entries:
                results.append({
                    'symbol': meta.get('symbol'), 'currency': meta.get('currency'),
                    'exchangeName': meta.get('exchangeName'),
                    'dataGranularity': meta.get('dataGranularity'),
                    'regularMarketPrice': meta.get('regularMarketPrice'),
                    'timestamp': timestamp, 'date': item.get('date'),
                    'open': item.get('open'), 'high': item.get('high'),
                    'low': item.get('low'), 'close': item.get('close'),
                    'volume': item.get('volume'),
                })

        elif base.endswith('/screener'):
            meta = data.get('meta', {})
            for item in data.get('body', []):
                results.append({
                    'screenerDescription': meta.get('description'),
                    'symbol': item.get('symbol'), 'shortName': item.get('shortName'),
                    'regularMarketPrice': item.get('regularMarketPrice'),
                    'regularMarketChangePercent': item.get('regularMarketChangePercent'),
                    'marketCap': item.get('marketCap'),
                    'trailingPE': item.get('trailingPE'),
                    'dividendYield': item.get('dividendYield'),
                    'averageAnalystRating': item.get('averageAnalystRating'),
                    'fiftyTwoWeekChangePercent': item.get('fiftyTwoWeekChangePercent'),
                })

        else:  # news
            for item in data.get('body', []):
                results.append({
                    'title': item.get('title'), 'source': item.get('source'),
                    'link': item.get('link'), 'pubDate': item.get('pubDate'),
                })

        return results

    except urllib.error.URLError as e:
        return {'error': str(e)}
    except Exception as e:
        return {'error': f'Error inesperado: {str(e)}'}


def router(action: dict) -> dict:
    tool = action['tool_name']
    args = action['args']

    if tool == 'v1_search':
        return {'result': connect_api(args.get('search'), '', '', '', '', '', '', '', '')}
    elif tool == 'v1_market_quotes':
        return {'result': connect_api('', args.get('ticker'), args.get('type', 'STOCKS'), '', '', '', '', '', '')}
    elif tool == 'v1_stock_modules':
        return {'result': connect_api('', args.get('ticker'), '', args.get('module', 'asset-profile,financial-data,earnings'), '', '', '', '', '')}
    elif tool == 'v2_stock_history':
        return {'result': connect_api('', '', '', '', args.get('symbol'), args.get('interval', '1d'), args.get('limit', '1y'), args.get('dividend', 'false'), '')}
    elif tool == 'v1_market_screener':
        return {'result': connect_api('', '', '', '', '', '', '', '', args.get('list'))}
    elif tool == 'v2_market_news':
        return {'result': connect_api('', args.get('ticker'), '', '', '', '', '', '', '')}
    elif tool == 'terminate':
        return {'terminate': True}
    elif tool == 'error':
        return {'error': args.get('message', 'Error desconocido')}
    else:
        return {'error': f'Herramienta desconocida: {tool}'}


# ─── API routes ───────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


def load_system_prompt() -> str:
    prompt_path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'system_prompt.txt'))
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'You are Warren, an AI financial analyst assistant.'


@app.post('/api/chat')
async def chat(req: ChatRequest):
    """Stream agent responses via Server-Sent Events."""
    system_prompt = load_system_prompt()

    async def event_stream():
        messages = [{'role': 'system', 'content': system_prompt}]

        # Inject conversation history (last 20 turns)
        for msg in req.history[-20:]:
            if msg.get('role') in ('user', 'assistant'):
                messages.append({'role': msg['role'], 'content': msg['content']})

        # Add the new user message
        messages.append({'role': 'user', 'content': req.message})
        learn('user', req.message)

        # Agentic loop
        max_steps = 10
        for _ in range(max_steps):
            # Run LLM call in executor so we don't block the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, generate_response, messages)

            messages.append({'role': 'assistant', 'content': response})
            learn('assistant', response)

            terminate_msg = parse_terminate(response)
            if terminate_msg:
                yield f"data: {json.dumps({'type': 'terminate', 'content': terminate_msg})}\n\n"
                return

            if '```action' in response:
                action = parse_action(response)
                tool_name = action.get('tool_name', 'unknown')
                label = TOOL_LABELS.get(tool_name, f'Ejecutando {tool_name}...')

                yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name, 'label': label})}\n\n"
                await asyncio.sleep(0)  # flush

                result = await loop.run_in_executor(None, router, action)

                if result.get('terminate'):
                    yield f"data: {json.dumps({'type': 'terminate', 'content': '¡Hasta pronto, Santi!'})}\n\n"
                    return

                yield f"data: {json.dumps({'type': 'tool_done', 'tool': tool_name})}\n\n"

                result_str = json.dumps(result)
                messages.append({'role': 'user', 'content': result_str})
                learn('user', result_str)

            else:
                # Final answer — send as markdown
                yield f"data: {json.dumps({'type': 'message', 'content': response})}\n\n"
                return

        yield f"data: {json.dumps({'type': 'error', 'content': 'El agente alcanzó el límite de pasos. Intenta reformular tu pregunta.'})}\n\n"

    return StreamingResponse(event_stream(), media_type='text/event-stream')


@app.get('/api/history')
async def get_history():
    """Return last 40 messages from memory."""
    messages = remember(limit=40)
    return {'messages': messages}


@app.delete('/api/history')
async def clear_history():
    """Clear conversation memory."""
    conn, cur = get_db()
    cur.execute('DELETE FROM Brain')
    conn.commit()
    conn.close()
    return {'status': 'cleared'}


# Serve the frontend
@app.get('/')
async def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), 'static', 'index.html'))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)
