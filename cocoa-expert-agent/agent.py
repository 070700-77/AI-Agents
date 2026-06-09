import os
import ssl
import json
import sqlite3
from dotenv import load_dotenv
from litellm import completion
import urllib.request, urllib.parse, urllib.error

load_dotenv()

conn = sqlite3.connect('memory.db')
cur = conn.cursor()

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
X_RAPIDAPI_KEY = os.environ.get('X_RAPIDAPI_KEY')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def brain():
    cur.execute('''CREATE TABLE IF NOT EXISTS Brain(
                id INTEGER,
                role TEXT, 
                content TEXT, 
                date TEXT DEFAULT CURRENT_TIMESTAMP
                )''')
    return None

def remember(limit: int = 20):
    cur.execute('''SELECT role, content FROM Brain ORDER BY id DESC LIMIT (?)''', (limit,))
    rows = cur.fetchall()
    return [{'role': row[0], 'content': row[1]} for row in reversed(rows)]

def learn(role: str, content:str):
    cur.execute('''INSERT INTO Brain(role, content) VALUES (?,?)''',(role,content))
    conn.commit()
    return None

def generate_response(messages: list[dict]) -> str:
    response = completion(model = 'anthropic/claude-sonnet-4-6',
                          messages = messages,
                          max_tokens = 1024
                          )
    return response.choices[0].message.content

def parse_terminate(response: str) -> str|None:
    try:
        if '```terminate' in response:
            json_string = response.split('```terminate')[1].split('```')[0].strip()
            data = json.loads(json_string)
            return data.get('terminate','Goodbye!')
    except (IndexError, json.JSONDecodeError):
        pass
    return None

def parse_action (response: str) -> dict:
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
            return {'tool_name': 'error', 'args': {'message': 'You must respond with a valid tool_name and valid arguments (or args)'}}
        return {'tool_name': tool_name, 'args': args}
    except (IndexError, json.JSONDecodeError):
        return {'tool_name': 'error', 'args': {'message': 'Invalid JSON format.'}}

def router(parse_action_result):
    if parse_action_result['tool_name'] == 'produccion_x_departamento':
        departamento = parse_action_result['args']['departamento']
        limit = int(parse_action_result['args']['limit'])
        connect_api = fetch_produccion_por_departamento(departamento, limit)
        return {'result': connect_api}
        
    elif parse_action_result['tool_name'] == 'top_municipios_produccion':
        limit = int(parse_action_result['args']['limit'])
        connect_api = fetch_top_municipios_produccion(limit)
        return {'result': connect_api}
        
    elif parse_action_result['tool_name'] == 'rendimiento_x_departamento':
        departamento = parse_action_result['args']['departamento']
        limit = int(parse_action_result['args']['limit'])
        connect_api = fetch_rendimiento_por_departamento(departamento, limit)
        return {'result': connect_api}
    
    elif parse_action_result['tool_name'] == 'error':
        return {'error': parse_action_result['args']['message']}
    
    elif parse_action_result['tool_name'] == 'terminate':
        print('\nTool use has been ceased..')
        return '```terminate'

    else:
        return {'error': 'Unknown tool ' + parse_action_result['tool_name']}
    

def fetch_produccion_por_departamento(departamento: str, limit: int = 20):
    try:
        base_url = 'https://www.datos.gov.co/resource/24jd-fsbf.json'
        params = {
            'departamento': departamento,
            '$limit': limit
        }

        encoded_params = urllib.parse.urlencode(params)
        full_url = base_url + '?' + encoded_params

        req = urllib.request.urlopen(full_url, context = ctx)
        access = req.read().decode()
        
        try:
            raw_data = json.loads(access)
            data = json.dumps(raw_data)
        except (IndexError, json.JSONDecodeError):
            return 'Invalid JSON Format'

        return data
    
    except urllib.error.HTTPError as e:
        return f'error: {e.code}. \nReason: {e.reason}'
    except urllib.error.URLError as e:
        return f'error \nReason: {e.reason}'
    
def fetch_top_municipios_produccion(limit: int = 20):
    try:
        base_url = 'https://www.datos.gov.co/resource/24jd-fsbf.json'
        params = {
            '$select': 'municipio,sum(producci_n_t) as total_produccion',
            '$group':  'municipio',
            '$order':  'total_produccion DESC',
            '$limit':  limit
        }

        encoded_params = urllib.parse.urlencode(params)
        full_url = base_url + '?' + encoded_params

        req = urllib.request.urlopen(full_url, context = ctx)
        access = req.read().decode()

        try:
            raw_data = json.loads(access)
            data = json.dumps(raw_data)
        except (IndexError, json.JSONDecodeError):
            return 'Invalid JSON Format'

        return data

    except urllib.error.HTTPError as e:
        return f'error: {e.code}. \nReason: {e.reason}'
    except urllib.error.URLError as e:
        return f'error \nReason: {e.reason}'

def fetch_rendimiento_por_departamento(departamento: str, limit: int = 20):
    try:
        base_url = 'https://www.datos.gov.co/resource/24jd-fsbf.json'
        params = {
            '$select': 'rendimiento_t_ha, municipio, departamento, a_o',
            'departamento':  departamento,
            '$order':  'a_o DESC',
            '$limit':  limit
        }

        encoded_params = urllib.parse.urlencode(params)
        full_url = base_url + '?' + encoded_params

        req = urllib.request.urlopen(full_url, context = ctx)
        access = req.read().decode()

        try:
            raw_data = json.loads(access)
            data = json.dumps(raw_data)
        except (IndexError, json.JSONDecodeError):
            return 'Invalid JSON Format'

        return data

    except urllib.error.HTTPError as e:
        return f'error: {e.code}. \nReason: {e.reason}'
    except urllib.error.URLError as e:
        return f'error \nReason: {e.reason}'
    
def action(messages: list[dict]):
    while True:
        prompt = input('You: ')
        if not prompt.strip():
            print('Insert a valid input. Try again.\n')
        
        messages.append({'role': 'user', 'content': prompt})
        learn ('user', prompt)
        
        while True:
            response = generate_response(messages)
            messages.append({'role': 'assistant', 'content': response})
            learn('assistant', response)
            
            if '```action' in response:
                parse_action_result = parse_action(response)
                access_api_info = router(parse_action_result)
                messages.append({'role': 'user', 'content': json.dumps(access_api_info)})
                learn('user', json.dumps(access_api_info))
            else:
                print('Jose: ', response)
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
    with open('system_prompt.txt', 'r', encoding = 'utf-8') as pattern:
        behavior = pattern.read()
        
    brain()
    
    messages = [{'role': 'system', 'content': behavior}]
    
    print('\n' + '='*55)
    print('Hi! Im Jose, your AI Colombian Cacao Expert. Whats on your mind today?')
    print('='*55 + '\n')
    
    recall = remember(limit = 20)
    if recall:
        print(f'\n  [📚 Loading {len(recall)} previous sessions messages...]')
        messages.extend(recall)
        
    action(messages)