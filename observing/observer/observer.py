import pytz
from datetime import datetime
from substrateinterface.base import SubstrateInterface
import bittensor as bt
import sqlite3
import sentry_sdk
from dotenv import load_dotenv
import os

load_dotenv()

def init_sentry():
    """
    Initializes the Sentry SDK to enable error tracking.
    """
    SENTRY_SDK = os.getenv('SENTRY_SDK')
    sentry_sdk.init(
        dsn=SENTRY_SDK,
        traces_sample_rate=1.0
    )

def setup_substrate_interface():
    """
    Initializes and returns a SubstrateInterface object configured to connect to a specified WebSocket URL.
    This interface will be used to interact with the blockchain.
    """
    SUBTENSOR_ENDPOINT = os.getenv('SUBTENSOR_ENDPOINT')
    return SubstrateInterface(
        url=SUBTENSOR_ENDPOINT,
        ss58_format=42,
        use_remote_preset=True,
    )

def get_block_data(substrate, block_number):
    """
    Retrieves block data and associated events from the blockchain for a given block number.
    """
    block_hash = substrate.get_block_hash(block_id=block_number)
    block = substrate.get_block(block_hash=block_hash)
    events = substrate.get_events(block_hash=block_hash)
    
    return block, events

def extract_block_timestamp(extrinsics):
    """
    Extracts the timestamp from a list of extrinsics by identifying the 'set' function call within the 'Timestamp' module.
    Returns the timestamp formatted as 'YYYY-MM-DD HH:MM:SS (UTC±X)'.
    """
    for extrinsic in extrinsics:
        extrinsic_value = getattr(extrinsic, 'value', None)
        if extrinsic_value and 'call' in extrinsic_value:
            call = extrinsic_value['call']
            if call['call_function'] == 'set' and call['call_module'] == 'Timestamp':
                # Convert timestamp from milliseconds to seconds
                timestamp = call['call_args'][0]['value'] / 1000
                # Create a timezone-aware datetime object
                dt_utc = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
                
                # Format the datetime to include UTC offset
                utc_offset = dt_utc.strftime('%z')
                formatted_offset = f'UTC{utc_offset[:3]}:{utc_offset[3:]}'              
                return dt_utc.strftime(f'%Y-%m-%d %H:%M:%S ({formatted_offset})')
            
    return None  # Return None if no valid timestamp is found

def check_extrinsic(extrinsics, func_schedule_swap_coldkey, func_schedule_dissolve_subnet, func_vote, module_name):
    """
    Checks for a specific extrinsic call in the list of extrinsics.
    Returns the index if found, otherwise -1.
    """
    schedule_swap_coldkey_idx, schedule_dissolve_network_idx, vote_idx = -1, -1, -1
    for idx, extrinsic in enumerate(extrinsics):
        extrinsic_value = getattr(extrinsic, 'value', None)
        if extrinsic_value and 'call' in extrinsic_value:
            call = extrinsic_value['call']
            if call['call_module'] == module_name:
                if call['call_function'] == func_schedule_swap_coldkey:
                    schedule_swap_coldkey_idx = idx
                elif call['call_function'] == func_schedule_dissolve_subnet:
                    schedule_dissolve_network_idx = idx
                elif call['call_function'] == func_vote:
                    vote_idx = idx
    
    return schedule_swap_coldkey_idx, schedule_dissolve_network_idx, vote_idx

def process_swap_extrinsics(extrinsic_events):
    """
    Processes extrinsic events related to coldkey swap and extracts relevant details.
    """
    for event in extrinsic_events:
        event_value = getattr(event, 'value', None)
        if event_value['event_id'] == 'ColdkeySwapScheduled':
            old_coldkey = event_value['attributes']['old_coldkey']
            new_coldkey = event_value['attributes']['new_coldkey']
            execution_block = event_value['attributes']['execution_block']
            return old_coldkey, new_coldkey, execution_block
    
    return None, None, None

def process_dissolve_extrinsics(extrinsic_events):
    """
    Processes extrinsic events related to network dissolve and extracts relevant details.
    """
    for event in extrinsic_events:
        event_value = getattr(event, 'value', None)
        if event_value['event_id'] == 'DissolveNetworkScheduled':
            netuid = event_value['attributes']['netuid']
            owner_coldkey = event_value['attributes']['account']
            execution_block = event_value['attributes']['execution_block']
            return netuid, owner_coldkey, execution_block
    
    return None, None, None

