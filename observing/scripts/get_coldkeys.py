# import requests

# url = "https://api.taostats.io/api/v1/subnet/owner?latest=true"

# headers = {
#     "accept": "application/json",
#     "Authorization": "V2SW2nSvQU4rmiVJjqFUXr0EimP8phUqD7cwGUf9bOy0jxssNv6jtG0E3KIdQmBk"
# }

# response = requests.get(url, headers=headers)
# results = response.json()

# # Extract owner coldkey list
# owner_coldkeys = [owner['owner'] for owner in results['subnet_owners']]

# print(len(owner_coldkeys))




import requests

url = "https://api.taostats.io/api/v1/validator"
headers = {
    "accept": "application/json",
    "Authorization": "V2SW2nSvQU4rmiVJjqFUXr0EimP8phUqD7cwGUf9bOy0jxssNv6jtG0E3KIdQmBk"
}

def fetch_all_validators(url, headers):
    """
    Fetches all validators using pagination.
    """
    validators = []
    page = 1
    while True:
        params = {
            "order": "validator_stake:desc",
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        if not data['validators']:
            break
        validators.extend(data['validators'])
        page += 1
    return validators

# Fetch all validators
all_validators = fetch_all_validators(url, headers)

# Extract validator coldkey SS58 address list
validator_coldkeys = []
validator_names = []
for validator in all_validators:
    validator_coldkeys.append(validator['cold_key']['ss58'])
    hotkey = validator['hot_key']['ss58']
    print(hotkey)
    # validator_names.append(name)

url = "https://api.taostats.io/api/v1/delegate/info"



response = requests.get(url, headers=headers).json()


print(response.text)

print(len(validator_coldkeys))
print(validator_coldkeys)