import os
import ssl
import json
import time
import sqlite3
from litellm import completion
from litellm.exceptions import RateLimitError
from dotenv import load_dotenv
import  urllib.request, urllib.parse, urllib.error

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
X_RAPIDAPI_KEY = os.environ.get('X_RAPIDAPI_KEY')

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

def remember(limit: int= 20):
    cur.execute('''SELECT role, content FROM Brain ORDER BY id DESC LIMIT (?)''', (limit, ))
    rows = cur.fetchall()
    return [{'role': row[0], 'content': row[1]} for row in reversed(rows)]

def learn(role: str, content: str):
    cur.execute('''INSERT INTO Brain (role, content) VALUES(?,?)''', (role, content))
    conn.commit()
    return None

def generate_response(messages: list[dict]) -> str:
    try:
        response = completion(
        model = 'anthropic/claude-sonnet-4-6',
        messages = messages,
        max_tokens = 1024
        )
        return response.choices[0].message.content
    except RateLimitError:
        print('\n  [⏳ Rate limit reached. Waiting 60 seconds before retrying...]\n')
        time.sleep(60)
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
            return data.get('terminate','Goodbye!')
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
            return {'tool_name': 'error', 'args': {'message': 'You must respond with a valid tool_name and args'}}
        return {'tool_name': tool_name, 'args': args}
    except (IndexError, json.JSONDecodeError):
        return {'tool_name': 'error', 'args': {'message': 'Invalid JSON format'}}
    return None

