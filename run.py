# This script orchestrates the process of monitoring a GitHub repository.
# It fetches repository data, compares current and previous states, generates reports on pull requests and branches,
# and posts these reports to Discord.

from observing.bot.bot import post_to_discord
from observing.observer.observer import observer_block
from observing.utils.
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import subprocess
import threading

def run_get_coldkey_script():
    """Runs the get_coldkey.py script in a new thread."""
    subprocess.run(['python', 'observing/utils/get_coldkey.py'])
    
def run():
    start_time = time.time()
    print(f"Start time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    load_dotenv()
    
    COLDKEY_SWAP_DISCORD_WEBHOOK_URL = os.getenv('COLDKEY_SWAP_DISCORD_WEBHOOK_URL')
    DISSOLVE_NETWORK_DISCORD_WEBHOOK_URL = os.getenv('DISSOLVE_NETWORK_DISCORD_WEBHOOK_URL')

    report_swap_coldkey, report_dissolve_network, report_vote, dissloved_subnet_resport, swapped_coldkey_report, should_db_update = observer_block()
    # print(report_swap_coldkey)
    if should_db_update:
        threading.Thread(target=run_get_coldkey_script).start()
    post_to_discord(report_swap_coldkey, COLDKEY_SWAP_DISCORD_WEBHOOK_URL)
    post_to_discord(report_dissolve_network, DISSOLVE_NETWORK_DISCORD_WEBHOOK_URL)
    post_to_discord(dissloved_subnet_resport, DISSOLVE_NETWORK_DISCORD_WEBHOOK_URL)
    post_to_discord(report_vote, COLDKEY_SWAP_DISCORD_WEBHOOK_URL)
    post_to_discord(swapped_coldkey_report, COLDKEY_SWAP_DISCORD_WEBHOOK_URL)
    
    
    end_time = time.time()
    print(f"End time: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    print(f"Time consumed: {end_time - start_time:.3f} seconds")

    
if __name__ == "__main__":
    run()
    