# https://rapidapi.com/dbarkman/api/everyearthquake/playground/apiendpoint_a597312d-8ef5-4d07-b953-755834c635f5
import os
import ssl
import json
import sqlite3
import urllib.request, urllib.parse, urllib.error
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
x_rapidapi_key = os.getenv("X_RAPIDAPI_KEY")

conn =sqlite3.connect('memory.db')
cur = conn.cursor()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def brain():
    cur.execute('''CREATE TABLE IF NOT EXISTS Brain (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    content TEXT, 
    date TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    return None

def remember(limit : int = 20):
    cur.execute('''SELECT role, content FROM Brain ORDER BY ID DESC LIMIT ?''', (limit,))
    rows = cur.fetchall()
    return [{'role': row[0], 'content': row[1]} for row in reversed(rows)]

def learn(role, content):
    cur.execute('''INSERT INTO Brain(role, content) VALUES (?,?)''', (role, content))
    conn.commit()
    return None

def generate_response(messages: list[dict]) -> str:
    response = completion(model= 'anthropic/claude-sonnet-4-6',
                        messages= messages,
                        max_tokens = 1024  
                        )
    return response.choices[0].message.content

def parse_terminate(response: str) -> str|None:
    try:
        if '```terminate' in response:
            json_string = response.split('```terminate')[1].split('```')[0]
            data = json.loads(json_string)
            return data.get('terminate', 'Goodbye!')
    except (IndexError, json.JSONDecodeError):
        pass
    
def parse_action(response: str) -> dict:
    print('         [🔍 Consultando API...]\n')
    try:
        if '```action' in response:
            json_string = response.split('```action')[1].split('```')[0]
        else:
            json_string = response
        data = json.loads(json_string)
        tool_name = data.get('tool_name', None)
        args = data.get('args', None)
        if tool_name is None or args is None:
            return {'tool_name': 'error', 'args': {'message': 'You must respond with a valid tool_name and valid arguments (or args)'}}
        return {'tool_name': tool_name, 'args': args}
    except (IndexError, json.JSONDecodeError):
        return {'tool_name': 'error', 'args': {'message': 'Invalid JSON format'}}
    
def call_api(interval, start, count, type_, latitude, longitude, radius, units, magnitude, intensity):
    try:
        headers = {
        "x-rapidapi-key": x_rapidapi_key,
        "x-rapidapi-host": "everyearthquake.p.rapidapi.com",
        "Content-Type": "application/json"
        }

        base_url = "https://everyearthquake.p.rapidapi.com/recentEarthquakes"

        endpoint_params = {
            "interval": interval,
            "start": start,
            "count": count,
            "type": type_,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "units": units,
            "magnitude": magnitude,
            "intensity": intensity
        }

        params = {k: v for k, v in endpoint_params.items() if v is not None}

        req =urllib.request.Request(base_url, headers=headers)
        get = urllib.request.urlopen(req, context=ctx)

        retrieve = get.read().decode()
        data = json.loads(retrieve)
        return data
    except urllib.error.URLError as e:
        return {'error': f'URL error: {e}'}
    except urllib.error.HTTPError as e:
        return {'error': f'HTTP error: {e}'}




def router(parse_action_result):
    if parse_action_result['tool_name'] == 'recent_earthquakes':
        interval = parse_action_result['args'].get('interval')
        start = parse_action_result ['args'].get('start', None)
        count = parse_action_result ['args'].get('count', None)
        type_ = parse_action_result ['args'].get('type', None)
        latitude = parse_action_result ['args'].get('latitude', None)
        longitude = parse_action_result ['args'].get('longitude', None)
        radius = parse_action_result ['args'].get('radius', None)
        units = parse_action_result ['args'].get('units', None)
        magnitude = parse_action_result ['args'].get('magnitude', None)
        intensity = parse_action_result ['args'].get('intensity', None)
        access_api = call_api(interval, start, count, type_, latitude, longitude, radius, units, magnitude, intensity)
        return access_api

    elif parse_action_result['tool_name'] == 'terminate':
        return '```terminate'

    else:
        return {'tool_name': 'unknown tool {parse_action_result["tool_name"]}'}
    return None

def action(messages: list[dict]):
    while True:
        prompt = input("Enter your prompt: ")
        if not prompt.strip():
            print("Prompt cannot be empty. Please enter a valid prompt.")
            return

        learn('user', prompt)
        messages.append({'role': 'user', 'content': prompt})
        while True:
            response = generate_response(messages)
            learn ('assistant', response)
            messages.append({'role': 'assistant', 'content': response})

            if '```action' in response:
                parse_action_result = parse_action(response)
                api_result = router(parse_action_result)
                clean_data = json.dumps(api_result)

                learn('user', clean_data)
                messages.append({'role': 'user', 'content': clean_data})

            else:
                print(f'Topo: {response}\n')

                if '```terminate' in response:
                    parse_terminate(response)
                    print('---------\n')
                    print('Tool use has been ceased. Goodbye!')
                    print('---------\n')
                    return
                break


if __name__ == "__main__":
    with open('system_prompt.txt', 'r', encoding='utf-8') as pattern:
        behavior = pattern.read()

    brain()
    
    print("Bienvenido, soy Topo, tu asistente para información sobre terremotos recientes. Puedes hacer preguntas y obtener información detallada.\n")

    messages = [{'role': 'system', 'content': behavior}]

    recall = remember(limit =20)
    if recall:
        print("Recordando conversaciones previas:")
        messages.extend(recall)

    print("\n En que te puedo ayudar hoy?:\n")

    action(messages)