def check_success(events, idx):
    """
    Checks if an extrinsic was successful and collects its events.
    """
    extrinsic_events = []
    extrinsic_success = False
    for event in events:
        event_value = getattr(event, 'value', None)
        if event_value and event_value.get('extrinsic_idx') == idx:
            extrinsic_events.append(event)
            if event_value['event_id'] == 'ExtrinsicSuccess':
                extrinsic_success = True
    
    return extrinsic_events, extrinsic_success

def generate_report(title, success, details, time_stamp):
    """
    Generates a report based on the extrinsic success and details provided.
    """
    fields = [{
        "name": "🧱 **CURRENT BLOCK** 🧱",
        "value": f"{details['current_block_number']}\n\n",
        "inline": False
    }]
    if success:
        for key, value in details.items():
            if key != 'current_block_number':
                fields.append({
                    "name": f"\n\n🔑 **{key.upper()}** \n\n\n",
                    "value": f"{value}\n\n",
                    "inline": False
                })
    else:
        fields.append({
            "name": "🔴 **Extrinsic Failed** 🔴",
            "value": "The extrinsic failed to execute.",
            "inline": False
        })
    fields.append({
        "name": "\n\n🕙  **CURRENT BLOCK TIMESTAMP** \n\n\n",
        "value": f"{time_stamp}\n\n",
        "inline": False
    })
    
    return {
        "title": title,
        "description": "",
        "color": 16776960 if "COLDKEY" in title else 12910592,  # Different colors for different reports
        "fields": fields,
    }
    
def generate_vote_report(title, success, details, time_stamp):
    """
    Generates a report based on the extrinsic success and details provided.
    """
    fields = [{
        "name": "🧱 **CURRENT BLOCK** 🧱",
        "value": f"{details['current_block_number']}\n\n",
        "inline": False
    }]
    for key, value in details.items():
        if key != 'current_block_number':
            fields.append({
                "name": f"\n\n🔑 **{key.upper()}** \n\n\n",
                "value": f"{value}\n\n",
                "inline": False
            })
    if success:
        fields.append({
            "name": "🍏 **Extrinsic Successful** 🍏",
            "value": "The extrinsic executed successfully.",
            "inline": False
        })
    else:
        fields.append({
            "name": "🍎 **Extrinsic Failed** 🍎",
            "value": "The extrinsic failed to execute.",
            "inline": False
        })
    fields.append({
        "name": "\n\n🕙  **CURRENT BLOCK TIMESTAMP** \n\n\n",
        "value": f"{time_stamp}\n\n",
        "inline": False
    })
    
    return {
        "title": title,
        "description": "",
        "color": 14776960 if "COLDKEY" in title else 14776960,  # Different colors for different reports
        "fields": fields,
    }

def generate_dissolved_netword(title, details, time_stamp):
    fields = []
    for key, value in details.items():

        fields.append({
            "name": f"\n\n🧩 **{key.upper()}** \n\n\n",
            "value": f"{value}\n\n",
            "inline": False
        })  
    fields.append({
        "name": "\n\n🕙  **CURRENT BLOCK TIMESTAMP** \n\n\n",
        "value": f"{time_stamp}\n\n",
        "inline": False
    })
    
    return {
        "title": title,
        "description": "",
        "color": 16273827 if "COLDKEY" in title else 16273827,  # Different colors for different reports
        "fields": fields,
    }

def get_validator_name(coldkey, hotkey = None):
    """
    Retrieves the name and hot_key of a validator based on their coldkey.
    
    Parameters:
    coldkey (str): The coldkey of the validator.
    
    Returns:
    tuple: (name, hot_key, status) where name and hot_key are the values of the validator if found,
           otherwise None, and status is 1 if the coldkey exists, otherwise 0.
    """
    db_path = 'DB/db.sqlite3'  # Update this path to the actual location of your database
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if coldkey:
            cursor.execute('SELECT name, hot_key FROM validators WHERE cold_key = ?', (coldkey,))
            result = cursor.fetchone()
        else:
            cursor.execute('SELECT name, cold_key FROM validators WHERE hot_key = ?', (hotkey,))
            result = cursor.fetchone()
        if result:
            return result[0], result[1], 1
        else:
            return None, None, 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None, None, 0
    finally:
        if conn:
            conn.close()

def get_owner_name(coldkey):
    """
    Retrieves the name of the owner based on their coldkey.
    
    Parameters:
    coldkey (str): The coldkey of the owner.
    
    Returns:
    tuple: (name, status) where name is the value of the owner if found, otherwise None, and status is 1 if the coldkey exists, otherwise 0.
    """
    db_path = 'DB/db.sqlite3'  
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT net_uid FROM owners WHERE owner_coldkey = ?', (coldkey,))
        result = cursor.fetchone()
        # print(result)
        if result:
            return result[0]
        else:
            return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()
    
