import subprocess
import time
import sched

def run_bot(scheduler, interval):
    """Runs a specified script and reschedules itself to run again after the interval."""
    start_time = time.time()
    subprocess.run(['python', 'run.py'])  # Replace 'run.py' with the actual filename if different
    end_time = time.time()
    elapsed_time = end_time - start_time
    next_run = max(0, interval - elapsed_time)
    scheduler.enter(next_run, 1, run_bot, (scheduler, interval))

if __name__ == "__main__":
    interval = 12  # Interval in seconds
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(0, 1, run_bot, (scheduler, interval))
    scheduler.run()