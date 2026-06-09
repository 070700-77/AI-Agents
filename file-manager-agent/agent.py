import os
import json
import sqlite3
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

conn = sqlite3.connect('memory.db')
cur = conn.cursor()

def brain():
    cur.execute('''CREATE TABLE IF NOT EXISTS Brain (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    role TEXT, 
    content TEXT, 
    date TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    return None

def remember(limit: int = 20):
    cur.execute('''SELECT role, content FROM Brain ORDER BY id DESC LIMIT (?)''', (limit,))
    rows = cur.fetchall()
    return [{'role': row[0], 'content': row[1]} for row in reversed(rows)]

def learn (role: str, content: str):
    cur.execute('''INSERT INTO Brain (role, content) VALUES (?,?)''', (role, content))
    conn.commit()
    return None

def parse_terminate(response: str) -> str | None:
    try:
        if '```terminate' in response:
            json_string = response.split('```terminate')[1].split('```')[0].strip()
            data = json.loads(json_string)
            return data.get('terminate','Goodbye!')
    except (IndexError, json.JSONDecodeError):
        pass
    return None

def generate_response (messages: list[dict]) -> str:
    response = completion(model = 'anthropic/claude-sonnet-4-5',
                         messages = messages,
                         max_tokens = 1024)
    return response.choices[0].message.content

def parse_action(response: str) -> dict:
    try:
        if '```action' in response:
            json_string = response.split('```action')[1].split('```')[0].strip()
        else:
            json_string = response
        data = json.loads(json_string)
        tool = data.get('tool_name', None)
        args = data.get('args', None)
        if tool is None or args is None:
            return {"tool_name": "error", "args": {"message": "You must respond with tool_name and args."}}
        return {'tool_name': tool, 'args': args}
            
    except (json.JSONDecodeError):
        return {"tool_name": "error", "args": {"message": "Invalid JSON response."}}
        pass
    return None  

def list_files():
    return os.listdir('.')

def read_file(file_name):
    try:
        with open(file_name, 'r', encoding = 'utf-8') as fhandle:
            read = fhandle.read()
            return read
    except FileNotFoundError:
        print('It was unable to access file')
        return None

def word_count(file_name):
    try:
        with open(file_name, 'r', encoding = 'utf-8') as fhandle:
            read = fhandle.read()
            count = len(read.split())
            return count
    except FileNotFoundError:
        print('It was unable to access file...\n')
        return None

def execute_tool(parse_action_result):
    
    if parse_action_result["tool_name"] == 'list_files':
        return {'result': list_files()}
    
    elif parse_action_result["tool_name"] == 'read_file':
        file_name = parse_action_result['args']['file_name']
        return {'result': read_file(file_name)}
    
    elif parse_action_result["tool_name"] == 'word_count':
        file_count = parse_action_result['args']['file_name']
        return {'result': word_count(file_count)}
    
    elif parse_action_result["tool_name"] == "terminate":
        print('The tool use has been ceased\n')
        return '```terminate'
    
    elif parse_action_result["tool_name"] == "error":
        file_error = parse_action_result['args']['message']
        return {'error': file_error}
    
    else:
        return {"error": "Unknown tool: " + parse_action_result["tool_name"]}

def action(messages: list[dict]):
    while True:                                    # loop externo — espera input
        prompt = input('\nYou: ')
        if not prompt.strip():
            print('\n'+'x'*55)
            print('Enter a valid input. Try again\n')
            continue

        messages.append({'role': 'user', 'content': prompt})
        learn('user', prompt)

        while True:                                # loop interno — ciclo agéntico
            response = generate_response(messages)
            messages.append({'role': 'assistant', 'content': response})
            learn('assistant', response)

            if '```action' in response:
                print('\n' + '.'*50)
                print("  Accessing to agentic tools.")
                print('.'*50)
                parse_action_result = parse_action(response)
                result_content = execute_tool(parse_action_result)
                messages.append({'role': 'user', 'content': json.dumps(result_content)})
                learn('user', json.dumps(result_content))
                # sin break ni continue — el loop interno llama solo a generate_response

            else:
                print(f'Koda: {response}')
                terminate = parse_terminate(response)
                if terminate:
                    print('\n' + '='*50)
                    print("  It's always a pleasure helping you, Santi.")
                    print('  Feel free to reach me out anytime. Goodbye! :)')
                    print('='*50)
                    conn.commit()
                    cur.close()
                    conn.close()
                    return
                break                              # sale del loop interno
        
        
        if '```action' in response:
            print('\n' + '.'*50)
            print("  Accessing to agentic tools.")
            print('.'*50)
            parse_action_result = parse_action(response)
            result_content = execute_tool(parse_action_result)
            messages.append({'role': 'user','content': json.dumps(result_content)})
            memoryze = learn('user', json.dumps(result_content))
            continue

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
    with open('system_prompt.txt', 'r', encoding= 'utf-8') as pattern:
        behavior = pattern.read()
    
    brain()
    
    messages = [{'role': 'system', 'content': behavior}]
    
    print('\n'+'='*55)
    print('Hi! Im Koda, your IA agent that can list files, read and word count them')
    print('='*55 + '\n')
    
    
    recall = remember(limit = 20)
    
    if recall:
        print(f'loading {len(recall)} previous messages...')
        messages.extend(recall)
        
    action(messages)  