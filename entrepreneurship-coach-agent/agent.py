import os
import sqlite3
import json
from litellm import completion
from dotenv import load_dotenv


conn = sqlite3.connect('memory.db')
cur = conn.cursor()


load_dotenv()
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    raise ValueError("Missing ANTHROPIC_API_KEY")


def brain():
    cur.execute('''CREATE TABLE IF NOT EXISTS Brain (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    content TEXT,
    date TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    return None

def remember(limit : int = 20):
    cur.execute('''SELECT role, content FROM Brain ORDER BY id DESC LIMIT (?)''', (limit,))
    rows = cur.fetchall()
    return [{'role': row[0], 'content':row[1]} for row in reversed(rows)]

def learn(role: str, content: str):
    cur.execute('''INSERT INTO Brain (role, content) VALUES (?,?)''', (role, content))
    conn.commit()
    return None

def parse_terminate(response: str) -> str | None:
    try:
        if '```terminate' in response:
            json_string = response.split('```terminate')[1].split('```')[0]
            data = json.loads(json_string)
            return data.get('terminate','Goodbye!')
    
    except (IndexError, json.JSONDecodeError):
        pass
    return None

def generate_response(messages : list[dict]) -> str:
    response = completion(model = 'anthropic/claude-sonnet-4-5',
                         messages = messages,
                         max_tokens = 1024)
    return response.choices[0].message.content

def action(messages: list[dict]):
    while True:
        prompt = input('\nYou: ')
        if not prompt.strip():
            print('Enter a valid prompt, please.\n')
            continue
        
        messages.append({'role': 'user', 'content': prompt})
        understand = learn('user', prompt)
        
        response = generate_response(messages)
        print(f'\nRoy: {response}')
        
        messages.append({'role': 'assistant', 'content': response})
        understand = learn('assistant', response)
        
        terminate = parse_terminate(response)
        if terminate:
            print('\n' + '='*50)
            print("  It's always a pleasure helping you, Santi.")
            print('  Feel free to reach me out anytime. Goodbye! :)')
            print('='*50)
            conn.commit()
            cur.close()
            conn.close()
            break
    return None

if __name__ == '__main__':
    with open('system_prompt.txt','r', encoding = 'utf-8') as personality:
        behavior = personality.read()
        
    messages = [{'role': 'system', 'content': behavior}]
    
    wake_up = brain()
    
    print('\n' + '='*55)
    print('Hi! Im Roy, your AI Strategy and Entrepeneurship coach! How are you today?')
    print('='*55 + '\n')
    
    recall = remember(limit = 20)
    if recall:
        print(f'\n  [📚 Loading {len(recall)} previous sessions messages...]')
        messages.extend(recall)
        
    start = action(messages)