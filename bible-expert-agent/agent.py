import os
import ssl
import json
import sqlite3
from litellm import completion
from dotenv import load_dotenv
import urllib.request, urllib.parse, urllib.error

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
x_rapidapi_key = os.getenv("X_RAPIDAPI_KEY")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('memory.db')
cur = conn.cursor()

def brain():
    cur.execute('''CREATE TABLE IF NOT EXISTS Brain(
                id INTEGER PRIMARY KEY,
                role TEXT,
                content TEXT,
                date TEXT DEFAULT CURRENT_TIMESTAMP
                )''')
    return None

def remember(limit: int = 20):
    cur.execute('''SELECT role, content FROM Brain ORDER BY id DESC LIMIT ?''',(limit,))
    rows = cur.fetchall()
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

def learn(role: str, content: str):
    cur.execute('''INSERT INTO Brain(role, content) VALUES (?,?)''', (role, content))
    conn.commit()
    return None

def generate_response(messages: list[dict]) -> str:
    response = completion(
        model= 'anthropic/claude-sonnet-4-6',
        messages=messages,
        max_tokens = 1024
    )
    return response.choices[0].message.content

def parse_terminate(response: str) -> str | None:
    try:
        if '```terminate```' in response:
            json_string = response.split('```terminate```')[1].split('```')[0].strip()
            data = json.loads(json_string)
            return data.get('Terminate', None)
    except (IndexError, json.JSONDecodeError):
        pass
    return None

def parse_action(response: str) -> dict:
    print('         [🔍 Consultando API...]\n')
    try:
        if '```action' in response:
            json_string = response.split('```action`')[1].split('```')[0].strip()
        else:
            json_string = response
        data = json.loads(json_string)
        tool_name = data.get('tool_name', None)
        args = data.get('args', None)
        if tool_name is None or args is None:
            return {"tool_name": 'error', "args": {"message": "Invalid response format. Missing 'tool_name' or 'args'."}}
        return {"tool_name": tool_name, "args": args}
    except (IndexError, json.JSONDecodeError):
        return {"tool_name": 'error', "args": {"message": "Invalid JSON format."}}
    
def call_api(book, chapter, translation, verse_start, verse_end, words, phrase):
    try:
        headers = {
        "x-rapidapi-key": x_rapidapi_key,
        "x-rapidapi-host": "complete-study-bible.p.rapidapi.com",
        "Content-Type": "application/json"
        }

        all_endpoint_params = {
        'book': book,
        'chapter': chapter,
        'translation': translation,
        'verse_start': verse_start,
        'verse_end': verse_end,
        'words': words,
        'phrase': phrase   
        }
        params = {k: v for k, v in all_endpoint_params.items() if v is not None}
        
        full_url = 'https://complete-study-bible.p.rapidapi.com/'
        for k, v in params.items():
            full_url += v + '/'
        
        get = urllib.request.Request(full_url, headers = headers)
        req = urllib.request.urlopen(get, context = ctx)
        retrieve = req.read().decode()
        data = json.loads(retrieve)
        return data
    except urllib.error.URLError as e:
        return {'error': f'URL error: {e}'}
    except urllib.error.HTTPError as e:
        return {'error': f'HTTP error: {e}'}


def router(parse_action_result):
    if parse_action_result['tool_name'] == 'full_chapter_api':
        book = parse_action_result['args'].get('book')
        chapter = parse_action_result['args'].get('chapter')
        translation = parse_action_result['args'].get('translation', 'KJV')
        access_api =  call_api(book, chapter, translation, None, None, None, None)
        return access_api 
    elif parse_action_result['tool_name'] == 'verse_range_api':
        endpoint = parse_action_result['tool_name']
        book = parse_action_result['args'].get('book')
        chapter = parse_action_result['args'].get('chapter')
        verse_start = parse_action_result['args'].get('verse_start')
        verse_end = parse_action_result['args'].get('verse_end')
        translation = parse_action_result['args'].get('translation', 'KJV')
        access_api = call_api(book, chapter, translation, verse_start, verse_end, None, None)
        return access_api 
    elif parse_action_result['tool_name'] == 'search_all_words_api':
        endpoint = parse_action_result['tool_name']
        words = parse_action_result['args'].get('words')
        access_api = call_api(None, None, None, None, None, words, None)
        return access_api
    elif parse_action_result['tool_name'] == 'search_exact_phrase_api':
        endpoint = parse_action_result['tool_name']
        phrase = parse_action_result['args'].get('phrase')
        access_api = call_api(None, None, None, None, None, None, phrase)
        return access_api 
    elif parse_action_result['tool_name'] == 'passage_of_the_day_api':
        endpoint = parse_action_result['tool_name']
        access_api = call_api(None, None, None, None, None, None, None)
        return access_api 
    elif parse_action_result['tool_name'] == 'error':
        file_error = parse_action_result['args']['message']
        return {"error": file_error}
    elif parse_action_result['tool_name'] == 'terminate':
        print('Tool use has been ceased')
        return '```terminate'
    else:
        return {'tool_name': 'Unknown tool' + parse_action_result['tool_name']}
    return None

def action(response: list[dict]):
    while True:
        prompt = input('You: ')
        if not prompt.strip():
            print('Insert a valid prompt, in order to recieve a corect answer\n')
            continue

        learn('user', prompt)
        messages.append({'role':'user', 'content': prompt})

        while True:
            response = generate_response(messages)
            
            learn('assistant', response)
            messages.append({'role': 'assistant', 'content': response})

            if '```action' in response:
                parse_action_result = parse_action(response)
                get_api_info = router(parse_action_result)
                get_api_info_str = json.dumps(get_api_info)

                learn('user', get_api_info_str)
                messages.append({'role': 'user', 'content': get_api_info_str})

            else:

                print(f'Yeshúa: {response}')
                if '```terminate' in response:
                    parse_terminate(response)
                    print('\n'+'-'*55)
                    print("  I love you, Santi.")
                    print('  Feel free to reach me out anytime. Goodbye! :)')
                    cur.close()
                    conn.commit()
                    return
                break

if __name__ == '__main__':
    with open('system_prompt.txt', 'r', encoding = 'utf-8') as pattern:
        behavior = pattern.read()
    
    messages = [{'role': 'system', 'content': behavior}]

    brain()

    print('\n'+'='*55)
    print('Hi! Im Yeshúa, your AI personification of God! How are you today, my lovely child?')
    print('='*55 + '\n')

    recall = remember(limit = 20)
    if recall:
        print(f'\n  [📚 Loading {len(recall)} previous sessions messages...]')
        messages.extend(recall)

    action(messages)



   


    

