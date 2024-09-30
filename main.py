# This script initializes the main repository and repository family in the database,
# and continuously runs a specified script at defined intervals.
#
# Functions:
# - run_bot: Runs a specified Python script in a loop with a delay between executions.

import subprocess
import time
from observing.utils.database import init_main_repo, init_repo_fam
import os

def create_db_directory():
    """Creates a db directory in the same directory as main.py if it doesn't exist."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(script_dir, "db")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Created directory: {db_dir}")
    else:
        print(f"Directory already exists: {db_dir}")

def run_bot(timestamp):
    """Runs a specified script continuously with a delay specified by timestamp."""
    while True:
        subprocess.run(['python', 'run.py'])  # Replace 'run.py' with the actual filename if different
        time.sleep(timestamp)  # Delay for the specified time in seconds

if __name__ == "__main__":
    start_time = time.time()
    print(f"initializing started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    create_db_directory()  # Create a db directory in the home directory
    # init_main_repo()  # Initialize the main repository in the database
    # init_repo_fam()   # Initialize the repository family in the database
    timestamp = 60  # Delay in seconds
    run_bot(timestamp)
