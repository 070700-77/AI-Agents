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

conn = sqlite3.connect('memory.db')
cur = conn.cursor()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def brain():
    cur.execute('''CREATE TABLE IF NOT EXISTS financial_teacher (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                date TEXT DEFAULT CURRENT_TIMESTAMP
                )'''
               )     
    return None

def remember(limit: int = 20):
    cur.execute('''SELECT role, content, date FROM financial_teacher ORDER BY date DESC LIMIT ?''', (limit,))
    rows = cur.fetchall()
    conn.commit()
    return [{'role': row[0], 'content': row[1]} for row in reversed(rows)]

def learn(role:str, content:str):
    cur.execute('''INSERT INTO financial_teacher (role, content) VALUES (?, ?)''', (role, content))
    conn.commit()
    return None

def generate_response(messages: list[dict]) -> str:
    response = completion(
        model = 'anthropic/claude-sonnet-4-6',
        messages = messages,
        max_tokens = 1024
    )
    return response.choices[0].message.content

def parse_terminate(response: str) -> str | None:
    try:
        if '```terminate' in response:
            json_string = response.split('```terminate')[1].split('```')[0].strip()
            data = json.loads(json_string)
            return data.get('Terminate', 'Goodbye!')
    except (IndexError, json.JSONDecodeError):
        pass
    return None

def parse_action(response: str) -> dict:
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
            return {'tool_name': 'error', 'args': {'message': 'Invalid response format. Missing "tool_name" or "args".'}}
        return {'tool_name': tool_name, 'args': args}
    except (IndexError, json.JSONDecodeError):
        return {'tool_name': 'error', 'args': {'message': 'Invalid JSON format.'}}

def connect_api(tool, symbol, language, period):
    try:
        headers = {
	    "x-rapidapi-key": x_rapidapi_key,
	    "x-rapidapi-host": "real-time-finance-data.p.rapidapi.com",
	    "Content-Type": "application/json"
        } 

        if tool == 'company_overview':
            url = 'https://real-time-finance-data.p.rapidapi.com/stock-overview'
        elif tool == 'company_income_statement':
            url = 'https://real-time-finance-data.p.rapidapi.com/company-income-statement'
        elif tool == 'company_balance_sheet':
            url = 'https://real-time-finance-data.p.rapidapi.com/company-balance-sheet'
        else:
            url = 'https://real-time-finance-data.p.rapidapi.com/company-cash-flow'

        full_endpoint_params = {
            'symbol': symbol,
            'language': language,
            'period': period
            } 

        params = {key: value for key, value in full_endpoint_params.items() if value is not None}

        full_url = url + '?' + urllib.parse.urlencode(params)

        request = urllib.request.Request(full_url, headers=headers)
        access = urllib.request.urlopen(request, context=ctx)

        get = access.read().decode()
        data = json.loads(get)

        results = []

        if tool == 'company_overview':
            stock_data = data["data"]
            results.append({
            "symbol_" : stock_data["symbol"],
            "name" : stock_data["name"],
            "stock_type" : stock_data["type"],
            "price" : stock_data["price"],
            "open_price" : stock_data["open"],
            "high" : stock_data["high"],
            "low" : stock_data["low"],
            "volume" : stock_data["volume"],
            "previous_close" : stock_data["previous_close"],
            "change" : stock_data["change"],
            "change_percent" : stock_data["change_percent"],
            "exchange" : stock_data["exchange"],
            "currency" : stock_data["currency"],
            "timezone" : stock_data["timezone"],
            "last_update_utc" : stock_data["last_update_utc"],
            "company_website" : stock_data["company_website"],
            "company_country" : stock_data["company_country"],
            "company_city" : stock_data["company_city"],
            "company_ceo" : stock_data["company_ceo"],
            "company_employees" : stock_data["company_employees"],
            "company_industry" : stock_data["company_industry"],
            "company_sector" : stock_data["company_sector"],
            "market_cap" : stock_data["company_market_cap"],
            "pe_ratio" : stock_data["company_pe_ratio"],
            "dividend_yield" : stock_data["company_dividend_yield"],
            "year_low" : stock_data["year_low"],
            "year_high" : stock_data["year_high"],
            "avg_volume" : stock_data["avg_volume"],
            })
            return results
        elif tool == 'company_income_statement':
            financial_data = data["data"]
            income_statements = financial_data["income_statement"]
            results.append({
                "symbol" : financial_data["symbol"],
                "stock_type" : financial_data["type"],
                "period" : financial_data["period"]
            })
            for statement in income_statements:
                date = statement["date"]
                year = statement["year"]
                month = statement["month"]
                day = statement["day"]
                currency = statement["currency"]
                revenue = statement["revenue"]
                operating_expense = statement["operating_expense"]
                net_income = statement["net_income"]
                net_profit_margin = statement["net_profit_margin"]
                earnings_per_share = statement["earnings_per_share"]
                ebitda = statement["EBITDA"]
                effective_task_rate_percent = statement["effective_task_rate_percent"]
                results.append({
                    "date" : date,
                    "year" : year,
                    "month" : month,
                    "day" : day,
                    "currency" : currency,
                    "revenue" : revenue,
                    "operating_expense" : operating_expense,
                    "net_income" : net_income,
                    "net_profit_margin" : net_profit_margin,
                    "earnings_per_share" : earnings_per_share,
                    "ebitda" : ebitda,
                    "effective_task_rate_percent" : effective_task_rate_percent                
                    })
            return results

        elif tool == 'company_balance_sheet':
            financial_data = data["data"]
            balance_sheets = financial_data["balance_sheet"]
            results.append({
                "symbol" : financial_data["symbol"],
                "stock_type" : financial_data["type"],
                "period" : financial_data["period"]
            })
            for balance in balance_sheets:
                date = balance["date"]
                year = balance["year"]
                month = balance["month"]
                day = balance["day"]
                currency = balance["currency"]
                cash = balance["cash_and_short_term_investments"]
                total_assets = balance["total_assets"]
                total_liabilities = balance["total_liabilities"]
                total_equity = balance["total_equity"]
                shares_outstanding = balance["shares_outstanding"]
                price_to_book = balance["price_to_book"]
                return_on_assets = balance["return_on_assets_percent"]
                return_on_capital = balance["return_on_capital_percent"]
                results.append({
                    "date" : date,
                    "year" : year,
                    "month" : month,
                    "day" : day,
                    "currency" : currency,
                    "cash" : cash,
                    "total_assets" : total_assets,
                    "total_liabilities" : total_liabilities,
                    "total_equity" : total_equity,
                    "shares_outstanding" : shares_outstanding,
                    "price_to_book" : price_to_book,
                    "return_on_assets" : return_on_assets,
                    "return_on_capital" : return_on_capital
                    })
            return results
        else:
            financial_data = data["data"]
            cash_flows = financial_data["cash_flow"]
            results.append({
                "symbol" : financial_data["symbol"],
                "stock_type" : financial_data["type"],
                "period" : financial_data["period"]
            })
            for cash_flow in cash_flows:
                date = cash_flow["date"]
                year = cash_flow["year"]
                month = cash_flow["month"]
                day = cash_flow["day"]
                currency = cash_flow["currency"]
                net_income = cash_flow["net_income"]
                cash_from_operations = cash_flow["cash_from_operations"]
                cash_from_investing = cash_flow["cash_from_investing"]
                cash_from_financing = cash_flow["cash_from_financing"]
                net_change_in_cash = cash_flow["net_change_in_cash"]
                free_cash_flow = cash_flow["free_cash_flow"]
                results.append({
                    "date" : date,
                    "year" : year,
                    "month" : month,
                    "day" : day,
                    "currency" : currency,
                    "net_income" : net_income,
                    "cash_from_operations" : cash_from_operations,
                    "cash_from_investing" : cash_from_investing,
                    "cash_from_financing" : cash_from_financing,
                    "net_change_in_cash" : net_change_in_cash,
                    "free_cash_flow" : free_cash_flow
                    })
            return results              
    except urllib.error.HTTPError as e:
        return {'error': f'HTTP error occurred: {e.code} - {e.reason}'}
    except urllib.error.URLError as e:
        return {'error': f'URL error occurred: {e.reason}'}

