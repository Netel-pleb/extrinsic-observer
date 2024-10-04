import requests
import sqlite3
from substrateinterface.utils.ss58 import ss58_encode
import time
import os
import sentry_sdk
from dotenv import load_dotenv
# Initialize Sentry

def init_sentry(): 
    
    load_dotenv()
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,  # Replace with your actual Sentry DSN
        traces_sample_rate=1.0
    )

def convert_hex_to_ss58(hex_address):
    """
    Converts a hexadecimal address to an SS58 address.
    
    Args:
        hex_address (str): The hexadecimal address to convert.
    
    Returns:
        str: The SS58 encoded address.
    """
    try:
        if hex_address.startswith('0x'):
            hex_address = hex_address[2:]
        
        address_bytes = bytes.fromhex(hex_address)
        ss58_address = ss58_encode(address_bytes)
        
        return ss58_address
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in convert_hex_to_ss58 (observing/utils/get_coldkeys.py): {e}")
        return None

def fetch_all_validators(url, headers):
    """
    Fetches all validators using pagination.
    
    Args:
        url (str): The API endpoint URL.
        headers (dict): The headers to include in the API request.
    
    Returns:
        list: A list of all validators.
    """
    try:
        validators = []
        page = 1
        while True:
            params = {
                "order": "amount:desc",
                "page": page
            }
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            if not data['validators']:
                break
            validators.extend(data['validators'])
            page += 1
        return validators
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in fetch_all_validators (observing/utils/get_coldkeys.py): {e}")
        return []

def find_owner_coldkey():
    """
    Fetches owner coldkeys and net_uids from the API and saves them to the SQLite database.
    """
    
    init_sentry()
    load_dotenv()
    TAOSTATS_API_KEY = os.getenv('TAOSTATS_API_KEY')
    
    try:
        url = "https://api.taostats.io/api/v1/subnet/owner?latest=true"
        headers = {
            "accept": "application/json",
            "Authorization": TAOSTATS_API_KEY
        }

        response = requests.get(url, headers=headers)
        results = response.json()

        owner_coldkeys = []
        net_uids = []

        for owner in results['subnet_owners']:
            owner_coldkeys.append(convert_hex_to_ss58(owner['owner']))
            net_uids.append(owner['subnet_id'])

        db_path = 'DB/db.sqlite3'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('DROP TABLE IF EXISTS owners')

        cursor.execute('''
        CREATE TABLE owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            net_uid TEXT,
            owner_coldkey TEXT
        )
        ''')

        for net_uid, owner_coldkey in zip(net_uids, owner_coldkeys):
            cursor.execute('''
            INSERT INTO owners (net_uid, owner_coldkey)
            VALUES (?, ?)
            ''', (net_uid, owner_coldkey))
        conn.commit()
        conn.close()

        print("Owner coldkey data has been saved to the database.")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in find_owner_coldkey (observing/utils/get_coldkeys.py): {e}")

def find_validator_coldkey():
    """
    Fetches validator coldkeys, hotkeys, and amounts from the API and saves them to the SQLite database.
    """

    init_sentry()
    
    load_dotenv()
    TAOSTATS_API_KEY = os.getenv('TAOSTATS_API_KEY')
    
    try:
        url = "https://api.taostats.io/api/v1/validator"
        headers = {
            "accept": "application/json",
            "Authorization": TAOSTATS_API_KEY
        }

        all_validators = fetch_all_validators(url, headers)

        validator_coldkeys = []
        validator_hotkeys = []
        validator_amounts = []
        get_validator_names = []
        for validator in all_validators:
            amount = validator['amount']
            if int(amount) > 1000:
                validator_coldkeys.append(validator['cold_key']['ss58'])
                validator_hotkeys.append(validator['hot_key']['ss58'])
                name = get_validator_name(validator['hot_key']['ss58'], TAOSTATS_API_KEY)
                # print(name)
                get_validator_names.append(name)
                validator_amounts.append(amount)

        db_path = 'DB/db.sqlite3'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('DROP TABLE IF EXISTS validators')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS validators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cold_key TEXT,
            hot_key TEXT,
            amount TEXT,
            name TEXT
        )
        ''')
        print("validator dataset is updated")
        print((validator_coldkeys, validator_hotkeys, validator_amounts, get_validator_names))
        for cold_key, hot_key, amount, name in zip(validator_coldkeys, validator_hotkeys, validator_amounts, get_validator_names):
            try:
                print(f"Inserting: cold_key={cold_key}, hot_key={hot_key}, amount={amount}, name={name}")
                cursor.execute('''
                INSERT INTO validators (cold_key, hot_key, amount, name)
                VALUES (?, ?, ?, ?)
                ''', (cold_key, hot_key, amount, name))
            except sqlite3.Error as e:
                sentry_sdk.capture_exception(e)
                print(f"Error inserting data (observing/utils/get_coldkeys.py): {e}")
        conn.commit()
        conn.close()
        print("Validator coldkey data has been saved to the database.")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in find_validator_coldkey (observing/utils/get_coldkeys.py): {e}")

def get_validator_name(hotkey, TAOSTATS_API_KEY):
    try:
        url = f"https://api.taostats.io/api/v1/delegate/info?address={hotkey}"
        headers = {
            "accept": "application/json",
            "Authorization": TAOSTATS_API_KEY
        }

        response = requests.get(url, headers=headers)
        # print(response.status_code)
        if response.status_code == 429:  # Rate limit error
            # print("Rate limit exceeded. Retrying...")
            time.sleep(10)  # Wait for 10 seconds before retrying
            return get_validator_name(hotkey, TAOSTATS_API_KEY)  # Retry the request
        
        response = response.json()
        if response["count"] == 1:
            return response["delegates"][0]["name"]
        else:
            return None
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in get_validator_name (observing/utils/get_coldkeys.py): {e}")
        return None

if __name__ == "__main__":
    
    init_sentry()
    
    try:
        find_owner_coldkey()
        find_validator_coldkey()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in main (observing/utils/get_coldkeys.py): {e}")