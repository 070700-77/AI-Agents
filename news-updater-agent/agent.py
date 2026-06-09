import os
import ssl
import sqlite3
import json
from litellm import completion
from dotenv import load_dotenv
import urllib.request, urllib.parse, urllib.error

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
X_RAPIDAPI_KEY = os.environ.get('X_RAPIDAPI_KEY')

conn = sqlite3.connect('memory.db')
cur = conn.cursor()


def brain():
    cur.execute('''CREATE TABLE IF NOT EXISTS Brain (id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT, content TEXT,
    date TEXT DEFAULT CURRENT_TIMESTAMP)''')
    return None


def remember(limit: int = 20):
    cur.execute('''SELECT role, content FROM Brain ORDER BY id DESC LIMIT (?)''', (limit,))
    rows = cur.fetchall()
    return [{'role': row[0], 'content': row[1]} for row in reversed(rows)]


def learn(role: str, content: str):
    cur.execute('''INSERT INTO Brain (role, content) VALUES (?,?)''',(role, content))
    conn.commit()
    return None


def generate_response(messages: list[dict]) -> str:
    response = completion(model = 'anthropic/claude-sonnet-4-5',
                         messages = messages,
                         max_tokens = 1024)
    return response.choices[0].message.content


def parse_terminate(response: str) -> str | None:
    try:
        if '```terminate' in response:
            json_string = response.split('```terminate')[1].split('```')[0].strip()
            data = json.loads(json_string)
            return data.get('Terminate','Goodbye!')
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
        tool = data.get('tool_name', None)
        args = data.get('args', None)
        
        if tool is None or args is None:
            return {'tool_name': 'error', 'args': {'message': 'You must respond with tool_name and args.'}}
        return {'tool_name': tool, 'args': args}
    
    except json.JSONDecodeError:
        return {'tool_name': 'error', 'args': {'message': 'Invalid JSON response format.'}}
    return None

    
def access_news_api(topic, limit, country, lang):
    try:
        base_url = 'https://real-time-news-data.p.rapidapi.com/topic-headlines'

        query_string = {
        'topic': topic,
        'limit': limit,
        'country': country,
        'lang':lang
        }

        headers = {
        "x-rapidapi-key": X_RAPIDAPI_KEY,
        "x-rapidapi-host": "real-time-news-data.p.rapidapi.com",
        "Content-Type": "application/json"
        }

        query_encoded = urllib.parse.urlencode(query_string)
        full_url = base_url + '?' + query_encoded
        
        req = urllib.request.Request(full_url, headers=headers)
        access = urllib.request.urlopen(req, context = ctx)

        info = access.read().decode()
        data = json.loads(info)
        
        results = []
        for item in data['data']:
            results.append({
            'title':  item['title'],
            'link': item['link'],
            'published_datetime_utc': item ['published_datetime_utc'],
            'source_name': item['source_name']    
            })
        return results
        
    except urllib.error.URLError as e:
        return {'result': str(e)}
    
    return None

def router (parse_action_result):
    if parse_action_result['tool_name'] == 'access_news_api':
        topic = parse_action_result['args']['topic']
        limit = parse_action_result['args']['limit']
        country = parse_action_result['args']['country']
        lang = parse_action_result['args']['lang']
        connect = access_news_api(topic, limit, country, lang)
        return {'result': connect}
    
    elif parse_action_result["tool_name"] == "terminate":
        print('The tool use has been ceased\n')
        return '```terminate'
    
    elif parse_action_result["tool_name"] == "error":
        file_error = parse_action_result['args']['message']
        return {'error': file_error}
    
    else:
        return {"error": "Unknown tool: " + parse_action_result["tool_name"]}
    return None


def action(messages: list[dict]):
    while True:
        prompt = input('You: ')
        if not prompt:
            print('\n'+'x'*55)
            print('Insert a valid input.')
            continue
        
        messages.append({'role': 'user', 'content': prompt})
        learn('user', prompt)
        
        while True:
            response = generate_response(messages)
            messages.append({'role': 'assistant', 'content': response})
            learn('assistant', response)
            
            if '```action' in response:
                print('\n' + '.'*50)
                print("  Accessing to agentic tools.")
                print('.'*50)
                parse_action_result = parse_action(response)
                get_api_info = router(parse_action_result)
                messages.append({'role': 'user','content': json.dumps(get_api_info)})
                learn('user', json.dumps(get_api_info))
            else:
                print(f'Juli: {response}')
                terminate = parse_terminate(response)
                if terminate:
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
    with open('system_prompt.txt','r', encoding= 'utf-8') as pattern:
        behavior = pattern.read()
    
    brain()
    messages = [{'role':'system', 'content': behavior}]
    
    print('\n'+'='*55)
    print('Hi! Im Juli, your IA agent that can list files, read and word count them')
    print('='*55 + '\n')
    
    recall = remember(limit=20)
    if recall:
        print(f'\n  [📚 Loading {len(recall)} previous sessions messages...]')
        messages.extend(recall)
        
    action(messages)
        