def router(parse_action_result) -> dict:
    
    if parse_action_result['tool_name'] == 'company_overview':
        symbol = parse_action_result['args'].get('symbol', None)
        language = parse_action_result['args'].get('language', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(tool, symbol, language, None)
        return {'result': api_data}
    elif parse_action_result['tool_name'] == 'company_income_statement':
        symbol = parse_action_result['args'].get('symbol', None)
        language = parse_action_result['args'].get('language', None)
        period = parse_action_result['args'].get('period', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(tool, symbol, language, period)
        return {'result': api_data}
    elif parse_action_result['tool_name'] == 'company_balance_sheet':
        symbol = parse_action_result['args'].get('symbol', None)
        language = parse_action_result['args'].get('language', None)
        period = parse_action_result['args'].get('period', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(tool, symbol, language, period)
        return {'result': api_data}
    elif parse_action_result['tool_name'] == 'company_cash_flow':
        symbol = parse_action_result['args'].get('symbol', None)
        language = parse_action_result['args'].get('language', None)
        period = parse_action_result['args'].get('period', None)
        tool = parse_action_result['tool_name']
        api_data = connect_api(tool, symbol, language, period)
        return {'result': api_data}
    elif parse_action_result['tool_name'] == 'error':
        return {'result': parse_action_result['args']['message']}
    else:
        return {'result': 'Unknown tool_name.'}

def action(messages: list[dict]):
    while True:
        prompt = input("You: ")
        if not prompt.strip():
            print("Prompt cannot be empty.")
            continue

        learn('user', prompt)
        messages.append({'role': 'user', 'content': prompt})
        while True:
            response = generate_response(messages)
            learn('assistant', response)
            messages.append({'role': 'assistant', 'content': response})

            if '```action' in response:
                parse_action_result = parse_action(response)
                api_result = router(parse_action_result)
                learn('user', json.dumps(api_result))
                messages.append({'role': 'user', 'content': json.dumps(api_result)})
            else:
                print('Ray Dalio: ', response)

                if '```terminate' in response:
                    terminate_message = parse_terminate(response)
                    print('Termination message:', terminate_message)
                    return
                break

if __name__ == "__main__":
    with open('system_prompt.txt', 'r', encoding='utf-8') as pattern:
        behavior = pattern.read()

    brain()

    messages = [{'role': 'system', 'content': behavior}]

    print("Welcome to the Financial Teacher AI Agent!. Im here to help you learn about finance and investing. You can ask me questions")

    recall = remember(limit=20)
    if recall:
        print("Recalling previous conversations:")
        messages.extend(recall)

    action(messages)