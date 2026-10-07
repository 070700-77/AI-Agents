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

def learn(role: str, content: str):
    cur.execute('''INSERT INTO Brain (role, content) VALUES (?,?)''', (role, content))
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
        if '```termninate' in response:
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
            return {'tool_name': 'error', 'args': {'message': 'You must respond with a valid tool_name and valid arguments (or args)'}}
        return {'tool_name': tool, 'args': args}
    except (IndexError, json.JSONDecodeError):
        return {'tool_name': 'error', 'args': {'message': 'Invalid JSON format'}}
    
def access_api(tool, age, sex, gender, height, weight, waist_circumference, unit, units, body_frame, formula, equation, activity_level, goal, climate, fitness_level, body_fat, fmt, hip, wrist, hba1c):    
    try:
        headers = {
        "x-rapidapi-key": x_rapidapi_key,
        "x-rapidapi-host": "health-calculator-api.p.rapidapi.com",
        "Content-Type": "application/json"
        } 

        all_endpoint_query_params = {
            "age": age,
            "sex": sex,
            "gender": gender,
            "height": height,
            "weight": weight,
            "waist_circumference": waist_circumference,
            "hip": hip,
            "wrist": wrist,
            "body_fat": body_fat,
            "body_frame": body_frame,
            "fitness_level": fitness_level,
            "activity_level": activity_level,
            "climate": climate,
            "goal": goal,
            "formula": formula,
            "equation": equation,
            "unit": unit,
            "units": units,
            "format": fmt,
            "hba1c": hba1c
        }
        params = {k: v for k, v in all_endpoint_query_params.items() if v is not None}
        query_string = urllib.parse.urlencode(params)

        if tool == 'ibw':
            base_url = 'https://health-calculator-api.p.rapidapi.com/ibw'

        elif tool == 'absi':
            base_url = 'https://health-calculator-api.p.rapidapi.com/absi'

        elif tool == 'body_fat':
            base_url = 'https://health-calculator-api.p.rapidapi.com/body-fat'

        elif tool == 'bmi':
            base_url = 'https://health-calculator-api.p.rapidapi.com/bmi'

        elif tool == 'bmr':
            base_url = 'https://health-calculator-api.p.rapidapi.com/bmr'

        elif tool == 'daily_caloric_needs':
            base_url = 'https://health-calculator-api.p.rapidapi.com/dcn'

        elif tool == 'daily_water_intake':
            base_url = 'https://health-calculator-api.p.rapidapi.com/dwi'

        elif tool == 'target_heart_rate':
            base_url = 'https://health-calculator-api.p.rapidapi.com/thr'

        elif tool == 'ffmi':
            base_url = 'https://health-calculator-api.p.rapidapi.com/ffmi'

        elif tool == 'adjusted_body_weight':
            base_url = 'https://health-calculator-api.p.rapidapi.com/abw'

        elif tool == 'body_adiposity_index':
            base_url = 'https://health-calculator-api.p.rapidapi.com/bai'

        elif tool == 'body_frame_size':
            base_url = 'https://health-calculator-api.p.rapidapi.com/bfs'

        elif tool == 'estimated_average_glucose':
            base_url = 'https://health-calculator-api.p.rapidapi.com/eag'

        elif tool == 'estimated_energy_requirement':
            base_url = 'https://health-calculator-api.p.rapidapi.com/eer'

        else:
            base_url = 'https://health-calculator-api.p.rapidapi.com/tdee' 

        full_url = base_url + '?' + query_string

        req = urllib.request.Request(full_url, headers = headers)
        access= urllib.request.urlopen(req, context = ctx)
        get = access.read().decode()

        data = json.loads(get)

        results = []


        if base_url == 'https://health-calculator-api.p.rapidapi.com/ibw':
            results.append({
                'ideal_weight': data.get('ideal_weight')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/absi':
            results.append({
                'ABSI': data.get('ABSI'),
                'absi_z_score': data.get('ABSI z-score'),
                'age': data.get('Age'),
                'mortality_risk': data.get('Mortality risk'),
                'sex': data.get('Sex')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/body-fat':
            results.append({
                'age': data.get('age'),
                'bmi': data.get('bmi'),
                'bodyfat': data.get('bodyfat'),
                'bodyfat_status': data.get('bodyfat_status'),
                'gender': data.get('gender'),
                'height': data.get('height'),
                'weight': data.get('weight')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/bmi':
            results.append({
                'bmi': data.get('bmi'),
                'height': data.get('height'),
                'weight': data.get('weight'),
                'weight_status': data.get('weight_status')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/bmr':
            results.append({
                'bmr': data.get('bmr')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/dcn':
            caloric_needs = data.get('caloric_needs', {})
            results.append({
                'calories': caloric_needs.get('calories'),
                'equation': caloric_needs.get('equation'),
                'goal': caloric_needs.get('goal')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/dwi':
            results.append({
                'water_intake': data.get('water_intake'),
                'unit': data.get('unit')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/thr':
            results.append({
                'thr_max': data.get('thr_max'),
                'thr_min': data.get('thr_min')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/ffmi':
            results.append({
                'FFMI': data.get('FFMI'),
                'fat_free_mass': data.get('Fat-free mass'),
                'normalized_FFMI': data.get('Normalized FFMI'),
                'sex': data.get('Sex'),
                'total_body_fat': data.get('Total body fat'),
                'unit': data.get('Unit')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/abw':
            results.append({
                'AjBW': data.get('AjBW'),
                'height': data.get('Height'),
                'IBW_robinson': data.get('IBW (Robinson)'),
                'sex': data.get('Sex'),
                'weight': data.get('Weight')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/bai':
            results.append({
                'adiposity_classification': data.get('Adiposity Classification'),
                'age': data.get('Age'),
                'BAI': data.get('BAI'),
                'height': data.get('Height'),
                'hip_circumference': data.get('Hip Circumference'),
                'sex': data.get('Sex')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/bfs':
            results.append({
                'BFSI': data.get('BFSI'),
                'frame_size': data.get('Frame Size'),
                'sex': data.get('Sex')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/eag':
            results.append({
                'HbA1c': data.get('HbA1c (%)'),
                'eAG_mg_dL': data.get('eAG (mg/dL)')
            })
            return results

        elif base_url == 'https://health-calculator-api.p.rapidapi.com/eer':
            results.append({
                'activity_level': data.get('Activity Level'),
                'age': data.get('Age'),
                'EER': data.get('EER'),
                'gender': data.get('Gender'),
                'height': data.get('Height'),
                'weight': data.get('Weight')
            })
            return results

        else:  # tdee
            results.append({
                'activity_level': data.get('Activity Level'),
                'age': data.get('Age'),
                'BMR': data.get('BMR'),
                'gender': data.get('Gender'),
                'height': data.get('Height'),
                'TDEE': data.get('TDEE'),
                'weight': data.get('Weight')
            })
            return results
        
    except urllib.error.URLError as e:
        return {'result': str(e)}


def router(parse_action_result):
    if parse_action_result['tool_name'] == 'ibw':
        height     = parse_action_result['args']['height']
        body_frame = parse_action_result['args']['body_frame']
        gender     = parse_action_result['args']['gender']
        formula    = parse_action_result['args']['formula']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, None, None, gender, height, None, None, None, None, body_frame, formula, None, None, None, None, None, None, None, None, None, None)
        return {'result': connect}
        
    elif parse_action_result['tool_name'] == 'absi':
        sex                 = parse_action_result['args']['sex']
        age                 = parse_action_result['args']['age']
        height              = parse_action_result['args']['height']
        weight              = parse_action_result['args']['weight']
        waist_circumference = parse_action_result['args']['waist_circumference']
        unit                = parse_action_result['args']['unit']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, age, sex, None, height, weight, waist_circumference, unit, None, None, None, None, None, None, None, None, None, None, None, None, None)
        return {'result': connect}
        
    elif parse_action_result['tool_name'] == 'body_fat':
        gender = parse_action_result['args']['gender']
        age    = parse_action_result['args']['age']
        height = parse_action_result['args']['height']
        weight = parse_action_result['args']['weight']
        unit   = parse_action_result['args']['unit']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, age, None, gender, height, weight, None, unit, None, None, None, None, None, None, None, None, None, None, None, None, None)
        return {'result': connect}
        
    elif parse_action_result['tool_name'] == 'bmi':
        height = parse_action_result['args']['height']
        weight = parse_action_result['args']['weight']
        units  = parse_action_result['args']['units']
        tool = parse_action_result['tool_name']     
        connect = access_api(tool, None, None, None, height, weight, None, None, units, None, None, None, None, None, None, None, None, None, None, None, None)
        return {'result': connect}
        
    elif parse_action_result['tool_name'] == 'bmr':
        age      = parse_action_result['args']['age']
        weight   = parse_action_result['args']['weight']
        height   = parse_action_result['args']['height']
        gender   = parse_action_result['args']['gender']
        equation = parse_action_result['args']['equation']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, age, None, gender, height, weight, None, None, None, None, None, equation, None, None, None, None, None, None, None, None, None)
        return {'result': connect}
        
    elif parse_action_result['tool_name'] == 'daily_caloric_needs':
        age            = parse_action_result['args']['age']
        weight         = parse_action_result['args']['weight']
        height         = parse_action_result['args']['height']
        gender         = parse_action_result['args']['gender']
        activity_level = parse_action_result['args']['activity_level']
        goal           = parse_action_result['args']['goal']
        equation       = parse_action_result['args']['equation']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, age, None, gender, height, weight, None, None, None, None, None, equation, activity_level, goal, None, None, None, None, None, None, None)
        return {'result': connect}
        
    elif parse_action_result['tool_name'] == 'daily_water_intake':
        weight         = parse_action_result['args']['weight']
        activity_level = parse_action_result['args']['activity_level']
        climate        = parse_action_result['args']['climate']
        unit           = parse_action_result['args']['unit']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, None, None, None, None, weight, None, unit, None, None, None, None, activity_level, None, climate, None, None, None, None, None, None)
        return {'result': connect}
    
    elif parse_action_result['tool_name'] == 'target_heart_rate':
        age           = parse_action_result['args']['age']
        fitness_level = parse_action_result['args']['fitness_level']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, age, None, None, None, None, None, None, None, None, None, None, None, None, None, fitness_level, None, None, None, None, None)
        return {'result': connect}

    elif parse_action_result['tool_name'] == 'ffmi':
        sex      = parse_action_result['args']['sex']
        height   = parse_action_result['args']['height']
        weight   = parse_action_result['args']['weight']
        body_fat = parse_action_result['args']['body_fat']
        unit     = parse_action_result['args']['unit']
        fmt      = parse_action_result['args']['format']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, None, sex, None, height, weight, None, unit, None, None, None, None, None, None, None, None, body_fat, fmt, None, None, None)
        return {'result': connect}  
        
    elif parse_action_result['tool_name'] == 'adjusted_body_weight':
        sex    = parse_action_result['args']['sex']
        height = parse_action_result['args']['height']
        weight = parse_action_result['args']['weight']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, None, sex, None, height, weight, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        return {'result': connect}

    elif parse_action_result['tool_name'] == 'body_adiposity_index':
        sex    = parse_action_result['args']['sex']
        age    = parse_action_result['args']['age']
        hip    = parse_action_result['args']['hip']
        height = parse_action_result['args']['height']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, age, sex, None, height, None, None, None, None, None, None, None, None, None, None, None, None, None, hip, None, None)
        return {'result': connect}

    elif parse_action_result['tool_name'] == 'body_frame_size':
        sex    = parse_action_result['args']['sex']
        height = parse_action_result['args']['height']
        wrist  = parse_action_result['args']['wrist']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, None, sex, None, height, None, None, None, None, None, None, None, None, None, None, None, None, None, None, wrist, None)
        return {'result': connect}

    elif parse_action_result['tool_name'] == 'estimated_average_glucose':
        hba1c = parse_action_result['args']['hba1c']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, hba1c)
        return {'result': connect}

    elif parse_action_result['tool_name'] == 'estimated_energy_requirement':
        gender         = parse_action_result['args']['gender']
        age            = parse_action_result['args']['age']
        height         = parse_action_result['args']['height']
        weight         = parse_action_result['args']['weight']
        activity_level = parse_action_result['args']['activity_level']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, age, None, gender, height, weight, None, None, None, None, None, None, activity_level, None, None, None, None, None, None, None, None)
        return {'result': connect}
        
    elif parse_action_result['tool_name'] == 'tdee':
        gender         = parse_action_result['args']['gender']
        age            = parse_action_result['args']['age']
        height         = parse_action_result['args']['height']
        weight         = parse_action_result['args']['weight']
        activity_level = parse_action_result['args']['activity_level']
        equation       = parse_action_result['args']['equation']
        tool = parse_action_result['tool_name']
        connect = access_api(tool, age, None, gender, height, weight, None, None, None, None, None, equation, activity_level, None, None, None, None, None, None, None, None)
        return {'result': connect}
        
    elif parse_action_result['tool_name'] == 'error':
        file_error = parse_action_result['args']['message']
        return {'error': file_error}
    
    elif parse_action_result ['tool_name'] == 'terminate':
        print('Tool use has been ceased...\n')
        return '```terminate'
    
    else:
        return {'error': 'Unknown tool' + parse_action_result['tool_name']}
    return None

def action(messages: list[dict]):
    while True:
        prompt = input('You: ')
        if not prompt.strip():
            print('Insert a valid input. Try again.\n')
            continue
        
        learn('user', prompt)
        messages.append({'role':'user', 'content': prompt})
        
        while True:
            response = generate_response(messages)
            learn('assistant', response)
            messages.append({'role':'assistant', 'content': response})
            
            if '```action' in response:
                parse_action_result = parse_action(response)
                get_api_info = router(parse_action_result)
                get_api_info_str = json.dumps(get_api_info) 
                
                learn('user', get_api_info_str)
                messages.append({'role':'user', 'content': get_api_info_str})
            
            else:
                print(f'Leyla: {response}')
                if '```terminate' in response:
                    parse_terminate(response)
                    print('\n'+'-'*55)
                    print("  It's always a pleasure helping you, Santi.")
                    print('  Feel free to reach me out anytime. Goodbye! :)')
                    cur.close()
                    conn.commit()
                    conn.close()
                    return
                break
    
if __name__ == '__main__':
    with open('system_prompt.txt','r', encoding = 'utf-8') as pattern:
        behavior = pattern.read()
        
    brain()
    
    messages = [{'role': 'system', 'content': behavior}]
    
    print('\n'+'='*55)
    print('Hi! Im Leyla, your AI fitness advisor! How are you today?')
    print('='*55 + '\n')
    
    recall = remember(limit = 20)
    if recall:
        print(f'\n  [📚 Loading {len(recall)} previous sessions messages...]')
        messages.extend(recall)
        
    action(messages)