import pytz
from datetime import datetime
from substrateinterface.base import SubstrateInterface
import bittensor as bt

def setup_substrate_interface():
    """
    Initializes and returns a SubstrateInterface object configured to connect to a specified WebSocket URL.
    This interface will be used to interact with the blockchain.
    """
    return SubstrateInterface(
        url="wss://archive.chain.opentensor.ai:443/",
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
    """
    for extrinsic in extrinsics:
        extrinsic_value = getattr(extrinsic, 'value', None)
        if extrinsic_value and 'call' in extrinsic_value:
            call = extrinsic_value['call']
            if call['call_function'] == 'set' and call['call_module'] == 'Timestamp':
                return datetime.fromtimestamp(call['call_args'][0]['value'] / 1000, tz=pytz.UTC)
    return None

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
        "color": 642600 if "COLDKEY" in title else 342600,  # Different colors for different reports
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
            "name": "🟢 **Extrinsic Successful** 🟢",
            "value": "The extrinsic executed successfully.",
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
        "color": 642600 if "COLDKEY" in title else 342600,  # Different colors for different reports
        "fields": fields,
    }

def get_validator_name(coldkey):
    """
    Retrieves the name of a validator based on their hotkey.
    """

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
    # current_block_number = 3941423  # Example block number
    # current_block_number = 3877258
    current_block_number = 3956804
    block, events = get_block_data(substrate, current_block_number)
    schedule_swap_coldkey_report, schedule_dissolve_subnet_report, vote_report = None, None, None
    
    # Check for extrinsics related to scheduled coldkey swap and network dissolve
    schedule_swap_coldkey_idx, schedule_dissolve_network_idx, vote_idx = check_extrinsic(block['extrinsics'], 'schedule_swap_coldkey', 'schedule_dissolve_network', 'vote', 'SubtensorModule')
    
    #check for scheduled coldkey swap
    if schedule_swap_coldkey_idx >= 0:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, schedule_swap_coldkey_idx)
        old_coldkey, new_coldkey, execution_block = process_swap_extrinsics(extrinsic_events) if extrinsic_success else (None, None, None)
        validator_name, check_validator = get_validator_name(new_coldkey)
        details = {
            "current_block_number": current_block_number,
            "old_coldkey": old_coldkey,
            "new_coldkey": new_coldkey,
            "execution_block": execution_block
        }
        schedule_swap_coldkey_report = generate_report("🌟 __ NEW SCHEDULE_SWAP_COLDKEY DETECTED __ 🌟", extrinsic_success, details, time_stamp)

    # Check for scheduled network dissolve
    if schedule_dissolve_network_idx >= 0:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, schedule_dissolve_network_idx)
        netuid, owner_coldkey, execution_block = process_dissolve_extrinsics(extrinsic_events) if extrinsic_success else (None, None, None)
        details = {
            "current_block_number": current_block_number,
            "netuid": netuid,
            "owner_coldkey": owner_coldkey,
            "execution_block": execution_block
        }
        schedule_dissolve_subnet_report = generate_report("🌟 __ NEW SCHEDULE_NETWORK_DISSOLVE DETECTED __ 🌟", extrinsic_success, details, time_stamp)

    #check for vote
    if vote_idx >= 0:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, vote_idx)
        hotkey, proposal, approve, index = process_vote(block['extrinsics'][vote_idx])
             
        details = {
            "current_block_number": current_block_number,
            "hotkey": hotkey,
            "proposal": proposal,
            "index": index,
            "approve": approve,
        }
        vote_report = generate_vote_report("🌟 __ NEW VOTE DETECTED __ 🌟", extrinsic_success, details, time_stamp)
        

    swap_coldkey_idx, dissolve_network_idx = check_events(events, 'NetworkRemoved', 'ColdkeySwapped')

    return schedule_swap_coldkey_report, schedule_dissolve_subnet_report, vote_report