def connect_api(tool_name, query, departure_id, arrival_id, outbound_date, return_date, travel_class, adults, children, infant_on_lap, infant_in_seat, show_hidden, currency, language_code, country_code, search_type, booking_token, start_date, end_date, trip_type, trip_days, next_token, start_date_x, end_date_x, start_date_y, end_date_y):
    try: 
        headers = {
        "x-rapidapi-key": X_RAPIDAPI_KEY,
        "x-rapidapi-host": "google-flights2.p.rapidapi.com",
        "Content-Type": "application/json"
        }
        full_endpoint_params = {
        "query": query,
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "travel_class": travel_class,
        "adults": adults,
        "children": children,
        "infant_on_lap": infant_on_lap,
        "infant_in_seat": infant_in_seat,
        "show_hidden": show_hidden,
        "currency": currency,
        "language_code": language_code,
        "country_code": country_code,
        "search_type": search_type,
        "booking_token": booking_token,
        "start_date": start_date,
        "end_date": end_date,
        "trip_type": trip_type,
        "trip_days": trip_days,
        "next_token": next_token,
        "start_date_x": start_date_x,
        "end_date_x": end_date_x,
        "start_date_y": start_date_y,
        "end_date_y": end_date_y
        }

        query_string = {key: value for key, value in full_endpoint_params.items() if value is not None and value != ""}
        encoded_query_string = urllib.parse.urlencode(query_string)

        if tool_name == 'search_flights':
            base_url = 'https://google-flights2.p.rapidapi.com/api/v1/searchFlights'
        elif tool_name == 'get_booking_details':
            base_url = 'https://google-flights2.p.rapidapi.com/api/v1/getBookingDetails'
        elif tool_name == 'get_booking_url':
            base_url = 'https://google-flights2.p.rapidapi.com/api/v1/getBookingURL'
        elif tool_name == 'search_airport':
            base_url = 'https://google-flights2.p.rapidapi.com/api/v1/searchAirport'
        elif tool_name == 'get_calendar_picker':
            base_url = 'https://google-flights2.p.rapidapi.com/api/v1/getCalendarPicker'
        elif tool_name == 'get_next_flights':
            base_url = 'https://google-flights2.p.rapidapi.com/api/v1/getNextFlights'
        elif tool_name == 'get_price_graph':
            base_url = 'https://google-flights2.p.rapidapi.com/api/v1/getPriceGraph'
        else:
            base_url = 'https://google-flights2.p.rapidapi.com/api/v1/getCalendarGrid'

        full_url = base_url + '?' + encoded_query_string

        req = urllib.request.Request(full_url, headers = headers)
        access = urllib.request.urlopen(req, context = ctx)

        load = access.read().decode()
        data = json.loads(load)

        if 'data' not in data:
            return {'error': f'API error: {data}'}

        results = []

        if base_url == 'https://google-flights2.p.rapidapi.com/api/v1/searchFlights':
            flights_list = data['data'].get('topFlights') or data['data'].get('bestFlights') or []
            for item in flights_list:
                for flight in item['flights']:
                    results.append({
                        # Información general del vuelo
                        'departure_time': item.get('departure_time'),
                        'arrival_time': item.get('arrival_time'),
                        'duration_raw': item.get('duration', {}).get('raw'),
                        'duration_text': item.get('duration', {}).get('text'),
                        'price': item.get('price'),
                        'stops': item.get('stops'),
                        # Token importante
                        'next_token': item.get('next_token'),
                        # Equipaje
                        'carry_on_bags': item.get('bags', {}).get('carry_on'),
                        'checked_bags': item.get('bags', {}).get('checked'),
                        # Emisiones
                        'co2e': item.get('carbon_emissions', {}).get('CO2e'),
                        'co2_difference_percent': item.get('carbon_emissions', {}).get('difference_percent'),
                        'typical_route_emissions': item.get('carbon_emissions', {}).get('typical_for_this_route'),
                        # Aeropuertos
                        'departure_airport_name': flight.get('departure_airport', {}).get('airport_name'),
                        'departure_airport_code': flight.get('departure_airport', {}).get('airport_code'),
                        'departure_airport_time': flight.get('departure_airport', {}).get('time'),
                        'arrival_airport_name': flight.get('arrival_airport', {}).get('airport_name'),
                        'arrival_airport_code': flight.get('arrival_airport', {}).get('airport_code'),
                        'arrival_airport_time': flight.get('arrival_airport', {}).get('time'),
                        # Aerolínea
                        'airline': flight.get('airline'),
                        'airline_logo': flight.get('airline_logo'),
                        'flight_number': flight.get('flight_number'),
                        # Avión
                        'aircraft': flight.get('aircraft'),
                        # Asiento
                        'seat': flight.get('seat'),
                        'legroom': flight.get('legroom'),
                        # Duración tramo
                        'flight_duration': flight.get('duration'),
                        'flight_duration_label': flight.get('duration_label'),
                        # Extras
                        'extensions': flight.get('extensions')
                    })
            return results
        elif base_url == 'https://google-flights2.p.rapidapi.com/api/v1/getBookingDetails':
            for item in data['data']:
                results.append({
                    # Información general de la opción de compra
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'website': item.get('website'),
                    'price': item.get('price'),
                    'is_airline': item.get('is_airline'),
                    # Token importante
                    'token': item.get('token')
                })
            return results
        elif base_url == 'https://google-flights2.p.rapidapi.com/api/v1/getBookingURL':
            results.append({
                'status': data.get('status'),
                'message': data.get('message'),
                'timestamp': data.get('timestamp'),
                'booking_url': data.get('data')
            })
            return results
        elif base_url == 'https://google-flights2.p.rapidapi.com/api/v1/searchAirport':
            for item in data['data']:
                # Resultado principal
                results.append({
                    'id': item.get('id'),
                    'type': item.get('type'),
                    'title': item.get('title'),
                    'subtitle': item.get('subtitle'),
                    'city': item.get('city'),
                    'distance': item.get('distance')
                })
                # Aeropuertos asociados
                for airport in item.get('list', []):
                    results.append({
                        'parent_destination': item.get('title'),
                        'airport_id': airport.get('id'),
                        'airport_type': airport.get('type'),
                        'airport_title': airport.get('title'),
                        'airport_subtitle': airport.get('subtitle'),
                        'airport_city': airport.get('city'),
                        'airport_distance': airport.get('distance')
                    })
            return results

        elif  base_url == 'https://google-flights2.p.rapidapi.com/api/v1/getCalendarPicker':
            for item in data['data']:
                results.append({
                    'departure_date': item.get('departure'),
                    'return_date': item.get('return'),
                    'price': item.get('price')
                })
            return results

        elif base_url == 'https://google-flights2.p.rapidapi.com/api/v1/getNextFlights':
            flights_list = data['data'].get('topFlights') or data['data'].get('bestFlights') or []
            for item in flights_list:
                for flight in item['flights']:
                    results.append({
                        # Información general
                        'departure_time': item.get('departure_time'),
                        'arrival_time': item.get('arrival_time'),
                        'duration_raw': item.get('duration', {}).get('raw'),
                        'duration_text': item.get('duration', {}).get('text'),
                        'price': item.get('price'),
                        'stops': item.get('stops'),
                        # Token importante
                        'booking_token': item.get('booking_token'),
                        # Equipaje
                        'carry_on': item.get('bags', {}).get('carry_on'),
                        'checked': item.get('bags', {}).get('checked'),
                        # Emisiones
                        'co2e': item.get('carbon_emissions', {}).get('CO2e'),
                        'difference_percent': item.get('carbon_emissions', {}).get('difference_percent'),
                        'typical_for_this_route': item.get('carbon_emissions', {}).get('typical_for_this_route'),
                        # Aeropuerto salida
                        'departure_airport_name': flight.get('departure_airport', {}).get('airport_name'),
                        'departure_airport_code': flight.get('departure_airport', {}).get('airport_code'),
                        'departure_airport_time': flight.get('departure_airport', {}).get('time'),
                        # Aeropuerto llegada
                        'arrival_airport_name': flight.get('arrival_airport', {}).get('airport_name'),
                        'arrival_airport_code': flight.get('arrival_airport', {}).get('airport_code'),
                        'arrival_airport_time': flight.get('arrival_airport', {}).get('time'),
                        # Aerolínea
                        'airline': flight.get('airline'),
                        'airline_logo': flight.get('airline_logo'),
                        'flight_number': flight.get('flight_number'),
                        # Avión
                        'aircraft': flight.get('aircraft'),
                        # Asiento
                        'seat': flight.get('seat'),
                        'legroom': flight.get('legroom'),
                        # Duración tramo
                        'flight_duration': flight.get('duration'),
                        'flight_duration_label': flight.get('duration_label'),
                        # Extras
                        'extensions': flight.get('extensions')
                    })
            return results

        elif base_url == 'https://google-flights2.p.rapidapi.com/api/v1/getPriceGraph':
            for item in data['data']:
                results.append({
                    'departure': item.get('departure'),
                    'return': item.get('return'),
                    'price': item.get('price')
                })
            return results

        else:
            for item in data['data']:
                results.append({
                    'departure_date': item.get('departure'),
                    'return_date': item.get('return'),
                    'price': item.get('price')
                })
            return results
        
    except urllib.error.HTTPError as e:
        return {'error': f'HTTP {e.code}: {e.reason}'}   # HTTPError sí tiene .code

    except urllib.error.URLError as e:
        return {'error': f'Conection failed: {e.reason}'}  # URLError no tiene .code
    return None

