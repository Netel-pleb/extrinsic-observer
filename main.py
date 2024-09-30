# This script initializes the main repository and repository family in the database,
# and continuously runs a specified script at defined intervals.
#
# Functions:
# - run_bot: Runs a specified Python script in a loop with a delay between executions.

import subprocess
import time


def run_bot(timestamp):
    """Runs a specified script continuously with a delay specified by timestamp."""
    while True:
        subprocess.run(['python', 'run.py'])  # Replace 'run.py' with the actual filename if different
        time.sleep(timestamp)  # Delay for the specified time in seconds

if __name__ == "__main__":
    start_time = time.time()
    print(f"initializing started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    timestamp = 120000  # Delay in seconds
    run_bot(timestamp)