def process_vote(extrinsic):
    """
    Extracts specific parameters from the extrinsic data.

    Parameters:
    extrinsic (GenericExtrinsic): The extrinsic data.

    Returns:
    dict: A dictionary containing the extracted parameters.
    """
    call_args = extrinsic.value['call']['call_args']

    for arg in call_args:
        if arg['name'] == 'hotkey':
            hotkey = arg['value']
        elif arg['name'] == 'proposal':
            proposal = arg['value']
        elif arg['name'] == 'approve':
            approve = arg['value']
        elif arg['name'] == 'index':
            index = arg['value']

    return hotkey, proposal, approve, index

def check_events(events, swap_event, dissolve_event):
    """
    Checks for specific events in the list of events.
    """
    swapped_old_coldkey, swapped_new_coldkey, dissolved_network_uid = None, None, None
    for idx, event in enumerate(events):
        event_value = getattr(event, 'value', None)
        if event_value and event_value.get('event_id') == swap_event:
            swapped_old_coldkey = event_value['attributes'].get('old_coldkey')
            swapped_new_coldkey = event_value['attributes'].get('new_coldkey')
            
        elif event_value and event_value.get('event_id') == dissolve_event:
            dissolved_network_uid = event_value.get('attributes')

    return swapped_old_coldkey, swapped_new_coldkey, dissolved_network_uid

def find_dissolve_subnet( block, events):
    """
    Finds and processes a scheduled network dissolve in the given block number.
    """
    idx = check_extrinsic(block['extrinsics'], 'schedule_dissolve_network', 'SubtensorModule')
    if idx >= 0:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, idx)
        netuid, owner_coldkey, execution_block = process_dissolve_extrinsics(extrinsic_events) if extrinsic_success else (None, None, None)
        return idx, extrinsic_success, netuid, owner_coldkey, execution_block, time_stamp
    return -1, False, None, None, None, None

def find_swap_coldkey(block, events):
    """
    Finds and processes a scheduled coldkey swap in the given block number.
    """
    idx = check_extrinsic(block['extrinsics'], 'schedule_swap_coldkey', 'SubtensorModule')
    if idx >= 0:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, idx)
        old_coldkey, new_coldkey, execution_block = process_swap_extrinsics(extrinsic_events) if extrinsic_success else (None, None, None)
        return idx, extrinsic_success, new_coldkey, old_coldkey, execution_block, time_stamp
    return -1, False, None, None, None, None