def router(parse_action_result):
    if parse_action_result['tool_name'] == 'search_flights':
        # Required params
        tool_name = parse_action_result['tool_name']
        departure_id   = parse_action_result['args']['departure_id']
        arrival_id     = parse_action_result['args']['arrival_id']
        outbound_date  = parse_action_result['args']['outbound_date']
        # Optional params
        return_date    = parse_action_result['args']['return_date']
        travel_class   = parse_action_result['args']['travel_class']
        adults         = parse_action_result['args']['adults']
        children       = parse_action_result['args']['children']
        infant_on_lap  = parse_action_result['args']['infant_on_lap']
        infant_in_seat = parse_action_result['args']['infant_in_seat']
        show_hidden    = parse_action_result['args']['show_hidden']
        currency       = parse_action_result['args']['currency']
        language_code  = parse_action_result['args']['language_code']
        country_code   = parse_action_result['args']['country_code']
        search_type    = parse_action_result['args']['search_type']
        connect = connect_api(tool_name, '', departure_id, arrival_id, outbound_date, return_date, travel_class, adults, children, infant_on_lap, infant_in_seat, show_hidden, currency, language_code, country_code, search_type, '', '', '', '', '', '', '', '', '', '')
        return {'result': connect}
        
    elif parse_action_result['tool_name'] == 'get_booking_details':
        # Required params
        tool_name = parse_action_result['tool_name']
        booking_token = parse_action_result['args']['booking_token']
        # Optional params
        currency      = parse_action_result['args']['currency']
        country_code  = parse_action_result['args']['country_code']
        connect = connect_api(tool_name, '', '', '', '', '', '', '', '', '', '', '', currency, '', country_code, '', booking_token, '', '', '', '', '', '', '', '', '')
        return {'result': connect}

    elif parse_action_result['tool_name'] == 'get_booking_url':
        tool_name = parse_action_result['tool_name']
        token = parse_action_result['args']['token']
        connect = connect_api(tool_name, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', token, '', '', '', '', '', '', '')
        return {'result': connect}
    
    elif parse_action_result['tool_name'] == 'search_airport':
        # Required params
        tool_name = parse_action_result['tool_name']
        query = parse_action_result['args']['query']
        # Optional params
        language_code = parse_action_result['args']['language_code']
        country_code  = parse_action_result['args']['country_code']
        connect = connect_api(tool_name, query, '', '', '', '', '', '', '', '', '', '', language_code, country_code, '', '', '', '', '', '', '', '', '', '', '', '')
        return {'result': connect}

    elif parse_action_result['tool_name'] == 'get_calendar_picker':
        # Required params
        tool_name = parse_action_result['tool_name']
        departure_id  = parse_action_result['args']['departure_id']
        arrival_id    = parse_action_result['args']['arrival_id']
        # Optional params
        outbound_date = parse_action_result['args']['outbound_date']
        start_date    = parse_action_result['args']['start_date']
        end_date      = parse_action_result['args']['end_date']
        travel_class  = parse_action_result['args']['travel_class']
        trip_type     = parse_action_result['args']['trip_type']
        trip_days     = parse_action_result['args']['trip_days']
        adults        = parse_action_result['args']['adults']
        children      = parse_action_result['args']['children']
        infant_on_lap = parse_action_result['args']['infant_on_lap']
        infant_in_seat = parse_action_result['args']['infant_in_seat']
        currency      = parse_action_result['args']['currency']
        country_code  = parse_action_result['args']['country_code']
        connect = connect_api(tool_name, '', departure_id, arrival_id, outbound_date, '', travel_class, adults, children, infant_on_lap, infant_in_seat, '', currency, '', country_code, '', '', start_date, end_date, trip_type, trip_days, '', '', '', '', '')
        return {'result': connect}

    elif parse_action_result['tool_name'] == 'get_next_flights':
        # Required params
        tool_name = parse_action_result['tool_name']
        next_token    = parse_action_result['args']['next_token']
        # Optional params
        show_hidden   = parse_action_result['args']['show_hidden']
        currency      = parse_action_result['args']['currency']
        language_code = parse_action_result['args']['language_code']
        country_code  = parse_action_result['args']['country_code']
        connect = connect_api(tool_name, '', '', '', '', '', '', '', '', '', '', show_hidden, currency, language_code, country_code, '', '', '', '', '', '', next_token, '', '', '', '')
        return {'result': connect}

    elif parse_action_result['tool_name'] == 'get_price_graph':
        # Required params
        tool_name = parse_action_result['tool_name']
        departure_id   = parse_action_result['args']['departure_id']
        arrival_id     = parse_action_result['args']['arrival_id']
        outbound_date  = parse_action_result['args']['outbound_date']
        # Optional params
        return_date    = parse_action_result['args']['return_date']
        start_date     = parse_action_result['args']['start_date']
        end_date       = parse_action_result['args']['end_date']
        travel_class   = parse_action_result['args']['travel_class']
        adults         = parse_action_result['args']['adults']
        children       = parse_action_result['args']['children']
        infant_on_lap  = parse_action_result['args']['infant_on_lap']
        infant_in_seat = parse_action_result['args']['infant_in_seat']
        currency       = parse_action_result['args']['currency']
        country_code   = parse_action_result['args']['country_code']
        connect = connect_api(tool_name, '', departure_id, arrival_id, outbound_date, return_date, travel_class, adults, children, infant_on_lap, infant_in_seat, '', currency, '', country_code, '', '', start_date, end_date, '', '', '', '', '', '', '')
        return {'result': connect}

    elif parse_action_result['tool_name'] == 'get_calendar_grid':
        # Required params
        tool_name = parse_action_result['tool_name']
        departure_id   = parse_action_result['args']['departure_id']
        arrival_id     = parse_action_result['args']['arrival_id']
        outbound_date  = parse_action_result['args']['outbound_date']
        # Optional params
        return_date    = parse_action_result['args']['return_date']
        start_date_x   = parse_action_result['args']['start_date_x']
        end_date_x     = parse_action_result['args']['end_date_x']
        start_date_y   = parse_action_result['args']['start_date_y']
        end_date_y     = parse_action_result['args']['end_date_y']
        travel_class   = parse_action_result['args']['travel_class']
        adults         = parse_action_result['args']['adults']
        children       = parse_action_result['args']['children']
        infant_on_lap  = parse_action_result['args']['infant_on_lap']
        infant_in_seat = parse_action_result['args']['infant_in_seat']
        currency       = parse_action_result['args']['currency']
        country_code   = parse_action_result['args']['country_code']
        connect = connect_api(tool_name, '', departure_id, arrival_id, outbound_date, return_date, travel_class, adults, children, infant_on_lap, infant_in_seat, '', currency, '', country_code, '', '', '', '', '', '', '', start_date_x, end_date_x, start_date_y, end_date_y)
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
            print('Insert a valid Input. Try again please.\n')
            continue
        
        messages.append({'role':'user','content': prompt})
        learn ('user', prompt)
        
        while True:
            response = generate_response(messages)
            messages.append({'role':'assistant','content': response})
            learn ('assistant', response)
            
            if '```action' in response:
                parse_action_result = parse_action(response)
                get_api_info = router(parse_action_result)
                
                messages.append({'role':'user','content': json.dumps(get_api_info)})
                learn ('user', json.dumps(get_api_info))
            
            else:
                print(f'Valya: {response}')
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
    with open('system_prompt.txt', 'r', encoding = 'utf-8') as rules:
        behavior = rules.read()
    
    brain()
    
    print('\n'+'='*55)
    print('Hi! Im Valya, your AI flight booker agent. Whats on your mind today?')
    print('='*55 + '\n')
    
    messages = [{'role': 'system', 'content': behavior}]
    
    recall = remember(limit = 6)
    if recall:
        print(f'\n  [📚 Loading {len(recall)} previous sessions messages...]')
        messages.extend(recall)
    
    action(messages)