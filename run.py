# This script orchestrates the process of monitoring a GitHub repository.
# It fetches repository data, compares current and previous states, generates reports on pull requests and branches,
# and posts these reports to Discord.

import os
import time
import threading
import subprocess
from datetime import datetime
from observing.bot.bot import post_to_discord
from observing.observer.observer import observer_block
from observing.utils.get_coldkeys import find_owner_coldkey
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

def run_update_owner_coldkey_function():
    """Runs the find_owner_coldkey function in a new thread."""
    try:
        # Update the status to running
        with open('thread_status.txt', 'w') as f:
            f.write('running')
        find_owner_coldkey()
        # Update the status to not running
        with open('thread_status.txt', 'w') as f:
            f.write('not running')
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in run_update_owner_coldkey_function (run.py): {e}")

def run():
    
    init_sentry()
    
    try:
        start_time = time.time()
        print(f"Start time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

        load_dotenv()
        
        COLDKEY_SWAP_DISCORD_WEBHOOK_URL = os.getenv('COLDKEY_SWAP_DISCORD_WEBHOOK_URL')
        DISSOLVE_NETWORK_DISCORD_WEBHOOK_URL = os.getenv('DISSOLVE_NETWORK_DISCORD_WEBHOOK_URL')

        report_swap_coldkey, report_dissolve_network, report_vote, dissloved_subnet_resport, swapped_coldkey_report, should_update_owner_table = observer_block()

        # Run the get_coldkey.py script in a new thread if the owner database should be updated.
        if should_update_owner_table:
            print("**********/n/n/n/n**********")
            if update_owner_thread is None or not update_owner_thread.is_alive():
                update_owner_thread = threading.Thread(target=run_update_owner_coldkey_function)
                update_owner_thread.start()
            else:
                print("Update owner coldkey function is already running.")
        
        post_to_discord(report_swap_coldkey, COLDKEY_SWAP_DISCORD_WEBHOOK_URL)
        post_to_discord(report_dissolve_network, DISSOLVE_NETWORK_DISCORD_WEBHOOK_URL)
        post_to_discord(dissloved_subnet_resport, DISSOLVE_NETWORK_DISCORD_WEBHOOK_URL)
        post_to_discord(report_vote, COLDKEY_SWAP_DISCORD_WEBHOOK_URL)
        post_to_discord(swapped_coldkey_report, COLDKEY_SWAP_DISCORD_WEBHOOK_URL)
        
        end_time = time.time()
        print(f"End time: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print(f"Time consumed: {end_time - start_time:.3f} seconds")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in run (run.py): {e}")

if __name__ == "__main__":
    
    init_sentry()
    
    try:
        run()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in main (run.py): {e}")