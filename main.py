# Description: Main script for running the bot and updating the dataset at regular intervals.
import subprocess
import time
import sched
import threading
from observing.utils.get_coldkeys import find_owner_coldkey, find_validator_coldkey
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

def run_bot():
    """Runs a specified script."""
    try:
        subprocess.run(['python', 'run.py'])  # Replace 'run.py' with the actual filename if different
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in run_bot (main.py): {e}")

def schedule_bot(scheduler, interval):
    """Schedules the bot to run at regular intervals."""
    try:
        threading.Thread(target=run_bot).start()
        scheduler.enter(interval, 1, schedule_bot, (scheduler, interval))
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in schedule_bot (main.py): {e}")

def update_coldkeys():
    """Runs find_validator_coldkey and find_owner_coldkey in sequence."""
    try:
        status = check_thread_status()
        if status == 'not running':
            find_owner_coldkey()
        find_validator_coldkey()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in update_coldkeys (main.py): {e}")

def schedule_update_dataset(scheduler, interval):
    """Schedules the dataset to update at regular intervals."""
    try:
        threading.Thread(target=update_coldkeys).start()
        scheduler.enter(interval, 1, schedule_update_dataset, (scheduler, interval))
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in schedule_update_dataset (main.py): {e}")

def check_thread_status():
    try:
        with open('thread_status.status', 'r') as f:
            status = f.read().strip()
            return status
    except FileNotFoundError:
        return 'not running'
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in check_thread_status (main.py): {e}")
        return 'not running'

if __name__ == "__main__":
    init_sentry()
    
    try:
        bot_interval = 12  # Interval in seconds for running the bot
        update_dataset_interval = 86400  # Interval in seconds for updating the dataset (1 day)
        initial_delay = 86400  # Delay in seconds before starting the dataset update (1 hour)

        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(0, 1, schedule_bot, (scheduler, bot_interval))
        scheduler.enter(initial_delay, 1, schedule_update_dataset, (scheduler, update_dataset_interval))
        scheduler.run()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Exception in main (main.py): {e}")