import os
import ssl
import json
import sqlite3
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
    cur.execute('''CREATE TABLE IF NOT EXISTS Brain(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    content TEXT,
    date TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    return None

def remember(limit: int= 20):
    cur.execute('''SELECT role, content FROM Brain ORDER BY id DESC LIMIT (?)''', (limit,))
    rows = cur.fetchall()
    return [{'role': row[0], 'content': row[1]} for row in reversed(rows)]

def learn(role: str, content: str):
    cur.execute('''INSERT INTO Brain(role, content) VALUES (?,?)''', (role, content))
    conn.commit()
    return None

def generate_response(messages: list[dict]) -> str:
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
            return data.get('Terminate', 'Goodbye!')
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
        if tool_name or args is None:
            return {'tool_name': 'error', 'args': {'message': 'You must respond with tool_name and args.'}}
        return{'tool_name': tool_name, 'args': args}
    except json.JSONDecodeError:
        return {'tool_name': 'error', 'args': {'message': 'invalid JSON format'}}
    return None

def connect_api(query, page, num_pages, country, language, location, date_posted, work_from_home, employment_types, job_requirements, radius, exclude_job_publishers, fields):
    try:
        base_url = 'https://linkedin-data-api.p.rapidapi.com/search-jobs'
        headers = {
        "x-rapidapi-key": X_RAPIDAPI_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
        "Content-Type": "application/json"
        }
        initial_params = {
        'query': query,
        'page': page,
        'num_pages': num_pages,
        'country': country,
        'language': language,
        'location': location,
        'date_posted': date_posted,
        'work_from_home': work_from_home,
        'employment_types': employment_types,
        'job_requirements': job_requirements,
        'radius': radius,
        'exclude_job_publishers': exclude_job_publishers,
        'fields': fields
        }

        # Filtrar solo los que NO son None
        querystring = {key: value for key, value in initial_params.items() if value is not None}
        encoded_querystring = urllib.parse.urlencode(querystring)
        full_url = base_url + '?' + encoded_querystring
        req = urllib.request.Request(full_url, headers = headers)
        access = urllib.request.urlopen(req, context = ctx)
        raw_info = access.read().decode()
        data = json.loads(raw_info)

        results = []
        for item in data['data']:
            results.append({
            "job_id": item['job_id'],
            "employer_name": item['employer_name'],
            "employer_logo": item['employer_logo'],
            "employer_website": item['employer_website'],
            "employer_company_type": item['employer_company_type'],
            "employer_linkedin": item['employer_linkedin'],
            "job_publisher": item['job_publisher'],
            "job_employment_type": item['job_employment_type'],
            "job_employment_type_text": item['job_employment_type_text'],
            "job_title": item['job_title'],
            "job_apply_link": item['job_apply_link'],
            "job_apply_is_direct": item['job_apply_is_direct'],
            "job_apply_quality_score": item['job_apply_quality_score'],
            "job_description": item['job_description'],
            "job_is_remote": item['job_is_remote'],
            "job_posted_human_readable": item['job_posted_human_readable'],
            "job_posted_at_timestamp": item['job_posted_at_timestamp'],
            "job_posted_at_datetime_utc": item['job_posted_at_datetime_utc'],
            "job_location": item['job_location'],
            "job_city": item['job_city'],
            "job_state": item['job_state'],
            "job_country": item['job_country'],
            "job_latitude": item['job_latitude'],
            "job_longitude": item['job_longitude']
            })
        return results
    except urllib.error.URLError as e:
        return {'result': str(e)}
    return None

def router(parse_action_result):
    if parse_action_result['tool_name'] == 'access_job_finder_api':
        query = parse_action_result['args']['query']
        page = parse_action_result['args']['page']
        num_pages = parse_action_result['args']['num_pages']
        country = parse_action_result['args']['country'] 
        language = parse_action_result['args']['language']
        location = parse_action_result['args']['location'] 
        date_posted = parse_action_result['args']['date_posted'] 
        work_from_home = parse_action_result['args']['work_from_home'] 
        employment_types = parse_action_result['args']['employment_types'] 
        job_requirements = parse_action_result['args']['job_requirements'] 
        radius = parse_action_result['args']['radius'] 
        exclude_job_publishers = parse_action_result['args']['exclude_job_publishers'] 
        fields = parse_action_result['args']['fields']
        connect = connect_api(query, page, num_pages, country, language, location, date_posted, work_from_home, employment_types, job_requirements, radius, exclude_job_publishers, fields)
        return {'result': connect}
    elif parse_action_result['tool_name'] == 'terminate':
        print('\nTool use has been ceased.')
        return '```terminate'
    elif parse_action_result['tool_name'] == 'error':
        file_error = parse_action_result['args']['message']
        return {'error': file_error}
    else:
        return {'error': 'Unknown tool' + parse_action_result['tool_name']}
    return None

def action(messages: list[dict]):
    while True:
        prompt = input('You: ')
        if not prompt.strip():
            print('\nInsert a valid input. Try again...\n')
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
                print('Joshua: ' + response)
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
        
if __name__ == "__main__":
    with open('system_prompt.txt', 'r', encoding = 'utf-8') as pattern:
        behavior = pattern.read()
    
    brain()
    
    messages = [{'role':'system','content': behavior}]
    
    print('\n'+'='*55)
    print('Hi! Im Joshua, your real-time job finder assistant.')
    print('='*55 + '\n')
    
    recall = remember(limit = 20)
    if recall:
        print(f'\n  [📚 Loading {len(recall)} previous sessions messages...]')
        messages.extend(recall)
    
    action(messages)