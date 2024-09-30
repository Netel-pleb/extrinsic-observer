
# This script orchestrates the process of monitoring a GitHub repository.
# It fetches repository data, compares current and previous states, generates reports on pull requests and branches,
# and posts these reports to Discord.

from observing.bot.bot import post_to_discord
from observing.observer.observer import observer_block
from dotenv import load_dotenv
import os
import time

def run():
    start_time = time.time()
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    load_dotenv()
    
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

    report_swap_coldkey = observer_block()
    print(report_swap_coldkey)
    post_to_discord(report_swap_coldkey, DISCORD_WEBHOOK_URL)
    end_time = time.time()
    print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"Time consumed: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    run()
