import requests
import os
from dotenv import load_dotenv
import sentry_sdk

# Load environment variables
load_dotenv()
TAOSTATS_API_KEY = os.getenv('TAOSTATS_API_KEY')

def fetch_all_pages(url, headers):
    results = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        results.extend(data['subnet_owners'])  # Adjust based on the actual structure of the response

        # Check for the next page URL
        url = data.get('next')  # Adjust based on the actual structure of the response
    return results

def main():
    url = "https://api.taostats.io/api/v1/subnet/owners?latest=true"  # Corrected URL
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TAOSTATS_API_KEY}"
    }

    try:
        results = fetch_all_pages(url, headers)
        print(results)
    except requests.exceptions.HTTPError as e:
        sentry_sdk.capture_exception(e)
        print(f"HTTPError: {e}")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()