def observer_block():
    """
    Observes the current block for scheduled coldkey swaps and network dissolves, generating reports for each.
    """
    substrate = setup_substrate_interface()
    current_block_number = bt.subtensor().get_current_block()
    
    #block numbers for testing
    # current_block_number = 3941423  # schdule swap coldkey
    # current_block_number = 3877258  # schedule dissolve network
    # current_block_number = 3956804  # vote
    # current_block_number = 3913258  # dissolved network
    current_block_number = 3948498  # coldkey swapped
    
    block, events = get_block_data(substrate, current_block_number)
    schedule_swap_coldkey_report, schedule_dissolve_subnet_report, vote_report, dissloved_subnet_resport, swapped_coldkey_report = None, None, None, None, None
    should_db_update = False
    
    # Check for extrinsics related to scheduled coldkey swap and network dissolve
    schedule_swap_coldkey_idx, schedule_dissolve_network_idx, vote_idx = check_extrinsic(block['extrinsics'], 'schedule_swap_coldkey', 'schedule_dissolve_network', 'vote', 'SubtensorModule')
    # Check for events related to coldkey swap and network dissolve
    swapped_old_coldkey, swapped_new_coldkey, dissolved_network_uid = check_events(events, 'ColdkeySwapped', 'NetworkRemoved')
    
    
    # Check for scheduled coldkey swap
    if schedule_swap_coldkey_idx >= 0:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, schedule_swap_coldkey_idx)
        old_coldkey, new_coldkey, execution_block = process_swap_extrinsics(extrinsic_events) if extrinsic_success else (None, None, None)
        old_coldkey = "5Cyfk5Jjee6uCafjZyUUjtKd7Q4qh1yJ48Ts7bkT9xXaDqe1"
        validator_name, validator_hotkey, check_validator = get_validator_name(old_coldkey)
        link = f"https://taostats.io/validators/{validator_hotkey}"
        original_coldkey = old_coldkey
        if check_validator:
            if validator_name:
                old_coldkey = old_coldkey + f"\n(Validator : [{validator_name}]({link}))"
            else: 
                old_coldkey = old_coldkey + f"\n(Validator : [no name]({link}))"
        netuid = get_owner_name(original_coldkey)
        if netuid:
            print("netuid", netuid)
            link = f"https://taostats.io/subnets/{netuid}/metagraph"
            old_coldkey = f"{old_coldkey}\n([subnet{netuid} owner]({link}))" 
        details = {
            "current_block_number": current_block_number,
            "old_coldkey": old_coldkey,
            "new_coldkey": new_coldkey,
            "execution_block": execution_block
        }
        schedule_swap_coldkey_report = generate_report("📅 __ NEW SCHEDULE_SWAP_COLDKEY DETECTED __ 📅", extrinsic_success, details, time_stamp)


    # Check for scheduled network dissolve
    if schedule_dissolve_network_idx >= 0:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, schedule_dissolve_network_idx)
        netuid, owner_coldkey, execution_block = process_dissolve_extrinsics(extrinsic_events) if extrinsic_success else (None, None, None)
        link = f"https://taostats.io/subnets/{netuid}/metagraph"
        netuid = f"[{netuid}]({link})"
        details = {
            "current_block_number": current_block_number,
            "netuid": netuid,
            "owner_coldkey": owner_coldkey,
            "execution_block": execution_block
        }
        schedule_dissolve_subnet_report = generate_report("⏳ __SCHEDULE_NETWORK_DISSOLVE DETECTED__ ⏳", extrinsic_success, details, time_stamp)


    # Check for vote
    if vote_idx >= 0:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, vote_idx)
        hotkey, proposal, approve, index = process_vote(block['extrinsics'][vote_idx])
        hotkey = "5HNQURvmjjYhTSksi8Wfsw676b4owGwfLR2BFAQzG7H3HhYf"
        validator_name, validator_coldkey, check_validator = get_validator_name(None, hotkey)
        link = f"https://taostats.io/validators/{hotkey}"
        if check_validator:
            if validator_name:
                hotkey = hotkey + f"\n([{validator_name}]({link}))"
            else: 
                hotkey = hotkey + f"\n([no name]({link}))"
        details = {
            "current_block_number": current_block_number,
            "hotkey": hotkey,
            "proposal": proposal,
            "index": index,
            "approve": approve,
        }
        vote_report = generate_vote_report("🗳️ __ NEW VOTE DETECTED __ 🗳️", extrinsic_success, details, time_stamp)
    
    
    # Check for coldkey swapped
    if swapped_old_coldkey:
        
        swapped_old_coldkey = "5Cyfk5Jjee6uCafjZyUUjtKd7Q4qh1yJ48Ts7bkT9xXaDqe1"
        time_stamp = extract_block_timestamp(block['extrinsics'])
        validator_name, validator_hotkey, check_validator = get_validator_name(swapped_old_coldkey)
        link = f"https://taostats.io/validators/{validator_hotkey}"
        original_coldkey = swapped_old_coldkey
        if check_validator:  
            if validator_name:
                swapped_old_coldkey = swapped_old_coldkey + f"\n(Validator : [{validator_name}]({link}))"
            else: 
                swapped_old_coldkey = swapped_old_coldkey + f"\n(Validator : [no name]({link}))" 
        netuid = get_owner_name(original_coldkey)
        if netuid:
            print("netuid", netuid)
            link = f"https://taostats.io/subnets/{netuid}/metagraph"
            swapped_old_coldkey = f"{swapped_old_coldkey}\n([subnet{netuid} owner]({link}))"       
        details = {
            "current_block_number": current_block_number,
            "old_coldkey": swapped_old_coldkey,
            "new_coldkey": swapped_new_coldkey,
        }
        swapped_coldkey_report = generate_report(" __😍 COLDKEY SWAPPED 😍__ ", True, details, time_stamp)
        should_db_update = True
    
    #Check for dissolved network
    if dissolved_network_uid:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        details = {
            "current_block_number": current_block_number,
            "netuid": dissolved_network_uid,
        }
        dissloved_subnet_resport = generate_dissolved_netword("😯 __ NETWORK DESSOLVED __ 😯", details, time_stamp)
        should_db_update = True

    return schedule_swap_coldkey_report, schedule_dissolve_subnet_report, vote_report, dissloved_subnet_resport, swapped_coldkey_report, should_db_update

