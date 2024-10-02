import requests
import sqlite3
import os

url = "https://api.taostats.io/api/v1/subnet/owner?latest=true"
headers = {
    "accept": "application/json",
    "Authorization": "V2SW2nSvQU4rmiVJjqFUXr0EimP8phUqD7cwGUf9bOy0jxssNv6jtG0E3KIdQmBk"
}

# Fetch data from the API
response = requests.get(url, headers=headers)
results = response.json()

# Extract owner coldkey list and net_uids
owner_coldkeys = [owner['owner'] for owner in results['subnet_owners']]
net_uids = [owner['subnet_id'] for owner in results['subnet_owners']]

# Connect to SQLite database (or create it if it doesn't exist)
db_path = '../../DB/db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the existing table if it exists
cursor.execute('DROP TABLE IF EXISTS owners')

# Create table
cursor.execute('''
CREATE TABLE owners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    net_uid TEXT,
    owner_coldkey TEXT
)
''')

# Insert data into the table
for net_uid, owner_coldkey in zip(net_uids, owner_coldkeys):
    cursor.execute('''
    INSERT INTO owners (net_uid, owner_coldkey)
    VALUES (?, ?)
    ''', (net_uid, owner_coldkey))

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("Data has been saved to the database.")



# import requests
# import sqlite3

# url = "https://api.taostats.io/api/v1/validator"
# headers = {
#     "accept": "application/json",
#     "Authorization": "V2SW2nSvQU4rmiVJjqFUXr0EimP8phUqD7cwGUf9bOy0jxssNv6jtG0E3KIdQmBk"
# }

# def fetch_all_validators(url, headers):
#     """
#     Fetches all validators using pagination.
#     """
#     validators = []
#     page = 1
#     while True:
#         params = {
#             "order": "amount:desc",
#             "page": page
#         }
#         response = requests.get(url, headers=headers, params=params)
#         data = response.json()
#         if not data['validators']:
#             break
#         validators.extend(data['validators'])
#         page += 1
#     return validators

# # Fetch all validators
# all_validators = fetch_all_validators(url, headers)

# # Extract data
# validator_coldkeys = []
# validator_hotkeys = []
# validator_amounts = []

# for validator in all_validators:
#     amount = validator['amount']
#     if int(amount) > 1000:
#         validator_coldkeys.append(validator['cold_key']['ss58'])
#         validator_hotkeys.append(validator['hot_key']['ss58'])
#         validator_amounts.append(amount)

# # Connect to SQLite database (or create it if it doesn't exist)
# conn = sqlite3.connect('../../DB/db.sqlite3')
# cursor = conn.cursor()
# cursor.execute('DROP TABLE IF EXISTS validators')
# # Create table
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS validators (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     cold_key TEXT,
#     hot_key TEXT,
#     amount TEXT
# )
# ''')

# # Insert data into the table
# for cold_key, hot_key, amount in zip(validator_coldkeys, validator_hotkeys, validator_amounts):
#     cursor.execute('''
#     INSERT INTO validators (cold_key, hot_key, amount)
#     VALUES (?, ?, ?)
#     ''', (cold_key, hot_key, amount))

# # Commit the transaction and close the connection
# conn.commit()
# conn.close()

# print("Data has been saved to the database.")

