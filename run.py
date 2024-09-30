
# This script orchestrates the process of monitoring a GitHub repository.
# It fetches repository data, compares current and previous states, generates reports on pull requests and branches,
# and posts these reports to Discord.

from observing.bot.bot import post_to_discord
from observing.utils.database import load_previous_main_repo, update_main_repo, update_database_with_branches
from observing.observer.observer import observer_block
from github import Github
from dotenv import load_dotenv
import os
import time

def run():
    start_time = time.time()
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    load_dotenv()

    # Load the previous state from the database
    previous_state = load_previous_main_repo()
    
    # Fetch current fork branches and main repository data
    access_token = os.getenv('GIT_ACCESS_TOKEN')
    g = Github(access_token)
    main_repo = g.get_repo(os.getenv('MAIN_REPO'))
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    # Gather pull requests and branches from the main repository
    main_prs = {pr.number: pr.state for pr in main_repo.get_pulls(state='all')}
    main_branches = [branch.name for branch in main_repo.get_branches()]

    # Prepare current state dictionary
    current_state = {
        "branches": main_branches,
        "prs": {int(key): value for key, value in main_prs.items()}
    }
    previous_state["prs"] = {int(key): value for key, value in previous_state["prs"].items()}

    # Find open and merged pull requests
    report_prs = find_open_merged_pr(previous_state, current_state, main_repo)
    print("Merged PR report")
    # print(report_prs)
    post_to_discord(report_prs, DISCORD_WEBHOOK_URL)

    # Generate branch reports
    branches_report, merged_branches_without_pr_report = branch_movements()
    post_to_discord(branches_report, DISCORD_WEBHOOK_URL)
    post_to_discord(merged_branches_without_pr_report, DISCORD_WEBHOOK_URL)
    print("Branch report")

    # Update the database with the current state
    # update_main_repo(current_state)
    # update_database_with_branches()
    print("Database update")
    end_time = time.time()
    print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"Time consumed: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    run()
